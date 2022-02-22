import mysql.connector
import os
import praw
from datetime import datetime


def GetAuthourId(mydb, username, commentUTC):
    """Obtiene el ID del autor del comentario desde la base de datos
    
    En caso de no encontrar el usuario, se crea la entrada en la base de datos
    y se asocia la fecha del comentario como su primer comentario publicado
    en un Random
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    username : str
        Username del autor
    commentUTC : int
        TimeStamp (en segundos) del comentario
    
    Returns
    -------
    int
        ID del usuario en la base de datos
    """
    
    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT `user_id` FROM `chile_users` WHERE `user_username` LIKE %s LIMIT 1', (username, ))
    if cursor.rowcount <= 0:
        #Hay que pasar de TimeStamp a DateTime para usarlo en la base de datos
        commentDate = datetime.fromtimestamp(commentUTC).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO `chile_users`(`user_username`, `user_first_comment`) VALUES (%s,%s)', (username, commentDate))
        mydb.commit()
        return cursor.lastrowid
    else:
        result = cursor.fetchone()
        return result[0]

def GetCommentLevel(mydb, reddit, commentParentRID, randomRID):
    """Obtiene el nivel del comentario en el árbol del Random
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    reddit : praw.Reddit
        Instancia de Reddit
    commentParentRID : str
        ID de Reddit para el comentario padre
    randomRID : str
        ID de Reddit para el Random
    
    Returns
    -------
    int
        0 en caso de ser un comentario inicial.
        Mayor que 0 en caso de ser una respuesta a un comentario anterior
    """
    
    #Si el padre tiene la misma ID del Random significa que es un comentario principal
    if commentParentRID == randomRID:
        return 0
    
    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT `comment_level` FROM `random_comments` WHERE `comment_reddit_id` = %s LIMIT 1', (commentParentRID, ))
    if cursor.rowcount <= 0:
        level = 0
        parentId = commentParentRID
        #Técnicamente este While nunca debería detenerse por su condición ya que
        #para eso está el break, pero igual por si acaso
        while parentId != randomRID:
            level = level + 1
            parentId = reddit.comment(parentId).parent_id
            if parentId.startswith('t3_'):
                break
        return level
    else:
        result = cursor.fetchone()
        return result[0] + 1

def GetRandomPostId(mydb, reddit, randomRID):
    """Obtiene el ID del Random desde la base de datos
    
    En caso de no encontrar el Random, se crea la entrada en la base de datos
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    reddit : praw.Reddit
        Instancia de Reddit
    randomRID : str
        ID de Reddit para el Random
    
    Returns
    -------
    int
        ID del Random en la base de datos
    """

    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT `post_id` FROM `random_posts` WHERE `post_reddit_id` = %s LIMIT 1', (randomRID, ))
    if cursor.rowcount <= 0:
        #Con esto podemos obtener el número de la semana de un TimeStamp (Y su año)
        randomPostDate = datetime.utcfromtimestamp(reddit.submission(id = randomRID).created_utc)
        randomPostDateIso = randomPostDate.date().isocalendar()
        
        #randomPostDateIso[1] -> Semana
        #randomPostDateIso[0] -> Año
        cursor.execute('INSERT INTO `random_posts`(`post_reddit_id`, `post_week`, `post_year`) VALUES (%s,%s,%s)', (randomRID, randomPostDateIso[1], randomPostDateIso[0]))
        mydb.commit()
        return cursor.lastrowid
    else:
        result = cursor.fetchone()
        return result[0]

def InsertComment(mydb, commentRID, commentLevel, authorId, randomId, commentUTC, commentNumber):
    """Inserta el comentario en la base de datos
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    commentRID : str
        ID de Reddit para el comentario
    commentLevel : int
        Nivel del comentario en el árbol del Random
    authorId : int
        ID del autor del comentario
    randomId : int
        ID del Random
    commentUTC : int
        TimeStamp (en segundos) del comentario
    commentNumber : int
        Número del comentario dentro del Random
    
    Returns
    -------
    Boolean
        True en caso de que se pudo insertar el comentario. False en caso contrario
    """

    cursor = mydb.cursor(buffered=True)
    cursor.execute('SELECT `comment_id` FROM `random_comments` WHERE `comment_reddit_id` = %s LIMIT 1', (commentRID, ))
    #Hay que evitar subir el mismo Comentario dos veces para que no se cuente de más
    if cursor.rowcount > 0:
        print('WARN: Comment', commentRID, 'is already in database. Ignoring...')
        return False
    
    commentDate = datetime.fromtimestamp(commentUTC).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO `random_comments`(`comment_reddit_id`, `comment_level`, `comment_user_id`, `comment_random_id`, `comment_UTC`, `comment_number`) VALUES (%s,%s,%s,%s,%s,%s)', (commentRID, commentLevel, authorId, randomId, commentDate, commentNumber))
    mydb.commit()
    return True

if __name__ == '__main__':
    print('Starting RandomBot')
    #Instancia de Reddit
    print('Connecting to Reddit')
    reddit = praw.Reddit(
        client_id = os.environ['r_client_id'],
        client_secret = os.environ['r_client_secret'],
        user_agent = 'rChileRandom Bot 0.1'
    )
    #Instancia de MySQL
    print('Connecting to DataBase')
    mydb = mysql.connector.connect(
        host = os.environ['db_host'],
        user = os.environ['db_user'],
        password = os.environ['db_pass'],
        database = os.environ['db_database']
    )
    
    #Este for nunca se termina ya que es un Stream
    print('Watching for new comments on r/Chile')
    for comment in reddit.subreddit('chile').stream.comments():
        #Hay que comprobar que el creador del Random sea el AutoModerator
        #para evitar que un usuario cree un post fraudulento.
        #
        #Si un Mod empieza a crear por su cuenta el Random como era antes hay que cambiar
        #esta linea
        if comment.link_title.lower() != 'discusión random semanal' or comment.link_author.lower() != 'automoderator':
            continue
        
        #Ya que el ID de Reddit puede contener un identificador antes del ID,
        #hay que obtener todo lo que se encuentre a la derecha de un '_'
        randomRID = comment.link_id.split('_', 1)[-1]
        #Nota: commentAuthor es una instancia de un User de Reddit
        commentAuthor = comment.author
        commentRID = comment.id
        commentNumber = comment.num_comments
        commentParentRID = comment.parent_id.split('_', 1)[-1]
        commentUTC = comment.created_utc
        
        authorId = GetAuthourId(mydb, commentAuthor.name, commentUTC)
        commentLevel = GetCommentLevel(mydb, reddit, commentParentRID, randomRID)
        randomId = GetRandomPostId(mydb, reddit, randomRID)
        
        if InsertComment(mydb, commentRID, commentLevel, authorId, randomId, commentUTC, commentNumber):
            print('Comment', commentRID, 'from Random', randomRID, 'added successfully')
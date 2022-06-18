import mysql.connector
import os
import praw
import re
from datetime import datetime, timedelta
from git import Repo

IsTesting = True
if 'prod' in os.environ and os.environ['prod'] == '1':
    IsTesting = False

def CommentTop3ToRandom(mydb):
    """Comenta el Top3 del random anterior en el Random actual solo los lunes en la mañana
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    """

    today = datetime.today()
    if (today.weekday() != 0 or today.hour >= 15) and not IsTesting:
        return
    
    prevRandomPostDateIso = (today - timedelta(days=1)).date().isocalendar()
    
    #prevRandomPostDateIso[1] -> Semana
    #prevRandomPostDateIso[0] -> Año
    prevRandomWeek = prevRandomPostDateIso[1]
    prevRandomYear = prevRandomPostDateIso[0]
    
    prevRandom, topUsers = GetTopForRandomByWeek(mydb, prevRandomWeek, prevRandomYear, 3)
    if prevRandom is None or topUsers is None:
        return
    
    print('Connecting to Reddit')
    reddit = praw.Reddit(
        client_id = os.environ['r_client_id'],
        client_secret = os.environ['r_client_secret'],
        user_agent = 'rChileRandom Bot 0.1',
        username=os.environ['r_username'],
        password=os.environ['r_password']
    )
    
    randomsList = reddit.subreddit('chile').search('Discusión random semanal', sort='new', time_filter='week')
    currentRandom = None
    for random in randomsList:
        if random.stickied:
            currentRandom = random
            break
    if currentRandom is None:
        print('WARN: Current Random Not Found')
        return
    
    topMessage = """Estos son los usuarios con más mensajes en el [**Hilo Random anterior**](https://www.reddit.com/r/chile/comments/""" + prevRandom['reddit_id'] + """/discusi%C3%B3n_random_semanal/):

Lugar | Usuario | Comentarios
:--:|:--:|:--:"""
    topMedals = [ '🥇', '🥈', '🥉' ]
    topCount = 0
    for user in topUsers:
        topMessage = topMessage + '\n' + topMedals[topCount] + '|**' + user['user'] + '**|' + str(user['count'])
        topCount = topCount + 1
    
    topMessage = topMessage + """

Para ver todos los datos, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly/""" + str(prevRandomYear) + '_' + str(prevRandomWeek) + """_comments.csv)

Para ver los datos del hilo actual, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly/current_comments.csv)
""" + GetInfoText()
    
    if IsTesting:
        topMessage = topMessage + '\n\nEste mensaje debería haberse publicado en el hilo ' + currentRandom.url
        print(topMessage)
        botUser = reddit.redditor('rChileRandomBot').message('TEST', topMessage)
    else:
        currentRandom.reply(topMessage)

def GetAllRandoms(mydb):
    """Obtiene todos los Hilos Randoms almacenados en la base de datos
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    
    Returns
    -------
    list
        Listado de diccionarios con las llaves 'id', 'week', 'year' y 'last_comment'
    """
    
    cursor = mydb.cursor(dictionary=True)
    query = """SELECT `post_id` as `id`, `post_week` as `week`, `post_year` as `year`, UNIX_TIMESTAMP(MAX(`comment_UTC`)) as `last_comment` FROM `random_posts`
            LEFT JOIN `random_comments` ON `post_id` = `comment_random_id`
            GROUP BY `post_id`
            ORDER BY `post_year` DESC, `post_week` DESC"""
    cursor.execute(query)
    result = cursor.fetchall()
    
    return result

def GetAllUsersStats(mydb):
    """Obtiene las estádisticas de todos los usuarios que comentaron en todos
    los Hilos Random
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    
    Returns
    -------
    list
        Listado de diccionarios con las llaves 'user' y 'count'
    """
    
    cursor = mydb.cursor(dictionary=True)
    query = """SELECT `user_username` as `user`, COUNT(`comment_id`) as `count` FROM `random_comments`
            INNER JOIN `chile_users` ON `comment_user_id` = `user_id`
            GROUP BY `comment_user_id`
            ORDER BY `count` DESC"""
    cursor.execute(query)
    result = cursor.fetchall()
    
    return result

def GetInfoText():
    """Genera y devuelve el Texto de Más Info para los comentarios
    
    Returns
    -------
    MultiLine String
        Texto de Más Info
    """
    
    return """
___

Soy un bot y este mensaje fue realizado automáticamente. [**Más información**](https://github.com/JPZV/rChileRandom-Bot/)
"""

def GetRandomByWeek(mydb, week, year):
    """Obtiene el Hilo Random según su año y número de semana
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    week : int
        Número de semana del Random
    year : int
        Año del Random
    
    Returns
    -------
    dict
        Diccionario con las llaves 'id', 'week', 'year' y 'last_comment'
    """
    
    cursor = mydb.cursor(dictionary=True)
    query = """SELECT `post_id` as `id`, `post_week` as `week`, `post_year` as `year`, `post_reddit_id` as `reddit_id`, UNIX_TIMESTAMP(MAX(`comment_UTC`)) as `last_comment` FROM `random_posts`
            LEFT JOIN `random_comments` ON `post_id` = `comment_random_id`
            WHERE `post_year` = %s AND `post_week` = %s
            GROUP BY `post_id`"""
    cursor.execute(query, (year, week))
    result = cursor.fetchone()
    
    return result

def GetTopForRandomByWeek(mydb, week, year, amount):
    """Obtiene el Top de un Random por semana y año
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    week : int
        Número de la semana
    year : int
        Año en formato YYYY
    amount : int
        Cantidad de entradas a buscar
    
    Returns
    -------
    tuple (Dict<Random>, List<User>)
        El primer valor es un diccionario obtenido por GetRandomByWeek(mydb, week, year)
        El segundo valor es un listado de diccionarios con las llaves 'user' y 'count'
    """

    prevRandom = GetRandomByWeek(mydb, week, year)
    if prevRandom is None:
        print('WARN: Entry not found for Random ', week, '-', year)
        return (None,None)
    
    randomData = GetUsersStatsByRandom(mydb, prevRandom['id'])
    if randomData == None:
        print('WARN: Data not found for Random ', week, '-', year)
        return (None,None)
    
    topUsers = []
    topCount = 0
    for data in randomData:
        topUsers.append(data)
        topCount = topCount + 1
        if topCount >= amount:
            break
    
    if len(topUsers) <= 0:
        print('WARN: No users for Random ', week, '-', year)
        return (None,None)
    
    return (prevRandom, topUsers)

def GetUsersStatsByRandom(mydb, randomId):
    """Obtiene las estádisticas de todos los usuarios que comentaron en un
    Hilo Random en específico
    
    Parameters
    ----------
    mydb : connection.MySQLConnection
        Instancia de la base de datos
    randomId : int
        ID del Random
    
    Returns
    -------
    list
        Listado de diccionarios con las llaves 'user' y 'count'
    """
    
    cursor = mydb.cursor(dictionary=True)
    query = """SELECT `user_username` as `user`, COUNT(`comment_id`) as `count` FROM `random_comments`
            INNER JOIN `chile_users` ON `comment_user_id` = `user_id`
            WHERE `comment_random_id` = %s
            GROUP BY `comment_user_id`
            ORDER BY `count` DESC"""
    cursor.execute(query, (randomId, ))
    result = cursor.fetchall()
    
    return result

def PrepareFolders():
    """Crea todas las carpetas necesarias para almacenar los datos
    """
    
    if not os.path.exists('./Data/weekly'):
        os.makedirs('./Data/weekly')
    
def PushUpdatedData():
    """Sube todos los datos actualizados al Git
    """
    
    today = datetime.now()

    repo = Repo('./Data/.git')
    repo.git.add(all=True)
    repo.index.commit('Data updated until ' + today.strftime('%Y-%m-%d'))
    origin = repo.remote(name='origin')
    origin.push()

def WriteCSVFileWithStats(stats, file):
    """Escribe los datos estadísticos de los usuarios en la
    instancia del archivo .csv
    
    Parameters
    ----------
    stats : list
        Listado de diccionarios con las llaves 'user' y 'count'
    file : File
        Archivo .csv donde se escribiran los datos
    """
    #Solo vamos a escribir un .csv, así que no creo necesario implementar
    #una librería de .csv (Ni aunque fueramos NodeJS)
    file.write('Usuario,Comentarios\n')
    for stat in stats:
        file.write(stat['user'] + ',' + str(stat['count']) + '\n')
    file.close()

if __name__ == '__main__':
    #Si bien no es necesario que sea la primera llamada, prefiero que así lo
    #sea para evitar seguir procesando si hay un problema con el
    #almacenamiento desde un principio
    PrepareFolders()

    #Instancia de MySQL
    mydb = mysql.connector.connect(
        host = os.environ['db_host'],
        user = os.environ['db_user'],
        password = os.environ['db_pass'],
        database = os.environ['db_database']
    )
    
    #Ocuparemos esto para comprobar el Random después
    todayIso = datetime.now().date().isocalendar()
    
    randoms = GetAllRandoms(mydb)
    for random in randoms:
        randomFileName = './Data/weekly/' + str(random['year']) + '_' + str(random['week'])
        #Comprobamos si el Random actual corresponde a la de esta semana
        #NOTA: Esto generará un problema los lunes entre las 00:00 y las 05:59,
        #en donde se confundirá cual es el hilo actual, aunque si se corre
        #este programa a las 07:00 no debería haber problema
        
        #todayIso[1] -> Semana
        #todayIso[0] -> Año
        if todayIso[0] == random['year'] and todayIso[1] == random['week']:
            randomFileName = './Data/weekly/current'
        
        try:
            metaFile = open(randomFileName + '.meta', 'r')
            metaData = metaFile.read()
            metaFile.close()
            lastCommentRe = re.search('last_comment=(.+)', metaData)
            #Comprobamos que no haya actividad nueva en el Hilo
            if lastCommentRe and int(lastCommentRe.group(1)) >= random['last_comment']:
                continue
        except FileNotFoundError:
            pass
        except ValueError:
            pass
        
        usersStats = GetUsersStatsByRandom(mydb, random['id'])
        
        WriteCSVFileWithStats(usersStats, open(randomFileName + '_comments.csv', 'w'))
        
        metaFile = open(randomFileName + '.meta', 'w')
        #Guardamos el último comentario publicado para ahorrar recursos
        #en el futuro
        metaFile.write('last_comment=' + str(random['last_comment']))
        metaFile.close()
    
    allStats = GetAllUsersStats(mydb)
    WriteCSVFileWithStats(allStats, open('./Data/Users_comments.csv', 'w'))
    
    if not IsTesting:
        PushUpdatedData()
    
    CommentTop3ToRandom(mydb)
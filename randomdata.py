import mysql.connector
import os
import re
from datetime import datetime
from git import Repo

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

def GetRandomUsersStats(mydb, randomId):
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
        
        usersStats = GetRandomUsersStats(mydb, random['id'])
        
        weekFile = open(randomFileName + '_comments.csv', 'w')
        #Solo vamos a escribir un .csv, así que no creo necesario implementar
        #una librería de .csv (Ni aunque fueramos NodeJS)
        weekFile.write('Usuario,Comentarios\n')
        for stats in usersStats:
            weekFile.write(stats['user'] + ',' + str(stats['count']) + '\n')
        weekFile.close()
        
        metaFile = open(randomFileName + '.meta', 'w')
        #Guardamos el último comentario publicado para ahorrar recursos
        #en el futuro
        metaFile.write('last_comment=' + str(random['last_comment']))
        metaFile.close()
    
    PushUpdatedData()
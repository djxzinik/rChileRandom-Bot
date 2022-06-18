from .BaseInterpreter import BaseInterpreter
import randomdata
from datetime import datetime, timedelta

class TopInterpreter(BaseInterpreter):
    """ Clase para interpretar y mostrar la tabla de Tops
    """

    def __init__(self, mydb):
        """ Constructor de la clase
        
        Parameters
        ----------
        mydb : connection.MySQLConnection
            Instancia de la base de datos
        """
        BaseInterpreter.__init__(self, mydb, __class__.__name__)
        
        self.cmd = 'top'
    
    def CanInterpretate(self, command):
        """ Comprueba que el comando se puede interpretar con este interpretador
        
        Parameters
        ----------
        command : String
            Comando ingresado por el usuario (incluye parámetros)
        
        Returns
        -------
        Boolean
            True en caso de que se puede interpretar el comando. False en caso contrario
        """
    
        return command is not None and command.startswith(self.cmd)
    
    def Interpretate(self, command, comment):
        """ Interpreta el comando
        
        Parameters
        ----------
        command : String
            Comando ingresado por el usuario (incluye parámetros)
        comment : praw.models.Comment
            Comentario de donde provino el comando
        """
        
        realCmd = command.split(maxsplit=1)[0]
        arg = realCmd[len(self.cmd):]
        maxTop = self.IntTryParse(arg)
        if maxTop is None or maxTop <= 0:
            maxTop = 3
        elif maxTop > 50:
            maxTop = 25
        
        if comment is None:
            return
        
        randomPostDateIso = datetime.today().date().isocalendar()
        #randomPostDateIso[1] -> Semana
        #randomPostDateIso[0] -> Año
        randomWeek = randomPostDateIso[1]
        randomYear = randomPostDateIso[0]
        
        random, topUsers = randomdata.GetTopForRandomByWeek(self.MyDB, randomWeek, randomYear, maxTop)
        if random is None or topUsers is None:
            randomPostDateIso = (datetime.today() - timedelta(days=1)).date().isocalendar()
            #randomPostDateIso[1] -> Semana
            #randomPostDateIso[0] -> Año
            randomWeek = randomPostDateIso[1]
            randomYear = randomPostDateIso[0]
            
            random, topUsers = randomdata.GetTopForRandomByWeek(self.MyDB, randomWeek, randomYear, maxTop)
            if random is None or topUsers is None:
                errorMessage = """Lo siento, no pude encontrar los datos para este Hilo Random.

Por favor, intenta nuevamente más tarde. También puedes ver los últimos datos que tengo [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly/current_comments.csv)
""" + randomdata.GetInfoText()
                
                comment.reply(errorMessage)
                return
        
        topMessage = """Estos son los usuarios con más mensajes en el Hilo Random actual:

Lugar | Usuario | Comentarios
:--:|:--:|:--:"""
        topMedals = [ '🥇', '🥈', '🥉' ]
        topCount = 0
        for user in topUsers:
            if topCount >= maxTop:
                break
            
            if topCount < len(topMedals):
                medal = topMedals[topCount]
            else:
                medal = str(topCount + 1) + '°'
            
            topMessage = topMessage + '\n' + medal + '|**' + user['user'] + '**|' + str(user['count'])
            topCount = topCount + 1
        
        topMessage = topMessage + """

Para ver todos los datos, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly/current_comments.csv)

También puedes ver los datos de forma gráfica [**aquí**](https://rchile.0x00.cl/)
""" + randomdata.GetInfoText()
        
        comment.reply(topMessage)
    
    def IntTryParse(self, value):
        """ Intenta convertir un String en un Int de forma literal. Si Value es vacio o None, retornará None
        Ej: '99' -> 99
        Ej: '' -> None
        Ej: 'abc55' -> None
        
        Parameters
        ----------
        value : String
            Valor string a tratar de convertir en Int
        
        Returns
        -------
        Int
            Valor convertido en caso de ser posible. En caso de no ser posible la conversión, se retorna None.
        """
        
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None
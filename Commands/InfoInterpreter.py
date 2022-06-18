from .BaseInterpreter import BaseInterpreter
import randomdata

class InfoInterpreter(BaseInterpreter):
    """ Clase para mostrar el mensaje de Info
    """

    def __init__(self, mydb):
        """ Constructor de la clase
        
        Parameters
        ----------
        mydb : connection.MySQLConnection
            Instancia de la base de datos
        """
        
        BaseInterpreter.__init__(self, mydb, __class__.__name__)
        
        self.cmds = [ 'info', 'link' ]
    
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
        
        if command is None:
            return
        for cmd in self.cmds:
            if command.startswith(cmd):
                return True
        return False
    
    def Interpretate(self, command, comment):
        """ Interpreta el comando
        
        Parameters
        ----------
        command : String
            Comando ingresado por el usuario (incluye parámetros)
        comment : praw.models.Comment
            Comentario de donde provino el comando
        """

        if comment is None:
            return
    
        replyMessage = """Este es un bot realizado por [**u/**](https://reddit.com/u/jzpv/)[**JPZV**](https://reddit.com/u/jzpv/) para mantener un registro de cuantos comentarios realiza cada usuario en el Random de r/Chile

Para ver todos los datos del hilo actual, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly/current_comments.csv)

Para ver los datos de hilos anteriores, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/blob/data/weekly)

Si quieres ver los datos de forma más visual, visita esta [**página**](https://rchile.0x00.cl/) (Hecho por [**u/**](https://reddit.com/u/0x00cl/)[**0x00cl**](https://reddit.com/u/0x00cl/))

Si quieres revisar el código del bot, haz click [**aquí**](https://github.com/JPZV/rChileRandom-Bot/)

Si tienes ideas, sugerencias, o encontraste un error, puedes dejar tu mensaje en [**GitHub**](https://github.com/JPZV/rChileRandom-Bot/issues) o enviarle un mensaje privado a [**JPZV**](https://www.reddit.com/message/compose/?to=jpzv&subject=Bot%20Hilo%20Random)
""" + randomdata.GetInfoText()
        
        comment.reply(replyMessage)
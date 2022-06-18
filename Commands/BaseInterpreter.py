class BaseInterpreter:
    """ Clase Base de los sub-módulos para Comandos
    """
    
    def __init__(self, mydb, interpreterName):
        """ Constructor de la clase
        
        Parameters
        ----------
        mydb : connection.MySQLConnection
            Instancia de la base de datos
        interpreterName : String
            Nombre del interpretador
        """
        
        self.MyDB = mydb
        self.InterpreterName = interpreterName
    
    def CanInterpretate(self, command):
        """ Comprueba que el comando se puede interpretar con este interpretador
        
        Parameters
        ----------
        command : String
            Comando ingresado por el usuario (incluye parámetros)
        """
    
        raise Exception(self.InterpreterName + ": CanInterpretate wasn't overridden or it was used with super")
    
    def Interpretate(self, command, comment):
        """ Interpreta el comando
        
        Parameters
        ----------
        command : String
            Comando ingresado por el usuario (incluye parámetros)
        comment : praw.models.Comment
            Comentario de donde provino el comando
        """
        
        raise Exception(self.InterpreterName + ": Interpretate wasn't overridden or it was used with super")
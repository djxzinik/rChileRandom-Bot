![alt text](https://github.com/JPZV/rChileRandom-Bot/blob/main/Assets/Profile%20Picture.png?raw=true)

# r/Chile Random bot

Este es un simple *bot* diseñado para contar y mantener un registro de la cantidad de comentarios que realiza un usuario en cada Hilo Random Semanal que se realiza en [r/Chile](https://www.reddit.com/r/chile)

## Datos
Todos los datos procesados por el *bot* se pueden encontrar en la rama [**Data**](https://github.com/JPZV/rChileRandom-Bot/tree/data).

También se pueden visualizar los datos en forma visualmente más atractivo en [esta página](https://rchile.0x00.cl/) realizada por [**u/0x00cl**](https://www.reddit.com/user/0x00cl/)

Con el objetivo de poder procesar los datos correctamente, el *bot* captura los siguientes datos/parámetros y los almacena en su propia base de datos:

- **Usuarios**:
  - Nombre de Usuario de los usuarios
  - Fecha del primer comentario visto por el *bot* de cada usuario
- **Hilos**:
  - ID del hilo
  - Año del hilo
  - Número de semana del hilo
- **Comentarios**:
  - ID del comentario
  - Nivel del hilo/conversación del comentario
  - Fecha y hora del comentario
  - Número del comentario en el Hilo


## Uso

Para ocupar este *bot*, se tienen que cumplir ciertos requisitos:

1. Tener una base de datos MySQL con una base de datos que contenga la [Estructura especial para el *bot*](Assets/rChileRandom.sql)
2. Tener Python3 y pip3 instalado.
3. Ejecutar el comando `pip3 install -r requirements.txt`
4. Dependiendo del OS/plataforma, crear un script ejecutable que contenga las variables del entorno que necesita el *bot*. En el caso de Linux, se puede ocupar el siguiente Script:

```bash
#!/bin/bash

export r_client_id=[CLIENT ID FROM REDDIT APPS]
export r_client_secret=[CLIENT SECRET FROM REDDIT APPS]

export r_username=[BOT USER ID FROM REDDIT]
export r_password=[BOT PASSWORD]

export db_host=[DATABASE HOST]
export db_user=[DATABASE USER]
export db_pass=[DATABASE PASS]
export db_database=[DATABASE NAME]

/usr/bin/python3 randomdata.py
```
5. Ejecutar el *bot* ocupando el Script.

## Contribuciones
Todo tipo de contribución es bienvenido, ya sean ideas (Issues) o mejoras en el código (Pull Request).

La única condición es que se mantenga el objetivo inicial del *bot*: Poder contar y procesar los comentarios de los usuarios manteniendo la transparencia y privacidad.

Cualquier idea o aporte que presente un problema para mantener la transparencia o la privacidad, o que tenga como objetivo comercializar, exponer, perjudicar o atacar a uno o varios usuarios será rechazado.

## Librerías utilizadas
- [**PRAW**](https://github.com/praw-dev/praw) ([Licencia](https://github.com/praw-dev/praw/blob/master/LICENSE.txt))
- [**MySQL Connector**](https://dev.mysql.com/doc/connector-python/en/) ([Licencia](https://dev.mysql.com/doc/dev/connector-python/8.0/license.html))
- [**GitPython**](https://github.com/gitpython-developers/GitPython) ([Licencia](https://github.com/gitpython-developers/GitPython/blob/main/LICENSE))


## Licencia
[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html)

## Privacidad
Todos los datos capturados por este programa serán utilizados exclusivamente con fines estadísticos y en ningún momento se venderán a terceros. Agregando a lo anterior, todos los datos extraídos por el programa son de carácter público y en ningún momento se obtendrán, utilizarán ni se guardarán datos privados de los usuarios.
# Sistemas de recomendacion
REST-API para sistema de recomendacion, algoritmos de sistemas de recomendacion y preprocesado de datos.

Dependencias:

- python 3
- mysql
- flask flask-mysql surprise (bibliotecas de python)

```
sudo apt install mysql-server python 
pip3 install flask flask-mysql surprise
```
si hubo error
> pip3 install flask flask-mysql --user

#### Requerimientos: 
1. Tener una base de datos cargada, para iniciar la base en donde se probo esta aplicacion hacer **source db/software_rankings.sql** en mysql.
2. Tener el nombre de usuario y contraseña en config.py

#### Ejecucion de la aplicacion
> python rest.py 

Ahora podra ver la renderizacion de la pagina poniendo 127.0.0.1:5001 en el navegador.


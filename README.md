# microlearning_alexa
Creado por Sara Puente Chantada

## Alexa
### Launch Section
* hasAuthLaunchRequestHandler: comprueba si la skill ha sido ejecutada anteriormente en el dispositivo. Si es así, guarda los datos. Actualmente no funciona.
* LauchRequestHandler: inicio de la skill. Si el usuario tarda en contestar, recuerda que tiene que identificarse con su nombre y apellido
### Auth Section
Se usan las variables name, surname, day, month, year e id_device. Este último recoge la id del dispositivo de una función específica de Node.js, el resto los extrae del usuario.

Tenemos dos intents:
* getNameIntentHandler: adquiere el nombre, apellido e id_device. Si no consigue alguno de los datos lo vuelve a pedir.
* getBirthdayIntentHandler: adquiere la fecha de nacimiento del usuario. Esta se separa en día/mes/año por si no entiende bien algún dato. *necesario probar con AMAZON.DATE*

Falta la API REST para poder autentificar con el **Auth Server**.
### Microcontent Section
Por ahora tiene dos intents:
* getUnitIDIntentHandler: recoge el valor de la unidad
* getMCIDIntentHandler: recoge la posición del microcontenido

Falta la API REST para poder dictar la lista de unidades temáticas/secciones de microcontenidos.
### APL Section
Falta la reproducción de microcontenidos, así como dar una posibilidad de una interfaz para que el usuario reproduzca el contenido. 
### Quiz Section
Falta por implementar
## Recordatorios

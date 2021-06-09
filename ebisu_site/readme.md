# README API EBISU
API desarrollada en el entorno DJANGO. 

## Instalación
- ``` pip install requirements.txt ```
- ``` python manage.py makemigrations ```
- ``` python manage.py migrate ```
- ``` python manage.py runserver ```

## API
### 1. predictRecall
localhost:8000/apiEbisu/<str:student_id>/predictRecall

Utiliza la función predictRecall de la librería Ebisu y devuelve en formato JSON el tiempo que ha pasado desde el último intento y el porcentaje de recuerdo estimado:

```json
{
    "passed_time": 5.062110297777778, 
    "predictedRecall": 0.8547534790801364
}
```
### 2. updateRecall
localhost:8000/apiEbisu/<str:student_id>/updateRecall/<int:success>/<int:total>

Utiliza la función updateRecall de la librería Ebisu. Para eso utiliza el total de preguntas y los aciertos. Actualiza en la base de datos el nuevo modelo actualizado del usuario.
Devuelve el json actualizado del usuario. 

```json
{
    "id_alexa": "1", 
    "alpha": 4.009948598326216, 
    "beta": 4.00994859832622, 
    "halflife": 25.01785351638419, 
    "lastTest": "2021-05-18T21:10:30.543Z"
}
```
### 3. predictDate
localhost:8000/apiEbisu/<str:student_id>/predictDate/<str:percent>

Utiliza la función modelToPercentileDecay de la librería Ebisu. Devuelve en formato JSON la fecha estimada en el que se alcanzará el porcentaje de recuerdo **percent**

```json
{
    "timeToForget": 25.0178535163842, 
    "predictedDate": "2021-05-19T22:11:34.816Z"
}
```
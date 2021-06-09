import json
import ebisu

from .models import Student

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.core import serializers

from datetime import timedelta


# Create your views here.

def index(request):
    return HttpResponse("Ebisu API")

'''
Recibe como parámetro la id_student. De la base de datos saca estos argumentos:
    -lastTest: fecha en la que se realizó el último test
    -alpha: parámetro de modelo de ebisu
    -beta: parámetro de modelo de ebisu
    -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
Devuelve en formato JSON el tiempo pasado en horas y el porcentaje estimado de recuerdo
'''
def predictRecall(request, student_id):
    #sacamos de la base de datos los campos
    s = Student.objects.get(id_alexa=student_id)
    ebisuModel = (s.alpha, s.beta, s.halflife)
    lastTest = s.lastTest
    
    #calculamos la diferencia de horas entre la ultima fecha y la fecha actual
    oneHour = timedelta(hours=1)
    diffHours = (timezone.now() - lastTest) / oneHour

    #llamada a ebisu.predictRecall
    predictedRecall = ebisu.predictRecall(ebisuModel, diffHours, exact=True)

    return JsonResponse({'passed_time': diffHours, 'predictedRecall': predictedRecall})

'''
Recibe como parámetro la id_student, total de preguntas y total de aciertos. De la base de datos
saca estos argumentos:
    -lastTest: fecha en la que se realizó el último test
    -alpha: parámetro de modelo de ebisu
    -beta: parámetro de modelo de ebisu
    -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
Actualiza en la base de datos los campos alpha, beta, halflife, lastTest.
Devuelve el objeto modificado en formato JSON 
'''
def updateRecall(request, student_id, success, total):
    #sacamos de la base de datos los campos
    s = Student.objects.get(id_alexa=student_id)
    ebisuModel = (s.alpha, s.beta, s.halflife)
    lastTest = s.lastTest
    
    #calculamos la diferencia de horas entre la ultima fecha y la fecha actual
    oneHour = timedelta(hours=1)
    diffHours = (timezone.now() - lastTest) / oneHour
    
    #llamada a ebisu.updateRecall
    newModel = ebisu.updateRecall(ebisuModel, success, total, diffHours)
    
    #actualizamos los datos
    s.alpha = newModel[0]
    s.beta = newModel[1]
    s.halflife = newModel[2]
    s.lastTest = timezone.now()
    s.save()
    
    serialized = json.loads(serializers.serialize('json', [s]))[0]
    
    return JsonResponse(serialized["fields"])

'''
Recibe por parámetro id_student y percent. Este es el porcentaje de recuerdo.
De la base de datos se saca este parámetro:
    -alpha: parámetro de modelo de ebisu
    -beta: parámetro de modelo de ebisu
    -halflife: parámetro de modelo de ebisu. Indica el número de horas en el que el porcentaje decae al 50%
    -lastTest: fecha en la que se realizó el último test
Devuelve en formato JSON el tiempo en horas y la fecha estimada
'''
def predictDate(request, student_id, percent):
    #sacamos de la base de datos los campos
    s = Student.objects.get(id_alexa=student_id)
    model = (s.alpha, s.beta, s.halflife)
    lastTest = s.lastTest

    #llamada a ebisu.modelToPercentileDecay y calculo de fecha
    timeToForget = ebisu.modelToPercentileDecay(model, float(percent))
    predictedDate = lastTest + timedelta(hours=timeToForget)

    return JsonResponse({'timeToForget': timeToForget, 'predictedDate': predictedDate})
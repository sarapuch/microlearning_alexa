from django.db import models

# Create your models here.
'''
id_alexa: id del dispositivo alexa
alpha: parametro del modelo de ebisu
beta: parametro del modelo de ebisu
halflife: parametro del modelo de ebisu. Indica el tiempo estimado
    en llegar a un porcentaje de recuerdo del 50%
lastTest: ultima vez que se realizo un cuestionario
'''
class Student(models.Model):
    id_alexa = models.CharField(max_length=60,default='')
    alpha = models.FloatField(default=4)
    beta = models.FloatField(default=4)
    halflife = models.FloatField(default=24)
    lastTest = models.DateTimeField('date published')

    def __str__(self):
        return self.id_alexa
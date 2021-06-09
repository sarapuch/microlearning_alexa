from django.urls import path

from . import views

'''
URLS de la API
'''
urlpatterns = [
    path('', views.index, name='index'),
    path('<str:student_id>/predictRecall', view=views.predictRecall, name='predictRecall'),
    path('<str:student_id>/updateRecall/<int:success>/<int:total>', view=views.updateRecall, name='updateRecall'),
    path('<str:student_id>/predictDate/<str:percent>', view=views.predictDate, name='predictDate')

]
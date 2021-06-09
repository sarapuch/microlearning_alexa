from django.contrib import admin

from .models import Student

# Register your models here.
'''
Para poder hacer debug sobre la base de datos
user: admin
psw: admin
'''

admin.site.register(Student)
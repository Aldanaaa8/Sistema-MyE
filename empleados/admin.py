from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Empleado)
admin.site.register(Turno)
admin.site.register(EmpleadoTurno)
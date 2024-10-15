from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_empleados, name='lista_empleados'),  # Lista todos los empleados y permite agregar uno nuevo
    path('nuevo/', views.lista_empleados, name='nuevo_empleado'),  # Agregar un nuevo empleado (usa la misma vista que lista_empleados)
    path('editar/<int:pk>/', views.editar_empleado, name='editar_empleado'),  # Editar un empleado existente
    path('eliminar/<int:pk>/', views.eliminar_empleado, name='eliminar_empleado'),  # Eliminar un empleado existente
    path('empleados_por_turno/', views.empleados_por_turno, name='empleados_por_turno'),

]

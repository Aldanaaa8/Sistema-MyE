from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/nuevo/', views.nuevo_proveedor, name='nuevo_proveedor'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]

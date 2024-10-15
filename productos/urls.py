# productos/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('', views.lista_productos, name='lista_productos'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/ver_stock/', views.ver_stock, name='ver_stock'),
     # URLs para pérdidas
    path('perdidas/', views.lista_perdidas, name='lista_perdidas'),
    path('perdidas/nueva/', views.nueva_perdida, name='nueva_perdida'),
    path('perdidas/<int:pk>/editar/', views.editar_perdida, name='editar_perdida'),
    path('perdidas/<int:pk>/eliminar/', views.eliminar_perdida, name='eliminar_perdida'),
]

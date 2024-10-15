from django.urls import path
from . import views  # Importamos las vistas desde el archivo de views

urlpatterns = [
    path('vista_ventas/', views.vista_unificada_ventas, name='vista_ventas'),
    # Ruta para agregar producto al carrito
    path('agregar_al_carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),

    # Ruta para actualizar el carrito (cantidad o descuentos)
    path('actualizar_carrito/', views.actualizar_carrito, name='actualizar_carrito'),

    # Ruta para eliminar un producto del carrito
    path('eliminar_producto_del_carrito/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),

    # Ruta para seleccionar la forma de pago
    

    # Ruta para finalizar la venta (procesar la venta y guardarla)
    path('cobrar_venta/', views.cobrar_venta, name='cobrar_venta'),
    

    # Ruta para limpiar el carrito (opcional, si la implementación lo requiere)
    path('limpiar_carrito/', views.limpiar_carrito, name='limpiar_carrito'),

    path('historial/',views.historial_ventas,name='historial_ventas')
]




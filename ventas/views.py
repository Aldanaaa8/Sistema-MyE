from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Venta, DetalleVenta, FormaPagoxVentas, Empleado, FormaPago
from productos.models import StockProducto
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json,logging
from django.db import transaction
from django.contrib import messages
from .forms import *

# Carrito
def obtener_o_inicializar_carrito(request):
    if 'carrito' not in request.session:
        request.session['carrito'] = []
    return request.session['carrito']

def obtener_carrito(request):
    return request.session.get('carrito', [])

def limpiar_carrito(request):
    request.session['carrito'] = []
    request.session.modified = True
    return redirect('vista_ventas')
    

# Stock
def verificar_stock(producto, cantidad):
    stock_producto = get_object_or_404(StockProducto, producto=producto)
    return stock_producto.cantidad >= cantidad

def verificar_y_actualizar_stock(producto, cantidad):
    stock_producto = get_object_or_404(StockProducto, producto=producto)
    if stock_producto.cantidad < cantidad:
        raise ValueError(f'No hay suficiente stock para {producto.nombre}')
    stock_producto.cantidad -= cantidad
    stock_producto.save()

# Venta
def obtener_empleado(request):
    return get_object_or_404(Empleado, user=request.user)

def obtener_venta_activa(venta_id, finalizada=False):
    return get_object_or_404(Venta, id=venta_id, finalizada=finalizada)

def crear_detalle_venta(venta, item):
    logging.info(f"Creando detalle para el producto {item['id']}")
    producto = Producto.objects.get(id=item['id'])
    verificar_y_actualizar_stock(producto, item['cantidad'])
    DetalleVenta.objects.create(
        venta=venta,
        producto=producto,
        cantidad=item['cantidad'],
        precio_unitario=Decimal(str(item['precio']).replace(",", ".")),
        descuento=item.get('descuento', 0),
        subtotal=Decimal(str(item['subtotal']).replace(",", "."))
    )

def calcular_totales_carrito(carrito):
    total_venta = sum(item['subtotal'] for item in carrito)
    total_descuento = sum((item['precio'] * item['cantidad'] * item['descuento'] / 100) for item in carrito)
    return total_venta, total_descuento

# Vistas
def vista_unificada_ventas(request):
    codigo_producto = request.GET.get('codigo_producto')
    carrito = obtener_o_inicializar_carrito(request)
    producto = None

    if codigo_producto:
        try:
            producto = Producto.objects.get(id=codigo_producto)
        except Producto.DoesNotExist:
            producto = None

    productos_en_carrito = obtener_carrito(request)
    total_venta, total_descuento = calcular_totales_carrito(productos_en_carrito)
    empleado = obtener_empleado(request)
    venta = Venta.objects.filter(empleado=empleado, finalizada=False).last()

    if not venta:
        venta = Venta.objects.create(empleado=empleado)

    context = {
        'producto': producto,
        'productos_en_carrito': productos_en_carrito,
        'total_venta': total_venta,
        'total_descuento': total_descuento,
        'venta': venta,
    }
    return render(request, 'vista_unificada_ventas.html', context)

@require_POST
def agregar_al_carrito(request):
    data = json.loads(request.body)
    producto_id = data.get('producto_id')
    descuento = float(data.get('descuento', 0))
    carrito = obtener_o_inicializar_carrito(request)

    try:
        producto = get_object_or_404(Producto, id=producto_id)
        if not verificar_stock(producto, 1):
            return JsonResponse({'success': False, 'error': 'Producto sin stock'})

        producto_en_carrito = next((item for item in carrito if item['id'] == producto.id), None)
        precio = float(str(producto.precio).replace(",", "."))

        if producto_en_carrito:
            if not verificar_stock(producto, producto_en_carrito['cantidad'] + 1):
                return JsonResponse({'success': False, 'error': 'No hay suficiente stock disponible'})
            producto_en_carrito['cantidad'] += 1
            producto_en_carrito['subtotal'] = producto_en_carrito['cantidad'] * precio * (1 - descuento / 100)
        else:
            carrito.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': precio,
                'cantidad': 1,
                'descuento': descuento,
                'subtotal': precio * (1 - descuento / 100)
            })

        request.session['carrito'] = carrito
        request.session.modified = True
        
        total_venta, total_descuento = calcular_totales_carrito(carrito)
        return JsonResponse({
            'success': True, 
            'carrito': carrito, 
            'total_venta': float(total_venta),
            'total_descuento': float(total_descuento)
        })

    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})

def finalizar_venta_obj(venta):
    venta.finalizada = True
    venta.save()




@require_POST
@login_required
@transaction.atomic
def crear_venta(request):
    productos_en_carrito = obtener_carrito(request)
    if not productos_en_carrito:
        return JsonResponse({'success': False, 'error': 'El carrito está vacío'})
    
    empleado = obtener_empleado(request)
    venta = Venta.objects.create(empleado=empleado)
    
    for item in productos_en_carrito:
        try:
            crear_detalle_venta(venta, item)
        except ValueError as e:
            venta.delete()  # Revertir la creación de la venta si hay un error
            return JsonResponse({'success': False, 'error': str(e)})
    
    total_venta, total_descuento = calcular_totales_carrito(productos_en_carrito)
    venta.total = total_venta
    venta.descuento_total = total_descuento
    venta.save()
    
    limpiar_carrito(request)
    return JsonResponse({'success': True, 'venta_id': venta.id})


@require_POST
@login_required
@transaction.atomic
def cobrar_venta(request):
    # Primero, crear la venta con sus detalles
    crear_venta_response = crear_venta(request)
    if not crear_venta_response.get('success'):
        messages.error(request, crear_venta_response.get('error'))
        return redirect('vista_ventas')  # Redirige de vuelta a la vista de ventas si hay un error

    venta_id = crear_venta_response.get('venta_id')
    venta = obtener_venta_activa(venta_id, finalizada=False)
    
    if venta is None:
        messages.error(request, 'Venta no encontrada')
        return redirect('vista_ventas')
    
    total_venta = venta.total
    total_pagado = total_venta  # Asumimos pago completo en efectivo

    if total_pagado < total_venta:
        messages.error(request, 'El monto pagado no cubre el total de la venta')
        return redirect('vista_ventas')

    finalizar_venta_obj(venta)
    
    # Obtener la instancia de FormaPago para 'Efectivo'
    try:
        forma_pago_efectivo = FormaPago.objects.get(nombre='Efectivo')
    except FormaPago.DoesNotExist:
        messages.error(request, 'Forma de pago Efectivo no encontrada')
        return redirect('vista_ventas')
    # Crear registro de pago
    FormaPagoxVentas.objects.create(
        venta=venta,
        forma_pago=forma_pago_efectivo,
        monto=total_pagado
    )

    # Limpiar el carrito
    limpiar_carrito(request)

    messages.success(request, f'Venta {venta_id} cobrada exitosamente')
    return redirect('historial_ventas')  # Asume que 'historial_ventas' es el nombre de la URL para el historial



def historial_ventas(request):
    ventas = Venta.objects.prefetch_related('detalles', 'formapagoxventas_set').all()
    return render(request, 'ver_resumen_venta.html', {'ventas': ventas})


# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Producto, Venta, DetalleVenta, FormaPagoxVentas, Empleado, FormaPago
# from productos.models import StockProducto
# from django.contrib.auth.decorators import login_required
# from decimal import Decimal, InvalidOperation
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# import json,logging
# from django.db import transaction



# # Carrito
# def obtener_o_inicializar_carrito(request):
#     if 'carrito' not in request.session:
#         request.session['carrito'] = []
#     return request.session['carrito']

# def obtener_carrito(request):
#     return request.session.get('carrito', [])

# def limpiar_carrito(request):
#     request.session['carrito'] = []
#     request.session.modified = True

# # Stock
# def verificar_stock(producto, cantidad):
#     stock_producto = get_object_or_404(StockProducto, producto=producto)
#     return stock_producto.cantidad >= cantidad

# def verificar_y_actualizar_stock(producto, cantidad):
#     stock_producto = get_object_or_404(StockProducto, producto=producto)
#     if stock_producto.cantidad < cantidad:
#         raise ValueError(f'No hay suficiente stock para {producto.nombre}')
#     stock_producto.cantidad -= cantidad
#     stock_producto.save()

# # Venta
# def obtener_empleado(request):
#     return get_object_or_404(Empleado, user=request.user)

# def obtener_venta_activa(venta_id, finalizada=False):
#     return get_object_or_404(Venta, id=venta_id, finalizada=finalizada)

# def crear_detalle_venta(venta, item):
#     logging.info(f"Creando detalle para el producto {item['id']}")
#     producto = Producto.objects.get(id=item['id'])
#     verificar_y_actualizar_stock(producto, item['cantidad'])
#     DetalleVenta.objects.create(
#         venta=venta,
#         producto=producto,
#         cantidad=item['cantidad'],
#         precio_unitario=Decimal(str(item['precio']).replace(",", ".")),
#         descuento=item.get('descuento', 0),
#         subtotal=Decimal(str(item['subtotal']).replace(",", "."))
#     )

# def calcular_totales_carrito(carrito):
#     total_venta = sum(item['subtotal'] for item in carrito)
#     total_descuento = sum((item['precio'] * item['cantidad'] * item['descuento'] / 100) for item in carrito)
#     return total_venta, total_descuento



# # Vistas
# def vista_unificada_ventas(request):
#     codigo_producto = request.GET.get('codigo_producto')
#     carrito = obtener_o_inicializar_carrito(request)
#     producto = None

#     if codigo_producto:
#         try:
#             producto = Producto.objects.get(id=codigo_producto)
#         except Producto.DoesNotExist:
#             producto = None

#     productos_en_carrito = obtener_carrito(request)
#     total_venta, _ = calcular_totales_carrito(productos_en_carrito)
#     empleado = obtener_empleado(request)
#     venta = Venta.objects.filter(empleado=empleado, finalizada=False).last()

#     if not venta:
#         venta = Venta.objects.create(empleado=empleado)

#     context = {
#         'producto': producto,
#         'productos_en_carrito': productos_en_carrito,
#         'total_venta': total_venta,
#         'venta': venta,
#     }
#     return render(request, 'vista_unificada_ventas.html', context)

# @require_POST
# def agregar_al_carrito(request):
#     data = json.loads(request.body)
#     producto_id = data.get('producto_id')
#     descuento = float(data.get('descuento', 0))
#     carrito = obtener_o_inicializar_carrito(request)

#     try:
#         producto = get_object_or_404(Producto, id=producto_id)
#         if not verificar_stock(producto, 1):
#             return JsonResponse({'success': False, 'error': 'Producto sin stock'})

#         producto_en_carrito = next((item for item in carrito if item['id'] == producto.id), None)
#         precio = float(str(producto.precio).replace(",", "."))

#         if producto_en_carrito:
#             if not verificar_stock(producto, producto_en_carrito['cantidad'] + 1):
#                 return JsonResponse({'success': False, 'error': 'No hay suficiente stock disponible'})
#             producto_en_carrito['cantidad'] += 1
#         else:
#             carrito.append({
#                 'id': producto.id,
#                 'nombre': producto.nombre,
#                 'precio': precio,
#                 'cantidad': 1,
#                 'descuento': descuento,
#                 'subtotal': precio * (1 - descuento / 100)
#             })

#         request.session['carrito'] = carrito
#         request.session.modified = True
#         return JsonResponse({'success': True, 'carrito': carrito})

#     except Producto.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Producto no encontrado'})

def actualizar_producto_en_carrito(carrito, producto_id, cantidad, descuento):
    for item in carrito:
        if item['id'] == int(producto_id):
            try:
                cantidad = Decimal(str(cantidad).replace(",", ".")) if cantidad is not None else Decimal(item['cantidad'])
                descuento = Decimal(str(descuento).replace(",", ".")) if descuento is not None else Decimal(item['descuento'])

                # Verificar que la cantidad sea válida (mayor a 0)
                if cantidad <= 0:
                    cantidad = Decimal(item['cantidad'])

                # Verificar que el descuento esté en el rango válido
                if not (0 <= descuento <= 100):
                    descuento = Decimal(item['descuento'])

                precio = Decimal(item['precio'])
                subtotal_producto = precio * cantidad * (1 - descuento / Decimal(100))

                # Actualizar los valores en el carrito
                item['cantidad'] = float(cantidad)
                item['descuento'] = float(descuento)
                item['subtotal'] = float(subtotal_producto)

                return subtotal_producto  # Devolver el subtotal actualizado

            except InvalidOperation:
                return None  # Operación inválida
    return None  # Producto no encontrado


@require_POST
def actualizar_carrito(request):
    data = json.loads(request.body)
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad')
    descuento = data.get('descuento')

    carrito = obtener_carrito(request)
    subtotal_producto = actualizar_producto_en_carrito(carrito, producto_id, cantidad, descuento)

    if subtotal_producto is None:
        return JsonResponse({'success': False, 'error': 'Operación inválida o producto no encontrado en el carrito'})

    request.session['carrito'] = carrito
    request.session.modified = True

    total_venta, total_descuento = calcular_totales_carrito(carrito)
    return JsonResponse({
        'success': True,
        'subtotal': float(subtotal_producto),
        'total': float(total_venta),
        'total_descuento': float(total_descuento),
    })

# @require_POST
# @login_required
# @transaction.atomic
# def crear_venta(request):
#     if request.method == 'POST':
#         productos_en_carrito = obtener_carrito(request)
#         if productos_en_carrito:
#             empleado = obtener_empleado(request)
#             venta = Venta.objects.create(empleado=empleado)
#             for item in productos_en_carrito:
#                 try:
#                     crear_detalle_venta(venta, item)
#                 except ValueError as e:
#                     return JsonResponse({'success': False, 'error': str(e)})
#             limpiar_carrito(request)
#             return JsonResponse({'success': True, 'venta_id': venta.id})

#     return JsonResponse({'success': False, 'error': 'Método no permitido'})


# def finalizar_venta_obj(venta):
#     venta.finalizada = True
#     venta.save()

# @require_POST
# @login_required
# @transaction.atomic
# def cobrar_venta(request):
#     if request.method == "POST":
#         venta_id = request.POST.get('venta_id')
        
#         # Obtener la venta activa
#         venta = obtener_venta_activa(venta_id, finalizada=False)
        
#         if venta is None:
#             return JsonResponse({'success': False, 'error': 'Venta no encontrada'})
        
#         print(f"Procesando venta con ID: {venta_id}")

#         # Calcular el total de la venta
#         total_venta, _ = calcular_totales_carrito(venta.detalles.all())

#         # Asumimos que solo hay una forma de pago y es en efectivo
#         total_pagado = total_venta  # Se paga todo en efectivo

#         print(f"Total venta: {total_venta}, Total pagado: {total_pagado}")

#         if total_pagado < total_venta:
#             print("El monto pagado no cubre el total de la venta")
#             return JsonResponse({'success': False, 'error': 'El monto pagado no cubre el total de la venta'})

#         # Finalizar la venta y limpiar el carrito
#         finalizar_venta_obj(venta)
#         limpiar_carrito(request)

#         print("Venta finalizada y carrito limpiado")
#         return JsonResponse({'success': True, 'venta_id': venta.id})
    
#     return JsonResponse({'success': False, 'error': 'Método no permitido'})

# # def cobrar_venta(request):
# #     if request.method == "POST":
# #         venta_id = request.POST.get('venta_id')
        
# #         # Obtener la venta activa
# #         venta = obtener_venta_activa(venta_id, finalizada=False)
        
# #         # Calcular el total de la venta
# #         total_venta, _ = calcular_totales_carrito(venta.detalles.all())

# #         # Asumimos que solo hay una forma de pago y es en efectivo
# #         total_pagado = total_venta  # Se paga todo en efectivo

# #         if total_pagado < total_venta:
# #             return JsonResponse({'success': False, 'error': 'El monto pagado no cubre el total de la venta'})

# #         # Finalizar la venta y limpiar el carrito
# #         finalizar_venta_obj(venta)
# #         limpiar_carrito(request)

# #         # Redirigir al historial de ventas
# #         return redirect('historial_ventas')  # Redirige a la vista del historial de ventas
    
# #     return JsonResponse({'success': False, 'error': 'Método no permitido'})


# def historial_ventas(request):
#     # Obtener todas las ventas finalizadas
#     ventas = Venta.objects.filter(finalizada=True).prefetch_related('detalles', 'formapagoxventas_set')

#     # Preparar una lista para almacenar la información de cada venta con sus detalles
#     ventas_con_detalles = []
#     for venta in ventas:
#         detalles_venta = venta.detalles.all()  # Obtener todos los detalles de la venta
#         formas_pago = FormaPagoxVentas.objects.filter(venta=venta)  # Obtener las formas de pago
#         ventas_con_detalles.append({
#             'venta': venta,
#             'detalles': detalles_venta,
#             'formas_pago': formas_pago,
#         })

#     # Renderizar la plantilla y pasar la lista de ventas con detalles
#     return render(request, 'ver_resumen_venta.html', {'ventas_con_detalles': ventas_con_detalles})

@require_POST
def eliminar_producto_carrito(request):
    data = json.loads(request.body)
    producto_id = data.get('producto_id')

    carrito = [item for item in obtener_carrito(request) if item['id'] != int(producto_id)]
    request.session['carrito'] = carrito
    request.session.modified = True

    total = sum(item['subtotal'] for item in carrito)
    return JsonResponse({'success': True, 'total': total})


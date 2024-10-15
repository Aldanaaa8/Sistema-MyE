from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, TipoProducto, StockProducto, Perdida
from .forms import ProductoForm, TipoProductoForm, StockProductoForm, PerdidaForm
from django.contrib.auth.decorators import login_required

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            stock_inicial = request.POST.get('stock')
            StockProducto.objects.create(producto=producto, cantidad=stock_inicial)
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'lista_productos.html', {'productos': productos, 'form': form})

# Ver y actualizar stock de todos los productos
def ver_stock(request):
    productos = Producto.objects.all()
    
    if request.method == 'POST':
        for producto in productos:
            stock_id = f'stock_{producto.pk}'
            nuevo_stock = request.POST.get(stock_id)
            stock_producto, created = StockProducto.objects.get_or_create(producto=producto)
            stock_producto.cantidad = nuevo_stock
            stock_producto.save()
        return redirect('ver_stock')

    return render(request, 'ver_stock.html', {'productos': productos})

def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'detalle_producto.html', {'producto': producto})

def nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'nuevo_producto.html', {'form': form})

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'editar_producto.html', {'form': form, 'producto': producto})

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'eliminar_producto.html', {'producto': producto})


def nuevo_tipo_producto(request):
    if request.method == 'POST':
        form = TipoProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_productos')
    else:
        form = TipoProductoForm()
    return render(request, 'productos/nuevo_tipo_producto.html', {'form': form})


#perdidas
def lista_perdidas(request):
    perdidas = Perdida.objects.all()
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = PerdidaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_perdidas')
    return render(request, 'perdidas.html', {'perdidas': perdidas, 'productos': productos})

def nueva_perdida(request):
    if request.method == 'POST':
        form = PerdidaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_perdidas')
    else:
        form = PerdidaForm()
    return render(request, 'nueva_perdida.html', {'form': form})


def editar_perdida(request, pk):
    perdida = get_object_or_404(Perdida, pk=pk)
    productos = Producto.objects.all()
    if request.method == 'POST':
        form = PerdidaForm(request.POST, instance=perdida)
        if form.is_valid():
            form.save()
            return redirect('lista_perdidas')
    else:
        form = PerdidaForm(instance=perdida)
    return render(request, 'editar_perdida.html', {'form': form, 'productos': productos, 'perdida': perdida})

def eliminar_perdida(request, pk):
    perdida = get_object_or_404(Perdida, pk=pk)
    if request.method == 'POST':
        perdida.delete()
        return redirect('lista_perdidas')
    return render(request, 'eliminar_perdida.html', {'perdida': perdida})
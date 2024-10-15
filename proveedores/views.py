
from django.shortcuts import render, get_object_or_404, redirect
from .models import Proveedor, ProveedorProducto
from .forms import ProveedorForm, ProveedorProductoForm
from django.contrib.auth.decorators import login_required

@login_required
def lista_proveedores(request):
    proveedores = Proveedor.objects.all()
    form = ProveedorForm()
    return render(request, 'lista_proveedores.html', {'proveedores': proveedores, 'form': form})

def nuevo_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'editar_proveedor.html', {'form': form})

def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == "POST":
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'editar_proveedor.html', {'form': form})

def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.delete()
    return redirect('lista_proveedores')

def nuevo_producto_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
    if request.method == 'POST':
        form = ProveedorProductoForm(request.POST)
        if form.is_valid():
            producto_proveedor = form.save(commit=False)
            producto_proveedor.proveedor = proveedor
            producto_proveedor.save()
            return redirect('detalle_proveedor', pk=proveedor_id)
    else:
        form = ProveedorProductoForm(initial={'proveedor': proveedor})
    return render(request, 'proveedores/nuevo_producto_proveedor.html', {'form': form, 'proveedor': proveedor})
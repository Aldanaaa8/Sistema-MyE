# proveedores/forms.py
from django import forms
from .models import Proveedor, ProveedorProducto

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'direccion', 'telefono', 'email']

class ProveedorProductoForm(forms.ModelForm):
    class Meta:
        model = ProveedorProducto
        fields = ['proveedor', 'producto', 'precio']

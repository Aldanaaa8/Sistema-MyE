# productos/forms.py
from django import forms
from .models import Producto, TipoProducto, StockProducto, Perdida

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'tipo', 'precio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].queryset = TipoProducto.objects.all()
        self.fields['tipo'].empty_label = "Seleccione un tipo de producto"

class TipoProductoForm(forms.ModelForm):
    class Meta:
        model = TipoProducto
        fields = ['nombre']

class StockProductoForm(forms.ModelForm):
    class Meta:
        model = StockProducto
        fields = ['producto', 'cantidad']

class PerdidaForm(forms.ModelForm):
    class Meta:
        model = Perdida
        fields = ['producto', 'cantidad', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()

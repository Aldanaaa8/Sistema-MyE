from django import forms
from .models import Venta,DetalleVenta,FormaPago,FormaPagoxVentas
from empleados.models import Empleado
from productos.models import Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model=Venta
        fields=['empleado']

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['empleado'].queryset = Empleado.objects.filter(activo=True)

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model=DetalleVenta
        fields=['venta','producto','cantidad']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if 'producto' in self.data:
                try:
                    producto_id = int(self.data.get('producto'))
                    self.fields['producto'].queryset = Producto.objects.filter(id=producto_id)
                    self.fields['precio_unitario'].initial = Producto.objects.get(id=producto_id).precio
                except (ValueError, TypeError, Producto.DoesNotExist):
                    pass  
            else:
                self.fields['producto'].queryset = Producto.objects.all()

class FormaPagoForm(forms.ModelForm):
    class Meta:
        model=FormaPago
        fields=['nombre']

class FormaPagoxVentasForm(forms.ModelForm):
    class Meta:
        model=FormaPagoxVentas
        fields=['forma_pago','monto']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['forma_pago'].queryset = FormaPago.objects.all() 
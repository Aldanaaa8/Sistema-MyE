from django.db import models
from empleados.models import Empleado
from productos.models import Producto
from decimal import Decimal

class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    finalizada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fecha} - {self.empleado} - {self.total}"
    
    @property
    def detalles(self):
        return self.detalleventa_set.all()

    def calcular_total(self):
        # Suma todos los subtotales de los detalles de esta venta
        self.total = sum(detalle.subtotal for detalle in self.detalles.all())
        # Guarda la venta con el total actualizado
        self.save()

    
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def __str__(self):
        return f"{self.venta} - {self.producto} - {self.cantidad} - {self.precio_unitario} - {self.subtotal}"

    
    def calcular_subtotal(self):
        # Convertir ambos a Decimal si es necesario
        self.subtotal = Decimal(self.precio_unitario) * Decimal(self.cantidad)


    def save(self, *args, **kwargs):
        self.calcular_subtotal()
        super().save(*args, **kwargs)
        self.venta.calcular_total()


class FormaPago(models.Model):
    nombre=models.CharField(max_length=50)
    def __str__(self) :
        return f"{self.nombre}"

class FormaPagoxVentas(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    forma_pago = models.ForeignKey(FormaPago, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)  # Cambia de FloatField a DecimalField

    def __str__(self):
        return f"{self.venta} - {self.forma_pago} - {self.monto}"


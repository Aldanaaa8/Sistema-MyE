# productos/models.py
from django.db import models

class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class StockProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades'

class Perdida(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField()

    def __str__(self):
        return f'{self.producto.nombre} - {self.cantidad} unidades perdidas'

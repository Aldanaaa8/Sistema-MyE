# productos/admin.py
from django.contrib import admin
from .models import Producto, TipoProducto, StockProducto, Perdida

admin.site.register(Producto)
admin.site.register(TipoProducto)
admin.site.register(StockProducto)
admin.site.register(Perdida)

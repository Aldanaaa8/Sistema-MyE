# productos/management/commands/insertar_tipos_producto.py
from django.core.management.base import BaseCommand
from productos.models import TipoProducto

class Command(BaseCommand):
    help = 'Inserta varios tipos de producto en la base de datos'

    def handle(self, *args, **kwargs):
        tipos = [
            'Lácteos',
            'Carnes',
            'Frutas y Verduras',
            'Panadería',
            'Bebidas',
            'Snacks',
            'Congelados',
            'Limpieza',
            'Higiene Personal',
            'Mascotas'
        ]

        for tipo in tipos:
            TipoProducto.objects.get_or_create(nombre=tipo)

        self.stdout.write(self.style.SUCCESS('Tipos de producto insertados correctamente.'))

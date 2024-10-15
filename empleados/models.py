from django.contrib.auth.models import User
from django.db import models

class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado',default=1)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_ingreso = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Turno(models.Model):
    nombre = models.CharField(max_length=50)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio} - {self.hora_fin})"

class EmpleadoTurno(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    fecha = models.DateField()
    
    class Meta:
        unique_together = ('empleado', 'turno', 'fecha')

    def __str__(self):
        return f"{self.empleado} - {self.turno} ({self.fecha})"

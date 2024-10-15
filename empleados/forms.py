from django import forms
from .models import Empleado, Turno, EmpleadoTurno

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_ingreso']

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['nombre', 'hora_inicio', 'hora_fin']

class EmpleadoTurnoForm(forms.ModelForm):
    class Meta:
        model = EmpleadoTurno
        fields = ['empleado', 'turno', 'fecha']

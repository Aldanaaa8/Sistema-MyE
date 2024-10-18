from django import forms
from .models import Empleado, Turno, EmpleadoTurno
from django.contrib.auth.models import User, Permission
from django.contrib.auth.forms import UserCreationForm

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


#permisos

class CustomUserCreationForm(UserCreationForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),  # Mostrar todos los permisos disponibles
        required=False,  # Los permisos son opcionales
        widget=forms.CheckboxSelectMultiple,  # Mostrar los permisos como checkbox
        label="Asignar Permisos"
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'permissions']


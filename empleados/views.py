from django.shortcuts import render, get_object_or_404, redirect
from .models import Empleado
from .forms import EmpleadoForm,EmpleadoTurno, Turno
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
# Vista para listar empleados y agregar un nuevo empleado
@login_required
def lista_empleados(request):
    empleados = Empleado.objects.all()
    
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            # Crear usuario
            username = request.POST.get('username')
            password = request.POST.get('password')
            usuario = User.objects.create(
                username=username,
                password=make_password(password)
            )
            
            # Guardar el empleado asociado al usuario
            empleado = form.save(commit=False)
            empleado.user = usuario
            empleado.save()

            return redirect('lista_empleados')
    else:
        form = EmpleadoForm()

    return render(request, 'lista_empleados.html', {'empleados': empleados, 'form': form})

# Vista para editar un empleado existente
def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('lista_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'editar_empleado.html', {'form': form, 'empleado': empleado})

# Vista para eliminar un empleado existente
def eliminar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        empleado.delete()
        return redirect('lista_empleados')
    return render(request, 'eliminar_empleado.html', {'empleado': empleado})


def empleados_por_turno(request):
    turno_mañana = Turno.objects.get(nombre='Mañana')
    turno_tarde = Turno.objects.get(nombre='Tarde')
    
    empleados_mañana = EmpleadoTurno.objects.filter(turno=turno_mañana)
    empleados_tarde = EmpleadoTurno.objects.filter(turno=turno_tarde)

    context = {
        'empleados_mañana': empleados_mañana,
        'empleados_tarde': empleados_tarde,
    }

    return render(request, 'empleados_por_turno.html', context)



from django.shortcuts import render,redirect
#from django.http import HttpResponse
#from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.views import View


class VRegistro(View):
    def get(self, request):
        form= UserCreationForm()
        return render (request,"registro.html",{"form":form})

    def post(self, request):
        form=UserCreationForm(request.POST)
        if form.is_valid():
            usuario=form.save()
            login(request, usuario)

            return redirect("")
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
            return render (request,"registro.html",{"form":form})

def logear(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data.get("username")
            contraseña = form.cleaned_data.get("password")
            usuario = authenticate(username=nombre_usuario, password=contraseña)
            if usuario is not None:
                login(request, usuario)
                return redirect('home')
            else:
                # Error de autenticación, mensaje personalizado
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
                print('error1')
        else:
            # Mensajes de error del formulario
            
            
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
                print('error2')

    else:
        form = AuthenticationForm()

    return render(request, "registration/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect('logear')

@login_required
def home(request):
    return render(request, 'home.html')

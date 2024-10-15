from django.urls import path
from .views import VRegistro,logear,home,logout_view

urlpatterns = [
    path('register', VRegistro.as_view(), name='form'),
    path('',logear, name="logear"),
    path('logout/',logout_view, name='logout'),
    path('home/', home, name='home'),
    
    
]
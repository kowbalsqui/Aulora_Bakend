
from django.urls import path, re_path, include
from .import views  

urlpatterns = [
    path('', views.inicio, name= 'inicio'),]
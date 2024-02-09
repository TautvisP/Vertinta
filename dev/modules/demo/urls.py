from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'modules.demo'


urlpatterns = [
    path('data', views.DataView.as_view(), name='data'),
    path('cad', views.CADView.as_view(), name='cad'),
]

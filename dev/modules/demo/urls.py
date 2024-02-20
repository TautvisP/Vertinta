from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'modules.demo'


urlpatterns = [
    path('data', views.DataView.as_view(), name='data'),
    path('cad', views.CADView.as_view(), name='cad'),

    path('osom', views.OSOMView.as_view(), name='osom'),
    path('osom/api/create', views._osomapi_create),
    path('osom/api/list', views._osomapi_list),
    path('osom/api/remove', views._osomapi_remove),
]

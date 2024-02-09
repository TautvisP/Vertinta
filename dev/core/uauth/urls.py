from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views


app_name = 'core.uauth'


urlpatterns = [
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
]


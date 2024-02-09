from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views


app_name = 'parea'


urlpatterns = [
    path('', auth_views.LoginView.as_view(redirect_authenticated_user=True, template_name='parea/index.html'), name='index'),
]

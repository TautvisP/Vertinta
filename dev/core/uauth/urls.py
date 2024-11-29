from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views
from core.uauth.views.uauth_views import *

app_name = 'core.uauth'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/agency/', AgencyRegisterView.as_view(), name='agency_register'),
    path('register/evaluator/', EvaluatorRegisterView.as_view(), name='evaluator_register'),
    path('edit/', UserEditView.as_view(), name='edit_profile'),
]
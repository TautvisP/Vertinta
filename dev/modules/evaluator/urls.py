from django.urls import path
from . import views
from .views import *

app_name = 'modules.evaluator'

urlpatterns = [
    path('', views.index, name='evaluator_index'),

    path('edit/', EditEvaluatorAccountView.as_view(), name='edit_own_evaluator_account'),

    #used for agency to edit evaluator profile
    path('edit/<int:pk>/', EditEvaluatorAccountView.as_view(), name='edit_evaluator_account'),
]

#TODO: Make header functional, so that all the urls can be accesed by buttons and not by urls
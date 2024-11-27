from django.urls import path
from . import views
from .views import *

app_name = 'modules.agency'

urlpatterns = [
    path('', views.index, name='agency_index'),
    path('edit/', EditAgencyAccountView.as_view(), name='edit_agency_account'),
    path('evaluators/', EvaluatorListView.as_view(), name='evaluator_list'),
    path('create/', CreateEvaluatorAccountView.as_view(), name='create_evaluator_account'),
]

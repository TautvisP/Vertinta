from django.urls import path
from . import views
from .views import EditAgencyAccountView, EvaluatorListView, CreateEvaluatorAccountView

app_name = 'modules.agency'

urlpatterns = [
    path('', views.index, name='agency_index'),
    path('edit/', EditAgencyAccountView.as_view(), name='edit_agency_account'),
    path('evaluator_list/', EvaluatorListView.as_view(), name='evaluator_list'),
    path('create_evaluator_account/', CreateEvaluatorAccountView.as_view(), name='create_evaluator_account'),
]

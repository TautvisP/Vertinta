from django.urls import path
from . import views
from .views import EditAgencyAccountView, EvaluatorListView, CreateEvaluatorAccountView, ReassignEvaluatorView, AssignEvaluatorView

app_name = 'modules.agency'

urlpatterns = [
    path('', views.index, name='agency_index'),
    path('edit/', EditAgencyAccountView.as_view(), name='edit_agency_account'),
    path('evaluator_list/', EvaluatorListView.as_view(), name='evaluator_list'),
    path('create_evaluator_account/', CreateEvaluatorAccountView.as_view(), name='create_evaluator_account'),
    path('reassign_evaluator/<int:order_id>/', ReassignEvaluatorView.as_view(), name='reassign_evaluator'),
    path('assign_evaluator/<int:order_id>/<int:evaluator_id>/', AssignEvaluatorView.as_view(), name='assign_evaluator'),
]
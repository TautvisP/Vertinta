from django.urls import path
from . import views
from .views import EditAgencyAccountView, ReportReviewView, ApproveReportView, RejectReportView, EvaluatorListView, CreateEvaluatorAccountView, ReassignEvaluatorView, AssignEvaluatorView

app_name = 'modules.agency'

urlpatterns = [
    path('', views.index, name='agency_index'),
    path('edit/', EditAgencyAccountView.as_view(), name='edit_agency_account'),
    path('evaluator_list/', EvaluatorListView.as_view(), name='evaluator_list'),
    path('create_evaluator_account/', CreateEvaluatorAccountView.as_view(), name='create_evaluator_account'),
    path('reassign_evaluator/<int:order_id>/', ReassignEvaluatorView.as_view(), name='reassign_evaluator'),
    path('assign_evaluator/<int:order_id>/<int:evaluator_id>/', AssignEvaluatorView.as_view(), name='assign_evaluator'),
    
    # Report review URLs
    path('reports/review/<int:order_id>/', ReportReviewView.as_view(), name='review_report'),
    path('reports/approve/<int:order_id>/', ApproveReportView.as_view(), name='approve_report'),
    path('reports/reject/<int:order_id>/', RejectReportView.as_view(), name='reject_report'),
]
from django.urls import path
from core.uauth.views.uauth_views import CustomLoginView, CustomLogoutView, RegisterView, UserEditView, AgencyRegisterView, EvaluatorRegisterView

app_name = 'core.uauth'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/agency/', AgencyRegisterView.as_view(), name='agency_register'),
    path('register/evaluator/', EvaluatorRegisterView.as_view(), name='evaluator_register'),
    path('edit/', UserEditView.as_view(), name='edit_profile'),
]
# http://127.0.0.1:8000/auth/login/ is the starting, main, initial url of the project
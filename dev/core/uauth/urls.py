from django.urls import path
from core.uauth.views.uauth_views import CustomLoginView, CustomLogoutView, RegisterView, UserEditView, AgencyRegisterWithTokenView

app_name = 'core.uauth'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('edit/', UserEditView.as_view(), name='edit_profile'),

    # Secure agency registration with token
    path('register/agency/<uuid:token>/', AgencyRegisterWithTokenView.as_view(), name='agency_register_with_token'),
]
# http://127.0.0.1:8000/auth/login/ is the starting, main, initial url of the project
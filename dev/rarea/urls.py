from django.urls import path
from . import views


app_name = 'rarea'


urlpatterns = [
    path('', views.DashboardView.as_view(), { "app_name":app_name }, name='index'),
    path('ui-guidelines', views.UIGuidelinesView.as_view(), name='ui-guidelines')
]
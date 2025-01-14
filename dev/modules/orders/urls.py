from django.urls import path
from . import views
from .views import LandingView, FirsStepView, AdditionalBuildingsView, OrderListView, EvaluatorOrderListView, AgencySelectionView, EditAdditionalBuildingsView, OrderDeleteView

app_name = 'modules.orders'

urlpatterns = [
    path('', views.index, name='orders_index'),
    path('select/', LandingView.as_view(), name='selection'),
    path('first_step/', FirsStepView.as_view(), name='order_first_step'),
    path('additional_buildings/<int:order_id>/', AdditionalBuildingsView.as_view(), name='additional_buildings'),

    path('order_list/', OrderListView.as_view(), name='order_list'),
    path('evaluator_orders/', EvaluatorOrderListView.as_view(), name='evaluator_order_list'),

    #used by agency to look at evaluators orders
    path('evaluator_orders/<int:id>', EvaluatorOrderListView.as_view(), name='specific_evaluator_order_list'),

    path('object/<int:pk>/edit/', views.ObjectUpdateView.as_view(), name='object_update'),
    path('object/<int:pk>/edit_additional_buildings/', EditAdditionalBuildingsView.as_view(), name='edit_additional_buildings'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='delete_order'),

    path('select_agency/', AgencySelectionView.as_view(), name='select_agency'),
]

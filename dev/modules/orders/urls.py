from django.urls import path
from . import views
from .views import LandingView, OrderCreationStepView, ObjectCommonInfoStepView, OrderDecorationStepView, ObjectUtilityStepView, ObjectUtilityStepView, AdditionalBuildingsView, OrderListView, EvaluatorOrderListView, AgencySelectionView, EditAdditionalBuildingsView, OrderDeleteView, ViewObjectDataView, EditOrderStatusPriorityView

app_name = 'modules.orders'

urlpatterns = [
    path('', views.index, name='orders_index'),
    path('select/', LandingView.as_view(), name='selection'),

    path('order/create/', OrderCreationStepView.as_view(), name='order_creation_step'), #location and additional forms
    path('order/decoration/', OrderDecorationStepView.as_view(), name='order_decoration_step'), #decoration form


    path('order/common_info/', ObjectCommonInfoStepView.as_view(), name='order_common_info_step'),
    path('order/utility/', ObjectUtilityStepView.as_view(), name='order_utility_step'),

    path('additional_buildings/<int:object_id>/', AdditionalBuildingsView.as_view(), name='additional_buildings'),

    path('view_object_data/<int:order_id>/<int:pk>/', ViewObjectDataView.as_view(), name='view_object_data'),

    path('order_list/', OrderListView.as_view(), name='order_list'),
    path('evaluator_orders/', EvaluatorOrderListView.as_view(), name='evaluator_order_list'),

    #used by evaluator and agency to edit orders status and/or priority
    path('edit_order_status_priority/<int:pk>/', EditOrderStatusPriorityView.as_view(), name='edit_order_status_priority'),

    #used by agency to look at evaluators orders
    path('evaluator_orders/<int:id>', EvaluatorOrderListView.as_view(), name='specific_evaluator_order_list'),

    path('object/<int:pk>/edit/', views.ObjectUpdateView.as_view(), name='object_update'),
    path('object/<int:pk>/edit_additional_buildings/', EditAdditionalBuildingsView.as_view(), name='edit_additional_buildings'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='delete_order'),

    path('select_agency/<int:order_id>', AgencySelectionView.as_view(), name='select_agency'),
]

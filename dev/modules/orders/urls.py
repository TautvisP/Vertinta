from django.urls import path
from . import views
from .views import LandingView, OrderCreationStepView, ReportAccessView, EditObjectStepView, NotificationListView, MarkAllNotificationsReadView, MarkNotificationReadView, NotificationUnreadCountView, EditObjectCommonInfoStepView, EditObjectUtilityStepView, EditObjectDecorationStepView, ObjectCommonInfoStepView, OrderDecorationStepView, ObjectUtilityStepView, ObjectUtilityStepView, AdditionalBuildingsView, OrderListView, EvaluatorOrderListView, AgencySelectionView, EditAdditionalBuildingsView, OrderDeleteView, ViewObjectDataView, EditOrderStatusPriorityView

app_name = 'modules.orders'

urlpatterns = [
    path('', views.index, name='orders_index'),
    path('select/', LandingView.as_view(), name='selection'),

    #object creation
    path('order/create/', OrderCreationStepView.as_view(), name='order_creation_step'),
    path('order/decoration/', OrderDecorationStepView.as_view(), name='order_decoration_step'),
    path('order/common_info/', ObjectCommonInfoStepView.as_view(), name='order_common_info_step'),
    path('order/utility/', ObjectUtilityStepView.as_view(), name='order_utility_step'),

    #object editing
    path('object/<int:pk>/edit/', EditObjectStepView.as_view(), name='edit_object_step'),
    path('object/<int:pk>/edit/decoration/', EditObjectDecorationStepView.as_view(), name='edit_decoration_step'),
    path('object/<int:pk>/edit/common_info/', EditObjectCommonInfoStepView.as_view(), name='edit_common_info_step'),
    path('object/<int:pk>/edit/utility/', EditObjectUtilityStepView.as_view(), name='edit_utility_step'),


    path('additional_buildings/<int:object_id>/', AdditionalBuildingsView.as_view(), name='additional_buildings'),

    path('view_object_data/<int:order_id>/<int:pk>/', ViewObjectDataView.as_view(), name='view_object_data'),

    path('order_list/', OrderListView.as_view(), name='order_list'),
    path('evaluator_orders/', EvaluatorOrderListView.as_view(), name='evaluator_order_list'),

    #used by evaluator and agency to edit orders status and/or priority
    path('edit_order_status_priority/<int:pk>/', EditOrderStatusPriorityView.as_view(), name='edit_order_status_priority'),

    #used by agency to look at evaluators orders
    path('evaluator_orders/<int:id>', EvaluatorOrderListView.as_view(), name='specific_evaluator_order_list'),

    path('object/<int:pk>/edit_additional_buildings/', EditAdditionalBuildingsView.as_view(), name='edit_additional_buildings'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='delete_order'),

    path('select_agency/<int:object_id>/', AgencySelectionView.as_view(), name='select_agency'),
    path('select_agency/<int:order_id>/', AgencySelectionView.as_view(), name='select_agency_order'),
    path('select_agency/object/<int:object_id>/', AgencySelectionView.as_view(), name='select_agency_object'),


    path('report/access/<int:order_id>/', ReportAccessView.as_view(), name='view_report'),

    # API endpoints for notifications
    path('api/notifications/', NotificationListView.as_view(), name='notification_list'),
    path('api/notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification_unread_count'),
    path('api/notifications/<int:notification_id>/mark-read/', MarkNotificationReadView.as_view(), name='mark_notification_read'),
    path('api/notifications/mark-all-read/', MarkAllNotificationsReadView.as_view(), name='mark_all_notifications_read'),


    # Calendar urls
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('calendar/event/create/<int:order_id>/', views.EventCreateView.as_view(), name='create_event'),
    path('calendar/event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('calendar/event/<int:pk>/update/', views.EventUpdateView.as_view(), name='update_event'),
    path('calendar/event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='delete_event'),
    path('calendar/event/<int:pk>/confirm/', views.ConfirmEventView.as_view(), name='confirm_event'),
]
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from modules.orders.models  import Notification

@method_decorator(login_required, name='dispatch')
class NotificationListView(View):
    """API endpoint to get a list of notifications for the current user."""
    
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(recipient=request.user)[:30]  # Limit to 30 most recent
        
        notification_data = [{
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
            'is_read': notification.is_read,
            'notification_type': notification.notification_type,
            'action_url': notification.action_url,
        } for notification in notifications]
        
        return JsonResponse(notification_data, safe=False)


@method_decorator(login_required, name='dispatch')
class NotificationUnreadCountView(View):
    """API endpoint to get the count of unread notifications for the current user."""
    
    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'count': count})


@method_decorator([login_required, require_POST], name='dispatch')
class MarkNotificationReadView(View):
    """API endpoint to mark a specific notification as read."""
    
    def post(self, request, notification_id, *args, **kwargs):
        notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        
        return JsonResponse({'success': True})


@method_decorator([login_required, require_POST], name='dispatch')
class MarkAllNotificationsReadView(View):
    """API endpoint to mark all notifications as read for the current user."""
    
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
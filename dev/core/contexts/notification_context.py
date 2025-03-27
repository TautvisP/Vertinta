from modules.orders.models import Notification

def notification_context(request):
    """Add notification count to all templates."""
    if request.user.is_authenticated:
        unread_notification_count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        return {'unread_notification_count': unread_notification_count}
    return {'unread_notification_count': 0}
import functools
from django.urls import reverse
from .models import Notification

#Memoization is an optimization technique that stores the results of expensive function calls 
#and returns the cached result when the same inputs occur again.
def memoize(method):
    @functools.wraps(method)
    def memoizer(*args, **kwargs):
        method._cache = getattr(method, '_cache', {})
        key = args
        if key not in method._cache:
            method._cache[key] = method(*args, **kwargs)
        return method._cache[key]
    return memoizer



def create_report_submission_notification(report, sender):
    """Create notification for agency when evaluator submits a report."""
    if not report.order.agency:
        return
        
    agency = report.order.agency
    order = report.order
    
    Notification.objects.create(
        recipient=agency,
        sender=sender,
        notification_type='report_submission',
        title='Naujai ataskaitai reikalinga peržiūra',
        message=f'Nauja ataskaita užsakymui # {order.id} reikalauja jūsų peržiūros.',
        related_order=order,
        related_report=report,
        action_url=reverse('modules.agency:review_report', args=[order.id])
    )

def create_report_approval_notification(report, sender):
    """Create notification for evaluator and client when agency approves a report."""
    evaluator = report.order.evaluator
    client = report.order.client
    order = report.order
    
    # Notify evaluator
    if evaluator:
        Notification.objects.create(
            recipient=evaluator,
            sender=sender,
            notification_type='report_approval',
            title='Ataskaita patvirtinta',
            message=f'Ataskaita užsakymui # {order.id} patvirtinta.',
            related_order=order,
            related_report=report,
            action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
        )
    
    # Notify client
    if client:
        Notification.objects.create(
            recipient=client,
            sender=sender,
            notification_type='report_approval',
            title='Ataskaita prieinama',
            message=f'Ataskaita užsakymui # {order.id} patvirtinta.',
            related_order=order,
            related_report=report,
            action_url=reverse('modules.orders:view_report', args=[order.id])
        )

def create_report_rejection_notification(report, sender, reason):
    """Create notification for evaluator when agency rejects a report."""
    evaluator = report.order.evaluator
    order = report.order
    
    if not evaluator:
        return

    Notification.objects.create(
        recipient=evaluator,
        sender=sender,
        notification_type='report_rejection',
        title='Ataskaita atmesta',
        message=f'Jūsų ataskaita užsakymui # {order.id} atmesta. Priežastis: {reason}',
        related_order=order,
        related_report=report,
        action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
    )

def create_order_assignment_notification(order, evaluator, sender):
    """Create notification for evaluator when assigned to an order."""
    Notification.objects.create(
        recipient=evaluator,
        sender=sender,
        notification_type='order_assignment',
        title='Naujas užsakymas',
        message=f'Jums priskirtas užsakymas #{order.id}.',
        related_order=order,
        action_url=reverse('modules.evaluator:evaluation_steps', args=[order.id])
    )


def create_event_notification(event, recipient, sender, is_update=False, is_deleted=False, is_confirmed=False):
    """Create notification for event creation, updates, or deletion."""
    order = event.order
    
    if is_deleted:
        title = 'Įvykis atšauktas'
        message = f'Įvykis "{event.title}" užsakymui #{order.id} buvo atšauktas.'
    elif is_update:
        title = 'Įvykis atnaujintas'
        message = f'Įvykis "{event.title}" užsakymui #{order.id} buvo atnaujintas.'
    elif is_confirmed:
        title = 'Įvykis patvirtintas'
        message = f'Įvykis "{event.title}" užsakymui #{order.id} buvo patvirtintas kliento.'
    else:
        title = 'Naujas įvykis'
        message = f'Naujas įvykis"{event.title}" buvo suplanuotas užsakymui #{order.id}.'
    
    action_url = reverse('modules.orders:event_detail', args=[event.id])
    if is_deleted:
        action_url = reverse('modules.orders:calendar')
    
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type='event',
        title=title,
        message=message,
        related_order=order,
        action_url=action_url
    )

def create_event_transfer_notification(order, new_evaluator, event_count, sender):
    """Create notification for an evaluator when calendar events are transferred."""
    try:
        Notification.objects.create(
            recipient=new_evaluator,
            sender=sender,
            notification_type='event',
            title='Kalendoriaus įvykiai perkelti',
            message=f'Jums buvo perkelti {event_count} kalendoriaus įvykiai, susiję su užsakymu #{order.id}.',
            related_order=order,
            action_url=reverse('modules.orders:calendar')
        )
    except Exception as e:
        print(f"Error sending event transfer notification: {str(e)}")


def create_order_reassignment_notification(order, old_evaluator, new_evaluator, sender, events_transferred=0):
    """Create notification for previous evaluator when order is reassigned."""
    try:
        message = f'Užsakymas #{order.id} buvo perduotas vertintojui {new_evaluator.get_full_name()}.'
        
        if events_transferred > 0:
            message += f' {events_transferred} kalendoriaus įvykiai buvo perkelti.'
            
        Notification.objects.create(
            recipient=old_evaluator,
            sender=sender,
            notification_type='order_assignment',
            title='Užsakymas perduotas kitam vertintojui',
            message=message,
            related_order=order,
            action_url=reverse('modules.orders:evaluator_order_list')
        )
    except Exception as e:
        print(f"Error sending reassignment notification: {str(e)}")
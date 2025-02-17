from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from modules.orders.models import Order
from django.utils.translation import gettext as _

NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")

class EvaluatorAccessMixin:
    """
    Mixin to ensure that only the evaluator associated with the order can access the view.
    """

    def dispatch(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        user = request.user

        # Check if the user is the evaluator associated with the order
        if order.evaluator != user:
            messages.error(request, NO_PERMISSION_MESSAGE)
            return redirect('modules.orders:order_list')

        return super().dispatch(request, *args, **kwargs)
    




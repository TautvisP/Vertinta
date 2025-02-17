from django.contrib.auth.mixins import UserPassesTestMixin

class UserRoleContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_user'] = not (context['is_agency'] or context['is_evaluator'])
        return context

    def is_evaluator(self):
        return self.request.user.groups.filter(name='Evaluator').exists()

    def is_agency(self):
        return self.request.user.groups.filter(name='Agency').exists()

    def is_user(self):
        return not (self.is_agency() or self.is_evaluator())
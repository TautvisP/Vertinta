class UserRoleContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_user'] = not (context['is_agency'] or context['is_evaluator'])
        return context
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.edit import DeleteView
from django.urls import reverse
from .models import PricingConfig


class PricingConfigDeleteView(UserPassesTestMixin, DeleteView):
    """Custom delete view for PricingConfig with audit logging"""
    model = PricingConfig
    template_name = 'admin/pricing/pricingconfig/confirm_delete.html'

    def test_func(self):
        """Ensure only staff users can access"""
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse('admin:pricing_pricingconfig_changelist')

    def delete(self, request, *args, **kwargs):
        """Override delete to log the action"""
        self.object = self.get_object()
        self.object.log_change('DELETE', request.user)
        return super().delete(request, *args, **kwargs)


# Add any other view functions as needed
def pricing_calculator(request):
    """Example view for API calculations"""
    pass  # Implement your pricing logic here
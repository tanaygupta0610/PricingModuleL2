from django.urls import path
from .views import PricingConfigDeleteView

urlpatterns = [
    # Custom delete URL for admin
    path(
        'pricingconfig/<int:pk>/delete/',
        PricingConfigDeleteView.as_view(),
        name='pricingconfig_delete'
    ),

    # Add other app-specific URLs here
    # path('calculate/', pricing_calculator, name='calculate-price'),
]
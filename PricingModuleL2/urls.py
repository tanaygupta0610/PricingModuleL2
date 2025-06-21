"""
URL configuration for PricingModuleL2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
path('pricing/', include('pricing.urls')),
    ]

admin.site.admin_view
admin.site.get_urls = lambda: [
    path('pricing/pricingconfig/<int:pk>/delete/',
         admin.site.admin_view(PricingConfigDeleteView.as_view()),
         name='pricing_pricingconfig_delete')
] + admin.site.get_urls()
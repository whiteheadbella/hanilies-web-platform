"""
URL configuration for hanilies_cakeshoppe_event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from products.views import cake_list
from orders.views import manager_dashboard

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Accounts (login, register, logout, profiles)
    path('accounts/', include('accounts.urls')),

    # OPTIONAL SAFETY REDIRECTS (prevents 404 if you type /login/)
    path('login/', RedirectView.as_view(
        url='/accounts/login/', permanent=False
    )),
    path('register/', RedirectView.as_view(
        url='/accounts/register/', permanent=False
    )),
    path('packages/', RedirectView.as_view(
        url='/products/packages/', permanent=False
    )),

    # App routes
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('customization/', include('customization.urls')),
    path('notifications/', include('notifications.urls')),
    path('audit/', include('audit.urls')),
    path('scheduling/', include('scheduling.urls')),

    # Direct views
    path('cakes/', cake_list, name='cake_list_direct'),
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),

    # Default redirect
    path('', RedirectView.as_view(
        url='/products/home/', permanent=False
    )),
]

# Static & media files (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

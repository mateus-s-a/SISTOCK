"""
URL configuration for sistock project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def redirect_to_dashboard(request):
    """Redireciona ao Dashboard"""
    return redirect('inventory:dashboard')


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Apps URLs
    path('accounts/', include('apps.accounts.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('products/', include('apps.products.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('reports/', include('apps.reports.urls')),

    # Root redirect
    path('', redirect_to_dashboard, name='root'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_header = 'SISTOCK - Administração'
admin.site.site_title = 'SISTOCK Admin'
admin.site.index_title = 'Painel de Controle'

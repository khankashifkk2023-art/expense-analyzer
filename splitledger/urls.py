"""
Root URL configuration for splitledger.

Routes:
    /admin/         — Django admin
    /auth/          — Login, register, logout (Deliverable 2)
    /               — All other app routes (groups, expenses, balances, etc.)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve uploaded files (CSV imports) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL configuration for xamila project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Xamila API is running',
        'debug': settings.DEBUG
    })

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    path('', health_check, name='root_health_check'),
    
    # Admin Django
    path('admin/', admin.site.urls),
    
    # API Authentication (JWT)
    path('api/auth/', include('core.urls_auth')),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Core (SGI Matching System)
    path('api/', include('core.urls')),
    
    # API Documentation (Swagger/OpenAPI)
    path('api/docs/', include('core.urls_swagger')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

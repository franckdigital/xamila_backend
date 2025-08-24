"""
URLs pour la documentation Swagger/OpenAPI de l'API Xamila
"""

from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

app_name = 'api_docs'

urlpatterns = [
    # Schema OpenAPI (JSON/YAML)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interface Swagger UI (recommandée)
    path('', SpectacularSwaggerView.as_view(url_name='api_docs:schema'), name='swagger-ui'),
    
    # Interface ReDoc (alternative)
    path('redoc/', SpectacularRedocView.as_view(url_name='api_docs:schema'), name='redoc'),
]

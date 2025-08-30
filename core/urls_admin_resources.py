from django.urls import path
from .views_admin_resources import update_resource_content, get_admin_resource_content

urlpatterns = [
    path('', update_resource_content, name='update_resource_content'),
    path('get/', get_admin_resource_content, name='get_admin_resource_content'),
]

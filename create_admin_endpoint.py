#!/usr/bin/env python
"""
Script pour créer un endpoint temporaire de création d'admin via API
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@csrf_exempt
@require_http_methods(["POST"])
def create_admin_user(request):
    """
    Endpoint temporaire pour créer l'utilisateur admin via API
    POST /api/create-admin/
    """
    try:
        data = json.loads(request.body)
        
        # ID exact du token JWT
        user_id = data.get('id', "30039510-2cc1-41b5-a483-b668513cd4e8")
        email = data.get('email', "franckalain.digital@gmail.com")
        username = data.get('username', "franckalain.digital")
        first_name = data.get('first_name', "franck")
        last_name = data.get('last_name', "alain")
        password = data.get('password', "XamilaAdmin2025!")
        
        # Vérifier si l'utilisateur existe déjà
        try:
            existing_user = User.objects.get(id=user_id)
            return JsonResponse({
                'success': False,
                'message': f'Utilisateur existe déjà: {existing_user.email}',
                'user_id': str(existing_user.id),
                'role': existing_user.role
            })
        except User.DoesNotExist:
            pass
        
        # Créer l'utilisateur admin
        admin_user = User.objects.create_user(
            id=user_id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role="ADMIN",
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            password=password
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Utilisateur admin créé avec succès',
            'user': {
                'id': str(admin_user.id),
                'email': admin_user.email,
                'username': admin_user.username,
                'first_name': admin_user.first_name,
                'last_name': admin_user.last_name,
                'role': admin_user.role,
                'is_staff': admin_user.is_staff,
                'is_superuser': admin_user.is_superuser,
                'is_active': admin_user.is_active,
                'is_verified': admin_user.is_verified,
                'created_at': admin_user.created_at.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON invalide'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

if __name__ == '__main__':
    print("Endpoint de création admin défini")
    print("Ajoutez cette vue à vos URLs pour l'utiliser via Postman")

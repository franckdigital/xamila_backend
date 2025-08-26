#!/usr/bin/env python
"""
Script rapide pour créer l'utilisateur admin manquant avec l'ID exact du token JWT
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# ID exact du token JWT
user_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
email = "franckalain.digital@gmail.com"

try:
    # Vérifier si existe déjà
    user = User.objects.get(id=user_id)
    print(f"Utilisateur existe: {user.email}")
except User.DoesNotExist:
    # Créer l'utilisateur
    user = User.objects.create_user(
        id=user_id,
        email=email,
        username="franckalain.digital",
        first_name="franck",
        last_name="alain",
        role="ADMIN",
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_verified=True,
        password="XamilaAdmin2025!"
    )
    print(f"Admin créé: {user.email} - ID: {user.id}")

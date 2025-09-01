#!/usr/bin/env python3
"""
Script pour créer un utilisateur de test pour les objectifs d'épargne
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
sys.path.append('/app')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    """Créer un utilisateur de test"""
    email = "test3@xamila.finance"
    password = "test123"
    
    # Supprimer l'utilisateur s'il existe déjà
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        user.delete()
        print(f"Utilisateur existant supprimé: {email}")
    
    # Créer le nouvel utilisateur
    user = User.objects.create_user(
        email=email,
        password=password,
        is_active=True,
        is_verified=True
    )
    
    # Ajouter des champs utilisateur supplémentaires
    user.age_range = '25-34'
    user.gender = 'M'
    user.country = 'Sénégal'
    user.save()
    
    print(f"Utilisateur créé: {email}")
    print(f"ID utilisateur: {user.id}")
    
    return user

if __name__ == "__main__":
    create_test_user()

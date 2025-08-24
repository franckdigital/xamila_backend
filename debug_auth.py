#!/usr/bin/env python
"""
Script de diagnostic et correction pour l'authentification XAMILA
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import User
from django.contrib.auth.hashers import make_password, check_password

def create_test_user():
    """Créer un utilisateur de test"""
    email = "test@xamila.com"
    password = "test123"
    
    # Supprimer l'utilisateur existant s'il existe
    User.objects.filter(email=email).delete()
    
    # Créer un nouvel utilisateur
    user = User.objects.create(
        email=email,
        first_name="Test",
        last_name="User",
        role="CUSTOMER",
        is_active=True,
        is_verified=True,
        password=make_password(password)
    )
    
    print(f"✅ Utilisateur créé: {email}")
    print(f"   Mot de passe: {password}")
    print(f"   ID: {user.id}")
    print(f"   Actif: {user.is_active}")
    print(f"   Vérifié: {user.is_verified}")
    
    return user, password

def test_authentication():
    """Tester l'authentification"""
    print("\n🔍 Test d'authentification...")
    
    user, password = create_test_user()
    
    # Test 1: Vérifier le hash du mot de passe
    print(f"\n1. Test du hash du mot de passe:")
    print(f"   Hash stocké: {user.password[:50]}...")
    print(f"   Vérification: {check_password(password, user.password)}")
    
    # Test 2: Authentification Django
    print(f"\n2. Test d'authentification Django:")
    auth_user = authenticate(username=user.email, password=password)
    print(f"   Résultat: {auth_user is not None}")
    if auth_user:
        print(f"   Utilisateur authentifié: {auth_user.email}")
    
    # Test 3: Récupération par email
    print(f"\n3. Test de récupération par email:")
    try:
        db_user = User.objects.get(email=user.email)
        print(f"   Trouvé: {db_user.email}")
        print(f"   Actif: {db_user.is_active}")
    except User.DoesNotExist:
        print("   ❌ Utilisateur non trouvé")
    
    return user

def check_settings():
    """Vérifier les paramètres Django"""
    print("\n⚙️ Vérification des paramètres...")
    
    from django.conf import settings
    
    print(f"AUTH_USER_MODEL: {getattr(settings, 'AUTH_USER_MODEL', 'Non défini')}")
    print(f"AUTHENTICATION_BACKENDS: {getattr(settings, 'AUTHENTICATION_BACKENDS', 'Non défini')}")
    
    # Vérifier le modèle User
    print(f"\nModèle User:")
    print(f"   USERNAME_FIELD: {User.USERNAME_FIELD}")
    print(f"   REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")

def main():
    """Fonction principale"""
    print("🚀 Diagnostic d'authentification XAMILA")
    print("=" * 50)
    
    check_settings()
    test_user = test_authentication()
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic terminé")
    print(f"\n📝 Utilisateur de test créé:")
    print(f"   Email: test@xamila.com")
    print(f"   Mot de passe: test123")
    print(f"\n🔗 Testez la connexion sur: http://localhost:8000/auth/login/")

if __name__ == "__main__":
    main()

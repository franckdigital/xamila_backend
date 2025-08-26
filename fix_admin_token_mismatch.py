#!/usr/bin/env python
"""
Script pour résoudre la discordance entre l'ID du token JWT et l'ID réel de l'admin
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def fix_admin_token_mismatch():
    """
    Résout le problème de discordance entre l'ID du token JWT et l'ID réel de l'admin
    """
    
    print("=" * 80)
    print("           CORRECTION DISCORDANCE TOKEN JWT ADMIN")
    print("=" * 80)
    
    # ID dans le token JWT actuel (incorrect)
    token_user_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    
    # ID réel de l'admin en base de données
    real_admin_id = "74a5de49-eb85-48dc-9935-a5ae7e83cf2f"
    admin_email = "franckalain.digital@gmail.com"
    
    print(f"\n🔍 ANALYSE DU PROBLÈME:")
    print(f"   ID dans token JWT: {token_user_id}")
    print(f"   ID réel admin DB:  {real_admin_id}")
    print(f"   Email admin:       {admin_email}")
    
    # Vérifier l'utilisateur avec l'ID du token
    try:
        token_user = User.objects.get(id=token_user_id)
        print(f"\n❌ PROBLÈME: Utilisateur trouvé avec ID token:")
        print(f"   Email: {token_user.email}")
        print(f"   Role: {token_user.role}")
        print(f"   Username: {token_user.username}")
    except User.DoesNotExist:
        print(f"\n✅ CONFIRMÉ: Aucun utilisateur avec l'ID du token")
    
    # Vérifier l'admin réel
    try:
        real_admin = User.objects.get(id=real_admin_id)
        print(f"\n✅ ADMIN RÉEL TROUVÉ:")
        print(f"   ID: {real_admin.id}")
        print(f"   Email: {real_admin.email}")
        print(f"   Role: {real_admin.role}")
        print(f"   Username: {real_admin.username}")
        print(f"   Actif: {real_admin.is_active}")
        print(f"   Staff: {real_admin.is_staff}")
        print(f"   Superuser: {real_admin.is_superuser}")
        
        # Générer un nouveau token JWT avec l'ID correct
        print(f"\n🔑 GÉNÉRATION NOUVEAU TOKEN JWT:")
        refresh = RefreshToken.for_user(real_admin)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        print(f"\n✅ NOUVEAUX TOKENS GÉNÉRÉS:")
        print(f"Access Token: {access_token}")
        print(f"Refresh Token: {refresh_token}")
        
        print(f"\n📋 INSTRUCTIONS POUR CORRIGER:")
        print(f"1. Remplacer dans localStorage du frontend:")
        print(f"   access_token: {access_token}")
        print(f"   refresh_token: {refresh_token}")
        print(f"")
        print(f"2. Ou se reconnecter avec:")
        print(f"   Email: {real_admin.email}")
        print(f"   Mot de passe: [mot de passe admin]")
        print(f"")
        print(f"3. L'ID utilisateur sera maintenant: {real_admin.id}")
        
        return {
            'success': True,
            'real_admin': real_admin,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        
    except User.DoesNotExist:
        print(f"\n❌ ERREUR: Admin réel non trouvé avec ID {real_admin_id}")
        return {'success': False, 'error': 'Admin not found'}

def create_missing_admin_if_needed():
    """
    Crée l'utilisateur admin avec l'ID du token si nécessaire
    """
    
    token_user_id = "30039510-2cc1-41b5-a483-b668513cd4e8"
    admin_email = "franckalain.digital@gmail.com"
    
    print(f"\n🔧 OPTION ALTERNATIVE: Créer admin avec ID du token")
    
    try:
        # Vérifier si l'utilisateur avec l'ID du token existe
        User.objects.get(id=token_user_id)
        print(f"✅ Utilisateur avec ID token existe déjà")
        return False
    except User.DoesNotExist:
        pass
    
    try:
        # Créer l'utilisateur admin avec l'ID du token
        admin_user = User.objects.create_user(
            id=token_user_id,
            email=admin_email,
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
        
        print(f"✅ ADMIN CRÉÉ avec ID du token:")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur création admin: {e}")
        return False

if __name__ == '__main__':
    print(f"🚀 Script exécuté pour résoudre la discordance token JWT")
    
    # Option 1: Analyser et générer nouveau token
    result = fix_admin_token_mismatch()
    
    if not result['success']:
        print(f"\n🔄 TENTATIVE OPTION ALTERNATIVE...")
        # Option 2: Créer admin avec ID du token
        created = create_missing_admin_if_needed()
        
        if created:
            print(f"\n✅ PROBLÈME RÉSOLU: Admin créé avec ID du token")
            print(f"   Le token JWT existant fonctionnera maintenant")
        else:
            print(f"\n❌ ÉCHEC: Impossible de résoudre la discordance")
    else:
        print(f"\n✅ PROBLÈME ANALYSÉ: Utilisez les nouveaux tokens générés")
    
    print(f"\n" + "=" * 80)

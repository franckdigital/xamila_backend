#!/usr/bin/env python
"""
Script pour créer automatiquement un super administrateur XAMILA
"""

import os
import sys
import django
from django.contrib.auth.hashers import make_password

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User

def create_superuser_auto():
    """
    Créer automatiquement un super administrateur XAMILA
    """
    print("=== CRÉATION AUTOMATIQUE D'UN SUPER ADMINISTRATEUR XAMILA ===")
    
    # Informations par défaut du super admin
    email = "admin@xamila.com"
    first_name = "Super"
    last_name = "Admin"
    phone = "+33123456789"
    password = "SuperAdmin123!"
    
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            print(f"⚠️  Un utilisateur avec l'email {email} existe déjà.")
            print(f"🔄 Mise à jour des permissions super admin...")
            
            # Mettre à jour les permissions
            existing_user.role = 'ADMIN'
            existing_user.is_staff = True
            existing_user.is_superuser = True
            existing_user.is_active = True
            existing_user.email_verified = True
            existing_user.phone_verified = True
            existing_user.password = make_password(password)
            existing_user.save()
            
            superuser = existing_user
            print("✅ Utilisateur existant mis à jour avec les permissions super admin !")
        else:
            # Créer le super utilisateur
            superuser = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                password=make_password(password),
                role='ADMIN',
                is_staff=True,
                is_superuser=True,
                is_active=True,
                email_verified=True,
                phone_verified=True
            )
            print("✅ NOUVEAU SUPER ADMINISTRATEUR CRÉÉ AVEC SUCCÈS !")
        
        print(f"\n📋 INFORMATIONS DU SUPER ADMIN:")
        print(f"📧 Email: {superuser.email}")
        print(f"👤 Nom: {superuser.first_name} {superuser.last_name}")
        print(f"📱 Téléphone: {superuser.phone}")
        print(f"🔑 Mot de passe: {password}")
        print(f"🆔 ID: {superuser.id}")
        print(f"🔐 Role: {superuser.role}")
        print(f"✅ Actif: {superuser.is_active}")
        print(f"👑 Super Admin: {superuser.is_superuser}")
        print(f"📧 Email vérifié: {superuser.email_verified}")
        
        print(f"\n🚀 CONNEXION AU DASHBOARD ADMIN:")
        print(f"URL: http://localhost:3000/login")
        print(f"Email: {email}")
        print(f"Mot de passe: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {str(e)}")
        import traceback
        print(f"Détails: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = create_superuser_auto()
    if success:
        print("\n🎉 SUPER ADMIN PRÊT ! Vous pouvez maintenant vous connecter au dashboard.")
    else:
        print("\n❌ Échec de la création du super admin.")

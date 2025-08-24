#!/usr/bin/env python
"""
Script pour créer un super administrateur XAMILA
Usage: python create_superuser.py
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

def create_superuser():
    """
    Créer un super administrateur XAMILA
    """
    print("=== CRÉATION D'UN SUPER ADMINISTRATEUR XAMILA ===")
    
    # Vérifier si un super admin existe déjà
    existing_superuser = User.objects.filter(is_superuser=True).first()
    if existing_superuser:
        print(f"Un super administrateur existe déjà: {existing_superuser.email}")
        response = input("Voulez-vous en créer un nouveau ? (y/N): ")
        if response.lower() != 'y':
            print("Annulé.")
            return
    
    # Informations du super admin
    email = input("Email du super admin (ex: admin@xamila.com): ").strip()
    if not email:
        email = "admin@xamila.com"
    
    first_name = input("Prénom (ex: Super): ").strip()
    if not first_name:
        first_name = "Super"
    
    last_name = input("Nom (ex: Admin): ").strip()
    if not last_name:
        last_name = "Admin"
    
    phone = input("Téléphone (ex: +33123456789): ").strip()
    if not phone:
        phone = "+33123456789"
    
    password = input("Mot de passe (ex: SuperAdmin123!): ").strip()
    if not password:
        password = "SuperAdmin123!"
    
    try:
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
        
        print("\n✅ SUPER ADMINISTRATEUR CRÉÉ AVEC SUCCÈS !")
        print(f"📧 Email: {superuser.email}")
        print(f"👤 Nom: {superuser.first_name} {superuser.last_name}")
        print(f"📱 Téléphone: {superuser.phone}")
        print(f"🔑 Mot de passe: {password}")
        print(f"🆔 ID: {superuser.id}")
        print(f"🔐 Role: {superuser.role}")
        print(f"✅ Actif: {superuser.is_active}")
        print(f"👑 Super Admin: {superuser.is_superuser}")
        
        print("\n🚀 CONNEXION AU DASHBOARD ADMIN:")
        print(f"URL: http://localhost:3000/login")
        print(f"Email: {email}")
        print(f"Mot de passe: {password}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    create_superuser()

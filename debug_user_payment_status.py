#!/usr/bin/env python
"""
Script pour vérifier le statut de paiement de l'utilisateur demo@xamila.finance
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
sys.path.append('/var/www/xamila/xamila_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from django.db import connection

def check_user_payment_status():
    """Vérifie le statut de paiement de l'utilisateur demo"""
    print("=== VÉRIFICATION STATUT PAIEMENT UTILISATEUR ===")
    
    try:
        # Récupérer l'utilisateur demo
        user = User.objects.get(email='demo@xamila.finance')
        print(f"✅ Utilisateur trouvé: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Nom: {user.first_name} {user.last_name}")
        print(f"   Rôle: {user.role}")
        print(f"   Actif: {user.is_active}")
        
        # Vérifier si les nouveaux champs existent
        try:
            paye_status = getattr(user, 'paye', 'CHAMP_INEXISTANT')
            certif_status = getattr(user, 'certif_reussite', 'CHAMP_INEXISTANT')
            
            print(f"   Paiement (paye): {paye_status}")
            print(f"   Certificat (certif_reussite): {certif_status}")
            
            if paye_status == 'CHAMP_INEXISTANT':
                print("❌ Le champ 'paye' n'existe pas encore dans la base de données")
                print("   → Il faut terminer la migration")
            
            if certif_status == 'CHAMP_INEXISTANT':
                print("❌ Le champ 'certif_reussite' n'existe pas encore dans la base de données")
                print("   → Il faut terminer la migration")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'accès aux champs: {e}")
            
    except User.DoesNotExist:
        print("❌ Utilisateur demo@xamila.finance non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def check_database_schema():
    """Vérifie si les colonnes existent dans la base de données"""
    print("\n=== VÉRIFICATION SCHÉMA BASE DE DONNÉES ===")
    
    with connection.cursor() as cursor:
        # Vérifier les colonnes de la table User
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM information_schema.columns 
            WHERE table_name = 'core_user' 
            AND table_schema = DATABASE()
            AND COLUMN_NAME IN ('paye', 'certif_reussite')
            ORDER BY COLUMN_NAME
        """)
        
        columns = cursor.fetchall()
        
        if columns:
            print("✅ Colonnes de paiement trouvées:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        else:
            print("❌ Aucune colonne de paiement trouvée")
            print("   → Les migrations ne sont pas encore appliquées")

def check_migrations_status():
    """Vérifie l'état des migrations"""
    print("\n=== VÉRIFICATION ÉTAT DES MIGRATIONS ===")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name, applied 
            FROM django_migrations 
            WHERE app = 'core' 
            AND name LIKE '%payment%' OR name LIKE '%007%'
            ORDER BY applied DESC
        """)
        
        migrations = cursor.fetchall()
        
        if migrations:
            print("Migrations liées au paiement:")
            for migration in migrations:
                print(f"   - {migration[0]}: {migration[1]}")
        else:
            print("❌ Aucune migration de paiement trouvée")

if __name__ == "__main__":
    try:
        check_database_schema()
        check_migrations_status()
        check_user_payment_status()
        
        print("\n=== SOLUTIONS POSSIBLES ===")
        print("1. Si les champs n'existent pas:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        print()
        print("2. Si les champs existent mais l'utilisateur n'est pas payant:")
        print("   python manage.py shell -c \"")
        print("   from core.models import User")
        print("   user = User.objects.get(email='demo@xamila.finance')")
        print("   user.paye = True")
        print("   user.save()\"")
        print()
        print("3. L'utilisateur doit se déconnecter et se reconnecter")
        print("   pour récupérer les nouvelles données")
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()

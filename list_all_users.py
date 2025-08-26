#!/usr/bin/env python
"""
Script pour lister tous les utilisateurs de la base de données Xamila
"""
import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

def list_all_users():
    """Liste tous les utilisateurs avec leurs informations détaillées"""
    
    print("=" * 80)
    print("                    LISTE DES UTILISATEURS XAMILA")
    print("=" * 80)
    
    try:
        # Récupérer tous les utilisateurs
        users = User.objects.all().order_by('-created_at')
        total_users = users.count()
        
        print(f"\n📊 STATISTIQUES GÉNÉRALES")
        print(f"   Total utilisateurs: {total_users}")
        
        # Statistiques par rôle
        role_stats = User.objects.values('role').annotate(count=Count('role')).order_by('role')
        print(f"\n📋 RÉPARTITION PAR RÔLE:")
        for stat in role_stats:
            role_name = stat['role'] or 'Non défini'
            count = stat['count']
            print(f"   {role_name}: {count} utilisateur(s)")
        
        # Statistiques par statut
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        superusers = User.objects.filter(is_superuser=True).count()
        
        print(f"\n🔐 STATUTS:")
        print(f"   Actifs: {active_users}")
        print(f"   Vérifiés: {verified_users}")
        print(f"   Staff: {staff_users}")
        print(f"   Superusers: {superusers}")
        
        print(f"\n" + "=" * 80)
        print("                      DÉTAIL DES UTILISATEURS")
        print("=" * 80)
        
        if total_users == 0:
            print("\n❌ Aucun utilisateur trouvé dans la base de données")
            return
        
        # Afficher chaque utilisateur
        for i, user in enumerate(users, 1):
            print(f"\n👤 UTILISATEUR #{i}")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Nom: {user.first_name} {user.last_name}")
            print(f"   Téléphone: {user.phone or 'Non renseigné'}")
            print(f"   Rôle: {user.role}")
            
            # Informations géographiques
            if user.country_of_residence or user.country_of_origin:
                print(f"   Pays résidence: {user.country_of_residence or 'Non renseigné'}")
                print(f"   Pays origine: {user.country_of_origin or 'Non renseigné'}")
            
            # Statuts
            statuses = []
            if user.is_active:
                statuses.append("✅ Actif")
            else:
                statuses.append("❌ Inactif")
            
            if user.is_verified:
                statuses.append("✅ Vérifié")
            else:
                statuses.append("⏳ Non vérifié")
            
            if user.is_staff:
                statuses.append("👨‍💼 Staff")
            
            if user.is_superuser:
                statuses.append("🔑 Superuser")
            
            print(f"   Statuts: {' | '.join(statuses)}")
            
            # Vérifications email/téléphone
            verifications = []
            if user.email_verified:
                verifications.append("📧 Email vérifié")
            else:
                verifications.append("📧 Email non vérifié")
            
            if user.phone_verified:
                verifications.append("📱 Téléphone vérifié")
            else:
                verifications.append("📱 Téléphone non vérifié")
            
            print(f"   Vérifications: {' | '.join(verifications)}")
            
            # Dates
            created_date = user.created_at.strftime("%d/%m/%Y %H:%M") if user.created_at else "Non disponible"
            updated_date = user.updated_at.strftime("%d/%m/%Y %H:%M") if user.updated_at else "Non disponible"
            last_login = user.last_login.strftime("%d/%m/%Y %H:%M") if user.last_login else "Jamais connecté"
            
            print(f"   Créé le: {created_date}")
            print(f"   Modifié le: {updated_date}")
            print(f"   Dernière connexion: {last_login}")
            
            print("-" * 60)
        
        print(f"\n✅ Affichage terminé - {total_users} utilisateur(s) listé(s)")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la récupération des utilisateurs: {e}")
        return False
    
    return True

def search_user_by_id(user_id):
    """Recherche un utilisateur spécifique par ID"""
    
    print(f"\n🔍 RECHERCHE UTILISATEUR ID: {user_id}")
    print("-" * 50)
    
    try:
        user = User.objects.get(id=user_id)
        
        print(f"✅ Utilisateur trouvé:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nom complet: {user.first_name} {user.last_name}")
        print(f"   Rôle: {user.role}")
        print(f"   Actif: {'Oui' if user.is_active else 'Non'}")
        print(f"   Staff: {'Oui' if user.is_staff else 'Non'}")
        print(f"   Superuser: {'Oui' if user.is_superuser else 'Non'}")
        
        return True
        
    except User.DoesNotExist:
        print(f"❌ Aucun utilisateur trouvé avec l'ID: {user_id}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la recherche: {e}")
        return False

def search_admin_users():
    """Liste uniquement les utilisateurs admin"""
    
    print(f"\n👑 UTILISATEURS ADMINISTRATEURS")
    print("-" * 50)
    
    try:
        admins = User.objects.filter(role='ADMIN').order_by('-created_at')
        
        if not admins.exists():
            print("❌ Aucun administrateur trouvé")
            return False
        
        for admin in admins:
            print(f"\n👤 {admin.username}")
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   Nom: {admin.first_name} {admin.last_name}")
            print(f"   Actif: {'✅' if admin.is_active else '❌'}")
            print(f"   Staff: {'✅' if admin.is_staff else '❌'}")
            print(f"   Superuser: {'✅' if admin.is_superuser else '❌'}")
            print(f"   Créé: {admin.created_at.strftime('%d/%m/%Y %H:%M') if admin.created_at else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la recherche des admins: {e}")
        return False

if __name__ == '__main__':
    print(f"🚀 Script exécuté le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}")
    
    # Vérifier les arguments de ligne de commande
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'admin' or command == 'admins':
            # Lister uniquement les admins
            search_admin_users()
        elif command.startswith('id:'):
            # Rechercher par ID
            user_id = command.split(':', 1)[1]
            search_user_by_id(user_id)
        else:
            print(f"❌ Commande inconnue: {command}")
            print("Usage:")
            print("  python list_all_users.py           # Lister tous les utilisateurs")
            print("  python list_all_users.py admin     # Lister uniquement les admins")
            print("  python list_all_users.py id:UUID   # Rechercher par ID")
    else:
        # Lister tous les utilisateurs par défaut
        list_all_users()

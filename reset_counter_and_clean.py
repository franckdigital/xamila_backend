#!/usr/bin/env python
"""
Script pour réinitialiser le compteur et nettoyer les données
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import SavingsDeposit, SavingsAccount, ChallengeParticipation

def reset_counter_and_clean():
    """Réinitialise le compteur et nettoie les données"""
    
    print("=== RESET COMPTEUR ET NETTOYAGE ===")
    
    try:
        # 1. Supprimer tous les dépôts existants
        print("\n1. Suppression des dépôts existants...")
        deposits_count = SavingsDeposit.objects.count()
        SavingsDeposit.objects.all().delete()
        print(f"   {deposits_count} dépôts supprimés")
        
        # 2. Supprimer les comptes d'épargne en double
        print("\n2. Nettoyage des comptes d'épargne...")
        user = User.objects.get(email='test@xamila.com')
        accounts = SavingsAccount.objects.filter(user=user)
        print(f"   {accounts.count()} comptes trouvés pour {user.email}")
        
        # Supprimer tous les comptes
        accounts.delete()
        print("   Tous les comptes supprimés")
        
        # 3. Réinitialiser les participations
        print("\n3. Réinitialisation des participations...")
        participations = ChallengeParticipation.objects.all()
        for participation in participations:
            participation.current_amount = 0
            participation.save()
            print(f"   Participation {participation.user.email}: montant remis à 0")
        
        # 4. Vérifier l'utilisateur test
        print("\n4. Vérification utilisateur test...")
        try:
            user = User.objects.get(email='test@xamila.com')
            print(f"   Utilisateur trouvé: {user.email} (ID: {user.id})")
            
            # Créer un nouveau compte d'épargne
            account = SavingsAccount.objects.create(
                user=user,
                account_number=f'SAV{str(user.id)[:8]}',
                account_name='Compte Principal',
                account_type='BASIC',
                balance=0,
                status='ACTIVE'
            )
            print(f"   Nouveau compte créé: {account.account_number} - Solde: {account.balance}")
                
        except User.DoesNotExist:
            print("   ERREUR: Utilisateur test non trouvé!")
            return
        
        print("\n=== RESET TERMINÉ ===")
        print("Le système est prêt pour de nouveaux tests")
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_counter_and_clean()

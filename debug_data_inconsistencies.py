#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.append('/Users/kfran/CascadeProjects/fintech/xamila_backend')
os.chdir('/Users/kfran/CascadeProjects/fintech/xamila_backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import User, SavingsAccount, SavingsDeposit, ChallengeParticipation
from django.db.models import Sum

def debug_data_inconsistencies():
    print("=== DEBUG DATA INCONSISTENCIES ===\n")
    
    try:
        # Vérifier l'utilisateur test
        user = User.objects.get(email='test@xamila.com')
        print(f"Utilisateur: {user.first_name} {user.last_name} (ID: {user.id})")
        
        # Vérifier le compte d'épargne
        account = SavingsAccount.objects.filter(user=user).first()
        if account:
            print(f"Solde compte épargne: {account.balance} FCFA")
        else:
            print("Aucun compte épargne trouvé")
        
        # Vérifier les dépôts
        deposits = SavingsDeposit.objects.filter(participation__user=user)
        total_deposits = deposits.aggregate(Sum('amount'))['amount__sum'] or 0
        print(f"Total des dépôts: {total_deposits} FCFA")
        print(f"Nombre de dépôts: {deposits.count()}")
        
        # Vérifier les participations
        participations = ChallengeParticipation.objects.filter(user=user)
        print(f"\nParticipations ({participations.count()}):")
        for p in participations:
            print(f"- {p.challenge.title}: {p.total_saved} FCFA (Status: {p.status})")
        
        # Vérifier les transactions récentes
        print("\nDernières transactions:")
        for deposit in deposits.order_by('-created_at')[:10]:
            print(f"- {deposit.created_at.strftime('%Y-%m-%d %H:%M')}: {deposit.amount} FCFA ({deposit.deposit_method})")
        
        # Calculer le solde réel basé sur les transactions
        deposits_sum = SavingsDeposit.objects.filter(
            participation__user=user,
            status='CONFIRMED'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        print(f"\nCalcul du solde réel:")
        print(f"- Dépôts confirmés: {deposits_sum} FCFA")
        print(f"- Solde en BD: {account.balance if account else 0} FCFA")
        print(f"- Différence: {(account.balance if account else 0) - deposits_sum} FCFA")
        
        # Vérifier les retraits (si ils existent)
        # Note: Il faudra créer un modèle SavingsWithdrawal si pas encore fait
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data_inconsistencies()

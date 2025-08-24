#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import User, SavingsAccount, SavingsDeposit, ChallengeParticipation
from django.db.models import Sum

def check_data_consistency():
    print("=== VÉRIFICATION COHÉRENCE DONNÉES ===\n")
    
    try:
        # Utilisateur test
        user = User.objects.get(email='test@xamila.com')
        print(f"Utilisateur: {user.first_name} {user.last_name} (ID: {user.id})")
        
        # Compte d'épargne
        account = SavingsAccount.objects.filter(user=user).first()
        if account:
            print(f"Solde compte épargne BD: {account.balance} FCFA")
        else:
            print("❌ Aucun compte épargne trouvé")
            return
        
        # Dépôts confirmés
        confirmed_deposits = SavingsDeposit.objects.filter(
            participation__user=user,
            status='CONFIRMED'
        )
        total_deposits = confirmed_deposits.aggregate(Sum('amount'))['amount__sum'] or 0
        print(f"Total dépôts confirmés: {total_deposits} FCFA")
        print(f"Nombre de dépôts: {confirmed_deposits.count()}")
        
        # Participations
        participations = ChallengeParticipation.objects.filter(user=user, status='ACTIVE')
        print(f"\nParticipations actives ({participations.count()}):")
        total_participation_saved = 0
        for p in participations:
            print(f"- {p.challenge.title}: {p.total_saved} FCFA")
            total_participation_saved += p.total_saved
        
        print(f"\nTotal épargné via participations: {total_participation_saved} FCFA")
        
        # Transactions récentes
        print(f"\nDernières transactions ({confirmed_deposits.count()}):")
        for deposit in confirmed_deposits.order_by('-created_at')[:10]:
            print(f"- {deposit.created_at.strftime('%Y-%m-%d %H:%M')}: +{deposit.amount} FCFA ({deposit.deposit_method})")
        
        # Analyse des incohérences
        print(f"\n=== ANALYSE INCOHÉRENCES ===")
        print(f"Solde BD compte épargne: {account.balance} FCFA")
        print(f"Total dépôts confirmés: {total_deposits} FCFA")
        print(f"Total participations: {total_participation_saved} FCFA")
        
        if account.balance != total_deposits:
            print(f"❌ INCOHÉRENCE: Solde BD ({account.balance}) ≠ Total dépôts ({total_deposits})")
        else:
            print("✅ Cohérence: Solde BD = Total dépôts")
            
        if total_participation_saved != total_deposits:
            print(f"❌ INCOHÉRENCE: Participations ({total_participation_saved}) ≠ Dépôts ({total_deposits})")
        else:
            print("✅ Cohérence: Participations = Dépôts")
        
        # Vérifier s'il y a des retraits (transactions négatives)
        all_deposits = SavingsDeposit.objects.filter(participation__user=user)
        negative_amounts = all_deposits.filter(amount__lt=0)
        if negative_amounts.exists():
            print(f"\n⚠️  Retraits détectés ({negative_amounts.count()}):")
            for withdrawal in negative_amounts.order_by('-created_at'):
                print(f"- {withdrawal.created_at.strftime('%Y-%m-%d %H:%M')}: {withdrawal.amount} FCFA")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data_consistency()

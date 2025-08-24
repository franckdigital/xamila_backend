#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import User, SavingsAccount, SavingsDeposit, ChallengeParticipation
from django.db.models import Sum
from decimal import Decimal

def fix_data_inconsistencies():
    print("=== CORRECTION DES INCOHÉRENCES ===\n")
    
    try:
        # Utilisateur test
        user = User.objects.get(email='test@xamila.com')
        print(f"Utilisateur: {user.first_name} {user.last_name}")
        
        # Compte d'épargne
        account = SavingsAccount.objects.filter(user=user, status='ACTIVE').first()
        if not account:
            print("❌ Aucun compte d'épargne trouvé")
            return
            
        print(f"Solde actuel BD: {account.balance} FCFA")
        
        # Calculer le solde réel basé sur les transactions
        deposits = SavingsDeposit.objects.filter(
            participation__user=user,
            status='CONFIRMED'
        )
        
        total_transactions = deposits.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        print(f"Total des transactions: {total_transactions} FCFA")
        
        # Corriger le solde du compte
        if account.balance != total_transactions:
            print(f"🔧 Correction du solde: {account.balance} → {total_transactions}")
            account.balance = total_transactions
            account.save()
        
        # Corriger les participations
        participations = ChallengeParticipation.objects.filter(user=user, status='ACTIVE')
        for participation in participations:
            print(f"\nParticipation: {participation.challenge.title}")
            print(f"Total épargné actuel: {participation.total_saved} FCFA")
            
            # Calculer le total réel des dépôts pour cette participation
            participation_deposits = SavingsDeposit.objects.filter(
                participation=participation,
                status='CONFIRMED'
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
            
            print(f"Total réel des dépôts: {participation_deposits} FCFA")
            
            if participation.total_saved != participation_deposits:
                print(f"🔧 Correction participation: {participation.total_saved} → {participation_deposits}")
                participation.total_saved = participation_deposits
                
                # Recalculer la progression
                if participation.personal_target > 0:
                    participation.progress_percentage = (participation_deposits / participation.personal_target) * 100
                
                # Recalculer les points
                participation.points_earned = int(participation_deposits / 1000)
                
                # Compter les dépôts (positifs seulement)
                participation.deposits_count = SavingsDeposit.objects.filter(
                    participation=participation,
                    status='CONFIRMED',
                    amount__gt=0
                ).count()
                
                participation.save()
        
        print(f"\n✅ Corrections appliquées")
        
        # Vérification finale
        print(f"\n=== VÉRIFICATION FINALE ===")
        account.refresh_from_db()
        print(f"Solde compte: {account.balance} FCFA")
        
        for participation in participations:
            participation.refresh_from_db()
            print(f"Participation {participation.challenge.title}: {participation.total_saved} FCFA")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_data_inconsistencies()

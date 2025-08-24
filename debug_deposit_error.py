#!/usr/bin/env python
"""
Debug l'erreur de dépôt
"""

import os
import sys
import django
import requests
import traceback

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import SavingsDeposit, SavingsAccount, ChallengeParticipation, SavingsChallenge
from decimal import Decimal
from django.utils import timezone
import uuid

def debug_deposit():
    """Debug le processus de dépôt"""
    
    print("=== DEBUG DEPOT ===")
    
    try:
        # 1. Vérifier l'utilisateur
        user = User.objects.get(email='test@xamila.com')
        print(f"OK Utilisateur: {user.email}")
        
        # 2. Vérifier les défis
        challenges = SavingsChallenge.objects.filter(status='ACTIVE', is_public=True)
        print(f"OK Défis actifs: {challenges.count()}")
        for challenge in challenges:
            print(f"  - {challenge.title}")
        
        # 3. Vérifier les participations
        participations = ChallengeParticipation.objects.filter(user=user, status='ACTIVE')
        print(f"OK Participations actives: {participations.count()}")
        for participation in participations:
            print(f"  - {participation.challenge.title}")
        
        # 4. Vérifier le compte d'épargne
        accounts = SavingsAccount.objects.filter(user=user, status='ACTIVE')
        print(f"OK Comptes d'épargne: {accounts.count()}")
        for account in accounts:
            print(f"  - {account.account_number}: {account.balance} FCFA")
        
        # 5. Simuler la création d'un dépôt
        print("\n=== SIMULATION DEPOT ===")
        
        # Récupérer ou créer une participation
        participation = participations.first()
        if not participation and challenges.exists():
            default_challenge = challenges.first()
            participation = ChallengeParticipation.objects.create(
                user=user,
                challenge=default_challenge,
                personal_target=default_challenge.target_amount,
                status='ACTIVE'
            )
            print(f"OK Participation créée: {participation.challenge.title}")
        
        if participation:
            # Créer un dépôt de test
            montant = Decimal('25000')
            deposit = SavingsDeposit.objects.create(
                participation=participation,
                amount=montant,
                deposit_method='BANK_TRANSFER',
                bank_name='ADEC',
                status='CONFIRMED',
                transaction_reference=f'DEP{uuid.uuid4().hex[:20]}',
                processed_at=timezone.now()
            )
            print(f"OK Dépôt créé: {deposit.transaction_reference}")
            
            # Mettre à jour la participation
            participation.total_saved += montant
            participation.deposits_count += 1
            participation.points_earned += int(montant / 1000)
            participation.save()
            print(f"OK Participation mise à jour: {participation.total_saved} FCFA")
            
            # Mettre à jour le compte
            account = accounts.first()
            if account:
                account.balance += montant
                account.save()
                print(f"OK Compte mis à jour: {account.balance} FCFA")
            
        else:
            print("ERREUR Aucune participation disponible")
            
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_deposit()

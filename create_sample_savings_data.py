#!/usr/bin/env python
"""
Script pour créer des données d'exemple pour tester le dashboard dynamique
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import (
    SavingsChallenge, ChallengeParticipation, SavingsDeposit, 
    SavingsGoal, SavingsAccount
)

def create_sample_data():
    """Créer des données d'exemple pour test@xamila.com"""
    
    print("=== CRÉATION DES DONNÉES D'EXEMPLE ===")
    
    # Récupérer l'utilisateur test
    try:
        user = User.objects.get(email="test@xamila.com")
        print(f"OK Utilisateur trouve: {user.email}")
    except User.DoesNotExist:
        print("ERROR Utilisateur test@xamila.com non trouve")
        return
    
    # 1. Créer des défis d'épargne
    print("\n1. Création des défis d'épargne...")
    
    challenge1 = SavingsChallenge.objects.create(
        title="Challenge Vacances Maldives 2025",
        description="Économiser pour des vacances de rêve aux Maldives",
        short_description="Objectif vacances aux Maldives",
        challenge_type="YEARLY",
        category="INTERMEDIATE",
        target_amount=Decimal('2500000'),
        minimum_deposit=Decimal('50000'),
        duration_days=365,
        reward_points=500,
        reward_percentage=Decimal('5.0'),
        max_participants=50,
        is_public=True,
        status="ACTIVE",
        start_date=date(2024, 8, 1),
        end_date=date(2025, 7, 31),
        created_by=user
    )
    print(f"OK Defi cree: {challenge1.title}")
    
    challenge2 = SavingsChallenge.objects.create(
        title="Projet Immobilier",
        description="Apport pour l'achat d'un appartement",
        short_description="Épargne pour achat immobilier",
        challenge_type="YEARLY",
        category="ADVANCED",
        target_amount=Decimal('15000000'),
        minimum_deposit=Decimal('100000'),
        duration_days=730,
        reward_points=1000,
        reward_percentage=Decimal('3.0'),
        max_participants=20,
        is_public=True,
        status="ACTIVE",
        start_date=date(2024, 1, 1),
        end_date=date(2025, 12, 31),
        created_by=user
    )
    print(f"OK Defi cree: {challenge2.title}")
    
    challenge3 = SavingsChallenge.objects.create(
        title="Fonds d'Urgence",
        description="Constitution d'un fonds de sécurité",
        short_description="Fonds d'urgence familial",
        challenge_type="YEARLY",
        category="BEGINNER",
        target_amount=Decimal('3000000'),
        minimum_deposit=Decimal('25000'),
        duration_days=365,
        reward_points=300,
        reward_percentage=Decimal('2.0'),
        max_participants=100,
        is_public=True,
        status="COMPLETED",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        created_by=user
    )
    print(f"OK Defi cree: {challenge3.title}")
    
    # 2. Créer des participations
    print("\n2. Création des participations...")
    
    participation1 = ChallengeParticipation.objects.create(
        user=user,
        challenge=challenge1,
        status="ACTIVE",
        personal_target=Decimal('2500000'),
        total_saved=Decimal('1875000'),
        deposits_count=15,
        current_streak=12,
        longest_streak=15,
        points_earned=375,
        bonus_earned=Decimal('93750'),
        last_deposit_at=date(2025, 8, 20)
    )
    print(f"OK Participation creee: {participation1.challenge.title}")
    
    participation2 = ChallengeParticipation.objects.create(
        user=user,
        challenge=challenge2,
        status="ACTIVE",
        personal_target=Decimal('15000000'),
        total_saved=Decimal('8750000'),
        deposits_count=35,
        current_streak=8,
        longest_streak=20,
        points_earned=875,
        bonus_earned=Decimal('262500'),
        last_deposit_at=date(2025, 8, 18)
    )
    print(f"OK Participation creee: {participation2.challenge.title}")
    
    participation3 = ChallengeParticipation.objects.create(
        user=user,
        challenge=challenge3,
        status="COMPLETED",
        personal_target=Decimal('3000000'),
        total_saved=Decimal('3000000'),
        deposits_count=24,
        current_streak=0,
        longest_streak=24,
        points_earned=300,
        bonus_earned=Decimal('60000'),
        last_deposit_at=date(2024, 12, 15),
        completed_at=date(2024, 12, 31)
    )
    print(f"OK Participation creee: {participation3.challenge.title}")
    
    # 3. Créer des dépôts
    print("\n3. Création des dépôts...")
    
    # Dépôts pour challenge1
    deposits_data = [
        (participation1, Decimal('125000'), 'AUTOMATIC', date(2025, 8, 22)),
        (participation1, Decimal('75000'), 'AUTOMATIC', date(2025, 8, 15)),
        (participation1, Decimal('50000'), 'AUTOMATIC', date(2025, 8, 8)),
        (participation1, Decimal('125000'), 'AUTOMATIC', date(2025, 8, 1)),
        (participation1, Decimal('100000'), 'MOBILE_MONEY', date(2025, 7, 25)),
        
        # Dépôts pour challenge2
        (participation2, Decimal('250000'), 'BANK_TRANSFER', date(2025, 8, 20)),
        (participation2, Decimal('500000'), 'BANK_TRANSFER', date(2025, 8, 10)),
        (participation2, Decimal('300000'), 'BANK_TRANSFER', date(2025, 7, 30)),
        (participation2, Decimal('200000'), 'MOBILE_MONEY', date(2025, 7, 15)),
        
        # Dépôts pour challenge3 (complété)
        (participation3, Decimal('150000'), 'AUTOMATIC', date(2024, 12, 15)),
        (participation3, Decimal('125000'), 'AUTOMATIC', date(2024, 12, 1)),
        (participation3, Decimal('100000'), 'MOBILE_MONEY', date(2024, 11, 15)),
    ]
    
    for participation, amount, method, deposit_date in deposits_data:
        deposit = SavingsDeposit.objects.create(
            participation=participation,
            amount=amount,
            deposit_method=method,
            status="CONFIRMED",
            transaction_reference=f"TXN{deposit_date.strftime('%Y%m%d')}{amount}",
            points_awarded=int(amount / 1000),  # 1 point par 1000 FCFA
            processed_at=deposit_date
        )
        print(f"OK Depot cree: {amount} FCFA - {method}")
    
    # 4. Créer des objectifs d'épargne
    print("\n4. Création des objectifs d'épargne...")
    
    goal1 = SavingsGoal.objects.create(
        user=user,
        title="Voyage en Europe",
        description="Voyage de découverte en Europe",
        goal_type="VACATION",
        target_amount=Decimal('4000000'),
        current_amount=Decimal('1200000'),
        target_date=date(2025, 12, 31),
        status="ACTIVE"
    )
    print(f"OK Objectif cree: {goal1.title}")
    
    goal2 = SavingsGoal.objects.create(
        user=user,
        title="Formation MBA",
        description="Financement formation MBA",
        goal_type="EDUCATION",
        target_amount=Decimal('8000000'),
        current_amount=Decimal('2400000'),
        target_date=date(2026, 9, 1),
        status="ACTIVE"
    )
    print(f"OK Objectif cree: {goal2.title}")
    
    # 5. Créer des comptes d'épargne
    print("\n5. Création des comptes d'épargne...")
    
    account1 = SavingsAccount.objects.create(
        user=user,
        goal=goal1,
        account_number="XAMILA-EP-001",
        account_name="Compte Voyage Europe",
        account_type="GOAL",
        balance=Decimal('1200000'),
        interest_rate=Decimal('3.5'),
        status="ACTIVE"
    )
    print(f"OK Compte cree: {account1.account_name}")
    
    account2 = SavingsAccount.objects.create(
        user=user,
        goal=goal2,
        account_number="XAMILA-EP-002",
        account_name="Compte Formation MBA",
        account_type="GOAL",
        balance=Decimal('2400000'),
        interest_rate=Decimal('4.0'),
        status="ACTIVE"
    )
    print(f"OK Compte cree: {account2.account_name}")
    
    account3 = SavingsAccount.objects.create(
        user=user,
        account_number="XAMILA-EP-003",
        account_name="Compte Épargne Général",
        account_type="BASIC",
        balance=Decimal('850000'),
        interest_rate=Decimal('2.5'),
        status="ACTIVE"
    )
    print(f"OK Compte cree: {account3.account_name}")
    
    print("\n=== RESUME DES DONNEES CREEES ===")
    print(f"Defis d'epargne: {SavingsChallenge.objects.count()}")
    print(f"Participations: {ChallengeParticipation.objects.filter(user=user).count()}")
    print(f"Depots: {SavingsDeposit.objects.filter(participation__user=user).count()}")
    print(f"Objectifs d'epargne: {SavingsGoal.objects.filter(user=user).count()}")
    print(f"Comptes d'epargne: {SavingsAccount.objects.filter(user=user).count()}")
    
    # Calculs de vérification
    import django.db.models
    total_savings = ChallengeParticipation.objects.filter(user=user).aggregate(
        total=django.db.models.Sum('total_saved')
    )['total'] or 0
    
    total_balance = SavingsAccount.objects.filter(user=user, status='ACTIVE').aggregate(
        total=django.db.models.Sum('balance')
    )['total'] or 0
    
    print(f"\n=== STATISTIQUES ===")
    print(f"Total epargne dans les defis: {total_savings:,.0f} FCFA")
    print(f"Total soldes comptes: {total_balance:,.0f} FCFA")
    print(f"Portfolio total: {total_savings + total_balance:,.0f} FCFA")
    
    print("\nOK Donnees d'exemple creees avec succes!")

if __name__ == "__main__":
    create_sample_data()

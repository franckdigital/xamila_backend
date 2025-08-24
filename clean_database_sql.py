#!/usr/bin/env python
"""
Script pour nettoyer la base de données avec SQL direct
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.db import connection
from core.models import User
from core.models_savings_challenge import (
    SavingsChallenge, ChallengeParticipation, SavingsDeposit, 
    SavingsGoal, SavingsAccount
)

def clean_database_sql():
    """Nettoyer la base de données avec SQL direct"""
    
    print("=== NETTOYAGE SQL DIRECT ===")
    
    try:
        with connection.cursor() as cursor:
            # Supprimer toutes les données des tables savings
            print("Suppression des données corrompues...")
            
            cursor.execute("DELETE FROM core_savingsdeposit")
            print(f"  - Dépôts supprimés")
            
            cursor.execute("DELETE FROM core_challengeparticipation")
            print(f"  - Participations supprimées")
            
            cursor.execute("DELETE FROM core_savingsaccount")
            print(f"  - Comptes supprimés")
            
            cursor.execute("DELETE FROM core_savingsgoal")
            print(f"  - Objectifs supprimés")
            
            cursor.execute("DELETE FROM core_savingschallenge")
            print(f"  - Défis supprimés")
            
        # Maintenant recréer avec l'ORM Django
        print("\n=== RECREATION DES DONNEES ===")
        
        # Récupérer l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        print(f"Utilisateur: {user.email}")
        
        # Créer des défis d'épargne
        challenge1 = SavingsChallenge.objects.create(
            title="Défi Épargne 500K",
            description="Économisez 500,000 FCFA en 6 mois",
            short_description="Défi d'épargne de 500K FCFA sur 6 mois",
            target_amount=Decimal('500000'),
            minimum_deposit=Decimal('10000'),
            duration_days=180,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=180)).date(),
            status='ACTIVE',
            challenge_type='MONTHLY',
            category='INTERMEDIATE',
            is_public=True,
            reward_points=500,
            reward_percentage=Decimal('5.0'),
            created_by=user
        )
        print(f"  - Défi créé: {challenge1.title}")
        
        challenge2 = SavingsChallenge.objects.create(
            title="Épargne Mensuelle",
            description="Économisez 50,000 FCFA chaque mois",
            short_description="Défi d'épargne mensuel de 50K FCFA",
            target_amount=Decimal('50000'),
            minimum_deposit=Decimal('5000'),
            duration_days=30,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            status='ACTIVE',
            challenge_type='MONTHLY',
            category='BEGINNER',
            is_public=True,
            reward_points=100,
            reward_percentage=Decimal('2.0'),
            created_by=user
        )
        print(f"  - Défi créé: {challenge2.title}")
        
        # Créer des participations
        participation1 = ChallengeParticipation.objects.create(
            user=user,
            challenge=challenge1,
            personal_target=Decimal('500000'),
            total_saved=Decimal('150000'),
            deposits_count=3,
            status='ACTIVE',
            current_streak=15,
            points_earned=150
        )
        print(f"  - Participation créée: {participation1.challenge.title}")
        
        participation2 = ChallengeParticipation.objects.create(
            user=user,
            challenge=challenge2,
            personal_target=Decimal('50000'),
            total_saved=Decimal('50000'),
            deposits_count=1,
            status='COMPLETED',
            current_streak=30,
            points_earned=100
        )
        print(f"  - Participation créée: {participation2.challenge.title}")
        
        # Créer des dépôts
        deposit1 = SavingsDeposit.objects.create(
            participation=participation1,
            amount=Decimal('50000'),
            deposit_method='BANK_TRANSFER',
            status='CONFIRMED',
            transaction_reference='TXN001',
            points_awarded=50
        )
        print(f"  - Dépôt créé: {deposit1.amount} FCFA")
        
        deposit2 = SavingsDeposit.objects.create(
            participation=participation1,
            amount=Decimal('75000'),
            deposit_method='MOBILE_MONEY',
            status='CONFIRMED',
            transaction_reference='TXN002',
            points_awarded=75
        )
        print(f"  - Dépôt créé: {deposit2.amount} FCFA")
        
        deposit3 = SavingsDeposit.objects.create(
            participation=participation2,
            amount=Decimal('50000'),
            deposit_method='CASH',
            status='CONFIRMED',
            transaction_reference='TXN003',
            points_awarded=50
        )
        print(f"  - Dépôt créé: {deposit3.amount} FCFA")
        
        # Créer des objectifs d'épargne
        goal1 = SavingsGoal.objects.create(
            user=user,
            title="Achat Voiture",
            description="Économiser pour acheter une voiture",
            target_amount=Decimal('2000000'),
            current_amount=Decimal('200000'),
            target_date=(datetime.now() + timedelta(days=365)).date(),
            status='ACTIVE',
            goal_type='PURCHASE'
        )
        print(f"  - Objectif créé: {goal1.title}")
        
        goal2 = SavingsGoal.objects.create(
            user=user,
            title="Fonds d'Urgence",
            description="Constituer un fonds d'urgence",
            target_amount=Decimal('1000000'),
            current_amount=Decimal('300000'),
            target_date=(datetime.now() + timedelta(days=180)).date(),
            status='ACTIVE',
            goal_type='EMERGENCY'
        )
        print(f"  - Objectif créé: {goal2.title}")
        
        # Créer des comptes d'épargne
        account1 = SavingsAccount.objects.create(
            user=user,
            account_name="Compte Principal",
            account_number="ACC001",
            balance=Decimal('500000'),
            account_type='GOAL',
            status='ACTIVE',
            goal=goal1
        )
        print(f"  - Compte créé: {account1.account_name}")
        
        account2 = SavingsAccount.objects.create(
            user=user,
            account_name="Compte Urgence",
            account_number="ACC002",
            balance=Decimal('300000'),
            account_type='GOAL',
            status='ACTIVE',
            goal=goal2
        )
        print(f"  - Compte créé: {account2.account_name}")
        
        print("\n=== DONNEES RECREEES AVEC SUCCES ===")
        print(f"Défis: {SavingsChallenge.objects.count()}")
        print(f"Participations: {ChallengeParticipation.objects.filter(user=user).count()}")
        print(f"Dépôts: {SavingsDeposit.objects.filter(participation__user=user).count()}")
        print(f"Objectifs: {SavingsGoal.objects.filter(user=user).count()}")
        print(f"Comptes: {SavingsAccount.objects.filter(user=user).count()}")
        
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    clean_database_sql()

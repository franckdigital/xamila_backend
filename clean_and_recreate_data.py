#!/usr/bin/env python
"""
Script pour nettoyer les données corrompues et recréer des données de test propres
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from core.models import User
from core.models_savings_challenge import (
    SavingsChallenge, ChallengeParticipation, SavingsDeposit, 
    SavingsGoal, SavingsAccount
)

def clean_and_recreate_data():
    """Nettoyer et recréer des données de test propres"""
    
    print("=== NETTOYAGE ET RECREATION DES DONNEES ===")
    
    try:
        # 1. Récupérer l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        print(f"Utilisateur trouvé: {user.email}")
        
        # 2. Supprimer toutes les données liées à cet utilisateur
        print("\n2. Suppression des données existantes...")
        
        # Supprimer les dépôts
        deposits_deleted = SavingsDeposit.objects.filter(participation__user=user).delete()
        print(f"  - Dépôts supprimés: {deposits_deleted[0]}")
        
        # Supprimer les participations
        participations_deleted = ChallengeParticipation.objects.filter(user=user).delete()
        print(f"  - Participations supprimées: {participations_deleted[0]}")
        
        # Supprimer les comptes d'épargne
        accounts_deleted = SavingsAccount.objects.filter(user=user).delete()
        print(f"  - Comptes supprimés: {accounts_deleted[0]}")
        
        # Supprimer les objectifs
        goals_deleted = SavingsGoal.objects.filter(user=user).delete()
        print(f"  - Objectifs supprimés: {goals_deleted[0]}")
        
        # Supprimer tous les défis (pour éviter les références corrompues)
        challenges_deleted = SavingsChallenge.objects.all().delete()
        print(f"  - Défis supprimés: {challenges_deleted[0]}")
        
        # 3. Recréer des données propres
        print("\n3. Création de nouvelles données...")
        
        # Créer des défis d'épargne
        challenge1 = SavingsChallenge.objects.create(
            title="Défi Épargne 500K",
            description="Économisez 500,000 FCFA en 6 mois",
            target_amount=Decimal('500000'),
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=180)).date(),
            status='ACTIVE',
            challenge_type='PERSONAL',
            category='GENERAL',
            is_public=True
        )
        print(f"  - Défi créé: {challenge1.title}")
        
        challenge2 = SavingsChallenge.objects.create(
            title="Épargne Mensuelle",
            description="Économisez 50,000 FCFA chaque mois",
            target_amount=Decimal('50000'),
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            status='ACTIVE',
            challenge_type='RECURRING',
            category='MONTHLY',
            is_public=True
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
            progress_percentage=30.0,
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
            progress_percentage=100.0,
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
            category='TRANSPORT'
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
            category='EMERGENCY'
        )
        print(f"  - Objectif créé: {goal2.title}")
        
        # Créer des comptes d'épargne
        account1 = SavingsAccount.objects.create(
            user=user,
            account_name="Compte Principal",
            account_number="ACC001",
            balance=Decimal('500000'),
            account_type='SAVINGS',
            status='ACTIVE',
            goal=goal1
        )
        print(f"  - Compte créé: {account1.account_name}")
        
        account2 = SavingsAccount.objects.create(
            user=user,
            account_name="Compte Urgence",
            account_number="ACC002",
            balance=Decimal('300000'),
            account_type='EMERGENCY',
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
    clean_and_recreate_data()

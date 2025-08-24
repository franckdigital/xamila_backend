"""
Commande Django pour créer un Challenge Semestriel (6 mois)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from core.models_savings_challenge import SavingsChallenge

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée un Challenge Semestriel (6 mois) avec des paramètres prédéfinis'

    def handle(self, *args, **options):
        # Récupérer un admin pour créer le challenge
        admin_user = User.objects.filter(role='ADMIN').first()
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            self.stdout.write(
                self.style.ERROR('Aucun utilisateur admin trouvé. Créez d\'abord un superuser.')
            )
            return

        # Créer le Challenge Semestriel
        challenge = SavingsChallenge.objects.create(
            title="Challenge Semestriel - 6 Mois d'Épargne",
            description="""
            Relevez le défi de l'épargne sur 6 mois ! 
            
            Objectif : Économiser 100 000 FCFA en 6 mois
            - Dépôt minimum : 5 000 FCFA par mois
            - Bonus de récompense : 5% du montant total épargné
            - Points de fidélité : 1000 points
            - Certificat d'accomplissement
            
            Idéal pour :
            - Constituer un fonds d'urgence
            - Préparer un projet à moyen terme
            - Développer une habitude d'épargne régulière
            
            Rejoignez des milliers d'épargnants et atteignez vos objectifs financiers !
            """,
            short_description="Épargnez 100 000 FCFA en 6 mois avec un bonus de 5% et des récompenses exclusives",
            challenge_type='SEMIANNUAL',
            category='INTERMEDIATE',
            target_amount=Decimal('100000.00'),
            minimum_deposit=Decimal('5000.00'),
            duration_days=180,  # 6 mois = 180 jours
            reward_points=1000,
            reward_percentage=Decimal('5.00'),
            max_participants=500,
            is_public=True,
            status='ACTIVE',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            created_by=admin_user
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Challenge Semestriel créé avec succès !\n'
                f'ID: {challenge.id}\n'
                f'Titre: {challenge.title}\n'
                f'Objectif: {challenge.target_amount} FCFA\n'
                f'Durée: {challenge.duration_days} jours\n'
                f'Date de fin: {challenge.end_date}'
            )
        )

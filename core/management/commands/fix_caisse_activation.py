from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from core.models_savings_challenge import SavingsGoal

class Command(BaseCommand):
    help = 'Corrige les dates d\'activation de Ma Caisse pour les objectifs existants'

    def handle(self, *args, **options):
        self.stdout.write("Correction de l'activation Ma Caisse...")
        
        # Récupérer tous les objectifs sans date d'activation
        objectifs_sans_date = SavingsGoal.objects.filter(date_activation_caisse__isnull=True)
        
        self.stdout.write(f"Objectifs trouvés sans date d'activation: {objectifs_sans_date.count()}")
        
        updated_count = 0
        
        for objectif in objectifs_sans_date:
            # Calculer la date d'activation basée sur la date de création + 21 jours
            creation_date = objectif.created_at.date()
            activation_date = creation_date + timedelta(days=21)
            
            # Mettre à jour l'objectif
            objectif.date_activation_caisse = activation_date
            objectif.save()
            
            updated_count += 1
            
            self.stdout.write(f"Objectif '{objectif.title}' - Activation: {activation_date} (Créé: {creation_date})")
        
        # Vérifier les objectifs avec activation immédiate (créés aujourd'hui)
        today = date.today()
        objectifs_immediats = SavingsGoal.objects.filter(
            created_at__date=today,
            date_activation_caisse__lte=today
        )
        
        if objectifs_immediats.exists():
            self.stdout.write(f"\nObjectifs avec activation immédiate détectés: {objectifs_immediats.count()}")
            
            for objectif in objectifs_immediats:
                # Recalculer la date d'activation
                new_activation_date = today + timedelta(days=21)
                objectif.date_activation_caisse = new_activation_date
                objectif.save()
                
                self.stdout.write(f"Corrigé: '{objectif.title}' - Nouvelle activation: {new_activation_date}")
        
        self.stdout.write(f"\nCorrection terminée. {updated_count} objectifs mis à jour.")
        
        # Afficher un résumé
        self.stdout.write("\nRésumé des objectifs:")
        all_objectifs = SavingsGoal.objects.all().order_by('created_at')
        
        for objectif in all_objectifs:
            is_activated = objectif.is_caisse_activated
            status = "ACTIVE" if is_activated else "PENDING"
            days_remaining = (objectif.date_activation_caisse - today).days if objectif.date_activation_caisse and not is_activated else 0
            
            self.stdout.write(f"{status} {objectif.title} - Activation: {objectif.date_activation_caisse} - "
                            f"{'Activé' if is_activated else f'Dans {days_remaining} jours'}")
        
        self.stdout.write(self.style.SUCCESS('Correction terminée avec succès!'))

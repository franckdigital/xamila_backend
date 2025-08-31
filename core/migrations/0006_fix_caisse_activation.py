# Generated migration to fix Ma Caisse activation dates

from django.db import migrations
from datetime import date, timedelta

def fix_caisse_activation_dates(apps, schema_editor):
    """
    Met à jour tous les objectifs d'épargne existants pour avoir la bonne date d'activation
    """
    SavingsGoal = apps.get_model('core', 'SavingsGoal')
    
    # Récupérer tous les objectifs sans date d'activation
    objectifs_sans_date = SavingsGoal.objects.filter(date_activation_caisse__isnull=True)
    
    for objectif in objectifs_sans_date:
        # Calculer la date d'activation basée sur la date de création + 21 jours
        creation_date = objectif.created_at.date()
        activation_date = creation_date + timedelta(days=21)
        
        # Mettre à jour l'objectif
        objectif.date_activation_caisse = activation_date
        objectif.save()
    
    # Vérifier les objectifs avec activation immédiate (créés aujourd'hui)
    today = date.today()
    objectifs_immediats = SavingsGoal.objects.filter(
        created_at__date=today,
        date_activation_caisse__lte=today
    )
    
    for objectif in objectifs_immediats:
        # Recalculer la date d'activation
        new_activation_date = today + timedelta(days=21)
        objectif.date_activation_caisse = new_activation_date
        objectif.save()

def reverse_fix_caisse_activation_dates(apps, schema_editor):
    """
    Fonction de rollback - ne fait rien car on ne peut pas revenir en arrière
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_add_and_fix_caisse_activation'),
    ]

    operations = [
        migrations.RunPython(
            fix_caisse_activation_dates,
            reverse_fix_caisse_activation_dates,
        ),
    ]

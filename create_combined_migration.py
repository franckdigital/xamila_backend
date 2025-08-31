#!/usr/bin/env python
"""
Script pour créer une migration combinée qui ajoute le champ date_activation_caisse
et corrige les données existantes en une seule migration
"""

migration_content = '''# Generated migration to add date_activation_caisse field and fix activation dates

from django.db import migrations, models
from datetime import date, timedelta

def add_activation_dates_and_fix_data(apps, schema_editor):
    """
    Ajoute les dates d'activation pour tous les objectifs existants
    """
    SavingsGoal = apps.get_model('core', 'SavingsGoal')
    
    # Récupérer tous les objectifs
    for objectif in SavingsGoal.objects.all():
        # Calculer la date d'activation basée sur la date de création + 21 jours
        creation_date = objectif.created_at.date()
        activation_date = creation_date + timedelta(days=21)
        
        # Mettre à jour l'objectif
        objectif.date_activation_caisse = activation_date
        objectif.save()

def reverse_add_activation_dates(apps, schema_editor):
    """
    Fonction de rollback - supprime les dates d'activation
    """
    SavingsGoal = apps.get_model('core', 'SavingsGoal')
    SavingsGoal.objects.update(date_activation_caisse=None)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_user_country_of_origin_and_more'),
    ]

    operations = [
        # Ajouter le champ date_activation_caisse
        migrations.AddField(
            model_name='savingsgoal',
            name='date_activation_caisse',
            field=models.DateField(blank=True, help_text="Date à partir de laquelle Ma Caisse devient accessible (21 jours après création)", null=True, verbose_name="Date d'activation Ma Caisse"),
        ),
        # Remplir les données pour les objectifs existants
        migrations.RunPython(
            add_activation_dates_and_fix_data,
            reverse_add_activation_dates,
        ),
    ]
'''

# Écrire le fichier de migration
with open('/tmp/0005_add_and_fix_caisse_activation.py', 'w', encoding='utf-8') as f:
    f.write(migration_content)

print("Migration combinée créée dans /tmp/0005_add_and_fix_caisse_activation.py")
print("Copiez ce fichier vers core/migrations/ sur le serveur de production")

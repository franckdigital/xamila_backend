# Generated migration for payment and certificate fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_fix_caisse_activation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='paye',
            field=models.BooleanField(default=False, help_text="Détermine si l'utilisateur a accès à toutes les fonctionnalités du challenge épargne", verbose_name='Utilisateur payant'),
        ),
        migrations.AddField(
            model_name='user',
            name='certif_reussite',
            field=models.BooleanField(default=False, help_text="Permet aux utilisateurs non-payants d'accéder au certificat de réussite", verbose_name='Certificat de réussite activé'),
        ),
    ]

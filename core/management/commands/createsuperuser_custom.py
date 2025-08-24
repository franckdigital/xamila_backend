from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Créer un superutilisateur pour XAMILA'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            help='Email du superutilisateur',
        )
        parser.add_argument(
            '--first_name',
            help='Prénom du superutilisateur',
        )
        parser.add_argument(
            '--last_name',
            help='Nom du superutilisateur',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')

        # Demander l'email si pas fourni
        if not email:
            email = input('Email: ')

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'Un utilisateur avec l\'email {email} existe déjà.')
            )
            return

        # Demander le prénom si pas fourni
        if not first_name:
            first_name = input('Prénom: ')

        # Demander le nom si pas fourni
        if not last_name:
            last_name = input('Nom: ')

        # Demander le mot de passe
        password = None
        while not password:
            password = getpass.getpass('Mot de passe: ')
            password2 = getpass.getpass('Confirmer le mot de passe: ')
            
            if password != password2:
                self.stdout.write(self.style.ERROR('Les mots de passe ne correspondent pas.'))
                password = None
                continue
                
            if len(password) < 8:
                self.stdout.write(self.style.ERROR('Le mot de passe doit contenir au moins 8 caractères.'))
                password = None
                continue

        try:
            # Utiliser create_superuser qui gère automatiquement le username
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email_verified=True
            )

            self.stdout.write(
                self.style.SUCCESS(f'Superutilisateur créé avec succès: {email}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'Vous pouvez maintenant vous connecter à http://localhost:8000/admin/')
            )

        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur de validation: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la création: {e}')
            )

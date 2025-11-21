# Migration - Ajout des champs PDF

## Commande à exécuter

```bash
cd xamila_backend
python manage.py makemigrations core
python manage.py migrate core
```

## Champs ajoutés au modèle AccountOpeningRequest

```python
# PDF générés
contract_pdf = models.FileField(
    upload_to="contracts/main/",
    blank=True,
    null=True,
    help_text="Contrat principal (statique)"
)
annexes_pdf = models.FileField(
    upload_to="contracts/annexes/",
    blank=True,
    null=True,
    help_text="Annexes avec données dynamiques"
)
```

## Configuration settings.py

Ajouter dans `settings.py`:

```python
# Email configuration
XAMILA_TEAM_EMAIL = 'team@xamila.com'  # Email de l'équipe Xamila
DEFAULT_FROM_EMAIL = 'noreply@xamila.com'  # Email d'envoi

# Media files (pour les PDF)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## Dossiers à créer

```bash
mkdir -p media/contracts/main
mkdir -p media/contracts/annexes
```

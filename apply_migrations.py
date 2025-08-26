#!/usr/bin/env python
"""
Script pour appliquer les migrations Django
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

def apply_migrations():
    """Applique toutes les migrations"""
    print("=== Application des migrations ===")
    
    try:
        # Appliquer les migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✓ Migrations appliquées avec succès")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'application des migrations: {e}")
        return False

if __name__ == '__main__':
    apply_migrations()

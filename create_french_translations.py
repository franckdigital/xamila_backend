#!/usr/bin/env python3
"""
Script pour créer les traductions françaises Django sur le serveur de production
"""

import os
import sys
import django
import subprocess

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
sys.path.append('/var/www/xamila/xamila_backend')
django.setup()

def create_translations():
    """Créer les fichiers de traduction française"""
    
    print("🚀 Création des traductions françaises Django")
    print("="*50)
    
    try:
        # Créer le répertoire locale s'il n'existe pas
        locale_dir = '/var/www/xamila/xamila_backend/locale'
        if not os.path.exists(locale_dir):
            os.makedirs(locale_dir)
            print(f"✅ Répertoire locale créé: {locale_dir}")
        
        # Générer les messages pour le français
        print("📝 Génération des messages français...")
        result = subprocess.run([
            'python', 'manage.py', 'makemessages', '-l', 'fr'
        ], cwd='/var/www/xamila/xamila_backend', capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Messages français générés avec succès")
            print(result.stdout)
        else:
            print("❌ Erreur lors de la génération des messages:")
            print(result.stderr)
            return False
        
        # Compiler les messages
        print("🔨 Compilation des messages...")
        result = subprocess.run([
            'python', 'manage.py', 'compilemessages'
        ], cwd='/var/www/xamila/xamila_backend', capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Messages compilés avec succès")
            print(result.stdout)
        else:
            print("❌ Erreur lors de la compilation:")
            print(result.stderr)
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_french_messages():
    """Tester les messages français"""
    
    print("\n" + "="*50)
    print("🧪 Test des messages français")
    
    from django.utils.translation import gettext as _
    from django.utils.translation import activate
    
    # Activer le français
    activate('fr')
    
    # Tester quelques messages
    test_messages = [
        'Cette adresse email est déjà utilisée.',
        'Ce nom d\'utilisateur est déjà utilisé.',
        'username',
        'Email address'
    ]
    
    for msg in test_messages:
        translated = _(msg)
        print(f"'{msg}' → '{translated}'")

if __name__ == "__main__":
    success = create_translations()
    
    if success:
        test_french_messages()
        print("\n" + "="*50)
        print("✅ Traductions françaises configurées avec succès!")
        print("Redémarrez le serveur Django pour appliquer les changements.")
    else:
        print("\n" + "="*50)
        print("❌ Échec de la configuration des traductions")
    
    print("Script terminé")

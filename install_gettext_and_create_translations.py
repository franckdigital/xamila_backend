#!/usr/bin/env python3
"""
Script pour installer gettext et créer les traductions françaises Django
"""

import os
import sys
import django
import subprocess

def install_gettext():
    """Installer GNU gettext tools"""
    
    print("🔧 Installation des outils GNU gettext")
    print("="*50)
    
    try:
        # Mettre à jour les paquets
        print("📦 Mise à jour des paquets...")
        result = subprocess.run(['apt', 'update'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ Avertissement lors de la mise à jour:", result.stderr)
        
        # Installer gettext
        print("📥 Installation de gettext...")
        result = subprocess.run(['apt', 'install', '-y', 'gettext'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ gettext installé avec succès")
        else:
            print("❌ Erreur lors de l'installation de gettext:")
            print(result.stderr)
            return False
        
        # Vérifier l'installation
        result = subprocess.run(['which', 'msguniq'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ msguniq trouvé: {result.stdout.strip()}")
            return True
        else:
            print("❌ msguniq non trouvé après installation")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_translations():
    """Créer les fichiers de traduction française"""
    
    print("\n🚀 Création des traductions françaises Django")
    print("="*50)
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
    sys.path.append('/var/www/xamila/xamila_backend')
    
    try:
        django.setup()
    except Exception as e:
        print(f"❌ Erreur Django setup: {e}")
        return False
    
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
            if result.stdout:
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
            if result.stdout:
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
    
    try:
        from django.utils.translation import gettext as _
        from django.utils.translation import activate
        
        # Activer le français
        activate('fr')
        
        # Tester quelques messages
        test_messages = [
            'Cette adresse email est déjà utilisée.',
            'Ce nom d\'utilisateur est déjà utilisé.',
        ]
        
        for msg in test_messages:
            translated = _(msg)
            print(f"'{msg}' → '{translated}'")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    # Installer gettext
    gettext_success = install_gettext()
    
    if not gettext_success:
        print("\n❌ Installation de gettext échouée. Arrêt du script.")
        sys.exit(1)
    
    # Créer les traductions
    translation_success = create_translations()
    
    if translation_success:
        test_french_messages()
        print("\n" + "="*50)
        print("✅ Traductions françaises configurées avec succès!")
        print("Redémarrez le serveur Django pour appliquer les changements:")
        print("sudo systemctl restart xamila-backend")
    else:
        print("\n" + "="*50)
        print("❌ Échec de la configuration des traductions")
    
    print("Script terminé")

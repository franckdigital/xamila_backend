#!/usr/bin/env python3
"""
Script pour corriger toutes les erreurs d'encodage dans services_email.py
"""

import os
import re

def fix_all_encoding_errors():
    file_path = '/var/www/xamila/xamila_backend/core/services_email.py'
    backup_path = file_path + '.backup2'
    
    print(f"Lecture de {file_path}...")
    
    try:
        # Lire le fichier avec différents encodages
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"✓ Fichier lu avec l'encodage {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("✗ Impossible de lire le fichier")
            return False
        
        # Créer une sauvegarde
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Sauvegarde créée: {backup_path}")
        
        # Corrections multiples
        corrections = [
            # Ligne 385 - Docstring admin
            ('        ""Envoie l\'email à un administrateur""', 
             '        """Envoie l\'email a un administrateur"""'),
            
            # Ligne 392 - HTML avec guillemets
            ('<h2 style="color: #d32f2f;">?? Nouvelle demande d\'ouverture de compte (ADMIN)</h2>',
             '<h2 style="color: #d32f2f;">🔐 Nouvelle demande d\'ouverture de compte (ADMIN)</h2>'),
            
            # Remplacer tous les caractères problématiques
            ('??', '🔐'),
            ('�', 'a'),
        ]
        
        original_content = content
        for old, new in corrections:
            if old in content:
                content = content.replace(old, new)
                print(f"✓ Corrigé: {repr(old[:50])} -> {repr(new[:50])}")
        
        if content == original_content:
            print("⚠ Aucune correction appliquée - le fichier semble déjà correct")
        
        # Écrire le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fichier corrigé et sauvegardé")
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  Correction complète de services_email.py")
    print("=" * 60)
    print()
    
    if fix_all_encoding_errors():
        print()
        print("✓ Toutes les corrections appliquées")
        print()
        print("Vérification du code Django...")
        result = os.system('cd /var/www/xamila/xamila_backend && python3 manage.py check 2>&1 | head -20')
        
        if result == 0:
            print()
            print("✓ Code Django valide")
            print()
            print("Redémarrage du service...")
            os.system('sudo systemctl restart xamila')
            print()
            print("Attente de 3 secondes...")
            import time
            time.sleep(3)
            print()
            print("Test du endpoint /health/...")
            os.system('curl -s http://localhost:8000/health/ | python3 -m json.tool')
        else:
            print()
            print("⚠ Il reste des erreurs dans le code")
            print("Voir les détails ci-dessus")
    else:
        print()
        print("✗ Échec de la correction")

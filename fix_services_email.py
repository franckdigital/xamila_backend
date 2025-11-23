#!/usr/bin/env python3
"""
Script pour corriger l'erreur d'encodage dans services_email.py ligne 385
"""

import os
import sys

def fix_encoding_error():
    file_path = '/var/www/xamila/xamila_backend/core/services_email.py'
    backup_path = file_path + '.backup'
    
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
        
        # Corriger la ligne problématique
        lines = content.split('\n')
        
        # Trouver et corriger la ligne 385 (index 384)
        if len(lines) > 384:
            old_line = lines[384]
            print(f"Ligne 385 actuelle: {repr(old_line)}")
            
            # Remplacer par la version correcte
            lines[384] = '        """Envoie l\'email a un administrateur"""'
            print(f"Ligne 385 corrigée: {repr(lines[384])}")
        
        # Écrire le fichier corrigé
        corrected_content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(corrected_content)
        
        print(f"✓ Fichier corrigé et sauvegardé")
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("  Correction de l'erreur d'encodage dans services_email.py")
    print("=" * 60)
    print()
    
    if fix_encoding_error():
        print()
        print("✓ Correction réussie")
        print()
        print("Vérification du code Django...")
        os.system('cd /var/www/xamila/xamila_backend && python3 manage.py check')
        print()
        print("Pour redémarrer le service:")
        print("  sudo systemctl restart xamila")
        sys.exit(0)
    else:
        print()
        print("✗ Échec de la correction")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script pour corriger les imports et redémarrer le serveur Django
"""

import subprocess
import sys
import os
import time

def run_command(command, description, cwd=None):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*50}")
    print(f"ÉTAPE: {description}")
    print(f"COMMANDE: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd,
            timeout=300
        )
        
        if result.stdout:
            print("SORTIE:")
            print(result.stdout)
        
        if result.stderr:
            print("ERREURS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCÈS")
            return True
        else:
            print(f"❌ {description} - ÉCHEC (code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERREUR: {str(e)}")
        return False

def main():
    """Fonction principale de correction et redémarrage"""
    print("🔧 CORRECTION DES IMPORTS ET REDÉMARRAGE DJANGO")
    print("=" * 60)
    
    # Configuration
    backend_dir = "/var/www/xamila/xamila_backend"
    
    steps = [
        {
            "command": "cd /var/www/xamila/xamila_backend && git pull origin master",
            "description": "Récupération des dernières modifications",
            "cwd": None
        },
        {
            "command": "cd /var/www/xamila/xamila_backend && python manage.py check",
            "description": "Vérification de la configuration Django",
            "cwd": None
        },
        {
            "command": "cd /var/www/xamila/xamila_backend && python manage.py collectstatic --noinput",
            "description": "Collecte des fichiers statiques",
            "cwd": None
        },
        {
            "command": "sudo systemctl restart xamila-backend",
            "description": "Redémarrage du service Django",
            "cwd": None
        },
        {
            "command": "sudo systemctl status xamila-backend --no-pager",
            "description": "Vérification du statut du service",
            "cwd": None
        },
        {
            "command": "curl -s -o /dev/null -w '%{http_code}' https://api.xamila.finance/api/auth/login/",
            "description": "Test de connectivité API",
            "cwd": None
        }
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for i, step in enumerate(steps, 1):
        print(f"\n📋 ÉTAPE {i}/{total_steps}")
        success = run_command(
            step["command"], 
            step["description"], 
            step.get("cwd")
        )
        
        if success:
            success_count += 1
        else:
            print(f"\n⚠️  ÉCHEC À L'ÉTAPE {i}: {step['description']}")
            
            # Pour certaines étapes, on peut continuer
            if "collectstatic" in step["command"] or "curl" in step["command"]:
                print("⏭️  Continuation malgré l'échec (étape non critique)")
                continue
            elif "python manage.py check" in step["command"]:
                print("🛑 Arrêt - Configuration Django invalide")
                break
            else:
                print("🛑 Arrêt du processus en raison de l'échec")
                break
        
        # Pause entre les étapes
        if i < total_steps:
            time.sleep(2)
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DE LA CORRECTION")
    print(f"{'='*60}")
    print(f"Étapes réussies: {success_count}/{total_steps}")
    
    if success_count >= total_steps - 1:  # Tolérer 1 échec
        print("🎉 CORRECTION RÉUSSIE!")
        print("\n📋 ENDPOINTS COHORT ACCESS DÉPLOYÉS:")
        print("- GET /api/user/cohort-access/ - Vérification accès cohorte")
        print("- POST /api/user/join-cohort/ - Adhésion via code cohorte")
        print("- GET /api/user/cohorts/ - Liste des cohortes utilisateur")
        
        print("\n🧪 TESTS RECOMMANDÉS:")
        print("1. Tester l'authentification API")
        print("2. Tester les endpoints de cohort access")
        print("3. Vérifier le fonctionnement du frontend")
        
    else:
        print("❌ CORRECTION ÉCHOUÉE")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez si nécessaire")
    
    return success_count >= total_steps - 1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

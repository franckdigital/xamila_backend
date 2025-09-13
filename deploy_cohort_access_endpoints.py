#!/usr/bin/env python3
"""
Script de déploiement des endpoints d'accès aux cohortes
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
    """Fonction principale de déploiement"""
    print("🚀 DÉPLOIEMENT DES ENDPOINTS D'ACCÈS AUX COHORTES")
    print("=" * 60)
    
    # Configuration
    backend_dir = "/var/www/xamila/xamila_backend"
    
    steps = [
        {
            "command": "cd /var/www/xamila/xamila_backend && git status",
            "description": "Vérification du statut Git",
            "cwd": None
        },
        {
            "command": "cd /var/www/xamila/xamila_backend && git pull origin master",
            "description": "Récupération des dernières modifications",
            "cwd": None
        },
        {
            "command": "cd /var/www/xamila/xamila_backend && python manage.py collectstatic --noinput",
            "description": "Collecte des fichiers statiques",
            "cwd": None
        },
        {
            "command": "cd /var/www/xamila/xamila_backend && python manage.py migrate",
            "description": "Application des migrations",
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
            
            # Pour certaines étapes critiques, on peut continuer
            if "collectstatic" in step["command"] or "migrate" in step["command"]:
                print("⏭️  Continuation malgré l'échec (étape non critique)")
                continue
            else:
                print("🛑 Arrêt du déploiement en raison de l'échec")
                break
        
        # Pause entre les étapes
        if i < total_steps:
            time.sleep(2)
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DU DÉPLOIEMENT")
    print(f"{'='*60}")
    print(f"Étapes réussies: {success_count}/{total_steps}")
    
    if success_count == total_steps:
        print("🎉 DÉPLOIEMENT RÉUSSI!")
        print("\n📋 ENDPOINTS DÉPLOYÉS:")
        print("- GET /api/user/cohort-access/ - Vérification accès cohorte")
        print("- POST /api/user/join-cohort/ - Adhésion via code cohorte")
        print("- GET /api/user/cohorts/ - Liste des cohortes utilisateur")
        
        print("\n🧪 TESTS RECOMMANDÉS:")
        print("1. Tester la vérification d'accès cohorte")
        print("2. Tester l'adhésion avec un code cohorte valide")
        print("3. Tester l'adhésion avec un code cohorte invalide")
        print("4. Vérifier la récupération des cohortes utilisateur")
        
    else:
        print("❌ DÉPLOIEMENT PARTIELLEMENT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus et relancez si nécessaire")
    
    return success_count == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script de déploiement des corrections de formatage des montants
Déploie les modifications backend sur le serveur de production
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, cwd=None):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info(f"✅ Commande réussie: {command}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur commande: {command}")
        logger.error(f"Error: {e.stderr}")
        return None

def deploy_backend_fixes():
    """Déploie les corrections backend sur le serveur de production"""
    
    logger.info("🚀 Début du déploiement des corrections de formatage des montants")
    
    # Chemin vers le backend
    backend_path = Path(__file__).parent / "xamila_backend"
    
    if not backend_path.exists():
        logger.error(f"❌ Répertoire backend non trouvé: {backend_path}")
        return False
    
    logger.info(f"📁 Répertoire backend: {backend_path}")
    
    # 1. Collecter les fichiers statiques
    logger.info("📦 Collection des fichiers statiques...")
    if not run_command("python manage.py collectstatic --noinput", cwd=backend_path):
        logger.error("❌ Échec de la collection des fichiers statiques")
        return False
    
    # 2. Vérifier la syntaxe Python
    logger.info("🔍 Vérification de la syntaxe des fichiers modifiés...")
    files_to_check = [
        "core/views_savings.py",
        "core/views_dashboard.py"
    ]
    
    for file_path in files_to_check:
        full_path = backend_path / file_path
        if full_path.exists():
            if not run_command(f"python -m py_compile {file_path}", cwd=backend_path):
                logger.error(f"❌ Erreur de syntaxe dans {file_path}")
                return False
            logger.info(f"✅ Syntaxe OK: {file_path}")
        else:
            logger.warning(f"⚠️  Fichier non trouvé: {file_path}")
    
    # 3. Créer un script de redémarrage
    restart_script = """#!/bin/bash
echo "Redemarrage du service Xamila..."

# Arreter le service
sudo systemctl stop xamila
echo "Service arrete"

# Attendre un moment
sleep 2

# Redemarrer le service
sudo systemctl start xamila
echo "Service redemarre"

# Verifier le statut
sudo systemctl status xamila --no-pager -l
echo "Verification du statut terminee"

# Verifier que le port 8000 est en ecoute
sleep 5
if netstat -tuln | grep :8000; then
    echo "Port 8000 en ecoute - Service operationnel"
else
    echo "Port 8000 non accessible - Probleme de demarrage"
fi
"""
    
    script_path = backend_path / "restart_service.sh"
    with open(script_path, 'w') as f:
        f.write(restart_script)
    
    # Rendre le script exécutable
    os.chmod(script_path, 0o755)
    logger.info(f"📝 Script de redémarrage créé: {script_path}")
    
    # 4. Afficher les instructions de déploiement
    logger.info("\n" + "="*60)
    logger.info("📋 INSTRUCTIONS DE DÉPLOIEMENT MANUEL")
    logger.info("="*60)
    logger.info("1. Connectez-vous au serveur de production")
    logger.info("2. Naviguez vers le répertoire du projet")
    logger.info("3. Exécutez les commandes suivantes:")
    logger.info("")
    logger.info("   # Sauvegarder les fichiers modifiés")
    logger.info("   git add core/views_savings.py core/views_dashboard.py")
    logger.info("   git commit -m 'Fix: Remplacer slash par points dans formatage montants'")
    logger.info("   git push")
    logger.info("")
    logger.info("   # Sur le serveur de production:")
    logger.info("   git pull")
    logger.info("   python manage.py collectstatic --noinput")
    logger.info("   ./restart_service.sh")
    logger.info("")
    logger.info("4. Vérifiez que le service fonctionne:")
    logger.info("   curl -k https://api.xamila.finance/health/")
    logger.info("")
    logger.info("5. Testez le PDF Ma Caisse pour vérifier le formatage")
    logger.info("="*60)
    
    return True

def main():
    """Fonction principale"""
    logger.info("🎯 Script de déploiement des corrections de formatage")
    
    if deploy_backend_fixes():
        logger.info("✅ Déploiement préparé avec succès")
        logger.info("📤 Prêt pour le déploiement sur le serveur de production")
        return 0
    else:
        logger.error("❌ Échec de la préparation du déploiement")
        return 1

if __name__ == "__main__":
    sys.exit(main())

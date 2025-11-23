#!/bin/bash

# Script de déploiement et correction erreur 502
# Usage: ./deploy_fix_502.sh

set -e  # Arrêter en cas d'erreur

echo "=========================================="
echo "  Déploiement Xamila Backend - Fix 502"
echo "=========================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/var/www/xamila/xamila_backend"
SERVICE_NAME="xamila"

echo -e "${YELLOW}1. Navigation vers le projet...${NC}"
cd $PROJECT_DIR
echo -e "${GREEN}✓ Dans $PROJECT_DIR${NC}"
echo ""

echo -e "${YELLOW}2. Récupération des dernières modifications...${NC}"
git fetch origin
git pull origin master
echo -e "${GREEN}✓ Code mis à jour${NC}"
echo ""

echo -e "${YELLOW}3. Nettoyage des fichiers Python compilés...${NC}"
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}✓ Fichiers compilés supprimés${NC}"
echo ""

echo -e "${YELLOW}4. Vérification du code Django...${NC}"
python3 manage.py check
echo -e "${GREEN}✓ Code Django valide${NC}"
echo ""

echo -e "${YELLOW}5. Application des migrations...${NC}"
python3 manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations appliquées${NC}"
echo ""

echo -e "${YELLOW}6. Collecte des fichiers statiques...${NC}"
python3 manage.py collectstatic --noinput
echo -e "${GREEN}✓ Fichiers statiques collectés${NC}"
echo ""

echo -e "${YELLOW}7. Vérification des permissions...${NC}"
chown -R www-data:www-data .
chmod -R 755 .
chown -R www-data:www-data media/ 2>/dev/null || true
chmod -R 775 media/ 2>/dev/null || true
echo -e "${GREEN}✓ Permissions corrigées${NC}"
echo ""

echo -e "${YELLOW}8. Redémarrage du service $SERVICE_NAME...${NC}"
systemctl restart $SERVICE_NAME
sleep 3
echo -e "${GREEN}✓ Service redémarré${NC}"
echo ""

echo -e "${YELLOW}9. Vérification du statut du service...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✓ Service $SERVICE_NAME est actif${NC}"
else
    echo -e "${RED}✗ Service $SERVICE_NAME n'est pas actif !${NC}"
    echo ""
    echo "Logs d'erreur :"
    journalctl -u $SERVICE_NAME -n 50 --no-pager
    exit 1
fi
echo ""

echo -e "${YELLOW}10. Test du endpoint /health/...${NC}"
sleep 2
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health/ || echo "ERROR")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✓ Backend répond correctement${NC}"
    echo "Réponse: $HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Backend ne répond pas correctement${NC}"
    echo "Réponse: $HEALTH_RESPONSE"
    echo ""
    echo "Logs récents :"
    journalctl -u $SERVICE_NAME -n 30 --no-pager
    exit 1
fi
echo ""

echo -e "${YELLOW}11. Vérification des processus Gunicorn...${NC}"
GUNICORN_COUNT=$(ps aux | grep gunicorn | grep -v grep | wc -l)
if [ $GUNICORN_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ $GUNICORN_COUNT processus Gunicorn en cours d'exécution${NC}"
else
    echo -e "${RED}✗ Aucun processus Gunicorn trouvé${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}12. Vérification du port 8000...${NC}"
if netstat -tlnp | grep -q ":8000"; then
    echo -e "${GREEN}✓ Port 8000 en écoute${NC}"
else
    echo -e "${RED}✗ Port 8000 n'est pas en écoute${NC}"
    exit 1
fi
echo ""

echo "=========================================="
echo -e "${GREEN}  ✓ Déploiement réussi !${NC}"
echo "=========================================="
echo ""
echo "Commandes utiles :"
echo "  - Voir les logs en temps réel : sudo journalctl -u $SERVICE_NAME -f"
echo "  - Vérifier le statut : sudo systemctl status $SERVICE_NAME"
echo "  - Redémarrer : sudo systemctl restart $SERVICE_NAME"
echo ""
echo "Tests :"
echo "  - Health check local : curl http://localhost:8000/health/"
echo "  - Health check externe : curl https://api.xamila.finance/health/"
echo ""

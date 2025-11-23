#!/bin/bash

# Script pour restaurer services_email.py depuis GitHub
# et redémarrer le service

set -e

echo "=========================================="
echo "  Restauration depuis GitHub"
echo "=========================================="
echo ""

cd /var/www/xamila/xamila_backend

echo "1. Sauvegarde du fichier actuel..."
cp core/services_email.py core/services_email.py.broken 2>/dev/null || true
echo "✓ Sauvegarde créée"
echo ""

echo "2. Restauration depuis GitHub..."
git checkout core/services_email.py
echo "✓ Fichier restauré depuis Git"
echo ""

echo "3. Vérification du code Django..."
python3 manage.py check
echo "✓ Code Django valide"
echo ""

echo "4. Redémarrage du service..."
sudo systemctl restart xamila
sleep 3
echo "✓ Service redémarré"
echo ""

echo "5. Vérification du statut..."
sudo systemctl status xamila | head -10
echo ""

echo "6. Test du endpoint /health/..."
curl -s http://localhost:8000/health/ | python3 -m json.tool
echo ""

echo "=========================================="
echo "  ✓ Restauration réussie !"
echo "=========================================="

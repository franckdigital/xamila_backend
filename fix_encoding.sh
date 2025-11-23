#!/bin/bash

# Script pour corriger l'erreur de syntaxe dans services_email.py
# Ligne 385 : problème d'encodage dans la docstring

echo "Correction de l'erreur de syntaxe dans services_email.py..."

cd /var/www/xamila/xamila_backend/core

# Créer une sauvegarde
cp services_email.py services_email.py.backup

# Corriger la ligne 385 - remplacer le caractère mal encodé
sed -i '385s/.*/        """Envoie l'\''email a un administrateur"""/' services_email.py

echo "✓ Correction appliquée"
echo ""
echo "Vérification du code Django..."
cd /var/www/xamila/xamila_backend
python3 manage.py check

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Code Django valide"
    echo ""
    echo "Redémarrage du service..."
    sudo systemctl restart xamila
    sleep 3
    sudo systemctl status xamila
    echo ""
    echo "Test du endpoint /health/..."
    curl http://localhost:8000/health/
else
    echo ""
    echo "✗ Erreur dans le code Django"
    echo "Restauration de la sauvegarde..."
    cp services_email.py.backup services_email.py
fi

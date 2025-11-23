#!/bin/bash

echo "=== Vérification du serveur Xamila Backend ==="
echo ""

echo "1. Vérification du service systemd..."
sudo systemctl status xamila

echo ""
echo "2. Vérification des logs récents..."
sudo journalctl -u xamila -n 50 --no-pager

echo ""
echo "3. Vérification des processus Gunicorn..."
ps aux | grep gunicorn

echo ""
echo "4. Vérification du port 8000..."
sudo netstat -tlnp | grep 8000

echo ""
echo "5. Test de connexion locale..."
curl -I http://localhost:8000/health/

echo ""
echo "=== Fin de la vérification ==="

# 🔴 Erreur 502 Bad Gateway - Diagnostic et Solution

## ❌ Erreur observée

```
Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at https://api.xamila.finance/api/notifications/user/count/. 
(Reason: CORS header 'Access-Control-Allow-Origin' missing). 
Status code: 502.
```

**Le vrai problème n'est PAS CORS, mais le code 502 !**

---

## 🔍 Diagnostic

### **Qu'est-ce qu'une erreur 502 ?**

Une erreur **502 Bad Gateway** signifie que :
- ✅ Nginx (serveur web) fonctionne
- ❌ Le backend Django/Gunicorn ne répond pas
- ❌ Nginx ne peut pas transférer les requêtes au backend

### **Causes possibles**

1. ❌ Le service Django (Gunicorn) est arrêté
2. ❌ Le service Django a crashé
3. ❌ Erreur Python dans le code (empêche le démarrage)
4. ❌ Port 8000 non accessible
5. ❌ Problème de permissions fichiers
6. ❌ Problème de base de données

---

## 🛠️ Solution étape par étape

### **Étape 1 : Se connecter au serveur**

```bash
ssh root@72.60.88.93
```

### **Étape 2 : Vérifier le statut du service**

```bash
sudo systemctl status xamila
```

**Si le service est inactif (dead) :**
```bash
# Le service est arrêté, il faut le redémarrer
sudo systemctl start xamila
sudo systemctl status xamila
```

**Si le service est en erreur (failed) :**
```bash
# Voir les logs d'erreur
sudo journalctl -u xamila -n 100 --no-pager
```

### **Étape 3 : Vérifier les logs**

```bash
# Logs du service systemd
sudo journalctl -u xamila -f

# Logs Django (si configurés)
tail -f /var/log/xamila/error.log
tail -f /var/log/xamila/access.log
```

### **Étape 4 : Vérifier les processus Gunicorn**

```bash
ps aux | grep gunicorn
```

**Si aucun processus Gunicorn n'est trouvé :**
```bash
# Le service n'est pas démarré
sudo systemctl restart xamila
```

### **Étape 5 : Vérifier le port 8000**

```bash
sudo netstat -tlnp | grep 8000
# ou
sudo ss -tlnp | grep 8000
```

**Si le port n'est pas en écoute :**
```bash
# Le backend ne démarre pas, vérifier les logs
sudo journalctl -u xamila -n 100
```

### **Étape 6 : Tester en local**

```bash
curl http://localhost:8000/health/
```

**Réponse attendue :**
```json
{"status": "healthy", "message": "Xamila API is running", "debug": false}
```

**Si erreur :**
```bash
# Le backend a un problème, vérifier les logs
sudo journalctl -u xamila -n 200
```

---

## 🔧 Corrections courantes

### **Problème 1 : Erreur Python dans le code**

**Symptôme :** Le service ne démarre pas après un `git pull`

**Solution :**
```bash
cd /var/www/xamila/xamila_backend

# Vérifier les erreurs de syntaxe
python3 manage.py check

# Vérifier les migrations
python3 manage.py migrate

# Nettoyer les fichiers Python compilés
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Redémarrer
sudo systemctl restart xamila
```

### **Problème 2 : Permissions fichiers**

**Symptôme :** Erreur "Permission denied"

**Solution :**
```bash
cd /var/www/xamila/xamila_backend

# Corriger les permissions
sudo chown -R www-data:www-data .
sudo chmod -R 755 .

# Permissions spéciales pour les dossiers média
sudo chown -R www-data:www-data media/
sudo chmod -R 775 media/

# Redémarrer
sudo systemctl restart xamila
```

### **Problème 3 : Base de données inaccessible**

**Symptôme :** Erreur de connexion à PostgreSQL

**Solution :**
```bash
# Vérifier PostgreSQL
sudo systemctl status postgresql

# Si arrêté
sudo systemctl start postgresql

# Tester la connexion
sudo -u postgres psql -c "SELECT version();"

# Redémarrer Django
sudo systemctl restart xamila
```

### **Problème 4 : Variables d'environnement manquantes**

**Symptôme :** Erreur "Environment variable not set"

**Solution :**
```bash
cd /var/www/xamila/xamila_backend

# Vérifier le fichier .env
cat .env

# S'assurer que toutes les variables sont définies
# DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.

# Redémarrer
sudo systemctl restart xamila
```

### **Problème 5 : Import manquant ou dépendance**

**Symptôme :** `ImportError` ou `ModuleNotFoundError`

**Solution :**
```bash
cd /var/www/xamila/xamila_backend

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Désactiver l'environnement
deactivate

# Redémarrer
sudo systemctl restart xamila
```

---

## 🚀 Procédure de redémarrage complète

```bash
# 1. Se connecter au serveur
ssh root@72.60.88.93

# 2. Aller dans le dossier du projet
cd /var/www/xamila/xamila_backend

# 3. Récupérer les dernières modifications
git pull origin master

# 4. Nettoyer les fichiers compilés
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 5. Vérifier le code
python3 manage.py check

# 6. Appliquer les migrations
python3 manage.py migrate

# 7. Collecter les fichiers statiques (si nécessaire)
python3 manage.py collectstatic --noinput

# 8. Redémarrer le service
sudo systemctl restart xamila

# 9. Vérifier le statut
sudo systemctl status xamila

# 10. Suivre les logs
sudo journalctl -u xamila -f
```

---

## 📋 Checklist de diagnostic

- [ ] Le service systemd est actif (`sudo systemctl status xamila`)
- [ ] Les processus Gunicorn sont en cours d'exécution (`ps aux | grep gunicorn`)
- [ ] Le port 8000 est en écoute (`sudo netstat -tlnp | grep 8000`)
- [ ] Le endpoint `/health/` répond (`curl http://localhost:8000/health/`)
- [ ] Aucune erreur dans les logs (`sudo journalctl -u xamila -n 100`)
- [ ] Les permissions fichiers sont correctes
- [ ] La base de données est accessible
- [ ] Toutes les variables d'environnement sont définies
- [ ] Toutes les dépendances Python sont installées

---

## 🔍 Commandes de diagnostic rapide

```bash
# Script de diagnostic complet
cat > /tmp/check_xamila.sh << 'EOF'
#!/bin/bash
echo "=== Diagnostic Xamila Backend ==="
echo ""
echo "1. Service status:"
sudo systemctl status xamila | head -20
echo ""
echo "2. Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep
echo ""
echo "3. Port 8000:"
sudo netstat -tlnp | grep 8000
echo ""
echo "4. Health check:"
curl -s http://localhost:8000/health/ | python3 -m json.tool
echo ""
echo "5. Recent logs:"
sudo journalctl -u xamila -n 20 --no-pager
EOF

chmod +x /tmp/check_xamila.sh
/tmp/check_xamila.sh
```

---

## 🆘 Si rien ne fonctionne

### **Redémarrage complet du serveur**

```bash
# En dernier recours
sudo reboot
```

Après le redémarrage, tous les services devraient redémarrer automatiquement.

---

## 📊 Logs à surveiller

### **Logs systemd (service Django)**
```bash
sudo journalctl -u xamila -f
```

### **Logs Nginx**
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### **Logs PostgreSQL**
```bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## ✅ Vérification finale

Une fois le service redémarré, vérifier que tout fonctionne :

```bash
# 1. Health check local
curl http://localhost:8000/health/

# 2. Health check externe
curl https://api.xamila.finance/health/

# 3. Test d'un endpoint API
curl https://api.xamila.finance/api/sgis/

# 4. Vérifier les logs en temps réel
sudo journalctl -u xamila -f
```

---

## 🎯 Résolution du problème CORS

**Important :** Le message d'erreur CORS est trompeur. Le vrai problème est le **502 Bad Gateway**.

Une fois le backend redémarré et fonctionnel :
- ✅ Les headers CORS seront automatiquement ajoutés
- ✅ Les requêtes frontend fonctionneront
- ✅ Plus d'erreur 502

**Le CORS n'est PAS le problème, c'est le backend qui ne répond pas !**

---

## 📞 Contact

Si le problème persiste après toutes ces étapes :
1. Copier les logs complets : `sudo journalctl -u xamila -n 500 > logs.txt`
2. Vérifier les erreurs Python spécifiques
3. Vérifier la configuration Nginx : `sudo nginx -t`
4. Vérifier la configuration systemd : `sudo systemctl cat xamila`

---

## 🎉 Résolution attendue

Après redémarrage du service :
- ✅ Le backend répond sur le port 8000
- ✅ Nginx peut transférer les requêtes
- ✅ Plus d'erreur 502
- ✅ Les headers CORS sont présents
- ✅ Le frontend fonctionne normalement

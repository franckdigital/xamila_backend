# 🗄️ CONFIGURATION MYSQL POUR XAMILA

## 📋 **GUIDE D'INSTALLATION ET CONFIGURATION**

### **1. Installation de MySQL Server**

#### **Option A : MySQL Community Server (Recommandé)**
```bash
# Télécharger depuis : https://dev.mysql.com/downloads/mysql/
# Ou utiliser Chocolatey sur Windows :
choco install mysql

# Ou utiliser XAMPP/WAMP qui inclut MySQL
```

#### **Option B : MySQL via Docker**
```bash
# Lancer MySQL dans un conteneur Docker
docker run --name xamila-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=xamila_db \
  -e MYSQL_USER=xamila_user \
  -e MYSQL_PASSWORD=password123 \
  -p 3306:3306 \
  -d mysql:8.0

# Vérifier que le conteneur fonctionne
docker ps
```

---

### **2. Configuration de la Base de Données**

#### **Connexion à MySQL**
```bash
# Via ligne de commande
mysql -u root -p

# Via MySQL Workbench (interface graphique)
# Télécharger depuis : https://dev.mysql.com/downloads/workbench/
```

#### **Création de la Base de Données et Utilisateur**
```sql
-- Créer la base de données
CREATE DATABASE xamila_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur
CREATE USER 'xamila_user'@'localhost' IDENTIFIED BY 'password123';

-- Accorder tous les privilèges
GRANT ALL PRIVILEGES ON xamila_db.* TO 'xamila_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Vérifier la création
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'xamila_user';
```

---

### **3. Configuration Django**

#### **Variables d'Environnement (.env)**
```bash
# Copier le fichier d'exemple
copy .env.example .env

# Éditer .env avec vos vraies valeurs MySQL
DB_NAME=xamila_db
DB_USER=xamila_user
DB_PASSWORD=password123
DB_HOST=localhost
DB_PORT=3306
```

#### **Installation du Driver MySQL**
```bash
# Installer mysqlclient (déjà dans requirements.txt)
pip install mysqlclient

# Si problème d'installation sur Windows, utiliser :
pip install mysqlclient --only-binary=all

# Ou alternative avec PyMySQL :
pip install PyMySQL
```

---

### **4. Test de Connexion**

#### **Test Django**
```bash
# Tester la connexion
python manage.py check --database default

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

#### **Test Direct MySQL**
```python
# Script de test (test_mysql.py)
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        database='xamila_db',
        user='xamila_user',
        password='password123'
    )
    
    if connection.is_connected():
        db_info = connection.get_server_info()
        print(f"✅ Connexion MySQL réussie ! Version: {db_info}")
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        database_name = cursor.fetchone()
        print(f"✅ Base de données active: {database_name[0]}")

except Error as e:
    print(f"❌ Erreur de connexion MySQL: {e}")
    
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("✅ Connexion MySQL fermée")
```

---

### **5. Configuration Avancée**

#### **Optimisation MySQL pour Django**
```sql
-- Dans MySQL, optimiser pour Django
SET GLOBAL innodb_file_format = 'Barracuda';
SET GLOBAL innodb_file_per_table = ON;
SET GLOBAL innodb_large_prefix = ON;

-- Vérifier la configuration
SHOW VARIABLES LIKE 'innodb_file_format';
SHOW VARIABLES LIKE 'innodb_file_per_table';
```

#### **Configuration my.cnf/my.ini**
```ini
[mysqld]
# Optimisations pour Django
innodb_file_format = Barracuda
innodb_file_per_table = 1
innodb_large_prefix = 1

# Encodage UTF-8
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Performance
max_connections = 200
innodb_buffer_pool_size = 256M
```

---

### **6. Sauvegarde et Restauration**

#### **Sauvegarde**
```bash
# Sauvegarde complète
mysqldump -u xamila_user -p xamila_db > xamila_backup.sql

# Sauvegarde avec structure seulement
mysqldump -u xamila_user -p --no-data xamila_db > xamila_structure.sql
```

#### **Restauration**
```bash
# Restaurer depuis une sauvegarde
mysql -u xamila_user -p xamila_db < xamila_backup.sql
```

---

### **7. Dépannage**

#### **Erreurs Communes**

**Erreur : "Access denied for user"**
```sql
-- Vérifier les privilèges
SHOW GRANTS FOR 'xamila_user'@'localhost';

-- Réinitialiser le mot de passe
ALTER USER 'xamila_user'@'localhost' IDENTIFIED BY 'nouveau_password';
```

**Erreur : "Can't connect to MySQL server"**
```bash
# Vérifier que MySQL fonctionne
sudo systemctl status mysql  # Linux
net start mysql              # Windows

# Vérifier le port
netstat -an | grep 3306
```

**Erreur : "mysqlclient installation failed"**
```bash
# Sur Windows, installer Visual C++ Build Tools
# Ou utiliser une wheel pré-compilée
pip install --only-binary=all mysqlclient
```

---

## ✅ **VÉRIFICATION FINALE**

Une fois la configuration terminée, vous devriez pouvoir :

1. ✅ Se connecter à MySQL avec `xamila_user`
2. ✅ Voir la base `xamila_db` créée
3. ✅ Lancer `python manage.py check` sans erreur
4. ✅ Créer et appliquer les migrations Django
5. ✅ Accéder à l'admin Django sur `http://127.0.0.1:8000/admin/`

**Votre projet Django Xamila est maintenant configuré avec MySQL !** 🚀

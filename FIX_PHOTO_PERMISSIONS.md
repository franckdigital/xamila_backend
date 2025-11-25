# 🔧 Correction : Problème de permissions pour la photo

## 🎯 Diagnostic

**Problème identifié :** "Aucune photo disponible pour la page 22"

**Cause probable :** Erreur de permissions lors de la sauvegarde des fichiers uploadés (photo et CNI). Le code supprime alors les fichiers et crée la demande sans eux.

---

## 📋 Vérification

### **1. Déployer les nouveaux logs**

```bash
cd /var/www/xamila/xamila_backend
git pull origin master
sudo systemctl restart xamila
```

### **2. Soumettre une nouvelle demande**

Remplir le formulaire et uploader une photo.

### **3. Consulter les logs**

```bash
sudo journalctl -u xamila -f
```

**Messages à rechercher :**

#### **✅ Cas normal (photo sauvegardée)**
```
Création AccountOpeningRequest - Photo: True, CNI: True
✅ AccountOpeningRequest créé avec succès (ID: xxx)
```

#### **⚠️ Cas problématique (erreur de permissions)**
```
Création AccountOpeningRequest - Photo: True, CNI: True
⚠️ Erreur de permissions lors de la sauvegarde des fichiers: [Errno 13] Permission denied
Nouvelle tentative sans les fichiers photo et CNI...
⚠️ AccountOpeningRequest créé SANS fichiers (ID: xxx)
```

#### **❌ Cas problématique (photo non envoyée)**
```
Création AccountOpeningRequest - Photo: False, CNI: False
✅ AccountOpeningRequest créé avec succès (ID: xxx)
```

---

## 🔧 Solutions

### **Solution 1 : Corriger les permissions du dossier media**

Si vous voyez "Permission denied" dans les logs :

```bash
# Vérifier les permissions actuelles
ls -la /var/www/xamila/xamila_backend/media/

# Corriger les permissions
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/

# Créer les sous-dossiers si nécessaire
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/id_scans/
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/

# Redémarrer le service
sudo systemctl restart xamila
```

### **Solution 2 : Vérifier la configuration Django**

Vérifier que `settings.py` contient :

```python
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### **Solution 3 : Vérifier que le frontend envoie bien la photo**

Si vous voyez "Photo: False" dans les logs, le problème vient du frontend.

**Vérifier dans le frontend :**

```typescript
// OpenAccountPage.tsx
const formData = new FormData();
// ...
if (photo) {
  formData.append('photo', photo);  // ✅ Doit être présent
}
if (idScan) {
  formData.append('id_card_scan', idScan);  // ✅ Doit être présent
}
```

### **Solution 4 : Vérifier la taille maximale des fichiers**

Django limite la taille des fichiers uploadés. Vérifier dans `settings.py` :

```python
# Taille maximale des fichiers (5 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
```

Si les fichiers sont trop gros, augmenter ces valeurs.

---

## 🧪 Test après correction

### **1. Corriger les permissions**

```bash
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/
sudo systemctl restart xamila
```

### **2. Soumettre une nouvelle demande**

1. Aller sur le formulaire
2. Remplir tous les champs
3. Uploader une photo (JPEG/PNG, < 2 MB)
4. Soumettre

### **3. Vérifier les logs**

```bash
sudo journalctl -u xamila -f | grep -E "Photo|photo|AccountOpeningRequest"
```

**Attendu :**
```
Création AccountOpeningRequest - Photo: True, CNI: True
✅ AccountOpeningRequest créé avec succès (ID: xxx)
Génération de Page 22 - Formulaire d'ouverture...
Tentative d'ajout de la photo: photo_xxx.jpg
Photo chargée: 800x600 pixels, format: JPEG
✅ Photo ajoutée sur l'annexe page 22
```

### **4. Télécharger les annexes**

1. Cliquer sur "Télécharger les annexes"
2. Ouvrir le PDF
3. Aller à la page 22
4. **La photo doit apparaître dans le cadre en haut à droite ! 📸**

---

## 📊 Checklist de résolution

- [ ] **Logs déployés** : `git pull` + `systemctl restart`
- [ ] **Permissions corrigées** : `chown` + `chmod` sur `/media/`
- [ ] **Dossiers créés** : `/media/kyc/account_opening/photos/`
- [ ] **Service redémarré** : `systemctl restart xamila`
- [ ] **Nouvelle demande soumise** : Avec photo uploadée
- [ ] **Logs consultés** : Vérifier "Photo: True" et "✅ créé avec succès"
- [ ] **PDF téléchargé** : Vérifier que la photo apparaît sur la page 22

---

## 🚨 Erreurs courantes

### **Erreur 1 : Permission denied**

```
⚠️ Erreur de permissions lors de la sauvegarde des fichiers: [Errno 13] Permission denied: '/var/www/xamila/xamila_backend/media/kyc/account_opening/photos/photo_xxx.jpg'
```

**Solution :**
```bash
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/
```

### **Erreur 2 : No such file or directory**

```
⚠️ Erreur de permissions lors de la sauvegarde des fichiers: [Errno 2] No such file or directory: '/var/www/xamila/xamila_backend/media/kyc/account_opening/photos/'
```

**Solution :**
```bash
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/id_scans/
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
```

### **Erreur 3 : Photo non envoyée par le frontend**

```
Création AccountOpeningRequest - Photo: False, CNI: False
```

**Solution :** Vérifier que le frontend envoie bien les fichiers dans le `FormData`.

### **Erreur 4 : Fichier trop gros**

```
Request entity too large
```

**Solution :** Augmenter `DATA_UPLOAD_MAX_MEMORY_SIZE` dans `settings.py`.

---

## ✅ Résultat attendu

**Logs :**
```
Création AccountOpeningRequest - Photo: True, CNI: True
✅ AccountOpeningRequest créé avec succès (ID: abc-123)
AccountOpeningRequest créé: abc-123
Génération de Page 22 - Formulaire d'ouverture...
Tentative d'ajout de la photo: photo_franck_kouadio.jpg
Photo chargée: 800x600 pixels, format: JPEG
Dimensions finales: 79.37pt x 107.72pt
✅ Photo ajoutée sur l'annexe page 22 à la position (123.45, 234.56)
✅ Page 22 - Formulaire d'ouverture générée avec succès
```

**PDF Annexe Page 22 :**
```
┌─────────────────────────────────────────────────┐
│ TITULAIRE PERSONNE PHYSIQUE          ┌────────┐│
│                                       │ [PHOTO]││
│ Civilité : Monsieur                  │ VISIBLE││
│ Nom : kouadio                         │   ICI  ││
│ Prénom(s) : franck                    │        ││
│ Date de naissance : 10/10/2005       └────────┘│
└─────────────────────────────────────────────────┘
```

---

## 🎯 Commandes rapides

```bash
# 1. Déployer
cd /var/www/xamila/xamila_backend
git pull origin master
sudo systemctl restart xamila

# 2. Corriger permissions
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/
sudo mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/id_scans/

# 3. Redémarrer
sudo systemctl restart xamila

# 4. Voir les logs
sudo journalctl -u xamila -f | grep -E "Photo|photo|AccountOpeningRequest"
```

**La photo devrait maintenant apparaître sur la page 22 ! 📸✅**

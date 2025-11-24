# 🔍 Debug : Photo manquante sur la page 22

## 🎯 Problème

La page 22 est générée mais la photo n'apparaît pas dans le cadre prévu.

---

## 📋 Vérifications à effectuer

### **1. Vérifier que la photo est uploadée**

Dans le formulaire frontend, assurez-vous que :
- ✅ Le champ photo est rempli
- ✅ Le fichier est bien envoyé au backend
- ✅ Le fichier est sauvegardé en base de données

**Test :**
```bash
# Sur le serveur
cd /var/www/xamila/xamila_backend
source venv/bin/activate
python manage.py shell

# Dans le shell Python
from core.models import AccountOpeningRequest
aor = AccountOpeningRequest.objects.latest('created_at')
print(f"Photo: {aor.photo}")
print(f"Photo path: {aor.photo.path if aor.photo else 'None'}")
print(f"Photo exists: {aor.photo.storage.exists(aor.photo.name) if aor.photo else False}")
```

### **2. Consulter les logs**

Les logs détaillés ont été ajoutés pour diagnostiquer le problème :

```bash
# Voir les logs en temps réel
sudo journalctl -u xamila -f

# Ou dans les logs Django
tail -f /var/log/xamila/debug.log
```

**Messages à rechercher :**

#### **✅ Photo chargée avec succès**
```
Tentative d'ajout de la photo: photo_123.jpg
Photo chargée: 800x600 pixels, format: JPEG
Dimensions finales: 79.37pt x 107.72pt
✅ Photo ajoutée sur l'annexe page 22 à la position (123.45, 234.56)
```

#### **⚠️ Aucune photo**
```
Aucune photo disponible pour la page 22
```

#### **❌ Erreur de chargement**
```
❌ Erreur lors de l'ajout de la photo sur page 22: [détails de l'erreur]
```

### **3. Vérifier les permissions**

```bash
# Vérifier les permissions du dossier media
ls -la /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/

# Les fichiers doivent être lisibles par l'utilisateur qui exécute Django
# Corriger si nécessaire :
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/
```

### **4. Vérifier le format de la photo**

Le code supporte les formats courants (JPEG, PNG, etc.). Vérifiez que :
- ✅ Le fichier n'est pas corrompu
- ✅ Le format est supporté par PIL/Pillow
- ✅ La taille du fichier est raisonnable (< 5 MB)

---

## 🔧 Solutions possibles

### **Solution 1 : Photo non uploadée**

**Problème :** Le champ photo est vide dans la base de données.

**Solution :**
1. Vérifier que le formulaire frontend envoie bien la photo
2. Vérifier que le serializer backend accepte le fichier
3. Re-soumettre une demande avec une photo

### **Solution 2 : Fichier introuvable**

**Problème :** Le fichier photo existe en base mais pas sur le disque.

**Solution :**
```bash
# Vérifier l'existence du fichier
ls -la /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/

# Si le dossier n'existe pas, le créer
mkdir -p /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/
sudo chown www-data:www-data /var/www/xamila/xamila_backend/media/kyc/account_opening/photos/
```

### **Solution 3 : Erreur de permissions**

**Problème :** Django ne peut pas lire le fichier photo.

**Solution :**
```bash
# Corriger les permissions
sudo chown -R www-data:www-data /var/www/xamila/xamila_backend/media/
sudo chmod -R 755 /var/www/xamila/xamila_backend/media/
```

### **Solution 4 : Format d'image non supporté**

**Problème :** Le format de l'image n'est pas reconnu par PIL.

**Solution :**
```bash
# Installer les dépendances pour tous les formats
pip install Pillow --upgrade

# Vérifier les formats supportés
python -c "from PIL import Image; print(Image.OPEN)"
```

### **Solution 5 : Erreur lors de la génération**

**Problème :** Une exception se produit lors de l'ajout de la photo.

**Solution :**
1. Consulter les logs détaillés (voir section 2)
2. Identifier l'erreur exacte
3. Corriger le code si nécessaire

---

## 🧪 Test manuel

### **Créer un PDF de test avec photo**

```python
# test_photo_page22.py
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

# Créer une image de test
img = Image.new('RGB', (300, 400), color='red')
img_buffer = BytesIO()
img.save(img_buffer, format='JPEG')
img_buffer.seek(0)

# Créer un PDF
pdf_buffer = BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=A4)
width, height = A4

# Dessiner un cadre
photo_box_x = width - 50*mm
photo_box_y = height - 100*mm
c.rect(photo_box_x, photo_box_y - 35*mm, 30*mm, 40*mm, fill=0, stroke=1)

# Ajouter l'image
img_buffer.seek(0)
photo_reader = ImageReader(img_buffer)
c.drawImage(photo_reader, photo_box_x + 1*mm, photo_box_y - 34*mm, 
            width=28*mm, height=38*mm, preserveAspectRatio=True)

c.showPage()
c.save()

# Sauvegarder le PDF
with open('test_photo.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())

print("✅ PDF de test créé: test_photo.pdf")
```

**Exécuter :**
```bash
cd /var/www/xamila/xamila_backend
source venv/bin/activate
python test_photo_page22.py
```

Si ce test fonctionne, le problème vient de la photo uploadée ou de son accès.

---

## 📊 Checklist de diagnostic

- [ ] **Photo uploadée** : Vérifier que `aor.photo` n'est pas vide
- [ ] **Fichier existe** : Vérifier que le fichier est sur le disque
- [ ] **Permissions OK** : Vérifier que Django peut lire le fichier
- [ ] **Format supporté** : Vérifier que PIL peut ouvrir l'image
- [ ] **Logs consultés** : Vérifier les messages de log détaillés
- [ ] **Test manuel** : Créer un PDF de test avec une image

---

## 🔄 Workflow de test

### **1. Soumettre une nouvelle demande**
```
1. Aller sur le formulaire d'ouverture de compte
2. Remplir tous les champs
3. Uploader une photo (JPEG ou PNG, < 2 MB)
4. Soumettre la demande
```

### **2. Vérifier les logs**
```bash
sudo journalctl -u xamila -f | grep -i photo
```

**Attendu :**
```
Tentative d'ajout de la photo: photo_xxx.jpg
Photo chargée: 800x600 pixels, format: JPEG
✅ Photo ajoutée sur l'annexe page 22
```

### **3. Télécharger les annexes**
```
1. Cliquer sur "Télécharger les annexes"
2. Ouvrir le PDF
3. Vérifier la page 22
4. La photo doit apparaître dans le cadre en haut à droite
```

---

## 🚨 Erreurs courantes

### **Erreur 1 : "No such file or directory"**
```
❌ Erreur: [Errno 2] No such file or directory: '/path/to/photo.jpg'
```

**Solution :** Le fichier n'existe pas sur le disque. Vérifier le chemin et les permissions.

### **Erreur 2 : "cannot identify image file"**
```
❌ Erreur: cannot identify image file <_io.BytesIO object>
```

**Solution :** Le format de l'image n'est pas reconnu. Vérifier que c'est un JPEG/PNG valide.

### **Erreur 3 : "Permission denied"**
```
❌ Erreur: [Errno 13] Permission denied: '/path/to/photo.jpg'
```

**Solution :** Django n'a pas les permissions pour lire le fichier. Corriger avec `chmod` et `chown`.

### **Erreur 4 : "seek() not supported"**
```
❌ Erreur: io.UnsupportedOperation: seek
```

**Solution :** Le fichier n'est pas un objet fichier valide. Vérifier le type de `aor.photo`.

---

## ✅ Résolution attendue

Après déploiement et test :

**Logs :**
```
Génération de Page 22 - Formulaire d'ouverture...
Tentative d'ajout de la photo: photo_franck_kouadio.jpg
Photo chargée: 800x600 pixels, format: JPEG
Dimensions finales: 79.37pt x 107.72pt
✅ Photo ajoutée sur l'annexe page 22 à la position (123.45, 234.56)
✅ Page 22 - Formulaire d'ouverture générée avec succès
```

**PDF :**
```
┌─────────────────────────────────────────────────┐
│ TITULAIRE PERSONNE PHYSIQUE          ┌────────┐│
│                                       │ [PHOTO]││
│ Civilité : Monsieur                  │        ││
│ Nom : kouadio                         │        ││
│ Prénom(s) : franck                    │        ││
│ Date de naissance : 10/10/2005       └────────┘│
└─────────────────────────────────────────────────┘
```

**La photo doit apparaître dans le cadre ! 📸**

---

## 📝 Prochaines étapes

1. **Déployer** les changements sur le serveur
2. **Soumettre** une nouvelle demande avec photo
3. **Consulter** les logs pour voir les messages détaillés
4. **Vérifier** le PDF généré
5. **Partager** les logs si le problème persiste

Les logs détaillés permettront d'identifier exactement où le problème se situe ! 🔍

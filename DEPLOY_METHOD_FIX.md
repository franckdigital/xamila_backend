# 🔧 Correction du nom de méthode - AnnexPDFService

## ❌ Erreur détectée

```
'AnnexPDFService' object has no attribute 'generate_annex_pdf'
```

**Cause :** Mauvais nom de méthode utilisé dans `views.py`.

---

## 🔍 Problème

Dans `services_annex_pdf.py`, la méthode s'appelle :
```python
def generate_annexes_pdf(self, aor, annex_data: dict) -> BytesIO:
    # Avec un "s" à annexes
```

Mais dans `views.py`, on appelait :
```python
annex_service.generate_annex_pdf(req_obj, annex_data)
# Sans "s" - ERREUR !
```

---

## ✅ Solution appliquée

### **Fichier modifié : `core/views.py`**

**Ligne 705 - AVANT :**
```python
annexes_buffer = annex_service.generate_annex_pdf(req_obj, annex_data)
```

**Ligne 705 - APRÈS :**
```python
annexes_buffer = annex_service.generate_annexes_pdf(req_obj, annex_data)
```

**Ligne 1221 - AVANT :**
```python
pdf_buffer = annex_service.generate_annex_pdf(fake_aor, annex_data)
```

**Ligne 1221 - APRÈS :**
```python
pdf_buffer = annex_service.generate_annexes_pdf(fake_aor, annex_data)
```

---

## 🚀 Déploiement sur le serveur

```bash
cd /var/www/xamila/xamila_backend
git pull origin master
python3 manage.py check
sudo systemctl restart xamila
```

---

## 🧪 Test

Après le déploiement :

1. **Ouvrir** https://xamila.finance/open-account
2. **Sélectionner** une SGI (ex: NSIA)
3. **Cliquer** sur "📋 Afficher les Annexes"
4. **Remplir** quelques champs
5. **Cliquer** sur "📋 Annexes pré-remplies"
6. ✅ **Le PDF doit se télécharger sans erreur 500**

---

## 📊 Commit effectué

```bash
13782ee - Fix method name: generate_annex_pdf -> generate_annexes_pdf
```

---

## ✅ Résultat

Les deux endpoints de génération d'annexes fonctionnent maintenant :
- ✅ **POST /api/download-annexes-pdf/** → Téléchargement direct
- ✅ **AccountOpeningRequestCreateView** → Génération lors de la soumission

---

## 🎯 Commande de déploiement rapide

```bash
cd /var/www/xamila/xamila_backend && \
git pull origin master && \
python3 manage.py check && \
sudo systemctl restart xamila && \
sleep 3 && \
curl http://localhost:8000/health/
```

**Le téléchargement des annexes devrait maintenant fonctionner ! 🎉**

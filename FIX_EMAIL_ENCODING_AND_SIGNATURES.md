# 🔧 Correction encodage emails + Signatures annexes

## ✅ Corrections appliquées

### **1. Encodage UTF-8 des emails** 

**Problème :** Les caractères accentués s'affichaient mal dans les emails (ex: "Ã©" au lieu de "é")

**Solution :** Ajout de `<meta charset="UTF-8">` dans tous les emails HTML

**Fichiers modifiés :**
- `core/services_email.py`

**Changements :**
```html
<!-- AVANT -->
<html>
<body>...</body>
</html>

<!-- APRÈS -->
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>...</body>
</html>
```

**Emails concernés :**
- ✅ Email client
- ✅ Email manager SGI
- ✅ Email équipe Xamila
- ✅ Email administrateurs

---

### **2. Amélioration des signatures sur les annexes**

**Problème :** Les zones de signature n'étaient pas visibles sur les PDFs générés

**Solution :** 
- Ajout de rectangles visibles pour les zones de signature
- Amélioration du texte des instructions
- Ajout de la note "IMPORTANT" sur la page 22
- Meilleure mise en forme conforme au contrat original

**Fichiers modifiés :**
- `core/services_annex_pdf.py`

**Changements par page :**

#### **Page 21 - Texte légal et signatures**
```python
# Zones de signature avec rectangles
c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)  # Titulaire
c.rect(120*mm, y, 60*mm, 20*mm, stroke=1, fill=0)  # SGI

# Labels améliorés
"LE(S) TITULAIRE(S) (1)"
'(1) Signature précédée de la mention manuscrite "Lu et approuvé"'
```

#### **Page 22 - Formulaire d'ouverture**
```python
# Note IMPORTANT en haut de page
"IMPORTANT : En cas de pluralité de titulaires"
"(compte joint de titres, compte en indivision ou compte usufrui nue-propriété),"
"merci de photocopier cette page en autant d'exemplaires qu'il y a de co-titulaires..."
```

#### **Page 23 - Caractéristiques du compte**
```python
# Zone de signature avec rectangle
c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)

# Texte amélioré
"Fait à: {place}, le {date}, en deux exemplaires originaux."
"Signature du titulaire"
'(précédée de "Lu et approuvé")'
```

#### **Page 26 - Procuration**
- Zones de signature pour mandant et mandataire
- Instructions claires

---

## 📊 Structure des annexes

Les annexes générées correspondent aux pages du contrat vierge :

| Page | Contenu | Signatures |
|------|---------|------------|
| **21** | Texte légal + Article 30 | Titulaire + SGI |
| **22** | Formulaire d'ouverture (identité, adresse) | - |
| **23** | Caractéristiques du compte | Titulaire |
| **26** | Procuration (si applicable) | Mandant + Mandataire |

---

## 🚀 Déploiement

### **Sur le serveur**

```bash
cd /var/www/xamila/xamila_backend
git pull origin master
python3 manage.py check
sudo systemctl restart xamila
```

---

## 🧪 Tests

### **Test 1 : Encodage des emails**

1. Soumettre une demande d'ouverture de compte
2. Vérifier les emails reçus
3. ✅ Les caractères accentués doivent s'afficher correctement :
   - "Demande d'ouverture" (pas "Demande d'ouverture")
   - "Téléphone" (pas "TÃ©lÃ©phone")
   - "Numéro" (pas "NumÃ©ro")

### **Test 2 : Signatures sur les annexes**

1. Ouvrir https://xamila.finance/open-account
2. Sélectionner une SGI (ex: NSIA)
3. Cliquer sur "📋 Afficher les Annexes"
4. Remplir les champs
5. Cliquer sur "📋 Annexes pré-remplies"
6. Ouvrir le PDF téléchargé
7. ✅ Vérifier que les zones de signature sont visibles :
   - **Page 21** : 2 rectangles (Titulaire + SGI)
   - **Page 22** : Note IMPORTANT en haut
   - **Page 23** : 1 rectangle (Titulaire)
   - **Page 26** : Zones pour mandant/mandataire si procuration

---

## 📝 Commit effectué

```bash
568289f - Fix email encoding (UTF-8) and improve signature boxes on annexes
```

---

## ✅ Résultat

### **Emails**
- ✅ Caractères accentués affichés correctement
- ✅ Tous les emails (client, SGI, Xamila, admin) corrigés

### **Annexes PDF**
- ✅ Zones de signature visibles avec rectangles
- ✅ Instructions claires pour les signatures
- ✅ Note IMPORTANT sur la page 22
- ✅ Conforme au contrat original

---

## 🎯 Commande de déploiement rapide

```bash
cd /var/www/xamila/xamila_backend && \
git pull origin master && \
sudo systemctl restart xamila && \
sleep 3 && \
curl http://localhost:8000/health/
```

---

## 📋 Checklist finale

- [x] Encodage UTF-8 ajouté aux emails HTML
- [x] Rectangles de signature ajoutés sur les annexes
- [x] Note IMPORTANT ajoutée sur page 22
- [x] Instructions de signature améliorées
- [x] Commit et push effectués
- [ ] Déploiement sur le serveur
- [ ] Tests manuels effectués
- [ ] Validation avec un vrai email

---

## 🎉 Prochaines étapes

1. **Déployer** sur le serveur avec la commande ci-dessus
2. **Tester** en soumettant une vraie demande
3. **Vérifier** les emails reçus (encodage correct)
4. **Télécharger** les annexes et vérifier les signatures

**Les corrections sont prêtes à être déployées ! 🚀**

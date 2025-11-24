# 🔄 Nouvelle approche : Contrat vierge commercial + Annexes pré-remplies

## 📋 Changement de stratégie

### **Ancienne approche**
- Générer un contrat HTML dynamique avec WeasyPrint
- Fusionner avec les annexes ReportLab
- Bouton "Télécharger le contrat complet" sur le frontend
- Emails avec le contrat fusionné

### **Nouvelle approche**
- ✅ Utiliser le **contrat vierge commercial** (PDF statique de la SGI)
- ✅ Générer les **annexes pré-remplies** (ReportLab)
- ✅ Envoyer par email : **Contrat vierge + Annexes + CNI + Photo**
- ✅ Supprimer le bouton "Télécharger le contrat complet"
- ✅ Un seul bouton : **"Soumettre la demande"** (envoie les emails)

---

## 🎯 Objectifs

1. **Simplifier le workflow** : Un seul bouton pour tout
2. **Utiliser les vrais contrats commerciaux** : PDFs officiels des SGI
3. **Séparation claire** : Contrat vierge (pages 1-20) + Annexes (pages 21-26)
4. **Emails complets** : Tous les documents nécessaires en pièces jointes

---

## 🔧 Modifications implémentées

### **1. Backend : Utiliser le contrat vierge commercial**

**Fichier :** `core/views.py` - `AccountOpeningRequestCreateView`

#### **Avant**
```python
# Générer le contrat avec WeasyPrint (HTML → PDF)
pdf_service = ContractPDFService()
ctx = pdf_service.build_context(req_obj)
html = pdf_service.render_html(ctx)
contract_response = pdf_service.generate_pdf_response(html)
contract_pdf_bytes = contract_response.content
```

#### **Après**
```python
# Charger le contrat vierge commercial (PDF statique)
import os
from django.conf import settings

# Déterminer le fichier selon la SGI
if req_obj.sgi and req_obj.sgi.name:
    sgi_name = req_obj.sgi.name.upper()
    if 'NSIA' in sgi_name:
        contract_filename = 'NSIA_Convention_Compte_Titres.pdf'
    elif 'GEK' in sgi_name:
        contract_filename = 'GEK --Convention commerciale VF 2025.pdf'
    else:
        contract_filename = 'NSIA_Convention_Compte_Titres.pdf'
else:
    contract_filename = 'NSIA_Convention_Compte_Titres.pdf'

contract_path = os.path.join(settings.BASE_DIR, 'contracts', contract_filename)

if os.path.exists(contract_path):
    with open(contract_path, 'rb') as f:
        contract_pdf_bytes = f.read()
    logger.info(f"Contrat vierge chargé: {contract_filename}")
```

**Avantages :**
- ✅ Utilise les PDFs officiels des SGI
- ✅ Pas de génération HTML (plus rapide)
- ✅ Contrats conformes aux modèles commerciaux
- ✅ Inclut déjà les pages 21-26 vierges

---

### **2. Frontend : Supprimer le bouton "Contrat complet"**

**Fichier :** `src/pages/OpenAccountPage.tsx`

#### **Avant**
```tsx
<Box sx={{ display:'flex', gap:2, flexWrap: 'wrap' }}>
  <Button 
    onClick={onPreview}
    disabled={previewLoading || loading}
  >
    📥 Télécharger le contrat complet
  </Button>
  <Button 
    type="submit"
    disabled={loading || previewLoading}
  >
    Soumettre la demande
  </Button>
</Box>
```

#### **Après**
```tsx
<Box sx={{ display:'flex', gap:2, flexWrap: 'wrap' }}>
  <Button 
    type="submit"
    disabled={loading}
    sx={{ flex: 1 }}
  >
    Soumettre la demande
  </Button>
</Box>
```

**Changements :**
- ❌ Supprimé : Bouton "Télécharger le contrat complet"
- ❌ Supprimé : Fonction `onPreview()`
- ❌ Supprimé : État `previewLoading`
- ✅ Simplifié : Un seul bouton "Soumettre la demande"

---

## 📧 Emails envoyés

Lors de la soumission, les emails sont envoyés avec les pièces jointes suivantes :

### **1. Email au client**
```
Pièces jointes :
- Contrat_[SGI]_[Nom].pdf        → Contrat vierge commercial
- Annexes_[SGI]_[Nom].pdf        → Annexes pré-remplies (pages 21-26)
- Photo_[Nom].jpg                → Photo d'identité
- CNI_[Nom].pdf                  → Scan de la CNI/Passeport
```

### **2. Email au manager SGI**
```
Pièces jointes :
- Contrat_[SGI]_[Nom].pdf        → Contrat vierge commercial
- Annexes_[SGI]_[Nom].pdf        → Annexes pré-remplies
- Photo_[Nom].jpg                → Photo d'identité
- CNI_[Nom].pdf                  → Scan de la CNI/Passeport
```

### **3. Email à l'équipe Xamila**
```
Pièces jointes :
- Contrat_[SGI]_[Nom].pdf        → Contrat vierge commercial
- Annexes_[SGI]_[Nom].pdf        → Annexes pré-remplies
- Photo_[Nom].jpg                → Photo d'identité
- CNI_[Nom].pdf                  → Scan de la CNI/Passeport
```

---

## 📊 Structure des documents

### **Contrat vierge commercial**
```
Pages 1-20  : Conditions générales, clauses légales
Pages 21-26 : Annexes vierges (à remplir)
```

### **Annexes pré-remplies (générées par ReportLab)**
```
Page 21 : Texte légal + Signatures (Titulaire + SGI)
Page 22 : Formulaire d'ouverture de compte
Page 23 : Caractéristiques du compte + Signature
Page 26 : Procuration + Signatures (Mandant + Mandataire)
```

### **Résultat final**
Le client reçoit :
1. **Contrat vierge** : PDF officiel de la SGI (pages 1-26 vierges)
2. **Annexes pré-remplies** : Pages 21-26 avec ses données et signatures
3. **Photo** : Photo d'identité
4. **CNI** : Scan de la pièce d'identité

Le client peut :
- Imprimer les annexes pré-remplies
- Les signer à nouveau physiquement si nécessaire
- Les retourner avec le contrat vierge signé

---

## 🎯 Avantages de la nouvelle approche

### **1. Simplicité**
- ✅ Un seul bouton : "Soumettre la demande"
- ✅ Pas de confusion entre "contrat complet" et "annexes"
- ✅ Workflow linéaire et clair

### **2. Conformité**
- ✅ Utilise les PDFs officiels des SGI
- ✅ Contrats conformes aux modèles commerciaux
- ✅ Pas de risque de différence entre versions

### **3. Performance**
- ✅ Pas de génération HTML (plus rapide)
- ✅ Pas de fusion de PDFs
- ✅ Chargement direct des fichiers statiques

### **4. Flexibilité**
- ✅ Le client peut choisir d'utiliser les annexes pré-remplies ou de remplir le contrat vierge
- ✅ Les deux versions sont disponibles
- ✅ Facilite le traitement par la SGI

### **5. Maintenance**
- ✅ Pas de templates HTML à maintenir
- ✅ Mise à jour simple : remplacer le PDF commercial
- ✅ Un seul endroit pour les annexes (ReportLab)

---

## 🔄 Workflow utilisateur

### **Avant**
```
1. Remplir le formulaire
2. Remplir les annexes
3. Signer sur les annexes
4. Cliquer "Télécharger le contrat complet" (optionnel)
5. Cliquer "Soumettre la demande"
6. Recevoir les emails
```

### **Après**
```
1. Remplir le formulaire
2. Remplir les annexes
3. Signer sur les annexes
4. Cliquer "Soumettre la demande"
5. Recevoir les emails avec :
   - Contrat vierge commercial
   - Annexes pré-remplies
   - Photo + CNI
```

---

## 📝 Fichiers modifiés

### **Backend**
- `core/views.py` (24 lignes ajoutées, 10 supprimées)
  - Modification de `AccountOpeningRequestCreateView`
  - Chargement du contrat vierge commercial au lieu de génération HTML

### **Frontend**
- `src/pages/OpenAccountPage.tsx` (2 lignes ajoutées, 56 supprimées)
  - Suppression du bouton "Télécharger le contrat complet"
  - Suppression de la fonction `onPreview()`
  - Suppression de l'état `previewLoading`

---

## 🧪 Tests à effectuer

### **Test 1 : Soumission avec NSIA**
1. Sélectionner NSIA comme SGI
2. Remplir le formulaire
3. Remplir les annexes et signer
4. Cliquer "Soumettre la demande"
5. ✅ Vérifier l'email reçu contient :
   - `NSIA_Convention_Compte_Titres.pdf`
   - `Annexes_NSIA_[Nom].pdf`
   - Photo + CNI

### **Test 2 : Soumission avec GEK CAPITAL**
1. Sélectionner GEK CAPITAL comme SGI
2. Remplir le formulaire
3. Remplir les annexes et signer
4. Cliquer "Soumettre la demande"
5. ✅ Vérifier l'email reçu contient :
   - `GEK --Convention commerciale VF 2025.pdf`
   - `Annexes_GEK_CAPITAL_[Nom].pdf`
   - Photo + CNI

### **Test 3 : Vérifier les annexes pré-remplies**
1. Ouvrir `Annexes_[SGI]_[Nom].pdf`
2. ✅ Vérifier page 21 : Texte légal + Signatures
3. ✅ Vérifier page 22 : Formulaire avec données
4. ✅ Vérifier page 23 : Caractéristiques + Signature
5. ✅ Vérifier page 26 : Procuration + Signatures

### **Test 4 : Vérifier le contrat vierge**
1. Ouvrir `Contrat_[SGI]_[Nom].pdf`
2. ✅ Vérifier pages 1-20 : Conditions générales
3. ✅ Vérifier pages 21-26 : Annexes vierges (non remplies)

### **Test 5 : Interface simplifiée**
1. Ouvrir la page d'ouverture de compte
2. ✅ Vérifier qu'il n'y a PAS de bouton "Télécharger le contrat complet"
3. ✅ Vérifier qu'il y a un seul bouton "Soumettre la demande"
4. ✅ Vérifier que le bouton est bien centré et occupe toute la largeur

---

## 📝 Commits

```
55df324 - Use commercial blank contract instead of generated HTML contract
aa58752 - Remove full contract download button - only submit to send emails
```

---

## 🚀 Déploiement

### **Backend**
```bash
cd /var/www/xamila/xamila_backend
git pull origin master
sudo systemctl restart xamila
sudo systemctl status xamila
```

### **Frontend**
```bash
cd /var/www/xamila/xamila-public
git pull origin master
npm run build
sudo systemctl restart nginx
```

### **Vérification**
```bash
# Vérifier que les contrats vierges sont présents
ls -lh /var/www/xamila/xamila_backend/contracts/
# Devrait afficher :
# - NSIA_Convention_Compte_Titres.pdf
# - GEK --Convention commerciale VF 2025.pdf
```

---

## ✅ Résultat final

**Avant :**
- ❌ Génération HTML du contrat
- ❌ Fusion de PDFs
- ❌ Deux boutons (confusion)
- ❌ Contrat généré différent du contrat commercial

**Après :**
- ✅ Contrat vierge commercial (PDF officiel)
- ✅ Annexes pré-remplies (ReportLab)
- ✅ Un seul bouton (simplicité)
- ✅ Emails avec tous les documents
- ✅ Conformité totale avec les modèles commerciaux
- ✅ Workflow simplifié et clair

---

**La nouvelle approche est plus simple, plus rapide et plus conforme ! 🎉**

Les emails contiennent maintenant :
1. **Contrat vierge commercial** (pages 1-26 vierges)
2. **Annexes pré-remplies** (pages 21-26 avec données et signatures)
3. **Photo d'identité**
4. **CNI/Passeport**

Le client peut utiliser les annexes pré-remplies ou remplir le contrat vierge selon ses préférences !

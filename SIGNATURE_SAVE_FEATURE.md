# ✅ Fonctionnalité de sauvegarde des signatures - Implémentée

## 📋 Problème résolu

**Avant :** Les signatures des annexes n'étaient pas sauvegardées dans la base de données. Elles étaient uniquement utilisées pour générer le PDF mais perdues après.

**Maintenant :** Les signatures sont sauvegardées dans le champ `annex_data` du modèle `AccountOpeningRequest` et peuvent être récupérées ultérieurement.

---

## 🎯 Solution implémentée

### **Backend (Django)**

#### **1. Nouveau endpoint API**

**Route :** `POST /api/save-annex-signatures/`

**Fichier :** `core/views.py`

**Classe :** `SaveAnnexSignaturesView`

**Payload :**
```json
{
  "request_id": "uuid-de-la-demande",
  "annex_data": {
    "page21": {
      "signature_titulaire": "data:image/png;base64,...",
      "signature_gek": "data:image/png;base64,...",
      "place": "Abidjan",
      "date": "2025-11-24"
    },
    "page23": {
      "signature": "data:image/png;base64,...",
      "place": "Abidjan",
      "date": "2025-11-24"
    },
    "page26": {
      "signature_mandant": "data:image/png;base64,...",
      "signature_mandataire": "data:image/png;base64,..."
    }
  }
}
```

**Réponse :**
```json
{
  "success": true,
  "message": "Signatures sauvegardées avec succès",
  "request_id": "uuid-de-la-demande"
}
```

#### **2. Route ajoutée**

**Fichier :** `core/urls.py`

```python
path('save-annex-signatures/', views.SaveAnnexSignaturesView.as_view(), name='save-annex-signatures'),
```

#### **3. Logique de sauvegarde**

```python
# Récupérer la demande
aor = AccountOpeningRequest.objects.get(id=request_id)

# Initialiser annex_data si vide
if not aor.annex_data:
    aor.annex_data = {}

# Fusionner les nouvelles données avec les anciennes
aor.annex_data.update(annex_data)

# Sauvegarder
aor.save()
```

---

### **Frontend (React/TypeScript)**

#### **1. Nouvelle fonction API**

**Fichier :** `src/services/sgiApi.ts`

```typescript
async saveAnnexSignatures(payload: { request_id: string; annex_data: any }): Promise<any> {
  const res = await fetch(
    (process.env.REACT_APP_API_URL || '') + '/save-annex-signatures/',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    }
  );
  if (!res.ok) {
    let errorMsg = 'Échec sauvegarde signatures';
    try {
      const errorData = await res.json();
      errorMsg = errorData.error || errorData.detail || errorMsg;
    } catch (e) {
      errorMsg = `${errorMsg} (Status: ${res.status})`;
    }
    throw new Error(errorMsg);
  }
  return res.json();
}
```

#### **2. Fonction de sauvegarde dans OpenAccountPage**

**Fichier :** `src/pages/OpenAccountPage.tsx`

```typescript
const saveSignatures = async () => {
  if (!createdRequestId) {
    setMsg('❌ Veuillez d\'abord soumettre la demande');
    return;
  }
  try {
    setMsg(`⏳ Sauvegarde des signatures...`);
    const annexData = getAnnexData();
    
    await SGIApi.saveAnnexSignatures({
      request_id: createdRequestId,
      annex_data: annexData
    });
    
    setMsg(`✅ Signatures sauvegardées avec succès`);
  } catch (e: any) {
    console.error('Error saving signatures:', e);
    setMsg(`❌ Erreur: ${e.message || 'Impossible de sauvegarder les signatures'}`);
  }
};
```

#### **3. Bouton "Sauvegarder les signatures"**

**Position :** Après le bouton "📋 Annexes pré-remplies"

**Conditions d'affichage :**
- `createdRequestId` existe (demande soumise)
- `showAnnex` est true (annexes affichées)

```tsx
{createdRequestId && showAnnex && (
  <Button 
    type="button" 
    variant="contained" 
    color="warning"
    onClick={saveSignatures}
    startIcon={<SendIcon />}
    sx={{ fontWeight: 600 }}
  >
    💾 Sauvegarder les signatures
  </Button>
)}
```

---

## 🔄 Flux d'utilisation

### **Étape 1 : Remplir le formulaire**
L'utilisateur remplit le formulaire d'ouverture de compte et les informations des annexes.

### **Étape 2 : Soumettre la demande**
L'utilisateur clique sur "Soumettre la demande" → Un `createdRequestId` est généré.

### **Étape 3 : Afficher les annexes**
L'utilisateur clique sur "📋 Afficher les Annexes" → Les 4 pages d'annexes s'affichent.

### **Étape 4 : Signer les annexes**
L'utilisateur signe sur les pads de signature :
- **Page 21 :** Signature titulaire + Signature SGI
- **Page 23 :** Signature titulaire
- **Page 26 :** Signature mandant + Signature mandataire (si procuration)

### **Étape 5 : Sauvegarder les signatures**
L'utilisateur clique sur "💾 Sauvegarder les signatures" → Les signatures sont envoyées au backend et sauvegardées dans la base de données.

### **Étape 6 : Télécharger les annexes**
L'utilisateur clique sur "📋 Annexes pré-remplies" → Un PDF avec les signatures est généré et téléchargé.

---

## 📊 Données sauvegardées

Les signatures sont stockées au format **base64** dans le champ JSON `annex_data` :

```json
{
  "page21": {
    "place": "Abidjan",
    "date": "2025-11-24",
    "signature_titulaire": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "signature_gek": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  },
  "page22": {
    "account_number": "...",
    "last_name": "...",
    "first_names": "...",
    ...
  },
  "page23": {
    "place": "Abidjan",
    "date": "2025-11-24",
    "signature": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    ...
  },
  "page26": {
    "has_procuration": true,
    "signature_mandant": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "signature_mandataire": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    ...
  }
}
```

---

## 🧪 Tests

### **Test 1 : Sauvegarde des signatures**

1. Remplir le formulaire d'ouverture de compte
2. Soumettre la demande
3. Afficher les annexes
4. Signer sur les 3 pages (21, 23, 26)
5. Cliquer sur "💾 Sauvegarder les signatures"
6. ✅ Vérifier le message "Signatures sauvegardées avec succès"

### **Test 2 : Récupération des signatures**

1. Après sauvegarde, télécharger les annexes
2. ✅ Vérifier que les signatures apparaissent sur le PDF

### **Test 3 : Persistance en base de données**

```python
# Dans Django shell
from core.models import AccountOpeningRequest

aor = AccountOpeningRequest.objects.get(id='uuid-de-la-demande')
print(aor.annex_data)
# Devrait afficher les signatures en base64
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
# Ou déployer sur Netlify
```

---

## 📝 Commits

### **Backend**
```
68d92d7 - Add signature save functionality - new endpoint and button to persist annex signatures
```

### **Frontend**
```
[local] - Add save signatures button and API call in frontend
```

---

## ✅ Résultat

**Avant :**
- ❌ Signatures perdues après génération du PDF
- ❌ Impossible de régénérer les annexes avec les signatures
- ❌ Pas de persistance en base de données

**Après :**
- ✅ Signatures sauvegardées dans `annex_data`
- ✅ Bouton dédié "💾 Sauvegarder les signatures"
- ✅ Persistance en base de données
- ✅ Possibilité de régénérer les annexes avec les signatures
- ✅ Traçabilité complète des signatures

---

## 🎨 Interface utilisateur

Le bouton "💾 Sauvegarder les signatures" apparaît :
- **Couleur :** Orange (warning)
- **Position :** Après "📋 Annexes pré-remplies"
- **Icône :** 💾 (disquette)
- **Condition :** Visible uniquement après soumission de la demande et affichage des annexes

---

**Les signatures sont maintenant sauvegardées et persistantes ! 🎉**

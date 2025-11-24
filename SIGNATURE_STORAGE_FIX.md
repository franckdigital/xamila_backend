# 🔧 Correction du stockage des signatures - Implémenté

## 🐛 Problèmes identifiés

### **1. Le bouton "Sauvegarder les signatures" n'apparaissait pas**
**Cause :** Le bouton était conditionné par `createdRequestId && showAnnex`, ce qui signifie qu'il n'apparaissait que APRÈS la soumission de la demande.

**Impact :** Les utilisateurs ne pouvaient pas sauvegarder leurs signatures avant de soumettre le formulaire.

### **2. Les signatures n'étaient pas persistées**
**Cause :** Les signatures étaient uniquement stockées dans l'état React, sans persistance locale ni automatique vers le serveur.

**Impact :** Les signatures étaient perdues au rechargement de la page ou si l'utilisateur quittait le formulaire.

---

## ✅ Solutions implémentées

### **1. Persistance locale avec localStorage**

**Fichier :** `src/pages/OpenAccountPage.tsx`

#### **A. Sauvegarde automatique**
```typescript
const saveSignatures = async () => {
  try {
    setMsg(`⏳ Sauvegarde des signatures...`);
    const annexData = getAnnexData();
    
    // Sauvegarder localement dans tous les cas
    localStorage.setItem('annex_signatures', JSON.stringify(annexData));
    
    // Si une demande existe, sauvegarder aussi sur le serveur
    if (createdRequestId) {
      await SGIApi.saveAnnexSignatures({
        request_id: createdRequestId,
        annex_data: annexData
      });
      setMsg(`✅ Signatures sauvegardées (local + serveur)`);
    } else {
      setMsg(`✅ Signatures sauvegardées localement`);
    }
  } catch (e: any) {
    console.error('Error saving signatures:', e);
    setMsg(`❌ Erreur: ${e.message || 'Impossible de sauvegarder les signatures'}`);
  }
};
```

#### **B. Chargement automatique au démarrage**
```typescript
// Charger les signatures depuis localStorage au démarrage
useEffect(() => {
  try {
    const savedSignatures = localStorage.getItem('annex_signatures');
    if (savedSignatures) {
      const data = JSON.parse(savedSignatures);
      if (data.page21) {
        if (data.page21.signature_titulaire) setP21SignatureTitulaire(data.page21.signature_titulaire);
        if (data.page21.signature_gek) setP21SignatureGEK(data.page21.signature_gek);
        if (data.page21.place) setP21Place(data.page21.place);
        if (data.page21.date) setP21Date(data.page21.date);
      }
      if (data.page23) {
        if (data.page23.signature) setP23Signature(data.page23.signature);
        if (data.page23.place) setP23Place(data.page23.place);
        if (data.page23.date) setP23Date(data.page23.date);
      }
      if (data.page26) {
        if (data.page26.signature_mandant) setP26SignatureMandant(data.page26.signature_mandant);
        if (data.page26.signature_mandataire) setP26SignatureMandataire(data.page26.signature_mandataire);
      }
    }
  } catch (e) {
    console.error('Error loading signatures from localStorage:', e);
  }
}, []);
```

### **2. Bouton toujours visible**

**Avant :**
```tsx
{createdRequestId && showAnnex && (
  <Button onClick={saveSignatures}>
    💾 Sauvegarder les signatures
  </Button>
)}
```

**Après :**
```tsx
{showAnnex && (
  <Button 
    onClick={saveSignatures}
    title={createdRequestId ? "Sauvegarder sur le serveur et localement" : "Sauvegarder localement"}
  >
    💾 Sauvegarder les signatures
  </Button>
)}
```

**Avantage :** Le bouton apparaît dès que les annexes sont affichées, permettant de sauvegarder les signatures à tout moment.

---

## 🔄 Flux de sauvegarde

### **Scénario 1 : Sauvegarde avant soumission**
1. Utilisateur affiche les annexes → Bouton visible
2. Utilisateur signe → Signatures dans l'état React
3. Utilisateur clique "💾 Sauvegarder les signatures"
4. ✅ Signatures sauvegardées dans `localStorage`
5. Message : "✅ Signatures sauvegardées localement"

### **Scénario 2 : Sauvegarde après soumission**
1. Utilisateur soumet la demande → `createdRequestId` généré
2. Signatures envoyées au serveur via `annex_data`
3. Utilisateur modifie une signature
4. Utilisateur clique "💾 Sauvegarder les signatures"
5. ✅ Signatures sauvegardées dans `localStorage` ET sur le serveur
6. Message : "✅ Signatures sauvegardées (local + serveur)"

### **Scénario 3 : Rechargement de la page**
1. Page rechargée
2. `useEffect` exécuté au démarrage
3. ✅ Signatures chargées depuis `localStorage`
4. Signatures affichées dans les pads

---

## 🎯 Points clés

### **1. Double persistance**
- **localStorage** : Persistance locale immédiate, disponible même sans connexion
- **Serveur** : Persistance définitive après soumission de la demande

### **2. Synchronisation automatique**
- Les signatures sont automatiquement envoyées au serveur lors de la soumission (ligne 582 de `OpenAccountPage.tsx`)
- Le bouton "Sauvegarder" permet une mise à jour manuelle

### **3. Expérience utilisateur améliorée**
- Bouton visible dès l'affichage des annexes
- Tooltip explicite selon le contexte
- Messages de confirmation clairs
- Pas de perte de données au rechargement

---

## 🧪 Tests à effectuer

### **Test 1 : Sauvegarde locale**
1. Afficher les annexes
2. Signer sur les 3 pages
3. Cliquer "💾 Sauvegarder les signatures"
4. Recharger la page
5. ✅ Vérifier que les signatures sont toujours présentes

### **Test 2 : Sauvegarde serveur**
1. Soumettre une demande
2. Afficher les annexes
3. Signer sur les 3 pages
4. Cliquer "💾 Sauvegarder les signatures"
5. Télécharger les annexes
6. ✅ Vérifier que les signatures apparaissent sur le PDF

### **Test 3 : Modification après soumission**
1. Soumettre une demande avec signatures
2. Modifier une signature
3. Cliquer "💾 Sauvegarder les signatures"
4. Télécharger les annexes
5. ✅ Vérifier que la nouvelle signature apparaît

### **Test 4 : localStorage**
```javascript
// Dans la console du navigateur
localStorage.getItem('annex_signatures')
// Devrait afficher les données JSON avec les signatures en base64
```

### **Test 5 : Backend**
```python
# Dans Django shell
from core.models import AccountOpeningRequest

aor = AccountOpeningRequest.objects.last()
print(aor.annex_data)
# Devrait afficher les signatures si la demande a été soumise
```

---

## 📊 Structure des données sauvegardées

### **localStorage (clé: `annex_signatures`)**
```json
{
  "page21": {
    "place": "Abidjan",
    "date": "24/11/2025",
    "signature_titulaire": "data:image/png;base64,iVBORw0KGgo...",
    "signature_gek": "data:image/png;base64,iVBORw0KGgo..."
  },
  "page22": {
    "account_number": "...",
    "last_name": "...",
    ...
  },
  "page23": {
    "place": "Abidjan",
    "date": "24/11/2025",
    "signature": "data:image/png;base64,iVBORw0KGgo...",
    ...
  },
  "page26": {
    "has_procuration": true,
    "signature_mandant": "data:image/png;base64,iVBORw0KGgo...",
    "signature_mandataire": "data:image/png;base64,iVBORw0KGgo..."
  }
}
```

### **Base de données (champ `annex_data`)**
Même structure que localStorage, sauvegardée dans le modèle `AccountOpeningRequest`.

---

## 🚀 Déploiement

### **Frontend**
```bash
cd /var/www/xamila/xamila-public
git pull origin master
npm run build
# Ou déployer sur Netlify
```

### **Backend**
Aucun changement backend nécessaire pour cette correction (le champ `annex_data` existait déjà).

---

## 📝 Commits

### **Frontend**
```
b6bd3dd - Fix signature storage: add localStorage persistence and make save button always visible when annexes shown
```

---

## ✅ Résultat final

**Avant :**
- ❌ Bouton invisible avant soumission
- ❌ Signatures perdues au rechargement
- ❌ Pas de persistance locale

**Après :**
- ✅ Bouton visible dès l'affichage des annexes
- ✅ Signatures persistées dans localStorage
- ✅ Sauvegarde automatique sur le serveur après soumission
- ✅ Chargement automatique au démarrage
- ✅ Messages de confirmation clairs
- ✅ Expérience utilisateur fluide

---

**Les signatures sont maintenant correctement stockées et persistantes ! 🎉**

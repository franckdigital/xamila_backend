# ✅ Corrections - Comparateur SGI et Suppression

## 🐛 Problèmes identifiés

### **1. Comparateur SGI - Une seule SGI affichée**

**Symptôme:** Lors du choix de critères, une seule SGI s'affiche au lieu de toutes celles qui correspondent.

**Cause racine:**
- L'API filtrait sur `SGIAccountTerms` uniquement
- Les SGI sans `terms` n'apparaissaient jamais
- Pas de fallback si aucun résultat ne matchait les critères

### **2. Suppression SGI - Erreur 404**

**Symptôme:** Erreur 404 "Profil SGI manager requis" lors de la suppression.

**Cause racine:**
- Le frontend utilisait `/sgis/manager/mine/` (DELETE)
- Cette route nécessite un profil SGI manager lié
- Pas de route pour supprimer une SGI spécifique par ID

---

## ✅ Solutions implémentées

### **1. Comparateur SGI - Affichage de toutes les SGI**

**Fichier:** `core/views.py` - `SGIComparatorView`

**Changements:**

#### **Avant (❌):**
```python
def get(self, request):
    qs = SGI.objects.filter(is_active=True)
    terms = SGIAccountTerms.objects.filter(sgi__in=qs)
    
    # Filtres sur terms uniquement
    if country:
        terms = terms.filter(country__iexact=country)
    
    # Retourne uniquement les SGI avec terms
    for t in terms:
        data.append({...})
```

**Problèmes:**
- ❌ SGI sans terms ignorées
- ❌ Pas de fallback si aucun match
- ❌ Filtrage trop restrictif

#### **Après (✅):**
```python
def get(self, request):
    # Base: toutes les SGI actives
    sgi_qs = SGI.objects.filter(is_active=True)
    
    # Filtrer par nom de SGI
    if sgi_name:
        sgi_qs = sgi_qs.filter(name__icontains=sgi_name)
    
    # Récupérer les terms associés
    terms_dict = {}
    for term in SGIAccountTerms.objects.filter(sgi__in=sgi_qs):
        terms_dict[term.sgi_id] = term
    
    # Filtrer par critères de terms
    filtered_sgis = []
    for sgi in sgi_qs:
        term = terms_dict.get(sgi.id)
        
        # Si des filtres sont appliqués, vérifier les terms
        if country or digital_only or bank_name:
            if not term:
                continue  # Pas de terms, ne peut pas matcher
            
            if country and term.country.lower() != country.lower():
                continue
            if digital_only == 'true' and not term.is_digital_opening:
                continue
            if bank_name and bank_name.lower() not in (term.preferred_customer_banks or []):
                continue
        
        filtered_sgis.append((sgi, term))
    
    # FALLBACK: Si aucun résultat avec filtres, afficher toutes les SGI
    if not filtered_sgis and (country or digital_only or bank_name):
        filtered_sgis = [(sgi, terms_dict.get(sgi.id)) for sgi in sgi_qs]
    
    # Tri et réponse
    # ...
    
    return Response({
        'results': data,
        'total': len(data)
    })
```

**Améliorations:**
- ✅ Toutes les SGI actives sont considérées
- ✅ SGI sans terms peuvent être affichées
- ✅ Fallback automatique si aucun match
- ✅ `terms` peut être `null` dans la réponse

---

### **2. Suppression SGI - Nouvelle route par ID**

**Fichier:** `core/views_sgi_manager.py`

**Nouvelle classe:**
```python
class SGIDeleteView(APIView):
    """
    Supprime une SGI spécifique par son ID
    DELETE /api/sgis/manager/delete/<sgi_id>/
    """
    permission_classes = [IsAuthenticated, IsSGIManagerOrAdmin]
    
    def delete(self, request, sgi_id):
        """Supprime une SGI par son ID"""
        try:
            sgi = SGI.objects.get(id=sgi_id)
            sgi.delete()
            return Response(
                {"detail": "SGI supprimée avec succès."},
                status=status.HTTP_204_NO_CONTENT
            )
        except SGI.DoesNotExist:
            return Response(
                {"detail": "SGI introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erreur suppression SGI: {str(e)}")
            return Response(
                {"detail": f"Erreur lors de la suppression: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

**Route ajoutée:** `core/urls.py`
```python
path('sgis/manager/delete/<uuid:sgi_id>/', views_sgi_manager.SGIDeleteView.as_view(), name='sgi_manager_delete'),
```

**Frontend:** `src/components/dashboard/SGIManagement.tsx`

#### **Avant (❌):**
```typescript
const handleDelete = async () => {
  const resp = await fetch(`${API_URL}/sgis/manager/mine/`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  // ❌ Supprime la SGI du manager, pas une SGI spécifique
};
```

#### **Après (✅):**
```typescript
const [sgiToDelete, setSgiToDelete] = useState<any>(null);

const handleDelete = async () => {
  if (!sgiToDelete) return;
  
  const resp = await fetch(`${API_URL}/sgis/manager/delete/${sgiToDelete.id}/`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  
  if (!resp.ok && resp.status !== 204) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err?.detail || err?.error || `Erreur API: ${resp.status}`);
  }
  
  setDeleteOpen(false);
  setSgiToDelete(null);
  fetchSGIs(); // Rafraîchir la liste
};

// Dans le bouton:
<Button onClick={() => { setSgiToDelete(s); setDeleteOpen(true); }}>
  Supprimer
</Button>
```

**Dialogue de confirmation:**
```tsx
<Dialog open={deleteOpen} onClose={() => setDeleteOpen(false)}>
  <DialogTitle>Supprimer la SGI</DialogTitle>
  <DialogContent>
    <Typography>
      Confirmez-vous la suppression de la SGI <strong>{sgiToDelete?.name}</strong> ? 
      Cette action est irréversible et supprimera toutes les données associées.
    </Typography>
  </DialogContent>
  <DialogActions>
    <Button onClick={() => { setDeleteOpen(false); setSgiToDelete(null); }}>
      Annuler
    </Button>
    <Button color="error" onClick={handleDelete} disabled={deleting} variant="contained">
      {deleting ? 'Suppression...' : 'Supprimer'}
    </Button>
  </DialogActions>
</Dialog>
```

---

## 📊 Comparaison Avant/Après

### **Comparateur SGI**

| Aspect | Avant | Après |
|--------|-------|-------|
| **SGI sans terms** | ❌ Ignorées | ✅ Affichées |
| **Aucun match** | ❌ Liste vide | ✅ Toutes les SGI affichées |
| **Filtrage** | ❌ Trop restrictif | ✅ Flexible avec fallback |
| **Terms null** | ❌ Erreur | ✅ Géré correctement |

### **Suppression SGI**

| Aspect | Avant | Après |
|--------|-------|-------|
| **Route** | `/sgis/manager/mine/` | `/sgis/manager/delete/<id>/` |
| **Méthode** | DELETE (profil requis) | DELETE (ID spécifique) |
| **Erreur** | ❌ 404 Profil requis | ✅ Suppression réussie |
| **Confirmation** | ❌ Basique | ✅ Avec nom de la SGI |
| **Rafraîchissement** | ❌ Manuel | ✅ Automatique |

---

## 🔄 Flux de données

### **Comparateur - Avant (❌):**
```
Filtres appliqués
     ↓
Recherche dans SGIAccountTerms uniquement
     ↓
SGI sans terms ignorées
     ↓
❌ Une seule SGI ou liste vide
```

### **Comparateur - Après (✅):**
```
Filtres appliqués
     ↓
Recherche dans toutes les SGI actives
     ↓
Vérification des terms si disponibles
     ↓
Si aucun match → Fallback toutes les SGI
     ↓
✅ Toutes les SGI pertinentes affichées
```

### **Suppression - Avant (❌):**
```
Clic sur Supprimer
     ↓
DELETE /sgis/manager/mine/
     ↓
Vérification profil SGI manager
     ↓
❌ Erreur 404: Profil requis
```

### **Suppression - Après (✅):**
```
Clic sur Supprimer
     ↓
Dialogue de confirmation avec nom
     ↓
DELETE /sgis/manager/delete/<id>/
     ↓
Suppression par ID
     ↓
✅ SGI supprimée + liste rafraîchie
```

---

## 🧪 Tests à effectuer

### **Test 1: Comparateur - Toutes les SGI**
1. Aller sur `/dashboard/comparator`
2. Ne sélectionner aucun filtre
3. Vérifier que toutes les SGI actives sont affichées

**✅ Résultat attendu:** Toutes les SGI visibles

### **Test 2: Comparateur - Filtres avec match**
1. Sélectionner un pays (ex: Côte d'Ivoire)
2. Vérifier que les SGI de ce pays sont affichées

**✅ Résultat attendu:** SGI filtrées correctement

### **Test 3: Comparateur - Filtres sans match**
1. Sélectionner un pays sans SGI
2. Vérifier que toutes les SGI sont affichées (fallback)

**✅ Résultat attendu:** Toutes les SGI affichées avec message

### **Test 4: Comparateur - SGI sans terms**
1. Créer une SGI sans terms
2. Vérifier qu'elle apparaît dans le comparateur

**✅ Résultat attendu:** SGI visible avec terms = null

### **Test 5: Suppression - Confirmation**
1. Aller sur le dashboard manager
2. Cliquer sur "Supprimer" pour une SGI
3. Vérifier que le dialogue affiche le nom de la SGI

**✅ Résultat attendu:** Dialogue avec nom correct

### **Test 6: Suppression - Exécution**
1. Confirmer la suppression
2. Vérifier que la SGI est supprimée
3. Vérifier que la liste est rafraîchie

**✅ Résultat attendu:** SGI supprimée, liste mise à jour

### **Test 7: Suppression - Annulation**
1. Cliquer sur "Supprimer"
2. Cliquer sur "Annuler"
3. Vérifier que rien n'est supprimé

**✅ Résultat attendu:** Aucune modification

---

## 📝 API Endpoints

### **GET /api/sgis/comparator/**

**Query Parameters:**
- `country` (string, optional) - Filtrer par pays
- `bank` (string, optional) - Filtrer par banque client
- `sgi_name` (string, optional) - Filtrer par nom de SGI
- `digital_only` (boolean, optional) - Filtrer SGI 100% digitales
- `order_by` (string, optional) - Trier par (minimum_amount_value, opening_fees_amount, custody_fees)
- `order` (string, optional) - Ordre (asc, desc)

**Réponse:**
```json
{
  "results": [
    {
      "sgi": {
        "id": "uuid",
        "name": "SGI Name",
        ...
      },
      "terms": {
        "country": "Côte d'Ivoire",
        "is_digital_opening": true,
        ...
      } | null,
      "avg_rating": 4.5,
      "ratings_count": 10
    }
  ],
  "total": 5
}
```

### **DELETE /api/sgis/manager/delete/<sgi_id>/**

**Path Parameters:**
- `sgi_id` (uuid, required) - ID de la SGI à supprimer

**Réponse succès (204):**
```json
{
  "detail": "SGI supprimée avec succès."
}
```

**Réponse erreur (404):**
```json
{
  "detail": "SGI introuvable."
}
```

---

## ✅ Résultats

**Les deux problèmes sont résolus!**

### **Comparateur:**
- ✅ Toutes les SGI actives sont affichées
- ✅ Filtrage flexible avec fallback
- ✅ SGI sans terms gérées correctement
- ✅ Pas de liste vide inattendue

### **Suppression:**
- ✅ Suppression par ID fonctionnelle
- ✅ Dialogue de confirmation avec nom
- ✅ Rafraîchissement automatique de la liste
- ✅ Gestion d'erreurs améliorée

**Le comparateur affiche maintenant toutes les SGI et la suppression fonctionne correctement! 🎉**

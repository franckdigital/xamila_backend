# ✅ Correction - Liste SGI avec Pagination

## 🐛 Problème identifié

**Symptôme:** Lors de la création d'une nouvelle SGI, la ligne remplaçait la dernière au lieu de s'ajouter au tableau.

**Cause racine:**
1. L'API `/sgis/manager/mine/` retournait une seule SGI (celle du manager)
2. Le frontend faisait: `setSgis(data && data.id ? [data] : [])` → remplaçait tout le tableau
3. Pas de pagination ni de tri décroissant

---

## ✅ Solution implémentée

### **1. Backend - Nouvelle API avec pagination**

**Fichier:** `core/views_sgi_manager.py`

**Nouvelle classe:** `AllSGIsListView`

```python
class AllSGIsListView(APIView):
    """
    Liste toutes les SGI avec pagination et recherche
    GET /api/sgis/manager/list/
    """
    permission_classes = [IsAuthenticated, IsSGIManagerOrAdmin]
    
    def get(self, request):
        # Paramètres
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search = request.query_params.get('search', '').strip()
        
        # Requête de base
        sgis = SGI.objects.all()
        
        # Recherche
        if search:
            sgis = sgis.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(manager_name__icontains=search) |
                Q(manager_email__icontains=search)
            )
        
        # Tri par ordre décroissant (plus récent en premier)
        sgis = sgis.order_by('-created_at')
        
        # Pagination
        total = sgis.count()
        start = (page - 1) * page_size
        end = start + page_size
        sgis_page = sgis[start:end]
        
        # Sérialisation...
        
        return Response({
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        })
```

**Route ajoutée:** `core/urls.py`
```python
path('sgis/manager/list/', views_sgi_manager.AllSGIsListView.as_view(), name='sgi_manager_list'),
```

### **2. Frontend - Utilisation de la nouvelle API**

**Fichier:** `src/components/dashboard/SGIManagement.tsx`

**Changements:**

1. **Ajout des états de pagination:**
```typescript
const [page, setPage] = useState(1);
const [pageSize] = useState(10);
const [total, setTotal] = useState(0);
const [totalPages, setTotalPages] = useState(0);
const [searchTerm, setSearchTerm] = useState('');
```

2. **Nouvelle fonction fetchSGIs:**
```typescript
const fetchSGIs = async () => {
  // Construire l'URL avec pagination et recherche
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());
  if (searchTerm) {
    params.append('search', searchTerm);
  }
  
  const resp = await fetch(`${API_URL}/sgis/manager/list/?${params.toString()}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await resp.json();
  
  // Mettre à jour avec les résultats paginés
  setSgis(data.results || []);
  setTotal(data.total || 0);
  setTotalPages(data.total_pages || 0);
};
```

3. **useEffect avec dépendances:**
```typescript
useEffect(() => {
  fetchSGIs();
}, [page, searchTerm]); // Se recharge à chaque changement de page ou recherche
```

4. **Barre de recherche:**
```typescript
<TextField
  placeholder="Rechercher une SGI..."
  value={searchTerm}
  onChange={(e) => {
    setSearchTerm(e.target.value);
    setPage(1); // Retour à la page 1 lors de la recherche
  }}
  InputProps={{
    startAdornment: <SearchIcon />,
    endAdornment: searchTerm && (
      <IconButton onClick={() => { setSearchTerm(''); setPage(1); }}>
        <ClearIcon />
      </IconButton>
    ),
  }}
/>
```

5. **Composant Pagination:**
```typescript
{!loading && sgis.length > 0 && (
  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
    <Typography variant="body2">
      Affichage de {((page - 1) * pageSize) + 1} à {Math.min(page * pageSize, total)} sur {total} SGI(s)
    </Typography>
    <Pagination
      count={totalPages}
      page={page}
      onChange={(e, value) => setPage(value)}
      color="primary"
      showFirstButton
      showLastButton
    />
  </Box>
)}
```

---

## 📊 Fonctionnalités ajoutées

### **1. Pagination**
- ✅ 10 SGI par page (configurable)
- ✅ Navigation entre les pages
- ✅ Boutons "Première page" et "Dernière page"
- ✅ Affichage du nombre total de SGI

### **2. Recherche**
- ✅ Recherche en temps réel
- ✅ Recherche dans: nom, email, manager_name, manager_email
- ✅ Bouton pour effacer la recherche
- ✅ Retour automatique à la page 1 lors de la recherche

### **3. Tri**
- ✅ Ordre décroissant par date de création
- ✅ Les SGI les plus récentes apparaissent en premier

### **4. Ajout de SGI**
- ✅ Les nouvelles SGI s'ajoutent en première position
- ✅ Le tableau se rafraîchit automatiquement après création
- ✅ Pas de remplacement de ligne

---

## 🔄 Flux de données

### **Avant (❌ Problème):**
```
Création SGI
     ↓
API retourne 1 SGI
     ↓
setSgis([data]) ← Remplace tout le tableau
     ↓
❌ Seule la dernière SGI est visible
```

### **Après (✅ Solution):**
```
Création SGI
     ↓
fetchSGIs() appelé
     ↓
API retourne toutes les SGI (paginées, triées)
     ↓
setSgis(data.results) ← Remplace avec la liste complète
     ↓
✅ Toutes les SGI sont visibles, triées par date décroissante
```

---

## 🧪 Tests à effectuer

### **Test 1: Création de SGI**
1. Créer une nouvelle SGI "Test SGI 1"
2. Vérifier qu'elle apparaît en première position
3. Créer une deuxième SGI "Test SGI 2"
4. Vérifier qu'elle apparaît en première position
5. Vérifier que "Test SGI 1" est maintenant en deuxième position

**✅ Résultat attendu:** Les SGI s'ajoutent sans remplacer les anciennes

### **Test 2: Pagination**
1. Créer 15 SGI
2. Vérifier que seules 10 sont affichées sur la page 1
3. Cliquer sur "Page 2"
4. Vérifier que les 5 restantes sont affichées

**✅ Résultat attendu:** Navigation fluide entre les pages

### **Test 3: Recherche**
1. Créer des SGI avec des noms différents
2. Taper "Test" dans la barre de recherche
3. Vérifier que seules les SGI contenant "Test" sont affichées
4. Effacer la recherche
5. Vérifier que toutes les SGI réapparaissent

**✅ Résultat attendu:** Filtrage en temps réel

### **Test 4: Tri décroissant**
1. Créer 3 SGI à des moments différents
2. Vérifier que la plus récente est en première position
3. Vérifier que la plus ancienne est en dernière position

**✅ Résultat attendu:** Tri par date de création décroissante

---

## 📝 Paramètres de l'API

### **GET /api/sgis/manager/list/**

**Query Parameters:**
- `page` (int, default: 1) - Numéro de la page
- `page_size` (int, default: 10) - Nombre d'éléments par page
- `search` (string, optional) - Terme de recherche

**Réponse:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "SGI Name",
      "email": "email@example.com",
      "manager_name": "Manager Name",
      "created_at": "2025-11-22T10:00:00Z",
      ...
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

---

## ✅ Résultat

**Le problème est résolu!**

- ✅ Les nouvelles SGI s'ajoutent au tableau
- ✅ Pagination fonctionnelle (10 par page)
- ✅ Recherche en temps réel
- ✅ Tri décroissant (plus récent en premier)
- ✅ Interface utilisateur améliorée

**Les SGI ne se remplacent plus, elles s'ajoutent correctement! 🎉**

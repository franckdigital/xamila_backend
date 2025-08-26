from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Q
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from .models_bilans import FluxFinancier, BilanFinancier
from .serializers_bilans import FluxFinancierSerializer, BilanFinancierSerializer, BilanCalculeSerializer

logger = logging.getLogger(__name__)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def flux_financiers_list(request):
    """Liste et création des flux financiers de l'utilisateur"""
    
    if request.method == 'GET':
        # Récupérer les flux de l'utilisateur
        flux = FluxFinancier.objects.filter(user=request.user)
        
        # Filtres optionnels
        type_filter = request.GET.get('type')
        if type_filter in ['revenus', 'depenses']:
            flux = flux.filter(type=type_filter)
        
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        if date_debut:
            flux = flux.filter(date__gte=date_debut)
        if date_fin:
            flux = flux.filter(date__lte=date_fin)
        
        serializer = FluxFinancierSerializer(flux, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Créer un nouveau flux
        serializer = FluxFinancierSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Nouveau flux créé pour {request.user.email}: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def flux_financier_detail(request, flux_id):
    """Détail, modification et suppression d'un flux financier"""
    
    try:
        flux = FluxFinancier.objects.get(id=flux_id, user=request.user)
    except FluxFinancier.DoesNotExist:
        return Response({'error': 'Flux financier non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = FluxFinancierSerializer(flux)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = FluxFinancierSerializer(flux, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        flux.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bilan_calcule(request):
    """Calcule et retourne le bilan financier dynamique"""
    
    user = request.user
    
    # Paramètres de période (par défaut: mois actuel)
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if not date_debut:
        # Premier jour du mois actuel
        today = date.today()
        date_debut = today.replace(day=1)
    else:
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    
    if not date_fin:
        # Dernier jour du mois actuel
        today = date.today()
        if today.month == 12:
            date_fin = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            date_fin = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Récupérer les flux de la période
    flux = FluxFinancier.objects.filter(
        user=user,
        date__gte=date_debut,
        date__lte=date_fin
    )
    
    # Calculer les totaux
    total_revenus = flux.filter(type='revenus').aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0')
    
    total_depenses = flux.filter(type='depenses').aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0')
    
    solde = total_revenus - total_depenses
    
    # Générer les suggestions
    suggestions = generer_suggestions(total_revenus, total_depenses, solde, flux)
    
    # Analyse par catégorie
    flux_par_categorie = {}
    for type_flux in ['revenus', 'depenses']:
        flux_type = flux.filter(type=type_flux)
        categories = flux_type.values('categorie').annotate(
            total=Sum('montant')
        ).order_by('-total')
        flux_par_categorie[type_flux] = list(categories)
    
    # Préparer la réponse
    bilan_data = {
        'total_revenus': total_revenus,
        'total_depenses': total_depenses,
        'solde': solde,
        'suggestions': suggestions,
        'flux_par_categorie': flux_par_categorie,
        'periode_debut': date_debut,
        'periode_fin': date_fin
    }
    
    serializer = BilanCalculeSerializer(bilan_data)
    return Response(serializer.data)

def generer_suggestions(total_revenus, total_depenses, solde, flux):
    """Génère des suggestions personnalisées basées sur le bilan"""
    suggestions = []
    
    if solde > 0:
        suggestions.append({
            'type': 'epargne',
            'titre': 'Optimisez votre épargne',
            'description': f'Avec un solde positif de {solde:,.0f} FCFA, vous pourriez épargner 20% de ce montant chaque mois.',
            'impact': 'eleve'
        })
        
        if solde > 50000:
            suggestions.append({
                'type': 'investissement',
                'titre': 'Investissement en bourse',
                'description': 'Considérez investir une partie de votre épargne en actions ou obligations pour faire fructifier votre capital.',
                'impact': 'eleve'
            })
    
    elif solde < 0:
        suggestions.append({
            'type': 'optimisation',
            'titre': 'Réduisez vos dépenses',
            'description': f'Votre solde est négatif de {abs(solde):,.0f} FCFA. Analysez vos dépenses pour identifier des économies possibles.',
            'impact': 'eleve'
        })
    
    # Analyse des dépenses de logement
    if total_revenus > 0:
        depenses_logement = flux.filter(
            type='depenses', 
            categorie__icontains='logement'
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
        
        ratio_logement = (depenses_logement / total_revenus) * 100
        if ratio_logement > 30:
            suggestions.append({
                'type': 'optimisation',
                'titre': 'Réduisez vos frais de logement',
                'description': f'Vos frais de logement représentent {ratio_logement:.1f}% de vos revenus. L\'idéal est de rester sous 30%.',
                'impact': 'moyen'
            })
    
    # Suggestion d'épargne d'urgence
    if total_revenus > 0:
        epargne_urgence_recommandee = total_revenus * 3  # 3 mois de revenus
        if solde < epargne_urgence_recommandee:
            suggestions.append({
                'type': 'epargne',
                'titre': 'Constituez une épargne d\'urgence',
                'description': f'Visez une épargne d\'urgence de {epargne_urgence_recommandee:,.0f} FCFA (3 mois de revenus).',
                'impact': 'moyen'
            })
    
    return suggestions

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def categories_disponibles(request):
    """Retourne les catégories disponibles pour les flux financiers"""
    
    categories = {
        'revenus': [
            {'value': 'Salaire', 'label': 'Salaire'},
            {'value': 'Freelance', 'label': 'Freelance'},
            {'value': 'Investissements', 'label': 'Investissements'},
            {'value': 'Autres revenus', 'label': 'Autres revenus'},
        ],
        'depenses': [
            {'value': 'Logement', 'label': 'Logement'},
            {'value': 'Alimentation', 'label': 'Alimentation'},
            {'value': 'Transport', 'label': 'Transport'},
            {'value': 'Loisirs', 'label': 'Loisirs'},
            {'value': 'Santé', 'label': 'Santé'},
            {'value': 'Autres', 'label': 'Autres'},
        ]
    }
    
    return Response(categories)

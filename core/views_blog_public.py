# -*- coding: utf-8 -*-
"""
Vues API publiques pour le blog XAMILA (Actualités)
Accès public pour la lecture des articles
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers

from .models import Actualites, Categorie, SousCategorie, Banniere


class PublicBlogPagination(PageNumberPagination):
    """Pagination pour les APIs publiques du blog"""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50


# ===== SERIALIZERS PUBLICS =====

class PublicCategorieSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'slug', 'description', 'image', 'articles_count']
    
    def get_articles_count(self, obj):
        return obj.actualites_set.filter(statut='PUBLISHED').count()


class PublicSousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields = ['id', 'nom', 'slug', 'description']


class PublicBanniereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banniere
        fields = ['id', 'nom', 'image', 'position', 'largeur', 'hauteur', 'lien']


class PublicActualitesListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des articles publics"""
    auteur_nom = serializers.CharField(source='auteur.get_full_name', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)
    temps_lecture_minutes = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    
    class Meta:
        model = Actualites
        fields = [
            'id', 'titre', 'slug', 'description', 'excerpt', 'image', 
            'auteur_nom', 'categorie_nom', 'sous_categorie_nom', 
            'date_publication', 'is_featured', 'vues', 'temps_lecture_minutes',
            'acces'
        ]
    
    def get_temps_lecture_minutes(self, obj):
        if obj.temps_lecture_estime:
            return int(obj.temps_lecture_estime.total_seconds() / 60)
        return 5  # Valeur par défaut
    
    def get_excerpt(self, obj):
        """Extrait du contenu pour l'aperçu"""
        if obj.contenu:
            # Supprime les balises HTML et limite à 150 caractères
            import re
            clean_content = re.sub(r'<[^>]+>', '', obj.contenu)
            return clean_content[:150] + '...' if len(clean_content) > 150 else clean_content
        return obj.description


class PublicActualitesDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'un article public"""
    auteur_nom = serializers.CharField(source='auteur.get_full_name', read_only=True)
    categorie = PublicCategorieSerializer(read_only=True)
    sous_categorie = PublicSousCategorieSerializer(read_only=True)
    temps_lecture_minutes = serializers.SerializerMethodField()
    bannieres = serializers.SerializerMethodField()
    articles_similaires = serializers.SerializerMethodField()
    
    class Meta:
        model = Actualites
        fields = [
            'id', 'titre', 'slug', 'description', 'contenu', 'image',
            'auteur_nom', 'categorie', 'sous_categorie', 'date_publication',
            'is_featured', 'vues', 'temps_lecture_minutes', 'acces',
            'meta_title', 'meta_description', 'bannieres', 'articles_similaires'
        ]
    
    def get_temps_lecture_minutes(self, obj):
        if obj.temps_lecture_estime:
            return int(obj.temps_lecture_estime.total_seconds() / 60)
        return 5
    
    def get_bannieres(self, obj):
        """Récupère les bannières associées à l'article"""
        bannieres = {}
        if obj.banniere_haut:
            bannieres['haut'] = PublicBanniereSerializer(obj.banniere_haut).data
        if obj.banniere_bas:
            bannieres['bas'] = PublicBanniereSerializer(obj.banniere_bas).data
        if obj.banniere_droite:
            bannieres['droite'] = PublicBanniereSerializer(obj.banniere_droite).data
        if obj.banniere_gauche:
            bannieres['gauche'] = PublicBanniereSerializer(obj.banniere_gauche).data
        return bannieres
    
    def get_articles_similaires(self, obj):
        """Articles similaires de la même catégorie"""
        articles_similaires = Actualites.objects.filter(
            categorie=obj.categorie,
            statut='PUBLISHED'
        ).exclude(id=obj.id).order_by('-date_publication')[:3]
        
        return PublicActualitesListSerializer(articles_similaires, many=True).data


# ===== VUES API PUBLIQUES =====

class PublicCategorieListView(ListAPIView):
    """
    Liste des catégories publiques
    GET /api/public/blog/categories/
    """
    queryset = Categorie.objects.filter(is_active=True).order_by('ordre', 'nom')
    serializer_class = PublicCategorieSerializer
    permission_classes = [permissions.AllowAny]


class PublicActualitesListView(ListAPIView):
    """
    Liste des articles publics avec filtres
    GET /api/public/blog/actualites/
    """
    serializer_class = PublicActualitesListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = PublicBlogPagination
    
    def get_queryset(self):
        queryset = Actualites.objects.filter(
            statut='PUBLISHED'
        ).select_related(
            'auteur', 'categorie', 'sous_categorie'
        ).order_by('-date_publication')
        
        # Filtres
        categorie = self.request.query_params.get('categorie', None)
        sous_categorie = self.request.query_params.get('sous_categorie', None)
        acces = self.request.query_params.get('acces', None)
        is_featured = self.request.query_params.get('is_featured', None)
        search = self.request.query_params.get('search', None)
        
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
        if sous_categorie:
            queryset = queryset.filter(sous_categorie_id=sous_categorie)
        if acces:
            queryset = queryset.filter(acces=acces)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(titre__icontains=search) | 
                Q(description__icontains=search) |
                Q(contenu__icontains=search)
            )
            
        return queryset


class PublicActualitesDetailView(RetrieveAPIView):
    """
    Détail d'un article public
    GET /api/public/blog/actualites/{slug}/
    """
    queryset = Actualites.objects.filter(statut='PUBLISHED').select_related(
        'auteur', 'categorie', 'sous_categorie'
    )
    serializer_class = PublicActualitesDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Incrémenter le nombre de vues
        instance.vues += 1
        instance.save(update_fields=['vues'])
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PublicActualitesFeaturedView(ListAPIView):
    """
    Articles à la une
    GET /api/public/blog/actualites/featured/
    """
    queryset = Actualites.objects.filter(
        statut='PUBLISHED',
        is_featured=True
    ).select_related(
        'auteur', 'categorie', 'sous_categorie'
    ).order_by('-date_publication')[:6]
    
    serializer_class = PublicActualitesListSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_blog_stats(request):
    """
    Statistiques publiques du blog
    GET /api/public/blog/stats/
    """
    try:
        stats = {
            'total_articles': Actualites.objects.filter(statut='PUBLISHED').count(),
            'categories': Categorie.objects.filter(is_active=True).count(),
            'articles_featured': Actualites.objects.filter(
                statut='PUBLISHED', is_featured=True
            ).count(),
            'total_views': Actualites.objects.filter(
                statut='PUBLISHED'
            ).aggregate(total=Sum('vues'))['total'] or 0,
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

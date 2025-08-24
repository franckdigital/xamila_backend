# -*- coding: utf-8 -*-
"""
Vues API pour la gestion du blog XAMILA (Actualités)
Accès restreint aux administrateurs uniquement
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers

from .models import Actualites, Categorie, SousCategorie, Banniere, CommentaireArticle, LectureArticle
from .permissions import IsAdminUser


class BlogPagination(PageNumberPagination):
    """Pagination pour les APIs du blog"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===== SERIALIZERS =====

class CategorieSerializer(serializers.ModelSerializer):
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Categorie
        fields = '__all__'
    
    def get_articles_count(self, obj):
        return obj.actualites_set.filter(statut='PUBLISHED').count()


class SousCategorieSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    articles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SousCategorie
        fields = '__all__'
    
    def get_articles_count(self, obj):
        return obj.actualites_set.filter(statut='PUBLISHED').count()


class BanniereSerializer(serializers.ModelSerializer):
    taux_clic_calcule = serializers.SerializerMethodField()
    
    class Meta:
        model = Banniere
        fields = '__all__'
    
    def get_taux_clic_calcule(self, obj):
        if obj.impressions > 0:
            return round((obj.clics / obj.impressions) * 100, 2)
        return 0.0


class ActualitesSerializer(serializers.ModelSerializer):
    auteur_nom = serializers.CharField(source='auteur.get_full_name', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    sous_categorie_nom = serializers.CharField(source='sous_categorie.nom', read_only=True)
    temps_lecture_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = Actualites
        fields = '__all__'
        read_only_fields = ('slug', 'created_at', 'updated_at', 'vues', 'partages')
    
    def get_temps_lecture_minutes(self, obj):
        if obj.temps_lecture_estime:
            return obj.temps_lecture_estime.total_seconds() / 60
        return 0


class ActualitesListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes"""
    auteur_nom = serializers.CharField(source='auteur.get_full_name', read_only=True)
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    
    class Meta:
        model = Actualites
        fields = ['id', 'titre', 'slug', 'description', 'image', 'auteur_nom', 
                 'categorie_nom', 'statut', 'acces', 'date_publication', 
                 'is_featured', 'vues', 'created_at']


# ===== VUES API ADMIN =====

class AdminCategorieListCreateView(ListAPIView, CreateAPIView):
    """
    Liste et création des catégories
    GET/POST /api/admin/blog/categories/
    """
    queryset = Categorie.objects.all().order_by('ordre', 'nom')
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminUser]
    pagination_class = BlogPagination


class AdminCategorieDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Détail, modification et suppression d'une catégorie
    GET/PUT/DELETE /api/admin/blog/categories/{id}/
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer
    permission_classes = [IsAdminUser]


class AdminSousCategorieListCreateView(ListAPIView, CreateAPIView):
    """
    Liste et création des sous-catégories
    GET/POST /api/admin/blog/sous-categories/
    """
    queryset = SousCategorie.objects.all().order_by('categorie__nom', 'ordre', 'nom')
    serializer_class = SousCategorieSerializer
    permission_classes = [IsAdminUser]
    pagination_class = BlogPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        categorie_id = self.request.query_params.get('categorie', None)
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)
        return queryset


class AdminSousCategorieDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Détail, modification et suppression d'une sous-catégorie
    GET/PUT/DELETE /api/admin/blog/sous-categories/{id}/
    """
    queryset = SousCategorie.objects.all()
    serializer_class = SousCategorieSerializer
    permission_classes = [IsAdminUser]


class AdminBanniereListCreateView(ListAPIView, CreateAPIView):
    """
    Liste et création des bannières
    GET/POST /api/admin/blog/bannieres/
    """
    queryset = Banniere.objects.all().order_by('-created_at')
    serializer_class = BanniereSerializer
    permission_classes = [IsAdminUser]
    pagination_class = BlogPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        position = self.request.query_params.get('position', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if position:
            queryset = queryset.filter(position=position)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
            
        return queryset


class AdminBanniereDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Détail, modification et suppression d'une bannière
    GET/PUT/DELETE /api/admin/blog/bannieres/{id}/
    """
    queryset = Banniere.objects.all()
    serializer_class = BanniereSerializer
    permission_classes = [IsAdminUser]


class AdminActualitesListCreateView(ListAPIView, CreateAPIView):
    """
    Liste et création des articles
    GET/POST /api/admin/blog/actualites/
    """
    permission_classes = [IsAdminUser]
    pagination_class = BlogPagination
    
    def get_queryset(self):
        queryset = Actualites.objects.all().select_related(
            'auteur', 'categorie', 'sous_categorie'
        ).order_by('-created_at')
        
        # Filtres
        statut = self.request.query_params.get('statut', None)
        categorie = self.request.query_params.get('categorie', None)
        acces = self.request.query_params.get('acces', None)
        is_featured = self.request.query_params.get('is_featured', None)
        search = self.request.query_params.get('search', None)
        
        if statut:
            queryset = queryset.filter(statut=statut)
        if categorie:
            queryset = queryset.filter(categorie_id=categorie)
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
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ActualitesListSerializer
        return ActualitesSerializer
    
    def perform_create(self, serializer):
        serializer.save(auteur=self.request.user)


class AdminActualitesDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Détail, modification et suppression d'un article
    GET/PUT/DELETE /api/admin/blog/actualites/{id}/
    """
    queryset = Actualites.objects.all().select_related(
        'auteur', 'categorie', 'sous_categorie'
    )
    serializer_class = ActualitesSerializer
    permission_classes = [IsAdminUser]


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_actualites_publish(request, pk):
    """
    Publier un article
    POST /api/admin/blog/actualites/{id}/publish/
    """
    try:
        article = get_object_or_404(Actualites, pk=pk)
        
        if article.statut == 'DRAFT':
            article.statut = 'PUBLISHED'
            article.date_publication = timezone.now()
            article.save()
            
            return Response({
                'message': 'Article publié avec succès',
                'article': ActualitesSerializer(article).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'L\'article n\'est pas en brouillon'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_actualites_archive(request, pk):
    """
    Archiver un article
    POST /api/admin/blog/actualites/{id}/archive/
    """
    try:
        article = get_object_or_404(Actualites, pk=pk)
        
        article.statut = 'ARCHIVED'
        article.save()
        
        return Response({
            'message': 'Article archivé avec succès',
            'article': ActualitesSerializer(article).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_blog_stats(request):
    """
    Statistiques du blog
    GET /api/admin/blog/stats/
    """
    try:
        stats = {
            'articles': {
                'total': Actualites.objects.count(),
                'published': Actualites.objects.filter(statut='PUBLISHED').count(),
                'draft': Actualites.objects.filter(statut='DRAFT').count(),
                'archived': Actualites.objects.filter(statut='ARCHIVED').count(),
                'featured': Actualites.objects.filter(is_featured=True).count(),
                'premium': Actualites.objects.filter(acces='PREMIUM').count(),
            },
            'categories': {
                'total': Categorie.objects.count(),
                'with_articles': Categorie.objects.annotate(
                    articles_count=Count('actualites')
                ).filter(articles_count__gt=0).count(),
            },
            'bannieres': {
                'total': Banniere.objects.count(),
                'active': Banniere.objects.filter(is_active=True).count(),
                'by_position': {
                    position[0]: Banniere.objects.filter(
                        position=position[0], is_active=True
                    ).count()
                    for position in Banniere.POSITION_CHOICES
                },
            },
            'engagement': {
                'total_views': Actualites.objects.aggregate(
                    total=Sum('vues')
                )['total'] or 0,
                'total_shares': Actualites.objects.aggregate(
                    total=Sum('partages')
                )['total'] or 0,
                'avg_reading_time': Actualites.objects.aggregate(
                    avg=Avg('temps_lecture_estime')
                )['avg'] or 0,
            }
        }
        
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models_blog import (
    Categorie, SousCategorie, Banniere, Actualites, 
    CommentaireArticle, LectureArticle
)


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug', 'ordre', 'nb_articles', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nom', 'description']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['ordre', 'nom']
    
    def nb_articles(self, obj):
        return obj.articles.count()
    nb_articles.short_description = 'Nb articles'


@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'slug', 'ordre', 'nb_articles', 'is_active']
    list_filter = ['categorie', 'is_active', 'created_at']
    search_fields = ['nom', 'description', 'categorie__nom']
    prepopulated_fields = {'slug': ('nom',)}
    ordering = ['categorie', 'ordre', 'nom']
    
    def nb_articles(self, obj):
        return obj.articles.count()
    nb_articles.short_description = 'Nb articles'


@admin.register(Banniere)
class BanniereAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'position', 'dimensions', 'annonceur', 
        'periode_affichage', 'statistiques', 'is_active'
    ]
    list_filter = ['position', 'is_active', 'date_debut', 'date_fin']
    search_fields = ['nom', 'annonceur']
    readonly_fields = ['nb_impressions', 'nb_clics', 'taux_clic_display']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'image', 'lien', 'annonceur', 'prix')
        }),
        ('Position et dimensions', {
            'fields': ('position', 'largeur', 'hauteur')
        }),
        ('Période d\'affichage', {
            'fields': ('date_debut', 'date_fin', 'is_active')
        }),
        ('Statistiques', {
            'fields': ('nb_impressions', 'nb_clics', 'taux_clic_display'),
            'classes': ('collapse',)
        }),
    )
    
    def dimensions(self, obj):
        return f"{obj.largeur}x{obj.hauteur}px"
    dimensions.short_description = 'Dimensions'
    
    def periode_affichage(self, obj):
        return f"{obj.date_debut.strftime('%d/%m/%Y')} - {obj.date_fin.strftime('%d/%m/%Y')}"
    periode_affichage.short_description = 'Période'
    
    def statistiques(self, obj):
        return f"{obj.nb_impressions} vues / {obj.nb_clics} clics ({obj.taux_clic:.1f}%)"
    statistiques.short_description = 'Stats'
    
    def taux_clic_display(self, obj):
        return f"{obj.taux_clic:.2f}%"
    taux_clic_display.short_description = 'Taux de clic'


class CommentaireInline(admin.TabularInline):
    model = CommentaireArticle
    extra = 0
    readonly_fields = ['auteur', 'created_at']
    fields = ['auteur', 'contenu', 'statut', 'created_at']


@admin.register(Actualites)
class ActualitesAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'auteur', 'categorie', 'acces_display', 
        'statut', 'date_publication', 'nb_vues', 'is_featured'
    ]
    list_filter = [
        'statut', 'acces', 'categorie', 'is_featured', 
        'date_publication', 'created_at'
    ]
    search_fields = ['titre', 'description', 'contenu', 'tags']
    prepopulated_fields = {'slug': ('titre',)}
    readonly_fields = ['nb_vues', 'nb_partages', 'reading_time_display', 'created_at', 'updated_at']
    filter_horizontal = []
    inlines = [CommentaireInline]
    
    fieldsets = (
        ('Contenu principal', {
            'fields': ('titre', 'slug', 'description', 'contenu', 'image', 'image_alt')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'sous_categorie', 'tags')
        }),
        ('Publication', {
            'fields': ('auteur', 'date_publication', 'statut', 'acces')
        }),
        ('Bannières publicitaires', {
            'fields': ('banniere_haut', 'banniere_bas', 'banniere_droite', 'banniere_gauche'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Options', {
            'fields': ('is_featured', 'allow_comments'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('nb_vues', 'nb_partages', 'reading_time_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def acces_display(self, obj):
        if obj.acces == 'PREMIUM':
            return format_html(
                '<span style="color: #ff9800; font-weight: bold;">💎 Premium</span>'
            )
        return format_html(
            '<span style="color: #4caf50; font-weight: bold;">🆓 Gratuit</span>'
        )
    acces_display.short_description = 'Accès'
    
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
    reading_time_display.short_description = 'Temps de lecture'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'auteur', 'categorie', 'sous_categorie'
        )


@admin.register(CommentaireArticle)
class CommentaireArticleAdmin(admin.ModelAdmin):
    list_display = [
        'article_link', 'auteur', 'contenu_court', 
        'statut', 'created_at', 'modere_par'
    ]
    list_filter = ['statut', 'created_at', 'article__categorie']
    search_fields = ['contenu', 'auteur__username', 'article__titre']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('article', 'auteur', 'parent', 'contenu')
        }),
        ('Modération', {
            'fields': ('statut', 'modere_par', 'raison_rejet')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_link(self, obj):
        url = reverse('admin:core_actualites_change', args=[obj.article.pk])
        return format_html('<a href="{}">{}</a>', url, obj.article.titre)
    article_link.short_description = 'Article'
    
    def contenu_court(self, obj):
        return obj.contenu[:50] + '...' if len(obj.contenu) > 50 else obj.contenu
    contenu_court.short_description = 'Contenu'
    
    actions = ['approuver_commentaires', 'rejeter_commentaires']
    
    def approuver_commentaires(self, request, queryset):
        updated = queryset.update(statut='APPROUVE', modere_par=request.user)
        self.message_user(request, f'{updated} commentaire(s) approuvé(s).')
    approuver_commentaires.short_description = "Approuver les commentaires sélectionnés"
    
    def rejeter_commentaires(self, request, queryset):
        updated = queryset.update(statut='REJETE', modere_par=request.user)
        self.message_user(request, f'{updated} commentaire(s) rejeté(s).')
    rejeter_commentaires.short_description = "Rejeter les commentaires sélectionnés"


@admin.register(LectureArticle)
class LectureArticleAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'article_link', 'pourcentage_lu', 
        'is_complete', 'is_bookmarked', 'last_read_at'
    ]
    list_filter = [
        'is_complete', 'is_bookmarked', 'last_read_at',
        'article__categorie', 'article__acces'
    ]
    search_fields = [
        'utilisateur__username', 'utilisateur__email', 'article__titre'
    ]
    readonly_fields = ['first_read_at', 'last_read_at', 'temps_lecture']
    
    def article_link(self, obj):
        url = reverse('admin:core_actualites_change', args=[obj.article.pk])
        return format_html('<a href="{}">{}</a>', url, obj.article.titre)
    article_link.short_description = 'Article'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'utilisateur', 'article'
        )

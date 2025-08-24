from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify
import uuid

User = get_user_model()


class Categorie(models.Model):
    """
    Catégories principales pour les articles du blog
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Image de la catégorie")
    
    # Ordre d'affichage
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Catégorie active")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class SousCategorie(models.Model):
    """
    Sous-catégories pour les articles du blog
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='sous_categories')
    nom = models.CharField(max_length=100, verbose_name="Nom de la sous-catégorie")
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")
    
    # Ordre d'affichage
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Sous-catégorie active")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"
        ordering = ['categorie', 'ordre', 'nom']
        unique_together = ['categorie', 'slug']
    
    def __str__(self):
        return f"{self.categorie.nom} > {self.nom}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)


class Banniere(models.Model):
    """
    Bannières publicitaires pour les articles
    """
    
    POSITION_CHOICES = [
        ('HAUT', 'Haut de page'),
        ('BAS', 'Bas de page'),
        ('DROITE', 'Côté droit'),
        ('GAUCHE', 'Côté gauche'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    nom = models.CharField(max_length=200, verbose_name="Nom de la bannière")
    image = models.ImageField(upload_to='bannieres/', verbose_name="Image de la bannière")
    lien = models.URLField(blank=True, null=True, verbose_name="Lien de redirection")
    
    # Position et dimensions
    position = models.CharField(
        max_length=10, choices=POSITION_CHOICES,
        verbose_name="Position sur la page"
    )
    largeur = models.PositiveIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(2000)],
        verbose_name="Largeur (px)"
    )
    hauteur = models.PositiveIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(1000)],
        verbose_name="Hauteur (px)"
    )
    
    # Informations publicitaires
    annonceur = models.CharField(max_length=200, blank=True, verbose_name="Nom de l'annonceur")
    prix = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Prix de la publicité"
    )
    
    # Période d'affichage
    date_debut = models.DateTimeField(verbose_name="Date de début d'affichage")
    date_fin = models.DateTimeField(verbose_name="Date de fin d'affichage")
    
    # Statistiques
    nb_impressions = models.PositiveIntegerField(default=0, verbose_name="Nombre d'impressions")
    nb_clics = models.PositiveIntegerField(default=0, verbose_name="Nombre de clics")
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Bannière active")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='bannieres_creees',
        limit_choices_to={'role__in': ['ADMIN', 'SUPPORT']}
    )
    
    class Meta:
        verbose_name = "Bannière publicitaire"
        verbose_name_plural = "Bannières publicitaires"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['position', 'is_active']),
            models.Index(fields=['date_debut', 'date_fin']),
        ]
    
    def __str__(self):
        return f"{self.nom} - {self.get_position_display()}"
    
    @property
    def is_currently_active(self):
        """Vérifie si la bannière est actuellement active selon les dates"""
        now = timezone.now()
        return (
            self.is_active and
            self.date_debut <= now <= self.date_fin
        )
    
    @property
    def taux_clic(self):
        """Calcule le taux de clic (CTR)"""
        if self.nb_impressions > 0:
            return (self.nb_clics / self.nb_impressions) * 100
        return 0


class Actualites(models.Model):
    """
    Articles du blog/actualités XAMILA
    """
    
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('PUBLIE', 'Publié'),
        ('ARCHIVE', 'Archivé'),
    ]
    
    ACCES_CHOICES = [
        ('FREE', 'Gratuit'),
        ('PREMIUM', 'Premium'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contenu de base
    titre = models.CharField(max_length=200, verbose_name="Titre de l'article")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(
        max_length=500,
        verbose_name="Description courte",
        help_text="Résumé de l'article affiché dans les listes"
    )
    contenu = models.TextField(verbose_name="Contenu complet de l'article")
    
    # Image principale
    image = models.ImageField(
        upload_to='actualites/',
        verbose_name="Image principale",
        help_text="Image affichée en tête d'article et dans les listes"
    )
    image_alt = models.CharField(
        max_length=200, blank=True,
        verbose_name="Texte alternatif de l'image"
    )
    
    # Catégorisation
    categorie = models.ForeignKey(
        Categorie, on_delete=models.CASCADE,
        related_name='articles'
    )
    sous_categorie = models.ForeignKey(
        SousCategorie, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='articles'
    )
    
    # Tags
    tags = models.JSONField(
        default=list, blank=True,
        verbose_name="Mots-clés",
        help_text="Liste des tags associés à l'article"
    )
    
    # Auteur et publication
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='articles_rediges',
        limit_choices_to={'role__in': ['ADMIN', 'INSTRUCTOR', 'SUPPORT']}
    )
    date_publication = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date de publication"
    )
    
    # Statut et accès
    statut = models.CharField(
        max_length=10, choices=STATUT_CHOICES,
        default='BROUILLON', verbose_name="Statut"
    )
    acces = models.CharField(
        max_length=10, choices=ACCES_CHOICES,
        default='FREE', verbose_name="Type d'accès"
    )
    
    # Bannières associées (optionnel)
    banniere_haut = models.ForeignKey(
        Banniere, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='articles_haut',
        limit_choices_to={'position': 'HAUT'}
    )
    banniere_bas = models.ForeignKey(
        Banniere, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='articles_bas',
        limit_choices_to={'position': 'BAS'}
    )
    banniere_droite = models.ForeignKey(
        Banniere, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='articles_droite',
        limit_choices_to={'position': 'DROITE'}
    )
    banniere_gauche = models.ForeignKey(
        Banniere, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='articles_gauche',
        limit_choices_to={'position': 'GAUCHE'}
    )
    
    # SEO
    meta_title = models.CharField(
        max_length=60, blank=True,
        verbose_name="Titre SEO",
        help_text="Titre optimisé pour les moteurs de recherche"
    )
    meta_description = models.CharField(
        max_length=160, blank=True,
        verbose_name="Description SEO",
        help_text="Description optimisée pour les moteurs de recherche"
    )
    
    # Statistiques
    nb_vues = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    nb_partages = models.PositiveIntegerField(default=0, verbose_name="Nombre de partages")
    
    # Options d'affichage
    is_featured = models.BooleanField(default=False, verbose_name="Article à la une")
    allow_comments = models.BooleanField(default=True, verbose_name="Autoriser les commentaires")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Article d'actualité"
        verbose_name_plural = "Articles d'actualités"
        ordering = ['-date_publication']
        indexes = [
            models.Index(fields=['statut', 'acces']),
            models.Index(fields=['categorie', 'statut']),
            models.Index(fields=['date_publication', 'statut']),
            models.Index(fields=['is_featured', 'statut']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.titre} ({self.get_acces_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        
        # Générer automatiquement les méta-données SEO si vides
        if not self.meta_title:
            self.meta_title = self.titre[:60]
        if not self.meta_description:
            self.meta_description = self.description[:160]
        if not self.image_alt:
            self.image_alt = f"Image de l'article: {self.titre}"
        
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Vérifie si l'article est publié et visible"""
        return (
            self.statut == 'PUBLIE' and
            self.date_publication <= timezone.now()
        )
    
    @property
    def is_premium(self):
        """Vérifie si l'article est premium"""
        return self.acces == 'PREMIUM'
    
    @property
    def reading_time(self):
        """Estime le temps de lecture en minutes (250 mots/minute)"""
        word_count = len(self.contenu.split())
        return max(1, round(word_count / 250))
    
    def increment_views(self):
        """Incrémente le nombre de vues"""
        self.nb_vues += 1
        self.save(update_fields=['nb_vues'])
    
    def increment_shares(self):
        """Incrémente le nombre de partages"""
        self.nb_partages += 1
        self.save(update_fields=['nb_partages'])


class CommentaireArticle(models.Model):
    """
    Commentaires sur les articles
    """
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente de modération'),
        ('APPROUVE', 'Approuvé'),
        ('REJETE', 'Rejeté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    article = models.ForeignKey(
        Actualites, on_delete=models.CASCADE,
        related_name='commentaires'
    )
    auteur = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='commentaires_articles'
    )
    
    # Commentaire parent pour les réponses
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='reponses'
    )
    
    # Contenu
    contenu = models.TextField(verbose_name="Contenu du commentaire")
    
    # Modération
    statut = models.CharField(
        max_length=15, choices=STATUT_CHOICES,
        default='EN_ATTENTE', verbose_name="Statut"
    )
    modere_par = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='commentaires_moderes',
        limit_choices_to={'role__in': ['ADMIN', 'SUPPORT']}
    )
    raison_rejet = models.TextField(blank=True, verbose_name="Raison du rejet")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Commentaire d'article"
        verbose_name_plural = "Commentaires d'articles"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'statut']),
            models.Index(fields=['auteur', 'statut']),
        ]
    
    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.article.titre}"
    
    @property
    def is_approved(self):
        """Vérifie si le commentaire est approuvé"""
        return self.statut == 'APPROUVE'


class LectureArticle(models.Model):
    """
    Suivi de lecture des articles par les utilisateurs
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='lectures_articles'
    )
    article = models.ForeignKey(
        Actualites, on_delete=models.CASCADE,
        related_name='lectures'
    )
    
    # Informations de lecture
    temps_lecture = models.DurationField(
        blank=True, null=True,
        verbose_name="Temps passé à lire"
    )
    pourcentage_lu = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Pourcentage lu"
    )
    
    # Statut
    is_complete = models.BooleanField(default=False, verbose_name="Lecture terminée")
    is_bookmarked = models.BooleanField(default=False, verbose_name="Article mis en favoris")
    
    # Métadonnées
    first_read_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Lecture d'article"
        verbose_name_plural = "Lectures d'articles"
        ordering = ['-last_read_at']
        unique_together = ['utilisateur', 'article']
        indexes = [
            models.Index(fields=['utilisateur', 'is_bookmarked']),
            models.Index(fields=['article', 'is_complete']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.article.titre} ({self.pourcentage_lu}%)"

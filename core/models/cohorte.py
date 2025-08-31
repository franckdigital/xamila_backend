from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime


class Cohorte(models.Model):
    """
    Modèle pour gérer les cohortes d'utilisateurs du Challenge Épargne
    Une cohorte regroupe les utilisateurs inscrits dans un mois donné
    """
    
    MOIS_CHOICES = [
        (1, 'Janvier'),
        (2, 'Février'),
        (3, 'Mars'),
        (4, 'Avril'),
        (5, 'Mai'),
        (6, 'Juin'),
        (7, 'Juillet'),
        (8, 'Août'),
        (9, 'Septembre'),
        (10, 'Octobre'),
        (11, 'Novembre'),
        (12, 'Décembre'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Code unique d'accès à la cohorte"
    )
    nom = models.CharField(
        max_length=100,
        help_text="Nom de la cohorte (ex: Cohorte Janvier 2024)"
    )
    mois = models.IntegerField(
        choices=MOIS_CHOICES,
        help_text="Mois de la cohorte (1-12)"
    )
    annee = models.IntegerField(
        default=datetime.now().year,
        help_text="Année de la cohorte"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cohortes',
        help_text="Utilisateur associé à cette cohorte"
    )
    email_utilisateur = models.EmailField(
        help_text="Email de l'utilisateur pour vérification"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Indique si la cohorte est active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cohortes'
        verbose_name = 'Cohorte'
        verbose_name_plural = 'Cohortes'
        unique_together = ['user', 'mois', 'annee']  # Un utilisateur par mois/année
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        mois_nom = dict(self.MOIS_CHOICES)[self.mois]
        return f"{self.nom} - {mois_nom} {self.annee} ({self.code})"
    
    def save(self, *args, **kwargs):
        # Synchroniser l'email avec l'utilisateur
        if self.user and not self.email_utilisateur:
            self.email_utilisateur = self.user.email
        
        # Générer automatiquement le nom si pas fourni
        if not self.nom:
            mois_nom = dict(self.MOIS_CHOICES)[self.mois]
            self.nom = f"Cohorte {mois_nom} {self.annee}"
            
        super().save(*args, **kwargs)
    
    @classmethod
    def verifier_code_acces(cls, code, user_email, user_id):
        """
        Vérifie si un code de cohorte est valide pour un utilisateur donné
        
        Args:
            code: Code de la cohorte
            user_email: Email de l'utilisateur connecté
            user_id: ID de l'utilisateur connecté
            
        Returns:
            bool: True si le code est valide pour cet utilisateur
        """
        try:
            cohorte = cls.objects.get(
                code=code,
                email_utilisateur=user_email,
                user_id=user_id,
                actif=True
            )
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def get_cohorte_utilisateur(cls, user_id, mois=None, annee=None):
        """
        Récupère la cohorte d'un utilisateur pour un mois/année donné
        """
        filters = {'user_id': user_id, 'actif': True}
        if mois:
            filters['mois'] = mois
        if annee:
            filters['annee'] = annee
            
        return cls.objects.filter(**filters).first()

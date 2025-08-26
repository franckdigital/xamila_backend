from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

class FluxFinancier(models.Model):
    """Modèle pour les flux financiers des utilisateurs"""
    
    TYPE_CHOICES = [
        ('revenus', 'Revenus'),
        ('depenses', 'Dépenses'),
    ]
    
    CATEGORIES_REVENUS = [
        ('salaire', 'Salaire'),
        ('freelance', 'Freelance'),
        ('investissements', 'Investissements'),
        ('autres_revenus', 'Autres revenus'),
    ]
    
    CATEGORIES_DEPENSES = [
        ('logement', 'Logement'),
        ('alimentation', 'Alimentation'),
        ('transport', 'Transport'),
        ('loisirs', 'Loisirs'),
        ('sante', 'Santé'),
        ('autres', 'Autres'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flux_financiers')
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    categorie = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'flux_financiers'
        verbose_name = 'Flux Financier'
        verbose_name_plural = 'Flux Financiers'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} - {self.montant} FCFA"

class BilanFinancier(models.Model):
    """Modèle pour sauvegarder les bilans calculés"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bilans_financiers')
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    total_revenus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_depenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    suggestions_generees = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bilans_financiers'
        verbose_name = 'Bilan Financier'
        verbose_name_plural = 'Bilans Financiers'
        ordering = ['-created_at']
        unique_together = ['user', 'periode_debut', 'periode_fin']
    
    def __str__(self):
        return f"Bilan {self.user.username} - {self.periode_debut} à {self.periode_fin}"
    
    def calculer_bilan(self):
        """Recalcule le bilan basé sur les flux de la période"""
        flux = FluxFinancier.objects.filter(
            user=self.user,
            date__gte=self.periode_debut,
            date__lte=self.periode_fin
        )
        
        self.total_revenus = flux.filter(type='revenus').aggregate(
            total=models.Sum('montant')
        )['total'] or 0
        
        self.total_depenses = flux.filter(type='depenses').aggregate(
            total=models.Sum('montant')
        )['total'] or 0
        
        self.solde = self.total_revenus - self.total_depenses
        self.save()
        
        return {
            'total_revenus': self.total_revenus,
            'total_depenses': self.total_depenses,
            'solde': self.solde
        }

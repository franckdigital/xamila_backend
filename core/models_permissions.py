from django.db import models

class Permission(models.Model):
    """Modèle pour les permissions système"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_permission'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.category} - {self.name}"

class RolePermission(models.Model):
    """Modèle pour associer les permissions aux rôles"""
    ROLE_CHOICES = [
        ('CUSTOMER', 'Client'),
        ('BASIC', 'Utilisateur de base'),
        ('SGI_MANAGER', 'Manager SGI'),
        ('INSTRUCTOR', 'Formateur'),
        ('SUPPORT', 'Support'),
        ('ADMIN', 'Administrateur'),
        ('STUDENT', 'Étudiant'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    is_granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_role_permission'
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission__category', 'permission__name']
    
    def __str__(self):
        status = "✓" if self.is_granted else "✗"
        return f"{self.role} - {self.permission.name} {status}"

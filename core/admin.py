from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .admin_blog import *

# Register your models here.
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry, ResourceContent
)
from .models_permissions import Permission, RolePermission
from .models_sgi_manager import SGIManagerProfile
from .models_sgi import SGIManager, SGIManagerAssignment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Administration des utilisateurs XAMILA
    """
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'role',
        'is_active', 'is_verified', 'is_staff', 'created_at'
    ]
    list_filter = [
        'role', 'is_active', 'is_verified', 'is_staff', 'is_superuser',
        'email_verified', 'phone_verified', 'created_at'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('id', 'username', 'email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Localisation', {
            'fields': ('country_of_residence',)
        }),
        ('Rôle et permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Vérifications', {
            'fields': ('is_verified', 'email_verified', 'phone_verified')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        ('Créer un utilisateur', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(SGI)
class SGIAdmin(admin.ModelAdmin):
    """
    Administration des SGI
    """
    list_display = [
        'name', 'manager_name', 'manager_email', 'min_investment_amount',
        'historical_performance', 'management_fees',
        'is_active', 'is_verified', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_verified', 'created_at'
    ]
    search_fields = ['name', 'manager_name', 'manager_email', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('id', 'name', 'description', 'logo', 'website')
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Manager SGI', {
            'fields': ('manager_name', 'manager_email', 'manager_phone')
        }),

        ('Investissement', {
            'fields': (
                'min_investment_amount', 'max_investment_amount',
                'historical_performance', 'management_fees', 'entry_fees'
            )
        }),
        ('Statut', {
            'fields': ('is_active', 'is_verified')
        }),
        ('Statistiques', {
            'fields': ('total_assets_under_management',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(ClientInvestmentProfile)
class ClientInvestmentProfileAdmin(admin.ModelAdmin):
    """
    Administration des profils clients
    """
    list_display = [
        'full_name', 'user_email', 'investment_amount', 'investment_objective',
        'risk_tolerance', 'investment_horizon', 'is_complete', 'created_at'
    ]
    list_filter = [
        'investment_objective', 'risk_tolerance', 'investment_horizon',
        'investment_experience', 'is_complete', 'created_at'
    ]
    search_fields = ['full_name', 'user__email', 'user__username', 'profession']
    readonly_fields = ['id', 'age', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('id', 'user')
        }),
        ('Informations personnelles', {
            'fields': (
                'full_name', 'phone', 'date_of_birth', 'age',
                'profession', 'monthly_income'
            )
        }),
        ('Profil d\'investissement', {
            'fields': (
                'investment_objective', 'risk_tolerance', 'investment_horizon',
                'investment_amount', 'investment_experience'
            )
        }),
        ('Préférences', {
            'fields': ('preferred_sectors', 'exclude_sectors')
        }),
        ('Statut', {
            'fields': ('is_complete',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email utilisateur'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(SGIMatchingRequest)
class SGIMatchingRequestAdmin(admin.ModelAdmin):
    """
    Administration des demandes de matching
    """
    list_display = [
        'client_name', 'total_matches', 'status', 'created_at', 'completed_at'
    ]
    list_filter = ['status', 'created_at', 'completed_at']
    search_fields = ['client_profile__full_name', 'client_profile__user__email']
    readonly_fields = ['id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Demande', {
            'fields': ('id', 'client_profile', 'status')
        }),
        ('Résultats', {
            'fields': ('matched_sgis', 'total_matches')
        }),
        ('Dates', {
            'fields': ('created_at', 'completed_at')
        })
    )
    
    def client_name(self, obj):
        return obj.client_profile.full_name
    client_name.short_description = 'Client'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client_profile')


@admin.register(ClientSGIInteraction)
class ClientSGIInteractionAdmin(admin.ModelAdmin):
    """
    Administration des interactions Client-SGI
    """
    list_display = [
        'client_name', 'sgi_name', 'interaction_type', 'matching_score',
        'status', 'created_at'
    ]
    list_filter = [
        'interaction_type', 'status', 'created_at',
        'sgi__is_verified', 'matching_score'
    ]
    search_fields = [
        'client_profile__full_name', 'sgi__name',
        'client_profile__user__email'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Interaction', {
            'fields': (
                'id', 'client_profile', 'sgi', 'matching_request',
                'interaction_type', 'matching_score'
            )
        }),
        ('Détails', {
            'fields': ('notes', 'status')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def client_name(self, obj):
        return obj.client_profile.full_name
    client_name.short_description = 'Client'
    
    def sgi_name(self, obj):
        return obj.sgi.name
    sgi_name.short_description = 'SGI'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client_profile', 'sgi', 'matching_request'
        )


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    """
    Administration des notifications email
    """
    list_display = [
        'subject', 'to_email', 'notification_type', 'status',
        'created_at', 'sent_at'
    ]
    list_filter = ['notification_type', 'status', 'created_at', 'sent_at']
    search_fields = ['to_email', 'subject', 'from_email']
    readonly_fields = ['id', 'created_at', 'sent_at']
    
    fieldsets = (
        ('Email', {
            'fields': (
                'id', 'to_email', 'from_email', 'subject',
                'notification_type'
            )
        }),
        ('Contenu', {
            'fields': ('message', 'html_message')
        }),
        ('Statut', {
            'fields': ('status', 'error_message')
        }),
        ('Référence', {
            'fields': ('client_interaction',)
        }),
        ('Dates', {
            'fields': ('created_at', 'sent_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client_interaction')


@admin.register(AdminDashboardEntry)
class AdminDashboardEntryAdmin(admin.ModelAdmin):
    """
    Administration du dashboard admin
    """
    list_display = [
        'client_name', 'sgi_name', 'priority', 'follow_up_status',
        'assigned_to', 'investment_amount', 'created_at'
    ]
    list_filter = [
        'priority', 'follow_up_status', 'assigned_to', 'created_at'
    ]
    search_fields = [
        'client_interaction__client_profile__full_name',
        'client_interaction__sgi__name',
        'admin_notes'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Interaction', {
            'fields': ('id', 'client_interaction')
        }),
        ('Suivi', {
            'fields': ('priority', 'follow_up_status', 'assigned_to')
        }),
        ('Notes', {
            'fields': ('admin_notes',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def client_name(self, obj):
        return obj.client_interaction.client_profile.full_name
    client_name.short_description = 'Client'
    
    def sgi_name(self, obj):
        return obj.client_interaction.sgi.name
    sgi_name.short_description = 'SGI'
    
    def investment_amount(self, obj):
        amount = obj.client_interaction.client_profile.investment_amount
        return f"{amount:,.0f} FCFA"
    investment_amount.short_description = 'Montant'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client_interaction__client_profile',
            'client_interaction__sgi',
            'assigned_to'
        )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Administration des permissions
    """
    list_display = ['code', 'name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Permission', {
            'fields': ('id', 'code', 'name', 'category')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """
    Administration des permissions par rôle
    """
    list_display = ['role', 'permission_code', 'permission_name', 'is_granted', 'created_at']
    list_filter = ['role', 'is_granted', 'permission__category', 'created_at']
    search_fields = ['permission__code', 'permission__name', 'role']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Attribution', {
            'fields': ('id', 'role', 'permission', 'is_granted')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def permission_code(self, obj):
        return obj.permission.code
    permission_code.short_description = 'Code Permission'
    
    def permission_name(self, obj):
        return obj.permission.name
    permission_name.short_description = 'Nom Permission'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('permission')


@admin.register(ResourceContent)
class ResourceContentAdmin(admin.ModelAdmin):
    """
    Administration du contenu des ressources
    """
    list_display = ['banner_title', 'youtube_video_id', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['banner_title', 'banner_description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Contenu de la bannière', {
            'fields': ('banner_title', 'banner_description')
        }),
        ('Vidéo YouTube', {
            'fields': ('youtube_video_id',),
            'description': 'Entrez uniquement l\'ID de la vidéo YouTube (la partie après "v=" dans l\'URL)'
        }),
        ('Paramètres', {
            'fields': ('is_active',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        # S'assurer qu'un seul contenu est actif à la fois
        if obj.is_active:
            ResourceContent.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)


# Personnalisation de l'admin Django
admin.site.site_header = "Administration Xamila"
admin.site.site_title = "Xamila Admin"
admin.site.index_title = "Gestion de la plateforme Xamila"


# ===== SGI Manager administration =====
@admin.register(SGIManagerProfile)
class SGIManagerProfileAdmin(admin.ModelAdmin):
    """
    Permet à l'admin d'associer un utilisateur manager à une SGI (modèle SGIManagerProfile)
    """
    list_display = ['user', 'sgi', 'manager_type', 'permission_level', 'is_active', 'created_at']
    list_filter = ['manager_type', 'permission_level', 'is_active', 'created_at']
    search_fields = ['user__email', 'user__username', 'sgi__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Lien', {
            'fields': ('id', 'user', 'sgi')
        }),
        ('Informations professionnelles', {
            'fields': ('manager_type', 'employee_id', 'department', 'hire_date')
        }),
        ('Permissions', {
            'fields': ('permission_level', 'can_approve_contracts', 'can_manage_clients', 'can_view_financials', 'can_generate_reports')
        }),
        ('Limites', {
            'fields': ('max_contract_amount', 'max_daily_approvals')
        }),
        ('Statut', {
            'fields': ('is_active', 'last_login_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SGIManager)
class SGIManagerAdmin(admin.ModelAdmin):
    """
    Modèle alternatif de manager (core/models_sgi.py). Lien avec SGIs via assignments.
    """
    list_display = ['user', 'professional_title', 'license_number', 'is_active', 'is_verified', 'total_managed_sgis']
    list_filter = ['is_active', 'is_verified', 'created_at']
    search_fields = ['user__email', 'user__username', 'license_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Utilisateur', {'fields': ('id', 'user')}),
        ('Profil', {'fields': ('professional_title', 'license_number', 'years_of_experience', 'specializations', 'certifications')}),
        ('Contact', {'fields': ('professional_email', 'professional_phone')}),
        ('Statut', {'fields': ('is_active', 'is_verified', 'verified_at', 'verified_by')}),
        ('Dates', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(SGIManagerAssignment)
class SGIManagerAssignmentAdmin(admin.ModelAdmin):
    """
    Permet d'associer un SGIManager à une SGI et définir le rôle (PRIMARY, ...)
    """
    list_display = ['sgi', 'manager', 'role', 'is_active', 'assigned_at']
    list_filter = ['role', 'is_active', 'assigned_at']
    search_fields = ['sgi__name', 'manager__user__email', 'manager__user__username']
    readonly_fields = ['id', 'assigned_at']
    fieldsets = (
        ('Assignation', {'fields': ('id', 'sgi', 'manager', 'role', 'permissions', 'is_active')}),
        ('Métadonnées', {'fields': ('assigned_at', 'assigned_by'), 'classes': ('collapse',)}),
    )

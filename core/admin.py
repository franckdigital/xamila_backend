from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .admin_blog import *

# Register your models here.
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    User, SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry
)


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
            'fields': ('country_of_residence', 'country_of_origin')
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


# Personnalisation de l'admin Django
admin.site.site_header = "Administration Xamila"
admin.site.site_title = "Xamila Admin"
admin.site.index_title = "Gestion de la plateforme Xamila"

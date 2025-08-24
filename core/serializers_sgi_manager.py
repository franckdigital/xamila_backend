"""
Serializers spécialisés pour les SGI_MANAGER
Sérialisation et validation des données SGI
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from .models import SGI, Contract
from .models_sgi_manager import (
    SGIManagerProfile, SGIPerformanceMetrics, 
    SGIClientRelationship, SGIAlert
)
from .serializers import UserSerializer, SGISerializer

User = get_user_model()


class SGIManagerProfileSerializer(serializers.ModelSerializer):
    """Serializer pour les profils de managers SGI"""
    
    user = UserSerializer(read_only=True)
    sgi = SGISerializer(read_only=True)
    daily_approvals_count = serializers.SerializerMethodField()
    can_approve_today = serializers.SerializerMethodField()
    
    class Meta:
        model = SGIManagerProfile
        fields = [
            'id', 'user', 'sgi', 'manager_type', 'employee_id', 'department',
            'hire_date', 'permission_level', 'can_approve_contracts',
            'can_manage_clients', 'can_view_financials', 'can_generate_reports',
            'max_contract_amount', 'max_daily_approvals', 'daily_approvals_count',
            'can_approve_today', 'is_active', 'created_at', 'updated_at',
            'last_login_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'daily_approvals_count', 'can_approve_today']
    
    def get_daily_approvals_count(self, obj):
        """Retourne le nombre d'approbations du jour"""
        return obj.get_daily_approvals_count()
    
    def get_can_approve_today(self, obj):
        """Vérifie si le manager peut encore approuver aujourd'hui"""
        return obj.can_approve_today()


class SGIManagerProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de profils de managers SGI"""
    
    class Meta:
        model = SGIManagerProfile
        fields = [
            'sgi', 'manager_type', 'employee_id', 'department', 'hire_date',
            'permission_level', 'can_approve_contracts', 'can_manage_clients',
            'can_view_financials', 'can_generate_reports', 'max_contract_amount',
            'max_daily_approvals'
        ]
    
    def create(self, validated_data):
        """Crée un profil manager pour l'utilisateur connecté"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_sgi(self, value):
        """Valide que la SGI est active et vérifiée"""
        if not value.is_active:
            raise serializers.ValidationError("La SGI doit être active.")
        if not value.is_verified:
            raise serializers.ValidationError("La SGI doit être vérifiée.")
        return value
    
    def validate(self, attrs):
        """Validations croisées"""
        user = self.context['request'].user
        
        # Vérifier que l'utilisateur a le bon rôle
        if user.role != 'SGI_MANAGER':
            raise serializers.ValidationError("Seuls les SGI_MANAGER peuvent créer ce profil.")
        
        # Vérifier qu'il n'y a pas déjà un profil pour cette SGI
        if SGIManagerProfile.objects.filter(user=user, sgi=attrs['sgi']).exists():
            raise serializers.ValidationError("Un profil existe déjà pour cette SGI.")
        
        # Valider les permissions cohérentes
        if attrs.get('can_approve_contracts') and not attrs.get('max_contract_amount'):
            raise serializers.ValidationError(
                "Un montant maximum doit être défini pour approuver des contrats."
            )
        
        return attrs


class SGIPerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer pour les métriques de performance SGI"""
    
    sgi = SGISerializer(read_only=True)
    client_retention_rate = serializers.ReadOnlyField()
    contract_success_rate = serializers.ReadOnlyField()
    alpha_performance = serializers.ReadOnlyField()
    
    class Meta:
        model = SGIPerformanceMetrics
        fields = [
            'id', 'sgi', 'period_type', 'period_start', 'period_end',
            'new_clients', 'active_clients', 'churned_clients',
            'total_investments', 'average_investment', 'total_fees_collected',
            'portfolio_return', 'benchmark_return', 'contracts_signed',
            'contracts_pending', 'contracts_rejected', 'client_satisfaction_score',
            'client_retention_rate', 'contract_success_rate', 'alpha_performance',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'client_retention_rate', 'contract_success_rate', 
            'alpha_performance', 'created_at', 'updated_at'
        ]


class SGIPerformanceMetricsCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de métriques de performance"""
    
    class Meta:
        model = SGIPerformanceMetrics
        fields = [
            'period_type', 'period_start', 'period_end', 'new_clients',
            'active_clients', 'churned_clients', 'total_investments',
            'average_investment', 'total_fees_collected', 'portfolio_return',
            'benchmark_return', 'contracts_signed', 'contracts_pending',
            'contracts_rejected', 'client_satisfaction_score'
        ]
    
    def validate(self, attrs):
        """Validations des métriques"""
        if attrs['period_start'] >= attrs['period_end']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        # Vérifier que les métriques sont cohérentes
        if attrs.get('churned_clients', 0) > attrs.get('active_clients', 0):
            raise serializers.ValidationError(
                "Le nombre de clients perdus ne peut pas dépasser le nombre de clients actifs."
            )
        
        return attrs


class SGIClientRelationshipSerializer(serializers.ModelSerializer):
    """Serializer pour les relations client-manager SGI"""
    
    manager = UserSerializer(read_only=True)
    client = UserSerializer(read_only=True)
    sgi = SGISerializer(read_only=True)
    is_active = serializers.SerializerMethodField()
    days_since_last_contact = serializers.SerializerMethodField()
    
    class Meta:
        model = SGIClientRelationship
        fields = [
            'id', 'manager', 'client', 'sgi', 'relationship_type', 'status',
            'start_date', 'end_date', 'last_contact', 'notes', 'is_active',
            'days_since_last_contact', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'days_since_last_contact', 'created_at', 'updated_at']
    
    def get_is_active(self, obj):
        """Vérifie si la relation est active"""
        return obj.is_active()
    
    def get_days_since_last_contact(self, obj):
        """Retourne le nombre de jours depuis le dernier contact"""
        return obj.days_since_last_contact()


class SGIClientRelationshipCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de relations client-manager"""
    
    client_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = SGIClientRelationship
        fields = [
            'client_id', 'relationship_type', 'status', 'start_date', 
            'end_date', 'notes'
        ]
    
    def create(self, validated_data):
        """Crée une relation pour le manager connecté"""
        client_id = validated_data.pop('client_id')
        client = User.objects.get(id=client_id, role='CUSTOMER')
        
        manager = self.context['request'].user
        manager_profile = manager.sgi_manager_profile
        
        validated_data.update({
            'manager': manager,
            'client': client,
            'sgi': manager_profile.sgi
        })
        
        return super().create(validated_data)
    
    def validate_client_id(self, value):
        """Valide que le client existe et est un CUSTOMER"""
        try:
            client = User.objects.get(id=value, role='CUSTOMER')
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Client introuvable ou rôle incorrect.")
    
    def validate(self, attrs):
        """Validations croisées"""
        manager = self.context['request'].user
        
        # Vérifier que le manager a un profil SGI
        if not hasattr(manager, 'sgi_manager_profile'):
            raise serializers.ValidationError("Profil manager SGI requis.")
        
        # Vérifier que le manager peut gérer des clients
        if not manager.sgi_manager_profile.can_manage_clients:
            raise serializers.ValidationError("Permission de gestion client requise.")
        
        return attrs


class SGIAlertSerializer(serializers.ModelSerializer):
    """Serializer pour les alertes SGI"""
    
    manager = UserSerializer(read_only=True)
    sgi = SGISerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = SGIAlert
        fields = [
            'id', 'manager', 'sgi', 'alert_type', 'priority', 'status',
            'title', 'message', 'action_required', 'action_url',
            'related_object_type', 'related_object_id', 'expires_at',
            'read_at', 'acknowledged_at', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_expired', 'read_at', 'acknowledged_at', 'created_at', 'updated_at'
        ]
    
    def get_is_expired(self, obj):
        """Vérifie si l'alerte a expiré"""
        return obj.is_expired()


class SGIAlertCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'alertes SGI"""
    
    manager_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="IDs des managers à alerter (optionnel, tous si vide)"
    )
    
    class Meta:
        model = SGIAlert
        fields = [
            'alert_type', 'priority', 'title', 'message', 'action_required',
            'action_url', 'related_object_type', 'related_object_id',
            'expires_at', 'manager_ids'
        ]
    
    def create(self, validated_data):
        """Crée des alertes pour les managers spécifiés"""
        manager_ids = validated_data.pop('manager_ids', [])
        sgi = self.context.get('sgi')
        
        if not sgi:
            raise serializers.ValidationError("SGI requise dans le contexte.")
        
        # Si aucun manager spécifié, alerter tous les managers de la SGI
        if not manager_ids:
            managers = User.objects.filter(
                sgi_manager_profile__sgi=sgi,
                sgi_manager_profile__is_active=True
            )
        else:
            managers = User.objects.filter(
                id__in=manager_ids,
                sgi_manager_profile__sgi=sgi,
                sgi_manager_profile__is_active=True
            )
        
        alerts = []
        for manager in managers:
            alert_data = validated_data.copy()
            alert_data.update({
                'manager': manager,
                'sgi': sgi
            })
            alerts.append(SGIAlert(**alert_data))
        
        return SGIAlert.objects.bulk_create(alerts)


class SGIDashboardSerializer(serializers.Serializer):
    """Serializer pour le dashboard SGI manager"""
    
    # Informations générales
    sgi_info = SGISerializer(read_only=True)
    manager_profile = SGIManagerProfileSerializer(read_only=True)
    
    # Métriques rapides
    total_clients = serializers.IntegerField(read_only=True)
    active_contracts = serializers.IntegerField(read_only=True)
    pending_contracts = serializers.IntegerField(read_only=True)
    total_assets = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    
    # Performance récente
    monthly_performance = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    quarterly_performance = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    yearly_performance = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    # Alertes
    unread_alerts = serializers.IntegerField(read_only=True)
    critical_alerts = serializers.IntegerField(read_only=True)
    
    # Activité récente
    recent_contracts = serializers.ListField(read_only=True)
    recent_clients = serializers.ListField(read_only=True)
    
    # Objectifs et KPIs
    monthly_target = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    monthly_progress = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)


class ContractApprovalSerializer(serializers.Serializer):
    """Serializer pour l'approbation de contrats"""
    
    contract_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_contract_id(self, value):
        """Valide que le contrat existe et est en attente"""
        try:
            contract = Contract.objects.get(id=value, status='PENDING')
            return value
        except Contract.DoesNotExist:
            raise serializers.ValidationError("Contrat introuvable ou déjà traité.")
    
    def validate(self, attrs):
        """Validations pour l'approbation"""
        manager = self.context['request'].user
        contract = Contract.objects.get(id=attrs['contract_id'])
        
        # Vérifier les permissions du manager
        if not hasattr(manager, 'sgi_manager_profile'):
            raise serializers.ValidationError("Profil manager SGI requis.")
        
        manager_profile = manager.sgi_manager_profile
        
        if not manager_profile.can_approve_contracts:
            raise serializers.ValidationError("Permission d'approbation requise.")
        
        # Vérifier le montant
        if not manager_profile.can_approve_amount(contract.investment_amount):
            raise serializers.ValidationError(
                f"Montant dépassant la limite autorisée ({manager_profile.max_contract_amount} FCFA)."
            )
        
        # Vérifier la limite quotidienne
        if not manager_profile.can_approve_today():
            raise serializers.ValidationError(
                f"Limite quotidienne d'approbations atteinte ({manager_profile.max_daily_approvals})."
            )
        
        # Vérifier que c'est la bonne SGI
        if contract.sgi != manager_profile.sgi:
            raise serializers.ValidationError("Ce contrat n'appartient pas à votre SGI.")
        
        return attrs


class SGIAnalyticsSerializer(serializers.Serializer):
    """Serializer pour les analytics SGI avancées"""
    
    # Période d'analyse
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    
    # Métriques clients
    client_acquisition = serializers.DictField(read_only=True)
    client_retention = serializers.DictField(read_only=True)
    client_segmentation = serializers.DictField(read_only=True)
    
    # Métriques financières
    revenue_breakdown = serializers.DictField(read_only=True)
    investment_flows = serializers.DictField(read_only=True)
    fee_analysis = serializers.DictField(read_only=True)
    
    # Performance
    portfolio_performance = serializers.DictField(read_only=True)
    benchmark_comparison = serializers.DictField(read_only=True)
    risk_metrics = serializers.DictField(read_only=True)
    
    # Opérations
    contract_analytics = serializers.DictField(read_only=True)
    manager_performance = serializers.DictField(read_only=True)
    
    def validate(self, attrs):
        """Valide la période d'analyse"""
        if attrs['period_start'] >= attrs['period_end']:
            raise serializers.ValidationError(
                "La date de fin doit être postérieure à la date de début."
            )
        
        # Limiter à 2 ans maximum
        max_period = timedelta(days=730)
        if attrs['period_end'] - attrs['period_start'] > max_period:
            raise serializers.ValidationError(
                "La période d'analyse ne peut pas dépasser 2 ans."
            )
        
        return attrs

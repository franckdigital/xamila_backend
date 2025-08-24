# -*- coding: utf-8 -*-
"""
Serializers avancés pour l'interface Web Admin XAMILA
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User as UserModel, SGI, Contract, QuizQuestion, OTP, RefreshToken

User = get_user_model()


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les utilisateurs (vue admin)"""
    
    full_name = serializers.SerializerMethodField()
    days_since_registration = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'is_active', 'is_verified', 'email_verified', 'phone_verified',
            'country_of_residence', 'country_of_origin', 'created_at', 'updated_at',
            'last_login', 'days_since_registration', 'profile_completion'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
    
    def get_days_since_registration(self, obj):
        from django.utils import timezone
        return (timezone.now() - obj.created_at).days
    
    def get_profile_completion(self, obj):
        fields = ['first_name', 'last_name', 'phone', 'country_of_residence', 'country_of_origin']
        completed = sum(1 for field in fields if getattr(obj, field))
        return round((completed / len(fields)) * 100, 2)


class AdminSGISerializer(serializers.ModelSerializer):
    """Serializer pour les SGI (vue admin)"""
    
    manager_info = serializers.SerializerMethodField()
    contracts_count = serializers.SerializerMethodField()
    performance_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = SGI
        fields = [
            'id', 'name', 'description', 'address', 'website', 'is_active',
            'created_at', 'updated_at', 'manager_info', 'contracts_count', 'performance_metrics'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_manager_info(self, obj):
        if obj.manager:
            return {
                'id': obj.manager.id,
                'name': f"{obj.manager.first_name} {obj.manager.last_name}".strip(),
                'email': obj.manager.email,
                'phone': obj.manager.phone,
                'is_active': obj.manager.is_active,
                'is_verified': obj.manager.is_verified
            }
        return None
    
    def get_contracts_count(self, obj):
        contracts = Contract.objects.filter(sgi=obj)
        return {
            'total': contracts.count(),
            'pending': contracts.filter(status='PENDING').count(),
            'approved': contracts.filter(status='APPROVED').count(),
            'rejected': contracts.filter(status='REJECTED').count()
        }
    
    def get_performance_metrics(self, obj):
        # Métriques de performance basiques
        contracts = Contract.objects.filter(sgi=obj)
        total_contracts = contracts.count()
        
        if total_contracts == 0:
            return {
                'approval_rate': 0,
                'average_processing_time': 0,
                'client_satisfaction': 0
            }
        
        approved_contracts = contracts.filter(status='APPROVED').count()
        approval_rate = round((approved_contracts / total_contracts) * 100, 2)
        
        return {
            'approval_rate': approval_rate,
            'average_processing_time': 0,  # À calculer plus tard
            'client_satisfaction': 0  # À implémenter avec système de notation
        }


class AdminContractSerializer(serializers.ModelSerializer):
    """Serializer pour les contrats (vue admin)"""
    
    client_info = serializers.SerializerMethodField()
    sgi_info = serializers.SerializerMethodField()
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'client_info', 'sgi_info', 'investment_amount', 'duration_months',
            'status', 'created_at', 'updated_at', 'processing_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_client_info(self, obj):
        return {
            'id': obj.client.id,
            'name': f"{obj.client.first_name} {obj.client.last_name}".strip(),
            'email': obj.client.email,
            'phone': obj.client.phone
        }
    
    def get_sgi_info(self, obj):
        return {
            'id': obj.sgi.id,
            'name': obj.sgi.name,
            'manager': f"{obj.sgi.manager.first_name} {obj.sgi.manager.last_name}".strip()
        }
    
    def get_processing_time(self, obj):
        if obj.status in ['APPROVED', 'REJECTED'] and obj.updated_at:
            delta = obj.updated_at - obj.created_at
            return delta.days
        return None


class AdminQuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer pour les questions de quiz (vue admin)"""
    
    creator_info = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizQuestion
        fields = [
            'id', 'question_text', 'question_type', 'category', 'difficulty',
            'correct_answer', 'explanation', 'is_active', 'created_at', 'updated_at',
            'creator_info', 'usage_stats'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_creator_info(self, obj):
        if obj.created_by:
            return {
                'id': obj.created_by.id,
                'name': f"{obj.created_by.first_name} {obj.created_by.last_name}".strip(),
                'role': obj.created_by.role
            }
        return None
    
    def get_usage_stats(self, obj):
        # Statistiques d'utilisation (à implémenter avec le système de quiz)
        return {
            'times_used': 0,  # Nombre de fois utilisée dans des quiz
            'success_rate': 0,  # Taux de réussite
            'average_time': 0  # Temps moyen de réponse
        }


class AdminOTPSerializer(serializers.ModelSerializer):
    """Serializer pour les codes OTP (vue admin)"""
    
    user_info = serializers.SerializerMethodField()
    
    class Meta:
        model = OTP
        fields = [
            'id', 'user_info', 'code', 'otp_type', 'is_used', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'role': obj.user.role
        }


class AdminActivityLogSerializer(serializers.Serializer):
    """Serializer pour les logs d'activité"""
    
    user = serializers.DictField()
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()
    details = serializers.DictField(required=False)
    ip_address = serializers.IPAddressField(required=False)
    user_agent = serializers.CharField(required=False)


class AdminStatsSerializer(serializers.Serializer):
    """Serializer pour les statistiques du dashboard admin"""
    
    users = serializers.DictField()
    sgis = serializers.DictField()
    contracts = serializers.DictField()
    otp = serializers.DictField()
    registration_evolution = serializers.ListField()
    last_updated = serializers.DateTimeField()


class AdminUserActionSerializer(serializers.Serializer):
    """Serializer pour les actions administratives sur les utilisateurs"""
    
    action = serializers.ChoiceField(choices=[
        ('activate', 'Activer'),
        ('deactivate', 'Désactiver'),
        ('verify', 'Vérifier'),
        ('unverify', 'Retirer la vérification'),
        ('reset_password', 'Réinitialiser le mot de passe'),
        ('send_otp', 'Envoyer un code OTP')
    ])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class AdminSGIActionSerializer(serializers.Serializer):
    """Serializer pour les actions administratives sur les SGI"""
    
    action = serializers.ChoiceField(choices=[
        ('approve', 'Approuver'),
        ('reject', 'Rejeter'),
        ('suspend', 'Suspendre'),
        ('reactivate', 'Réactiver')
    ])
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class AdminBulkActionSerializer(serializers.Serializer):
    """Serializer pour les actions en lot"""
    
    ids = serializers.ListField(child=serializers.UUIDField())
    action = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)


class AdminReportFilterSerializer(serializers.Serializer):
    """Serializer pour les filtres de rapports"""
    
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    role = serializers.ChoiceField(choices=UserModel.ROLE_CHOICES, required=False)
    country = serializers.CharField(required=False, max_length=100)
    status = serializers.ChoiceField(choices=[
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('verified', 'Vérifié'),
        ('unverified', 'Non vérifié')
    ], required=False)
    format = serializers.ChoiceField(choices=[
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel')
    ], default='json')


class AdminNotificationSerializer(serializers.Serializer):
    """Serializer pour les notifications admin"""
    
    type = serializers.ChoiceField(choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
        ('in_app', 'Notification In-App')
    ])
    recipients = serializers.ListField(child=serializers.UUIDField())
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    schedule_at = serializers.DateTimeField(required=False)
    template_id = serializers.UUIDField(required=False)

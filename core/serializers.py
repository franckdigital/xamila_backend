from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry,
    OTP, Contract, QuizQuestion, QuizSubmission, Stock
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'role', 'country_of_residence', 'country_of_origin',
            'is_verified', 'email_verified', 'phone_verified',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']


class SGISerializer(serializers.ModelSerializer):
    """Serializer pour les SGI"""
    
    class Meta:
        model = SGI
        fields = [
            'id', 'name', 'description', 'logo', 'website',
            'email', 'phone', 'address',
            'manager_name', 'manager_email', 'manager_phone',
            'min_investment_amount', 'max_investment_amount',
            'historical_performance', 'management_fees', 'entry_fees',
            'is_active', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SGIListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des SGI"""
    
    class Meta:
        model = SGI
        fields = [
            'id', 'name', 'description', 'logo',
            'manager_name', 'manager_email',
            'min_investment_amount', 'max_investment_amount',
            'historical_performance', 'management_fees',
            'is_active', 'is_verified'
        ]


class ClientInvestmentProfileSerializer(serializers.ModelSerializer):
    """Serializer pour les profils d'investissement clients"""
    
    user = UserSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = ClientInvestmentProfile
        fields = [
            'id', 'user', 'full_name', 'phone', 'date_of_birth', 'age',
            'profession', 'monthly_income',
            'investment_objective', 'risk_tolerance', 'investment_horizon',
            'investment_amount', 'investment_experience',
            'preferred_sectors', 'exclude_sectors',
            'created_at', 'updated_at', 'is_complete'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'age']
    
    def validate_investment_amount(self, value):
        """Validation du montant d'investissement"""
        if value < 10000:
            raise serializers.ValidationError(
                "Le montant minimum d'investissement est de 10,000 FCFA"
            )
        return value


class ClientInvestmentProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de profils d'investissement"""
    
    class Meta:
        model = ClientInvestmentProfile
        fields = [
            'full_name', 'phone', 'date_of_birth',
            'profession', 'monthly_income',
            'investment_objective', 'risk_tolerance', 'investment_horizon',
            'investment_amount', 'investment_experience',
            'preferred_sectors', 'exclude_sectors'
        ]
    
    def create(self, validated_data):
        """Crée un profil d'investissement pour l'utilisateur connecté"""
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['is_complete'] = True
        return super().create(validated_data)


class SGIMatchingRequestSerializer(serializers.ModelSerializer):
    """Serializer pour les demandes de matching SGI"""
    
    client_profile = ClientInvestmentProfileSerializer(read_only=True)
    
    class Meta:
        model = SGIMatchingRequest
        fields = [
            'id', 'client_profile', 'matched_sgis', 'total_matches',
            'status', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class SGIMatchingResultSerializer(serializers.Serializer):
    """Serializer pour les résultats de matching SGI"""
    
    sgi_id = serializers.UUIDField()
    sgi_name = serializers.CharField()
    sgi_description = serializers.CharField()
    manager_name = serializers.CharField()
    manager_email = serializers.EmailField()
    matching_score = serializers.IntegerField()
    min_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    max_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    historical_performance = serializers.DecimalField(max_digits=5, decimal_places=2)
    management_fees = serializers.DecimalField(max_digits=5, decimal_places=2)
    entry_fees = serializers.DecimalField(max_digits=5, decimal_places=2)
    logo = serializers.ImageField(allow_null=True)
    website = serializers.URLField(allow_null=True)


class ClientSGIInteractionSerializer(serializers.ModelSerializer):
    """Serializer pour les interactions Client-SGI"""
    
    client_profile = ClientInvestmentProfileSerializer(read_only=True)
    sgi = SGIListSerializer(read_only=True)
    
    class Meta:
        model = ClientSGIInteraction
        fields = [
            'id', 'client_profile', 'sgi', 'matching_request',
            'interaction_type', 'matching_score', 'notes', 'status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientSGIInteractionCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'interactions Client-SGI"""
    
    class Meta:
        model = ClientSGIInteraction
        fields = [
            'sgi', 'matching_request', 'interaction_type',
            'matching_score', 'notes'
        ]
    
    def create(self, validated_data):
        """Crée une interaction pour le profil client de l'utilisateur connecté"""
        user = self.context['request'].user
        try:
            client_profile = user.investment_profile
        except ClientInvestmentProfile.DoesNotExist:
            raise serializers.ValidationError(
                "Vous devez d'abord créer votre profil d'investissement"
            )
        
        validated_data['client_profile'] = client_profile
        return super().create(validated_data)


class EmailNotificationSerializer(serializers.ModelSerializer):
    """Serializer pour les notifications email"""
    
    class Meta:
        model = EmailNotification
        fields = [
            'id', 'to_email', 'from_email', 'subject', 'message',
            'html_message', 'notification_type', 'client_interaction',
            'status', 'error_message', 'created_at', 'sent_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at']


class AdminDashboardEntrySerializer(serializers.ModelSerializer):
    """Serializer pour les entrées du dashboard admin"""
    
    client_interaction = ClientSGIInteractionSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    
    class Meta:
        model = AdminDashboardEntry
        fields = [
            'id', 'client_interaction', 'priority', 'follow_up_status',
            'admin_notes', 'assigned_to', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MatchingCriteriaSerializer(serializers.Serializer):
    """Serializer pour les critères de matching disponibles"""
    
    investment_objectives = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )
    risk_levels = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )
    investment_horizons = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )
    experience_levels = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField())
    )


class SGISelectionSerializer(serializers.Serializer):
    """Serializer pour la sélection d'une SGI"""
    
    sgi_id = serializers.UUIDField()
    matching_score = serializers.IntegerField(min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_sgi_id(self, value):
        """Valide que la SGI existe et est active"""
        try:
            sgi = SGI.objects.get(id=value, is_active=True)
        except SGI.DoesNotExist:
            raise serializers.ValidationError("SGI non trouvée ou inactive")
        return value


class SGIStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques SGI"""
    
    total_sgis = serializers.IntegerField()
    active_sgis = serializers.IntegerField()
    verified_sgis = serializers.IntegerField()
    total_matching_requests = serializers.IntegerField()
    successful_matches = serializers.IntegerField()
    total_interactions = serializers.IntegerField()
    average_matching_score = serializers.DecimalField(max_digits=5, decimal_places=2)


class ClientStatisticsSerializer(serializers.Serializer):
    """Serializer pour les statistiques clients"""
    
    total_clients = serializers.IntegerField()
    complete_profiles = serializers.IntegerField()
    total_investment_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    average_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    most_popular_objective = serializers.CharField()
    most_popular_risk_level = serializers.CharField()
    most_popular_horizon = serializers.CharField()


# ================================
# SERIALIZERS POUR AUTHENTIFICATION ET OTP
# ================================

class OTPSerializer(serializers.ModelSerializer):
    """Serializer pour les codes OTP"""
    
    class Meta:
        model = OTP
        fields = ['id', 'user', 'code', 'otp_type', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at']


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer pour la vérification des codes OTP"""
    
    user_id = serializers.UUIDField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Le code OTP doit contenir uniquement des chiffres")
        return value


# ================================
# SERIALIZERS POUR ENREGISTREMENT PAR RÔLES
# ================================

class BaseUserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer de base pour l'enregistrement d'utilisateurs"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone',
            'country_of_residence', 'country_of_origin'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        
        # Validation du mot de passe
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class CustomerRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour l'enregistrement des clients/épargnants"""
    
    def create(self, validated_data):
        validated_data['role'] = 'CUSTOMER'
        return super().create(validated_data)


class StudentRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour l'enregistrement des étudiants/apprenants"""
    
    education_level = serializers.CharField(max_length=100, required=False, allow_blank=True)
    interests = serializers.CharField(required=False, allow_blank=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + ['education_level', 'interests']
    
    def create(self, validated_data):
        # Retirer les champs spécifiques à l'étudiant pour l'instant
        validated_data.pop('education_level', None)
        validated_data.pop('interests', None)
        
        validated_data['role'] = 'STUDENT'
        return super().create(validated_data)


class SGIManagerRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour l'enregistrement des managers SGI"""
    
    sgi_name = serializers.CharField(max_length=200, write_only=True)
    sgi_description = serializers.CharField(write_only=True)
    sgi_address = serializers.CharField(write_only=True)
    sgi_website = serializers.URLField(required=False, allow_blank=True, write_only=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + [
            'sgi_name', 'sgi_description', 'sgi_address', 'sgi_website'
        ]
    
    def create(self, validated_data):
        # Extraire les données SGI
        sgi_data = {
            'name': validated_data.pop('sgi_name'),
            'description': validated_data.pop('sgi_description'),
            'address': validated_data.pop('sgi_address'),
            'website': validated_data.pop('sgi_website', ''),
        }
        
        validated_data['role'] = 'SGI_MANAGER'
        user = super().create(validated_data)
        
        # Créer la SGI associée
        SGI.objects.create(
            manager_name=user.get_full_name(),
            manager_email=user.email,
            manager_phone=user.phone,
            email=user.email,
            **sgi_data
        )
        
        return user


class InstructorRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour l'enregistrement des instructeurs/formateurs"""
    
    specialization = serializers.CharField(max_length=200, required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + ['specialization', 'bio']
    
    def create(self, validated_data):
        # Retirer les champs spécifiques à l'instructeur pour l'instant
        validated_data.pop('specialization', None)
        validated_data.pop('bio', None)
        
        validated_data['role'] = 'INSTRUCTOR'
        return super().create(validated_data)


class SupportRegistrationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour l'enregistrement du support client"""
    
    department = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + ['department']
    
    def create(self, validated_data):
        validated_data.pop('department', None)  # Pour l'instant, pas de modèle spécifique
        validated_data['role'] = 'SUPPORT'
        return super().create(validated_data)


class AdminUserCreationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour la création d'utilisateurs par l'admin"""
    
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    is_active = serializers.BooleanField(default=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + ['role', 'is_active']
    
    def create(self, validated_data):
        return super().create(validated_data)

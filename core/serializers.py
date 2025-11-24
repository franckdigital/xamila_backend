from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    User, SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry,
    OTP, Contract, QuizQuestion, QuizSubmission, Stock, ResourceContent,
    Cohorte
)
from .models_sgi import SGIAccountTerms, SGIRating, AccountOpeningRequest
from .models_permissions import Permission, RolePermission


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'role', 'country', 'country_of_residence',
            'is_verified', 'email_verified', 'phone_verified', 'is_active',
            'paye', 'certif_reussite', 'is_certificate_unlocked',
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


class SGIAccountTermsSerializer(serializers.ModelSerializer):
    """Serializer pour les conditions d'ouverture de compte titre"""
    class Meta:
        model = SGIAccountTerms
        fields = [
            'country', 'headquarters_address', 'director_name', 'profile',
            'has_minimum_amount', 'minimum_amount_value', 'has_opening_fees', 'opening_fees_amount',
            'is_digital_opening', 'deposit_methods', 'is_bank_subsidiary', 'parent_bank_name',
            'custody_fees', 'account_maintenance_fees',
            'brokerage_fees_transactions_ordinary', 'brokerage_fees_files', 'brokerage_fees_transactions',
            'transfer_account_fees', 'transfer_securities_fees', 'pledge_fees', 'redemption_methods',
            'preferred_customer_banks'
        ]


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


class AccountOpeningRequestSerializer(serializers.ModelSerializer):
    """Serializer lecture des demandes d'ouverture de compte"""
    customer = UserSerializer(read_only=True)
    sgi = SGIListSerializer(read_only=True)
    annex_data = serializers.JSONField(required=False)
    class Meta:
        model = AccountOpeningRequest
        fields = [
            'id', 'customer', 'sgi', 'full_name', 'email', 'phone',
            'is_phone_linked_to_kyc_mobile_money', 'alternate_kyc_mobile_money_phone',
            'country_of_residence', 'nationality', 'customer_banks_current_account',
            'wants_digital_opening', 'wants_in_person_opening', 'available_minimum_amount', 'wants_100_percent_digital_sgi',
            'funding_by_visa', 'funding_by_mobile_money', 'funding_by_bank_transfer', 'funding_by_intermediary', 'funding_by_wu_mg_ria', 'wants_xamila_as_intermediary',
            'prefer_service_quality_over_fees', 'sources_of_income', 'investor_profile',
            'holder_info', 'photo', 'id_card_scan', 'annex_data',
            'wants_xamila_plus', 'authorize_xamila_to_receive_account_info',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'sgi', 'status', 'created_at', 'updated_at']


class ManagerContractSerializer(serializers.ModelSerializer):
    """Manager-facing contract serializer with KYC URLs and PDF link"""
    sgi = SGIListSerializer(read_only=True)
    sgi_name = serializers.SerializerMethodField()
    sgi_display = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    id_card_scan_url = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()

    annex_data = serializers.JSONField(required=False)
    class Meta:
        model = AccountOpeningRequest
        fields = [
            'id', 'created_at', 'updated_at', 'status',
            'sgi', 'sgi_name', 'sgi_display', 'full_name', 'email', 'phone',
            'country_of_residence', 'nationality', 'available_minimum_amount',
            'funding_by_visa', 'funding_by_mobile_money', 'funding_by_bank_transfer', 'funding_by_intermediary', 'funding_by_wu_mg_ria',
            'sources_of_income', 'investor_profile', 'customer_banks_current_account',
            'annex_data', 'photo_url', 'id_card_scan_url', 'pdf_url'
        ]
        read_only_fields = fields

    def get_sgi_name(self, obj):
        try:
            return obj.sgi.name if obj.sgi else None
        except Exception:
            return None

    def get_photo_url(self, obj):
        try:
            if not obj.photo:
                return None
            url = obj.photo.url
            request = self.context.get('request')
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_sgi_display(self, obj):
        # Prefer annotated sgi_name, then nested sgi.name, else None
        try:
            annotated = getattr(obj, 'sgi_name', None)
        except Exception:
            annotated = None
        try:
            nested = obj.sgi.name if obj.sgi else None
        except Exception:
            nested = None
        return annotated or nested

    def get_id_card_scan_url(self, obj):
        try:
            if not obj.id_card_scan:
                return None
            url = obj.id_card_scan.url
            request = self.context.get('request')
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_pdf_url(self, obj):
        request = self.context.get('request')
        base = request.build_absolute_uri('/')[:-1] if request else ''
        return f"{base}/api/account-opening/contract/pdf/?account_opening_request_id={obj.id}"


class ManagerClientListItemSerializer(serializers.Serializer):
    """Aggregated view of clients for a manager"""
    customer_id = serializers.UUIDField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    requests_count = serializers.IntegerField()
    last_request_at = serializers.DateTimeField()


class AccountOpeningRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer création de demande d'ouverture de compte (SGI optionnelle)"""
    sgi_id = serializers.UUIDField(required=False, allow_null=True, write_only=True)
    annex_data = serializers.JSONField(required=False)
    class Meta:
        model = AccountOpeningRequest
        fields = [
            'sgi_id', 'full_name', 'email', 'phone',
            'is_phone_linked_to_kyc_mobile_money', 'alternate_kyc_mobile_money_phone',
            'country_of_residence', 'nationality', 'customer_banks_current_account',
            'wants_digital_opening', 'wants_in_person_opening', 'available_minimum_amount', 'wants_100_percent_digital_sgi',
            'funding_by_visa', 'funding_by_mobile_money', 'funding_by_bank_transfer', 'funding_by_intermediary', 'funding_by_wu_mg_ria', 'wants_xamila_as_intermediary',
            'prefer_service_quality_over_fees', 'sources_of_income', 'investor_profile',
            'holder_info', 'photo', 'id_card_scan', 'annex_data', 'wants_xamila_plus', 'authorize_xamila_to_receive_account_info'
        ]
    def validate(self, attrs):
        # Normaliser les champs susceptibles d'arriver en multipart texte
        import json
        # customer_banks_current_account -> liste
        banks = attrs.get('customer_banks_current_account')
        if isinstance(banks, str):
            banks = banks.strip()
            if banks.startswith('['):
                try:
                    banks = json.loads(banks)
                except Exception:
                    # fallback: split by comma
                    banks = [s.strip() for s in banks.split(',') if s.strip()]
            else:
                banks = [s.strip() for s in banks.split(',') if s.strip()]
            attrs['customer_banks_current_account'] = banks

        # available_minimum_amount -> Decimal or None
        from decimal import Decimal, InvalidOperation
        amt = attrs.get('available_minimum_amount')
        if isinstance(amt, str) and amt != '':
            try:
                attrs['available_minimum_amount'] = Decimal(amt)
            except InvalidOperation:
                raise serializers.ValidationError({'available_minimum_amount': 'Montant invalide'})
        if amt in ('', None):
            attrs['available_minimum_amount'] = None

        # exiger au moins une méthode d'alimentation
        if not any([
            attrs.get('funding_by_visa'), attrs.get('funding_by_mobile_money'),
            attrs.get('funding_by_bank_transfer'), attrs.get('funding_by_intermediary'), attrs.get('funding_by_wu_mg_ria')
        ]):
            raise serializers.ValidationError("Sélectionnez au moins une méthode d'alimentation")
        # annex_data may come as JSON string; parse safely
        annex = attrs.get('annex_data')
        if isinstance(annex, str):
            try:
                import json
                attrs['annex_data'] = json.loads(annex)
            except Exception:
                attrs['annex_data'] = {}
        return attrs
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        user = self.context['request'].user
        sgi_id = validated_data.pop('sgi_id', None)
        sgi = None
        if sgi_id:
            try:
                sgi = SGI.objects.get(id=sgi_id)
            except SGI.DoesNotExist:
                raise serializers.ValidationError({'sgi_id': 'SGI introuvable'})
        
        # Log les fichiers reçus
        has_photo = 'photo' in validated_data and validated_data.get('photo')
        has_id_scan = 'id_card_scan' in validated_data and validated_data.get('id_card_scan')
        logger.info(f"Création AccountOpeningRequest - Photo: {has_photo}, CNI: {has_id_scan}")
        
        # Handle potential storage permission issues when saving files
        try:
            instance = AccountOpeningRequest.objects.create(customer=user, sgi=sgi, **validated_data)
            logger.info(f"✅ AccountOpeningRequest créé avec succès (ID: {instance.id})")
            return instance
        except (OSError, PermissionError) as e:
            # Retry without file fields
            logger.warning(f"⚠️ Erreur de permissions lors de la sauvegarde des fichiers: {e}")
            logger.warning("Nouvelle tentative sans les fichiers photo et CNI...")
            validated_data.pop('photo', None)
            validated_data.pop('id_card_scan', None)
            instance = AccountOpeningRequest.objects.create(customer=user, sgi=sgi, **validated_data)
            logger.warning(f"⚠️ AccountOpeningRequest créé SANS fichiers (ID: {instance.id})")
            return instance


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


class SGIRatingSerializer(serializers.ModelSerializer):
    """Serializer pour affichage de notation SGI"""
    customer = UserSerializer(read_only=True)
    class Meta:
        model = SGIRating
        fields = ['id', 'sgi', 'customer', 'score', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']


class SGIRatingCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/mettre à jour une note de SGI"""
    class Meta:
        model = SGIRating
        fields = ['sgi', 'score', 'comment']
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['customer'] = user
        # upsert unique (sgi, customer)
        rating, _created = SGIRating.objects.update_or_create(
            sgi=validated_data['sgi'], customer=user,
            defaults={
                'score': validated_data['score'],
                'comment': validated_data.get('comment', '')
            }
        )
        return rating


class ContractPrefillResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de préremplissage du contrat"""
    suggested_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    suggested_funding_source = serializers.CharField()
    required_documents = serializers.ListField(child=serializers.CharField())
    sgi = SGIListSerializer()
    terms = SGIAccountTermsSerializer(allow_null=True)


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
    """Serializer de base pour l'enregistrement des utilisateurs"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    id = serializers.UUIDField(required=False, allow_null=True)
    role = serializers.CharField(required=False)
    user_type = serializers.CharField(required=False, write_only=True)
    age_range = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role', 'user_type',
            'country', 'country_of_residence', 'age_range', 'gender'
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
        
        # Mapper user_type vers role si présent
        user_type = validated_data.pop('user_type', None)
        if user_type:
            validated_data['role'] = user_type
        
        # Si un ID est fourni, l'utiliser
        user_id = validated_data.pop('id', None)
        
        if user_id:
            user = User.objects.create_user(
                id=user_id,
                password=password,
                **validated_data
            )
        else:
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


class ResourceContentSerializer(serializers.ModelSerializer):
    """Serializer pour le contenu des ressources"""
    
    class Meta:
        model = ResourceContent
        fields = ['id', 'banner_title', 'banner_description', 'youtube_video_id', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminUserCreationSerializer(BaseUserRegistrationSerializer):
    """Serializer pour la création d'utilisateurs par l'admin"""
    
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    is_active = serializers.BooleanField(default=True)
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = BaseUserRegistrationSerializer.Meta.fields + ['role', 'is_active']
    
    def create(self, validated_data):
        return super().create(validated_data)


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer pour les permissions"""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'category', 'description']


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer pour les permissions de rôle"""
    permission = PermissionSerializer(read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'permission', 'is_granted']


class ContractSerializer(serializers.ModelSerializer):
    """Serializer lecture des contrats"""
    customer = UserSerializer(read_only=True)
    sgi = SGIListSerializer(read_only=True)
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'customer', 'sgi', 'investment_amount', 'funding_source',
            'bank_name', 'account_number', 'status', 'customer_notes', 'manager_notes', 'rejection_reason',
            'created_at', 'updated_at', 'approved_at', 'rejected_at'
        ]
        read_only_fields = ['id', 'contract_number', 'customer', 'sgi', 'status', 'created_at', 'updated_at', 'approved_at', 'rejected_at']


class ContractCreateSerializer(serializers.ModelSerializer):
    """Serializer création d'un contrat (soumission one-click)"""
    sgi_id = serializers.UUIDField(write_only=True)
    class Meta:
        model = Contract
        fields = ['sgi_id', 'investment_amount', 'funding_source', 'bank_name', 'account_number', 'customer_notes']
    def validate(self, attrs):
        return attrs
    def create(self, validated_data):
        user = self.context['request'].user
        sgi_id = validated_data.pop('sgi_id')
        try:
            sgi = SGI.objects.get(id=sgi_id, is_active=True)
        except SGI.DoesNotExist:
            raise serializers.ValidationError({'sgi_id': 'SGI introuvable'})
        contract = Contract.objects.create(customer=user, sgi=sgi, **validated_data)
        return contract


class ContractPrefillResponseSerializer(serializers.Serializer):
    """Données préremplies pour le contrat et pièces à fournir"""
    suggested_investment_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    suggested_funding_source = serializers.ChoiceField(choices=Contract.FUNDING_SOURCES)
    required_documents = serializers.ListField(child=serializers.CharField())
    sgi = SGIListSerializer()
    terms = SGIAccountTermsSerializer()


class CohorteSerializer(serializers.ModelSerializer):
    """Serializer pour les cohortes"""
    mois_display = serializers.CharField(source='get_mois_display', read_only=True)
    
    class Meta:
        model = Cohorte
        fields = [
            'id', 'code', 'nom', 'mois', 'mois_display', 'annee',
            'email_utilisateur', 'actif', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

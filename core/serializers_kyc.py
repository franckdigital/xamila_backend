"""
Serializers pour les modèles KYC (Know Your Customer)
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from .models_kyc import KYCProfile, KYCDocument, KYCVerificationLog
import mimetypes

User = get_user_model()


class KYCDocumentSerializer(serializers.ModelSerializer):
    """Serializer pour les documents KYC"""
    
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = KYCDocument
        fields = [
            'id', 'document_type', 'file', 'file_url', 'original_filename',
            'file_size', 'file_size_mb', 'mime_type', 'verification_status',
            'auto_verification_score', 'uploaded_at', 'verified_at',
            'rejection_reason'
        ]
        read_only_fields = [
            'id', 'file_url', 'file_size', 'file_size_mb', 'mime_type',
            'auto_verification_score', 'uploaded_at', 'verified_at',
            'verified_by', 'original_filename'
        ]
    
    def get_file_url(self, obj):
        """Retourne l'URL sécurisée du fichier"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_file_size_mb(self, obj):
        """Retourne la taille du fichier en MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None
    
    def validate_file(self, value):
        """Valide le fichier téléversé"""
        if not value:
            raise serializers.ValidationError("Aucun fichier fourni.")
        
        # Vérifier la taille du fichier (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"Le fichier est trop volumineux. Taille maximale: 10MB. "
                f"Taille actuelle: {round(value.size / (1024 * 1024), 2)}MB"
            )
        
        # Vérifier le type de fichier
        allowed_types = [
            'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
            'application/pdf', 'image/webp'
        ]
        
        # Détecter le type MIME
        mime_type = mimetypes.guess_type(value.name)[0]
        if hasattr(value, 'content_type'):
            mime_type = value.content_type
        
        if mime_type not in allowed_types:
            raise serializers.ValidationError(
                f"Type de fichier non autorisé: {mime_type}. "
                f"Types autorisés: {', '.join(allowed_types)}"
            )
        
        return value
    
    def create(self, validated_data):
        """Crée un nouveau document KYC"""
        file = validated_data['file']
        
        # Extraire les métadonnées du fichier
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['mime_type'] = getattr(file, 'content_type', 
                                            mimetypes.guess_type(file.name)[0])
        
        return super().create(validated_data)


class KYCProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil KYC"""
    
    documents = KYCDocumentSerializer(many=True, read_only=True)
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    is_kyc_complete = serializers.ReadOnlyField()
    completion_percentage = serializers.ReadOnlyField()
    user_email = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()
    
    class Meta:
        model = KYCProfile
        fields = [
            'id', 'user', 'user_email', 'user_phone',
            'first_name', 'last_name', 'middle_name', 'full_name',
            'date_of_birth', 'age', 'place_of_birth', 'nationality', 'gender',
            'address_line_1', 'address_line_2', 'city', 'state_province',
            'postal_code', 'country',
            'identity_document_type', 'identity_document_number',
            'identity_document_expiry', 'identity_document_issuing_country',
            'occupation', 'employer_name', 'monthly_income', 'source_of_funds',
            'kyc_status', 'risk_level',
            'identity_verification_status', 'address_verification_status',
            'selfie_verification_status',
            'verification_provider', 'verification_reference', 'verification_score',
            'submitted_at', 'reviewed_at', 'approved_at', 'rejected_at',
            'rejection_reason', 'is_kyc_complete', 'completion_percentage',
            'created_at', 'updated_at', 'documents'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'user_phone', 'full_name', 'age',
            'kyc_status', 'risk_level', 'identity_verification_status',
            'address_verification_status', 'selfie_verification_status',
            'verification_provider', 'verification_reference', 'verification_score',
            'submitted_at', 'reviewed_at', 'approved_at', 'rejected_at',
            'rejection_reason', 'is_kyc_complete', 'completion_percentage',
            'created_at', 'updated_at', 'reviewed_by'
        ]
    
    def get_user_email(self, obj):
        return obj.user.email if obj.user else None
    
    def get_user_phone(self, obj):
        return obj.user.phone if obj.user else None
    
    def validate_date_of_birth(self, value):
        """Valide la date de naissance"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not value:
            raise serializers.ValidationError("La date de naissance est obligatoire.")
        
        # Vérifier que la personne a au moins 18 ans
        today = timezone.now().date()
        min_age_date = today - timedelta(days=18*365.25)  # Approximation
        
        if value > min_age_date:
            raise serializers.ValidationError(
                "Vous devez avoir au moins 18 ans pour créer un compte."
            )
        
        # Vérifier que la date n'est pas dans le futur
        if value > today:
            raise serializers.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )
        
        # Vérifier que la personne n'a pas plus de 120 ans
        max_age_date = today - timedelta(days=120*365.25)
        if value < max_age_date:
            raise serializers.ValidationError(
                "Date de naissance invalide (âge maximum: 120 ans)."
            )
        
        return value
    
    def validate_identity_document_number(self, value):
        """Valide le numéro de document d'identité"""
        if not value:
            raise serializers.ValidationError(
                "Le numéro de document d'identité est obligatoire."
            )
        
        # Vérifier l'unicité du numéro de document
        if self.instance:
            # Mise à jour - exclure l'instance actuelle
            existing = KYCProfile.objects.filter(
                identity_document_number=value
            ).exclude(id=self.instance.id)
        else:
            # Création - vérifier tous les profils
            existing = KYCProfile.objects.filter(
                identity_document_number=value
            )
        
        if existing.exists():
            raise serializers.ValidationError(
                "Ce numéro de document d'identité est déjà utilisé."
            )
        
        return value
    
    def validate_monthly_income(self, value):
        """Valide les revenus mensuels"""
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Les revenus mensuels ne peuvent pas être négatifs."
            )
        return value


class KYCProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un profil KYC"""
    
    class Meta:
        model = KYCProfile
        fields = [
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'place_of_birth', 'nationality', 'gender',
            'address_line_1', 'address_line_2', 'city', 'state_province',
            'postal_code', 'country',
            'identity_document_type', 'identity_document_number',
            'identity_document_expiry', 'identity_document_issuing_country',
            'occupation', 'employer_name', 'monthly_income', 'source_of_funds'
        ]
    
    def validate_date_of_birth(self, value):
        """Valide la date de naissance"""
        return KYCProfileSerializer().validate_date_of_birth(value)
    
    def validate_identity_document_number(self, value):
        """Valide le numéro de document d'identité"""
        return KYCProfileSerializer().validate_identity_document_number(value)
    
    def create(self, validated_data):
        """Crée un nouveau profil KYC"""
        # L'utilisateur est automatiquement assigné depuis la vue
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class KYCProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'un profil KYC"""
    
    class Meta:
        model = KYCProfile
        fields = [
            'first_name', 'last_name', 'middle_name',
            'date_of_birth', 'place_of_birth', 'nationality', 'gender',
            'address_line_1', 'address_line_2', 'city', 'state_province',
            'postal_code', 'country',
            'identity_document_type', 'identity_document_number',
            'identity_document_expiry', 'identity_document_issuing_country',
            'occupation', 'employer_name', 'monthly_income', 'source_of_funds'
        ]
    
    def validate(self, attrs):
        """Valide que le profil peut être modifié"""
        if self.instance and self.instance.kyc_status in ['APPROVED', 'UNDER_REVIEW']:
            raise serializers.ValidationError(
                "Impossible de modifier un profil KYC approuvé ou en cours de révision."
            )
        return attrs
    
    def validate_date_of_birth(self, value):
        """Valide la date de naissance"""
        return KYCProfileSerializer().validate_date_of_birth(value)
    
    def validate_identity_document_number(self, value):
        """Valide le numéro de document d'identité"""
        return KYCProfileSerializer().validate_identity_document_number(value)


class KYCVerificationLogSerializer(serializers.ModelSerializer):
    """Serializer pour les logs de vérification KYC"""
    
    performed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = KYCVerificationLog
        fields = [
            'id', 'action_type', 'description',
            'performed_by', 'performed_by_name',
            'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return "Système automatique"


class KYCStatusUpdateSerializer(serializers.Serializer):
    """Serializer pour la mise à jour du statut KYC (admin uniquement)"""
    
    status = serializers.ChoiceField(choices=KYCProfile.KYC_STATUS_CHOICES)
    reason = serializers.CharField(required=False, allow_blank=True)
    verification_provider = serializers.CharField(required=False, allow_blank=True)
    verification_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False,
        min_value=0, max_value=100
    )
    
    def validate(self, attrs):
        status = attrs.get('status')
        reason = attrs.get('reason', '')
        
        # Si le statut est "rejeté", une raison est obligatoire
        if status == 'REJECTED' and not reason:
            raise serializers.ValidationError({
                'reason': 'Une raison est obligatoire pour rejeter un profil KYC.'
            })
        
        return attrs


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer pour l'upload de documents KYC"""
    
    document_type = serializers.ChoiceField(choices=KYCDocument.DOCUMENT_TYPES)
    file = serializers.FileField()
    
    def validate_file(self, value):
        """Valide le fichier téléversé"""
        return KYCDocumentSerializer().validate_file(value)
    
    def create(self, validated_data):
        """Crée un nouveau document KYC"""
        kyc_profile = self.context['kyc_profile']
        
        # Supprimer l'ancien document du même type s'il existe
        KYCDocument.objects.filter(
            kyc_profile=kyc_profile,
            document_type=validated_data['document_type']
        ).delete()
        
        # Créer le nouveau document
        validated_data['kyc_profile'] = kyc_profile
        
        file = validated_data['file']
        validated_data['original_filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['mime_type'] = getattr(file, 'content_type', 
                                            mimetypes.guess_type(file.name)[0])
        
        return KYCDocument.objects.create(**validated_data)


class KYCDashboardSerializer(serializers.Serializer):
    """Serializer pour le dashboard KYC (statistiques)"""
    
    total_profiles = serializers.IntegerField()
    pending_profiles = serializers.IntegerField()
    under_review_profiles = serializers.IntegerField()
    approved_profiles = serializers.IntegerField()
    rejected_profiles = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    average_processing_time = serializers.FloatField()  # en heures
    recent_submissions = KYCProfileSerializer(many=True)
    
    def to_representation(self, instance):
        """Calcule les statistiques KYC"""
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Statistiques de base
        profiles = KYCProfile.objects.all()
        status_counts = profiles.values('kyc_status').annotate(count=Count('id'))
        
        stats = {
            'total_profiles': profiles.count(),
            'pending_profiles': 0,
            'under_review_profiles': 0,
            'approved_profiles': 0,
            'rejected_profiles': 0,
        }
        
        for status_count in status_counts:
            status = status_count['kyc_status']
            count = status_count['count']
            
            if status == 'PENDING':
                stats['pending_profiles'] = count
            elif status == 'UNDER_REVIEW':
                stats['under_review_profiles'] = count
            elif status == 'APPROVED':
                stats['approved_profiles'] = count
            elif status == 'REJECTED':
                stats['rejected_profiles'] = count
        
        # Taux de completion
        if stats['total_profiles'] > 0:
            stats['completion_rate'] = (
                stats['approved_profiles'] / stats['total_profiles']
            ) * 100
        else:
            stats['completion_rate'] = 0
        
        # Temps de traitement moyen (en heures)
        processed_profiles = profiles.filter(
            kyc_status__in=['APPROVED', 'REJECTED'],
            submitted_at__isnull=False,
            reviewed_at__isnull=False
        )
        
        if processed_profiles.exists():
            avg_processing = processed_profiles.aggregate(
                avg_time=Avg(
                    models.F('reviewed_at') - models.F('submitted_at')
                )
            )['avg_time']
            
            if avg_processing:
                stats['average_processing_time'] = avg_processing.total_seconds() / 3600
            else:
                stats['average_processing_time'] = 0
        else:
            stats['average_processing_time'] = 0
        
        # Soumissions récentes (7 derniers jours)
        recent_date = timezone.now() - timedelta(days=7)
        recent_profiles = profiles.filter(
            created_at__gte=recent_date
        ).order_by('-created_at')[:10]
        
        stats['recent_submissions'] = KYCProfileSerializer(
            recent_profiles, many=True, context=self.context
        ).data
        
        return stats

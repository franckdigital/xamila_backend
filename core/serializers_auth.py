"""
Serializers pour l'authentification et l'inscription des utilisateurs
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class CustomerRegistrationSerializer(serializers.Serializer):
    """
    Serializer pour l'inscription d'un nouveau client CUSTOMER
    """
    email = serializers.EmailField(
        help_text="Adresse email du client (sera utilisée pour la connexion)"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Mot de passe sécurisé (minimum 8 caractères)"
    )
    phone = serializers.CharField(
        max_length=20,
        help_text="Numéro de téléphone au format international (+33...)"
    )
    first_name = serializers.CharField(
        max_length=30,
        help_text="Prénom du client"
    )
    last_name = serializers.CharField(
        max_length=30,
        help_text="Nom de famille du client"
    )

    def validate_email(self, value):
        """Valide que l'email n'est pas déjà utilisé"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée.")
        return value

    def validate_password(self, value):
        """Valide la force du mot de passe"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate_phone(self, value):
        """Valide le format du numéro de téléphone"""
        # Format international requis
        if not re.match(r'^\+[1-9]\d{1,14}$', value):
            raise serializers.ValidationError(
                "Le numéro de téléphone doit être au format international (+33...)"
            )
        
        # Vérifier que le numéro n'est pas déjà utilisé
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        
        return value


class CustomerRegistrationResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse d'inscription client
    """
    message = serializers.CharField(help_text="Message de confirmation")
    user_id = serializers.UUIDField(help_text="ID unique de l'utilisateur créé")
    email = serializers.EmailField(help_text="Email de l'utilisateur")
    phone = serializers.CharField(help_text="Téléphone de l'utilisateur")
    otp_sent = serializers.BooleanField(help_text="Codes OTP envoyés avec succès")
    next_step = serializers.CharField(help_text="Prochaine étape du processus")


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer pour la vérification des codes OTP
    """
    user_id = serializers.UUIDField(help_text="ID de l'utilisateur à vérifier")
    email_otp = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="Code OTP reçu par email (6 chiffres)"
    )
    sms_otp = serializers.CharField(
        max_length=6,
        min_length=6,
        help_text="Code OTP reçu par SMS (6 chiffres)"
    )

    def validate_email_otp(self, value):
        """Valide le format du code OTP email"""
        if not value.isdigit():
            raise serializers.ValidationError("Le code OTP doit contenir uniquement des chiffres.")
        return value

    def validate_sms_otp(self, value):
        """Valide le format du code OTP SMS"""
        if not value.isdigit():
            raise serializers.ValidationError("Le code OTP doit contenir uniquement des chiffres.")
        return value


class OTPVerificationResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse de vérification OTP
    """
    message = serializers.CharField(help_text="Message de confirmation")
    access_token = serializers.CharField(help_text="Token d'accès JWT")
    refresh_token = serializers.CharField(help_text="Token de rafraîchissement JWT")
    user_id = serializers.UUIDField(help_text="ID de l'utilisateur")
    email = serializers.EmailField(help_text="Email de l'utilisateur")
    is_verified = serializers.BooleanField(help_text="Compte vérifié avec succès")
    next_step = serializers.CharField(help_text="Prochaine étape recommandée")


class CustomerLoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion client
    """
    email = serializers.EmailField(help_text="Adresse email du client")
    password = serializers.CharField(
        write_only=True,
        help_text="Mot de passe du client"
    )


class CustomerLoginResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse de connexion client
    """
    message = serializers.CharField(help_text="Message de confirmation")
    access_token = serializers.CharField(help_text="Token d'accès JWT")
    refresh_token = serializers.CharField(help_text="Token de rafraîchissement JWT")
    user_id = serializers.UUIDField(help_text="ID de l'utilisateur")
    email = serializers.EmailField(help_text="Email de l'utilisateur")
    role = serializers.CharField(help_text="Rôle de l'utilisateur")
    kyc_status = serializers.CharField(help_text="Statut KYC de l'utilisateur")
    kyc_completion = serializers.FloatField(help_text="Pourcentage de completion KYC")


class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer pour le renvoi d'OTP
    """
    user_id = serializers.UUIDField(help_text="ID de l'utilisateur")
    otp_type = serializers.ChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Les deux')],
        default='both',
        help_text="Type d'OTP à renvoyer"
    )


class ResendOTPResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse de renvoi d'OTP
    """
    message = serializers.CharField(help_text="Message de confirmation")
    otp_sent = serializers.BooleanField(help_text="OTP renvoyé avec succès")
    otp_type = serializers.CharField(help_text="Type d'OTP envoyé")
    expires_at = serializers.DateTimeField(help_text="Date d'expiration du code OTP")


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer pour les réponses d'erreur standardisées
    """
    error = serializers.CharField(help_text="Message d'erreur principal")
    details = serializers.DictField(
        required=False,
        help_text="Détails spécifiques de l'erreur (validation, etc.)"
    )
    code = serializers.CharField(
        required=False,
        help_text="Code d'erreur spécifique"
    )

"""
Utilitaires pour l'envoi d'emails OTP et notifications
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_email_otp(email, otp_code, first_name=None):
    """
    Envoie un code OTP par email avec template HTML
    
    Args:
        email (str): Adresse email destinataire
        otp_code (str): Code OTP à envoyer
        first_name (str): Prénom de l'utilisateur (optionnel)
    
    Returns:
        dict: Résultat de l'envoi (success, error)
    """
    
    try:
        # Contexte pour le template
        context = {
            'otp_code': otp_code,
            'first_name': first_name or 'Cher utilisateur',
            'company_name': 'XAMILA',
            'validity_minutes': 10
        }
        
        # Générer le contenu HTML et texte
        html_content = render_to_string('emails/otp_verification.html', context)
        text_content = render_to_string('emails/otp_verification.txt', context)
        
        subject = f"Code de vérification XAMILA: {otp_code}"
        
        # Créer l'email avec version HTML et texte
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_message.attach_alternative(html_content, "text/html")
        
        # Envoyer l'email
        email_message.send()
        
        logger.info(f"Email OTP envoyé avec succès à {email}")
        return {
            'success': True,
            'message': 'Email OTP envoyé avec succès'
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email OTP à {email}: {str(e)}")
        
        # Fallback: envoi simple sans template
        try:
            simple_message = f"""
Bonjour {first_name or 'Cher utilisateur'},

Votre code de vérification XAMILA est: {otp_code}

Ce code expire dans 10 minutes. Ne le partagez avec personne.

Cordialement,
L'équipe XAMILA
            """
            
            send_mail(
                subject=f"Code de vérification XAMILA: {otp_code}",
                message=simple_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            
            logger.info(f"Email OTP simple envoyé avec succès à {email}")
            return {
                'success': True,
                'message': 'Email OTP envoyé avec succès (format simple)'
            }
            
        except Exception as fallback_error:
            logger.error(f"Erreur lors de l'envoi de l'email OTP simple à {email}: {str(fallback_error)}")
            return {
                'success': False,
                'error': f'Erreur lors de l\'envoi de l\'email: {str(fallback_error)}'
            }


def send_kyc_status_email(user, kyc_profile, status, reason=None):
    """
    Envoie un email de notification de changement de statut KYC
    
    Args:
        user: Instance utilisateur
        kyc_profile: Instance KYCProfile
        status (str): Nouveau statut KYC
        reason (str): Raison du changement (optionnel)
    
    Returns:
        dict: Résultat de l'envoi
    """
    
    try:
        # Contexte pour le template
        context = {
            'user': user,
            'kyc_profile': kyc_profile,
            'status': status,
            'status_display': dict(kyc_profile.KYC_STATUS_CHOICES)[status],
            'reason': reason,
            'company_name': 'XAMILA'
        }
        
        # Déterminer le template selon le statut
        if status == 'APPROVED':
            template_name = 'kyc_approved'
            subject = "Votre profil KYC a été approuvé"
        elif status == 'REJECTED':
            template_name = 'kyc_rejected'
            subject = "Votre profil KYC nécessite des corrections"
        elif status == 'UNDER_REVIEW':
            template_name = 'kyc_under_review'
            subject = "Votre profil KYC est en cours de révision"
        else:
            template_name = 'kyc_status_update'
            subject = f"Mise à jour de votre profil KYC - {context['status_display']}"
        
        # Générer le contenu
        html_content = render_to_string(f'emails/{template_name}.html', context)
        text_content = render_to_string(f'emails/{template_name}.txt', context)
        
        # Créer et envoyer l'email
        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
        
        logger.info(f"Email de statut KYC envoyé avec succès à {user.email}")
        return {
            'success': True,
            'message': 'Email de notification KYC envoyé avec succès'
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email KYC à {user.email}: {str(e)}")
        
        # Fallback: email simple
        try:
            status_messages = {
                'APPROVED': 'Félicitations ! Votre profil KYC a été approuvé. Vous pouvez maintenant accéder à tous nos services.',
                'REJECTED': f'Votre profil KYC nécessite des corrections. Raison: {reason or "Non spécifiée"}. Veuillez vous connecter pour corriger les informations.',
                'UNDER_REVIEW': 'Votre profil KYC est en cours de révision par notre équipe. Nous vous tiendrons informé.',
            }
            
            message = f"""
Bonjour {user.first_name},

{status_messages.get(status, f'Le statut de votre profil KYC a été mis à jour: {dict(kyc_profile.KYC_STATUS_CHOICES)[status]}')}

Cordialement,
L'équipe XAMILA
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return {
                'success': True,
                'message': 'Email de notification KYC simple envoyé avec succès'
            }
            
        except Exception as fallback_error:
            logger.error(f"Erreur lors de l'envoi de l'email KYC simple: {str(fallback_error)}")
            return {
                'success': False,
                'error': f'Erreur lors de l\'envoi de l\'email: {str(fallback_error)}'
            }


def send_welcome_email(user):
    """
    Envoie un email de bienvenue après activation du compte
    """
    try:
        context = {
            'user': user,
            'company_name': 'XAMILA',
            'login_url': f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        html_content = render_to_string('emails/welcome.html', context)
        text_content = render_to_string('emails/welcome.txt', context)
        
        email_message = EmailMultiAlternatives(
            subject="Bienvenue sur XAMILA !",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
        
        logger.info(f"Email de bienvenue envoyé à {user.email}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de bienvenue: {str(e)}")
        return {'success': False, 'error': str(e)}


def send_password_reset_email(user, reset_token):
    """
    Envoie un email de réinitialisation de mot de passe
    """
    try:
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}" if hasattr(settings, 'FRONTEND_URL') else '#'
        
        context = {
            'user': user,
            'reset_url': reset_url,
            'company_name': 'XAMILA',
            'validity_hours': 24
        }
        
        html_content = render_to_string('emails/password_reset.html', context)
        text_content = render_to_string('emails/password_reset.txt', context)
        
        email_message = EmailMultiAlternatives(
            subject="Réinitialisation de votre mot de passe XAMILA",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()
        
        logger.info(f"Email de réinitialisation envoyé à {user.email}")
        return {'success': True}
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {str(e)}")
        return {'success': False, 'error': str(e)}

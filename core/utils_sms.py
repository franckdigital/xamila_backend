"""
Utilitaires pour l'envoi de SMS OTP
Intégration avec des services SMS comme Twilio, Nexmo, etc.
"""

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_sms_otp(phone_number, otp_code, service='twilio'):
    """
    Envoie un code OTP par SMS
    
    Args:
        phone_number (str): Numéro de téléphone au format international
        otp_code (str): Code OTP à envoyer
        service (str): Service SMS à utiliser ('twilio', 'nexmo', 'mock')
    
    Returns:
        dict: Résultat de l'envoi (success, message_id, error)
    """
    
    # Formatage du message
    message = f"Votre code de vérification XAMILA est: {otp_code}. Ce code expire dans 10 minutes. Ne le partagez avec personne."
    
    if service == 'twilio':
        return send_sms_twilio(phone_number, message)
    elif service == 'nexmo':
        return send_sms_nexmo(phone_number, message)
    elif service == 'mock' or settings.DEBUG:
        return send_sms_mock(phone_number, message, otp_code)
    else:
        logger.error(f"Service SMS non supporté: {service}")
        return {
            'success': False,
            'error': f'Service SMS non supporté: {service}'
        }


def send_sms_twilio(phone_number, message):
    """
    Envoie un SMS via Twilio
    """
    try:
        from twilio.rest import Client
        
        # Configuration Twilio depuis les settings
        account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("Configuration Twilio incomplète")
            return {
                'success': False,
                'error': 'Configuration Twilio incomplète'
            }
        
        client = Client(account_sid, auth_token)
        
        message_instance = client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )
        
        logger.info(f"SMS envoyé avec succès via Twilio: {message_instance.sid}")
        return {
            'success': True,
            'message_id': message_instance.sid,
            'service': 'twilio'
        }
        
    except ImportError:
        logger.error("Twilio SDK non installé")
        return {
            'success': False,
            'error': 'Twilio SDK non installé. Installez: pip install twilio'
        }
    except Exception as e:
        logger.error(f"Erreur Twilio: {str(e)}")
        return {
            'success': False,
            'error': f'Erreur Twilio: {str(e)}'
        }


def send_sms_nexmo(phone_number, message):
    """
    Envoie un SMS via Nexmo (Vonage)
    """
    try:
        import vonage
        
        # Configuration Nexmo depuis les settings
        api_key = getattr(settings, 'NEXMO_API_KEY', None)
        api_secret = getattr(settings, 'NEXMO_API_SECRET', None)
        from_number = getattr(settings, 'NEXMO_FROM_NUMBER', 'XAMILA')
        
        if not all([api_key, api_secret]):
            logger.error("Configuration Nexmo incomplète")
            return {
                'success': False,
                'error': 'Configuration Nexmo incomplète'
            }
        
        client = vonage.Client(key=api_key, secret=api_secret)
        sms = vonage.Sms(client)
        
        response = sms.send_message({
            'from': from_number,
            'to': phone_number,
            'text': message
        })
        
        if response['messages'][0]['status'] == '0':
            logger.info(f"SMS envoyé avec succès via Nexmo: {response['messages'][0]['message-id']}")
            return {
                'success': True,
                'message_id': response['messages'][0]['message-id'],
                'service': 'nexmo'
            }
        else:
            error_text = response['messages'][0]['error-text']
            logger.error(f"Erreur Nexmo: {error_text}")
            return {
                'success': False,
                'error': f'Erreur Nexmo: {error_text}'
            }
        
    except ImportError:
        logger.error("Vonage SDK non installé")
        return {
            'success': False,
            'error': 'Vonage SDK non installé. Installez: pip install vonage'
        }
    except Exception as e:
        logger.error(f"Erreur Nexmo: {str(e)}")
        return {
            'success': False,
            'error': f'Erreur Nexmo: {str(e)}'
        }


def send_sms_mock(phone_number, message, otp_code):
    """
    Simulation d'envoi SMS pour le développement
    """
    logger.info(f"[MOCK SMS] Envoi simulé vers {phone_number}")
    logger.info(f"[MOCK SMS] Message: {message}")
    logger.info(f"[MOCK SMS] Code OTP: {otp_code}")
    
    # En mode développement, afficher le code dans les logs
    print(f"\n{'='*50}")
    print(f"SMS MOCK - Numéro: {phone_number}")
    print(f"Code OTP: {otp_code}")
    print(f"Message: {message}")
    print(f"{'='*50}\n")
    
    return {
        'success': True,
        'message_id': f'mock_{phone_number}_{otp_code}',
        'service': 'mock'
    }


def validate_phone_number(phone_number):
    """
    Valide le format du numéro de téléphone
    
    Args:
        phone_number (str): Numéro à valider
    
    Returns:
        dict: Résultat de la validation (valid, formatted_number, error)
    """
    import re
    
    # Supprimer les espaces et caractères spéciaux
    cleaned = re.sub(r'[^\d+]', '', phone_number)
    
    # Vérifier le format international
    if not cleaned.startswith('+'):
        # Ajouter le préfixe par défaut (exemple: +33 pour la France)
        default_country_code = getattr(settings, 'DEFAULT_COUNTRY_CODE', '+33')
        if cleaned.startswith('0'):
            cleaned = cleaned[1:]  # Supprimer le 0 initial
        cleaned = default_country_code + cleaned
    
    # Vérifier la longueur (entre 10 et 15 chiffres après le +)
    digits_only = cleaned[1:]  # Sans le +
    if len(digits_only) < 10 or len(digits_only) > 15:
        return {
            'valid': False,
            'error': 'Numéro de téléphone invalide (longueur incorrecte)'
        }
    
    # Vérifier que ce sont bien des chiffres
    if not digits_only.isdigit():
        return {
            'valid': False,
            'error': 'Numéro de téléphone invalide (caractères non numériques)'
        }
    
    return {
        'valid': True,
        'formatted_number': cleaned
    }


def get_sms_service():
    """
    Détermine quel service SMS utiliser selon la configuration
    """
    if settings.DEBUG:
        return 'mock'
    
    # Vérifier la configuration Twilio
    if all([
        getattr(settings, 'TWILIO_ACCOUNT_SID', None),
        getattr(settings, 'TWILIO_AUTH_TOKEN', None),
        getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    ]):
        return 'twilio'
    
    # Vérifier la configuration Nexmo
    if all([
        getattr(settings, 'NEXMO_API_KEY', None),
        getattr(settings, 'NEXMO_API_SECRET', None)
    ]):
        return 'nexmo'
    
    # Par défaut, utiliser le mode mock
    logger.warning("Aucun service SMS configuré, utilisation du mode mock")
    return 'mock'


# Configuration par défaut pour les settings Django
SMS_SETTINGS_TEMPLATE = """
# Configuration SMS
SMS_SERVICE = 'mock'  # 'twilio', 'nexmo', 'mock'
DEFAULT_COUNTRY_CODE = '+33'  # Code pays par défaut

# Twilio
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'

# Nexmo/Vonage
NEXMO_API_KEY = 'your_api_key'
NEXMO_API_SECRET = 'your_api_secret'
NEXMO_FROM_NUMBER = 'XAMILA'
"""

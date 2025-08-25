#!/usr/bin/env python
"""
Script pour tester l'envoi d'emails SMTP
Usage: python test_email.py
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xamila.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_sending():
    """Test l'envoi d'email avec la configuration actuelle"""
    
    print("=== Test d'envoi d'email ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    try:
        # Test d'envoi d'email
        subject = "Test Email - Xamila Platform"
        message = """
        Bonjour,
        
        Ceci est un email de test pour vérifier la configuration SMTP.
        
        Code de test: 123456
        
        Cordialement,
        L'équipe XAMILA
        """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['franckalain.digital@gmail.com']  # Email de test
        
        print("Envoi de l'email de test...")
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        print("✅ Email envoyé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_sending()
    sys.exit(0 if success else 1)

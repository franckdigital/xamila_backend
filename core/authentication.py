# -*- coding: utf-8 -*-
"""
Backend d'authentification personnalisé pour XAMILA
Permet la connexion avec email ou téléphone
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import re

User = get_user_model()


class EmailOrPhoneBackend(ModelBackend):
    """
    Backend d'authentification personnalisé qui permet la connexion
    avec email ou numéro de téléphone
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        # Déterminer si c'est un email ou un téléphone
        is_email = self.is_email(username)
        is_phone = self.is_phone(username)
        
        try:
            if is_email:
                # Authentification par email
                user = User.objects.get(email=username)
            elif is_phone:
                # Authentification par téléphone
                # Normaliser le numéro de téléphone
                normalized_phone = self.normalize_phone(username)
                user = User.objects.get(phone=normalized_phone)
            else:
                # Si ce n'est ni email ni téléphone, essayer par email d'abord
                user = User.objects.get(Q(email=username) | Q(phone=username))
            
            # Vérifier le mot de passe
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except User.DoesNotExist:
            # Essayer de chercher dans les deux champs
            try:
                user = User.objects.get(Q(email=username) | Q(phone=username))
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except User.DoesNotExist:
                pass
        
        return None
    
    def is_email(self, username):
        """Vérifier si le username est un email"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, username) is not None
    
    def is_phone(self, username):
        """Vérifier si le username est un numéro de téléphone"""
        # Accepter les formats: +33123456789, 0123456789, 123456789
        phone_pattern = r'^(\+\d{1,3})?[0-9\s\-\(\)]{8,15}$'
        return re.match(phone_pattern, username.replace(' ', '').replace('-', '')) is not None
    
    def normalize_phone(self, phone):
        """Normaliser le numéro de téléphone"""
        # Supprimer espaces, tirets, parenthèses
        normalized = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Si commence par 0, remplacer par +33 (France)
        if normalized.startswith('0'):
            normalized = '+33' + normalized[1:]
        
        # Si commence par 33 (sans +), ajouter le +
        elif normalized.startswith('33') and not normalized.startswith('+'):
            normalized = '+' + normalized
            
        # Si ne commence pas par + et n'est pas un format international, ajouter +33
        elif not normalized.startswith('+') and len(normalized) >= 9:
            # Si c'est un numéro français (9-10 chiffres), ajouter +33
            if len(normalized) in [9, 10]:
                normalized = '+33' + normalized
            
        return normalized
    
    def get_user(self, user_id):
        """Récupérer un utilisateur par son ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

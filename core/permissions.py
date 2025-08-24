# -*- coding: utf-8 -*-
"""
Permissions personnalisées pour la plateforme XAMILA
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission pour les administrateurs uniquement
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsSGIManagerOrAdmin(permissions.BasePermission):
    """
    Permission pour les managers SGI ou administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['SGI_MANAGER', 'ADMIN']
        )


class IsInstructorOrAdmin(permissions.BasePermission):
    """
    Permission pour les instructeurs ou administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['INSTRUCTOR', 'ADMIN']
        )


class IsSupportOrAdmin(permissions.BasePermission):
    """
    Permission pour le support ou administrateurs
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['SUPPORT', 'ADMIN']
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission pour le propriétaire de l'objet ou administrateur
    """
    def has_object_permission(self, request, view, obj):
        # Administrateurs ont accès à tout
        if request.user.role == 'ADMIN':
            return True
        
        # Vérifier si l'objet a un attribut 'user' ou 'owner'
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsVerifiedUser(permissions.BasePermission):
    """
    Permission pour les utilisateurs vérifiés uniquement
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class CanAccessLearningContent(permissions.BasePermission):
    """
    Permission pour accéder au contenu d'apprentissage
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['STUDENT', 'INSTRUCTOR', 'ADMIN']
        )


class CanManageContent(permissions.BasePermission):
    """
    Permission pour gérer le contenu (créer, modifier, supprimer)
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['INSTRUCTOR', 'ADMIN']
        )

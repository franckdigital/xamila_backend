from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime
import uuid
from .models import Cohorte

User = get_user_model()

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cohortes_list_create(request):
    """
    GET: Récupère la liste des cohortes avec le nombre d'utilisateurs
    POST: Crée une nouvelle cohorte
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':
            # Récupérer toutes les cohortes existantes
            cohortes_queryset = Cohorte.objects.all().order_by('-annee', '-mois')
            
            cohortes = []
            for cohorte in cohortes_queryset:
                cohortes.append({
                    'id': str(cohorte.id),
                    'code': cohorte.code,
                    'nom': cohorte.nom,
                    'date_creation': cohorte.created_at.isoformat(),
                    'actif': cohorte.actif,
                    'nombre_utilisateurs': 1,  # Une cohorte = un utilisateur dans ce modèle
                    'mois': cohorte.mois,
                    'annee': cohorte.annee,
                    'email_utilisateur': cohorte.email_utilisateur
                })

            return Response({
                'results': cohortes,
                'count': len(cohortes)
            })

        elif request.method == 'POST':
            # Créer une nouvelle cohorte
            mois = request.data.get('mois')
            annee = request.data.get('annee')
            email_utilisateur = request.data.get('email_utilisateur', '').strip()

            # Validation des données
            if not mois or not annee:
                return Response({
                    'error': 'Le mois et l\'année sont obligatoires'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not email_utilisateur:
                return Response({
                    'error': 'L\'email utilisateur est obligatoire'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                mois = int(mois)
                annee = int(annee)
                if mois < 1 or mois > 12:
                    raise ValueError("Mois invalide")
            except (ValueError, TypeError):
                return Response({
                    'error': 'Mois et année doivent être des nombres valides'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Trouver l'utilisateur
            try:
                user = User.objects.get(email=email_utilisateur)
            except User.DoesNotExist:
                return Response({
                    'error': f'Utilisateur avec l\'email {email_utilisateur} non trouvé'
                }, status=status.HTTP_404_NOT_FOUND)

            # Vérifier si une cohorte existe déjà pour cet utilisateur/mois/année
            existing_cohorte = Cohorte.objects.filter(
                user=user,
                mois=mois,
                annee=annee
            ).first()

            if existing_cohorte:
                return Response({
                    'success': False,
                    'message': f'Une cohorte existe déjà pour {email_utilisateur} en {dict(Cohorte.MOIS_CHOICES)[mois]} {annee}',
                    'cohorte': {
                        'id': str(existing_cohorte.id),
                        'code': existing_cohorte.code,
                        'nom': existing_cohorte.nom,
                        'mois': existing_cohorte.mois,
                        'annee': existing_cohorte.annee,
                        'email_utilisateur': existing_cohorte.email_utilisateur
                    }
                }, status=status.HTTP_200_OK)

            # Créer une nouvelle cohorte
            code_cohorte = f"COHORTE{annee}-{mois:02d}-{user.username}"
            
            # Générer le nom automatiquement
            mois_nom = dict(Cohorte.MOIS_CHOICES)[mois]
            nom = f"Cohorte {mois_nom} {annee}"

            cohorte = Cohorte.objects.create(
                code=code_cohorte,
                nom=nom,
                mois=mois,
                annee=annee,
                user=user,
                email_utilisateur=email_utilisateur
            )

            return Response({
                'success': True,
                'message': 'Cohorte créée avec succès',
                'cohorte': {
                    'id': str(cohorte.id),
                    'code': cohorte.code,
                    'nom': cohorte.nom,
                    'mois': cohorte.mois,
                    'annee': cohorte.annee,
                    'email_utilisateur': cohorte.email_utilisateur,
                    'date_creation': cohorte.created_at.isoformat(),
                    'actif': cohorte.actif
                }
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'opération: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cohorte_users(request, cohorte_code):
    """
    Récupère les utilisateurs d'une cohorte spécifique
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        # Trouver la cohorte par son code
        try:
            cohorte = Cohorte.objects.get(code=cohorte_code)
        except Cohorte.DoesNotExist:
            return Response({
                'error': f'Cohorte avec le code {cohorte_code} non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)

        # Retourner l'utilisateur associé à cette cohorte
        user = cohorte.user
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'cohorte_code': cohorte.code,
            'cohorte_nom': cohorte.nom
        }

        return Response({
            'results': [user_data],
            'count': 1
        })

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des utilisateurs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_cohorte(request, cohorte_id):
    """
    Met à jour une cohorte ou toggle son statut actif
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        # Trouver la cohorte
        try:
            cohorte = Cohorte.objects.get(id=cohorte_id)
        except Cohorte.DoesNotExist:
            return Response({
                'error': 'Cohorte non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            # Toggle du statut actif
            if 'actif' in request.data:
                cohorte.actif = request.data['actif']
                cohorte.save()
                
                return Response({
                    'success': True,
                    'message': f'Cohorte {"activée" if cohorte.actif else "désactivée"} avec succès',
                    'cohorte': {
                        'id': str(cohorte.id),
                        'code': cohorte.code,
                        'nom': cohorte.nom,
                        'actif': cohorte.actif,
                        'mois': cohorte.mois,
                        'annee': cohorte.annee,
                        'email_utilisateur': cohorte.email_utilisateur
                    }
                })
            else:
                return Response({
                    'error': 'Le champ "actif" est requis pour PATCH'
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            # Mise à jour complète (à implémenter si nécessaire)
            return Response({
                'message': 'Mise à jour complète des cohortes non implémentée'
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

    except Exception as e:
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cohorte(request, cohorte_id):
    """
    Supprime une cohorte
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        # Trouver la cohorte
        try:
            cohorte = Cohorte.objects.get(id=cohorte_id)
        except Cohorte.DoesNotExist:
            return Response({
                'error': 'Cohorte non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)

        # Sauvegarder les infos avant suppression
        cohorte_info = {
            'code': cohorte.code,
            'nom': cohorte.nom
        }

        # Supprimer la cohorte
        cohorte.delete()

        return Response({
            'success': True,
            'message': f'Cohorte "{cohorte_info["nom"]}" supprimée avec succès'
        })

    except Exception as e:
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

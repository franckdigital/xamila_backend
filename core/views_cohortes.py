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
            # Récupérer tous les codes de cohorte uniques avec statistiques
            cohortes_data = User.objects.exclude(
                code_cohorte__isnull=True
            ).exclude(
                code_cohorte__exact=''
            ).values('code_cohorte').annotate(
                nombre_utilisateurs=Count('id')
            ).order_by('code_cohorte')

            cohortes = []
            for idx, cohorte_data in enumerate(cohortes_data):
                # Récupérer un utilisateur de cette cohorte pour obtenir les détails
                sample_user = User.objects.filter(
                    code_cohorte=cohorte_data['code_cohorte']
                ).first()
                
                cohortes.append({
                    'id': idx + 1,
                    'code': cohorte_data['code_cohorte'],
                    'nom': f"Cohorte {cohorte_data['code_cohorte']}",
                    'date_creation': sample_user.date_joined.isoformat() if sample_user else timezone.now().isoformat(),
                    'actif': True,
                    'nombre_utilisateurs': cohorte_data['nombre_utilisateurs']
                })

            return Response({
                'results': cohortes,
                'count': len(cohortes)
            })

        elif request.method == 'POST':
            # Créer une nouvelle cohorte
            nom = request.data.get('nom', '').strip()
            mois = request.data.get('mois')
            annee = request.data.get('annee')
            email_utilisateur = request.data.get('email_utilisateur', '').strip()

            # Validation des données
            if not nom:
                return Response({
                    'error': 'Le nom de la cohorte est obligatoire'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not mois or not annee:
                return Response({
                    'error': 'Le mois et l\'année sont obligatoires'
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

            # Générer le code de cohorte automatiquement
            code_cohorte = f"COH{annee}{mois:02d}{uuid.uuid4().hex[:6].upper()}"

            # Vérifier que le code n'existe pas déjà
            while User.objects.filter(code_cohorte=code_cohorte).exists():
                code_cohorte = f"COH{annee}{mois:02d}{uuid.uuid4().hex[:6].upper()}"

            # Si un email utilisateur est fourni, l'assigner à cette cohorte
            if email_utilisateur:
                try:
                    user = User.objects.get(email=email_utilisateur)
                    user.code_cohorte = code_cohorte
                    user.save()
                except User.DoesNotExist:
                    return Response({
                        'error': f'Utilisateur avec l\'email {email_utilisateur} non trouvé'
                    }, status=status.HTTP_404_NOT_FOUND)

            return Response({
                'id': 1,  # ID temporaire
                'code': code_cohorte,
                'nom': nom,
                'date_creation': timezone.now().isoformat(),
                'actif': True,
                'nombre_utilisateurs': 1 if email_utilisateur else 0,
                'message': 'Cohorte créée avec succès'
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Erreur lors de l\'opération: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cohorte(request):
    """
    Crée un nouveau code de cohorte
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        nom = request.data.get('nom', '').strip()
        mois = request.data.get('mois')
        annee = request.data.get('annee')
        email_utilisateur = request.data.get('email_utilisateur', '').strip()

        # Validation des données
        if not nom:
            return Response({
                'error': 'Le nom de la cohorte est obligatoire'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not mois or not annee:
            return Response({
                'error': 'Le mois et l\'année sont obligatoires'
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

        # Générer le code de cohorte automatiquement
        code_cohorte = f"COH{annee}{mois:02d}{uuid.uuid4().hex[:6].upper()}"

        # Vérifier que le code n'existe pas déjà
        while User.objects.filter(code_cohorte=code_cohorte).exists():
            code_cohorte = f"COH{annee}{mois:02d}{uuid.uuid4().hex[:6].upper()}"

        # Si un email utilisateur est fourni, l'assigner à cette cohorte
        if email_utilisateur:
            try:
                user = User.objects.get(email=email_utilisateur)
                user.code_cohorte = code_cohorte
                user.save()
            except User.DoesNotExist:
                return Response({
                    'error': f'Utilisateur avec l\'email {email_utilisateur} non trouvé'
                }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'id': 1,  # ID temporaire
            'code': code_cohorte,
            'nom': nom,
            'date_creation': timezone.now().isoformat(),
            'actif': True,
            'nombre_utilisateurs': 1 if email_utilisateur else 0,
            'message': 'Cohorte créée avec succès'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la création de la cohorte: {str(e)}'
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

        users = User.objects.filter(code_cohorte=cohorte_code).values(
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'is_active', 'date_joined'
        )

        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role'],
                'is_active': user['is_active'],
                'date_joined': user['date_joined'].isoformat() if user['date_joined'] else None,
                'code_cohorte': cohorte_code
            })

        return Response({
            'results': users_list,
            'count': len(users_list)
        })

    except Exception as e:
        return Response({
            'error': f'Erreur lors de la récupération des utilisateurs: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cohorte(request, cohorte_id):
    """
    Met à jour une cohorte (placeholder pour compatibilité frontend)
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'message': 'Mise à jour des cohortes non implémentée'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    except Exception as e:
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cohorte(request, cohorte_id):
    """
    Supprime une cohorte (placeholder pour compatibilité frontend)
    """
    try:
        # Vérifier que l'utilisateur est admin
        if request.user.role != 'ADMIN':
            return Response({
                'error': 'Accès non autorisé'
            }, status=status.HTTP_403_FORBIDDEN)

        return Response({
            'message': 'Suppression des cohortes non implémentée'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

    except Exception as e:
        return Response({
            'error': f'Erreur: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

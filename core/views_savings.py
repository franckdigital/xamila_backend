"""
Vues pour les APIs d'épargne Ma Caisse
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
import uuid
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count
from .models_savings_challenge import SavingsAccount, SavingsDeposit, SavingsGoal, ChallengeParticipation
from .models import User

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_account(request):
    """Récupère le compte d'épargne principal de l'utilisateur"""
    
    try:
        # Pour test temporaire, utiliser l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        logger.info(f"Savings account request for test user: {user.email}")
        
        # Récupérer le compte d'épargne principal
        savings_account = SavingsAccount.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not savings_account:
            # Créer un compte par défaut s'il n'existe pas
            savings_account = SavingsAccount.objects.create(
                user=user,
                account_name="Compte Principal",
                account_number=f"ACC{user.id}",
                balance=Decimal('0.00'),
                account_type='BASIC',
                status='ACTIVE'
            )
            logger.info(f"Created default savings account for {user.email}")
        
        # Calculer les statistiques
        total_deposits = SavingsDeposit.objects.filter(
            participation__user=user,
            status='CONFIRMED'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Objectif mensuel basé sur les défis actifs
        monthly_goal = SavingsGoal.objects.filter(
            user=user,
            status='ACTIVE'
        ).aggregate(total=Sum('target_amount'))['total'] or Decimal('50000.00')
        
        # Progression mensuelle (pourcentage basé sur les dépôts récents)
        monthly_progress = min(100, float(total_deposits / monthly_goal * 100)) if monthly_goal > 0 else 0
        
        account_data = {
            'id': savings_account.id,
            'utilisateur': user.id,
            'utilisateur_nom': f"{user.first_name} {user.last_name}",
            'solde_actuel': str(savings_account.balance),
            'objectif_mensuel': str(monthly_goal),
            'progression_mensuelle': round(monthly_progress, 2),
            'date_creation': savings_account.created_at.isoformat(),
            'date_modification': savings_account.updated_at.isoformat()
        }
        
        logger.info(f"Returning savings account data for {user.email}")
        return Response(account_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving savings account: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Erreur lors de la récupération du compte d\'épargne: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_transactions(request):
    """Récupère l'historique des transactions d'épargne"""
    
    try:
        # Pour test temporaire, utiliser l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        limit = int(request.GET.get('limit', 10))
        logger.info(f"Savings transactions request for test user: {user.email}, limit: {limit}")
        
        # Récupérer les dépôts récents
        deposits = SavingsDeposit.objects.filter(
            participation__user=user
        ).order_by('-created_at')[:limit]
        
        transactions = []
        total_deposits = Decimal('0.00')
        total_withdrawals = Decimal('0.00')
        
        for deposit in deposits:
            transaction_data = {
                'id': str(deposit.id),
                'type': 'deposit',
                'amount': float(deposit.amount),
                'method': deposit.deposit_method.lower(),
                'status': deposit.status.lower(),
                'reference': deposit.transaction_reference or f"DEP{deposit.id}",
                'date': deposit.created_at.isoformat(),
                'points_awarded': deposit.points_awarded or 0
            }
            transactions.append(transaction_data)
            
            if deposit.status == 'CONFIRMED':
                total_deposits += deposit.amount
        
        response_data = {
            'transactions': transactions,
            'total_deposits': float(total_deposits),
            'total_withdrawals': float(total_withdrawals)
        }
        
        logger.info(f"Returning {len(transactions)} transactions for {user.email}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving transactions: {str(e)}")
        return Response({
            'error': 'Erreur lors de la récupération des transactions'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def savings_stats(request):
    """Récupère les statistiques d'épargne de l'utilisateur"""
    
    try:
        # Pour test temporaire, utiliser l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        logger.info(f"Savings stats request for test user: {user.email}")
        
        # Calculer les statistiques
        deposits_data = SavingsDeposit.objects.filter(
            participation__user=user,
            status='CONFIRMED'
        ).aggregate(
            total_amount=Sum('amount'),
            count=Count('id')
        )
        
        total_deposits = deposits_data['total_amount'] or Decimal('0.00')
        transaction_count = deposits_data['count'] or 0
        
        # Solde actuel des comptes
        current_balance = SavingsAccount.objects.filter(
            user=user,
            status='ACTIVE'
        ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        
        # Objectif mensuel
        monthly_goal = SavingsGoal.objects.filter(
            user=user,
            status='ACTIVE'
        ).aggregate(total=Sum('target_amount'))['total'] or Decimal('50000.00')
        
        # Progression mensuelle
        monthly_progress = min(100, float(total_deposits / monthly_goal * 100)) if monthly_goal > 0 else 0
        
        stats_data = {
            'solde_actuel': str(current_balance),
            'objectif_mensuel': str(monthly_goal),
            'progression_mensuelle': round(monthly_progress, 2),
            'total_depots': str(total_deposits),
            'total_retraits': '0.00',  # Pas de retraits pour l'instant
            'nombre_transactions': transaction_count
        }
        
        logger.info(f"Returning savings stats for {user.email}")
        return Response(stats_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving savings stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': 'Erreur lors de la récupération des statistiques'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def savings_deposit(request):
    """Crée un nouveau dépôt d'épargne"""
    
    try:
        # Pour test temporaire, utiliser l'utilisateur test
        user = User.objects.get(email="test@xamila.com")
        logger.info(f"Savings deposit request for test user: {user.email}")
        
        # Récupérer les données du dépôt
        montant = request.data.get('montant')
        methode_depot = request.data.get('methode_depot', 'bank')
        banque = request.data.get('banque')
        
        if not montant:
            return Response({
                'error': 'Le montant est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            montant = Decimal(str(montant))
            if montant <= 0:
                raise ValueError("Montant invalide")
        except (ValueError, TypeError):
            return Response({
                'error': 'Montant invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer ou créer une participation active
        from .models_savings_challenge import ChallengeParticipation, SavingsChallenge
        participation = ChallengeParticipation.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not participation:
            # Créer une participation par défaut si aucune n'existe
            default_challenge = SavingsChallenge.objects.filter(
                status='ACTIVE',
                is_public=True
            ).first()
            
            if default_challenge:
                participation = ChallengeParticipation.objects.create(
                    user=user,
                    challenge=default_challenge,
                    personal_target=default_challenge.target_amount,
                    status='ACTIVE'
                )
            else:
                return Response({
                    'error': 'Aucun défi d\'épargne disponible'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mapper la méthode de dépôt
        method_mapping = {
            'home': 'CASH',
            'bank': 'BANK_TRANSFER',
            'stock': 'MOBILE_MONEY'
        }
        deposit_method = method_mapping.get(methode_depot, 'BANK_TRANSFER')
        
        # Récupérer la banque depuis les données
        banque = request.data.get('banque', '')
        
        # Créer le dépôt
        deposit = SavingsDeposit.objects.create(
            participation=participation,
            amount=montant,
            deposit_method=deposit_method,
            bank_name=banque,
            status='CONFIRMED',
            transaction_reference=f'DEP{uuid.uuid4().hex[:20]}',
            processed_at=timezone.now()
        )
        
        # Mettre à jour la participation
        participation.total_saved += montant
        participation.deposits_count += 1
        participation.points_earned += int(montant / 1000)  # 1 point par 1000 FCFA
        participation.save()
        
        # Mettre à jour le compte d'épargne
        savings_account = SavingsAccount.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if savings_account:
            savings_account.balance += montant
            savings_account.save()
            nouveau_solde = str(savings_account.balance)
        else:
            nouveau_solde = str(montant)
        
        response_data = {
            'success': True,
            'message': f'Dépôt de {montant:,} FCFA effectué avec succès',
            'nouveau_solde': nouveau_solde,
            'reference': deposit.transaction_reference
        }
        
        logger.info(f"Deposit created successfully for {user.email}: {montant} FCFA")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error creating deposit: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Erreur lors de la création du dépôt: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def savings_withdraw(request):
    """Crée un nouveau retrait d'épargne"""
    
    try:
        # Utiliser l'utilisateur authentifié
        user = request.user
        logger.info(f"Savings withdrawal request for user: {user.email}")
        
        # Récupérer le montant du retrait
        montant = request.data.get('montant')
        
        if not montant:
            return Response({
                'error': 'Le montant est requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            montant = Decimal(str(montant))
            if montant <= 0:
                raise ValueError("Montant invalide")
        except (ValueError, TypeError):
            return Response({
                'error': 'Montant invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le solde disponible
        savings_account = SavingsAccount.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not savings_account or savings_account.balance < montant:
            return Response({
                'error': 'Solde insuffisant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Trouver la participation active
        participation = ChallengeParticipation.objects.filter(
            user=user,
            status='ACTIVE'
        ).first()
        
        if not participation:
            return Response({
                'error': 'Aucune participation active trouvée'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'enregistrement de retrait comme dépôt négatif
        withdrawal = SavingsDeposit.objects.create(
            participation=participation,
            amount=-montant,  # Montant négatif pour le retrait
            deposit_method='WITHDRAWAL',
            bank_name='',
            status='CONFIRMED',
            transaction_reference=f'WTH{uuid.uuid4().hex[:20]}',
            processed_at=timezone.now()
        )
        
        # Mettre à jour la participation
        participation.total_saved -= montant
        participation.save()
        
        # Mettre à jour le solde du compte
        savings_account.balance -= montant
        savings_account.save()
        
        response_data = {
            'success': True,
            'message': f'Retrait de {montant:,} FCFA effectué avec succès',
            'nouveau_solde': str(savings_account.balance),
            'reference': withdrawal.transaction_reference
        }
        
        logger.info(f"Withdrawal processed successfully for {user.email}: {montant} FCFA")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        logger.error("Test user not found")
        return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error processing withdrawal: {str(e)}")
        return Response({
            'error': 'Erreur lors du traitement du retrait'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def collective_progress(request):
    """Récupère les données de progression collective"""
    
    try:
        from .models_savings_challenge import ChallengeParticipation, SavingsChallenge
        
        # Statistiques globales - utiliser les comptes d'épargne pour cohérence
        total_participants = SavingsAccount.objects.filter(status='ACTIVE').count()
        total_saved = SavingsAccount.objects.filter(status='ACTIVE').aggregate(
            total=Sum('balance')
        )['total'] or 0
        
        # Défis actifs
        active_challenges = SavingsChallenge.objects.filter(
            status='ACTIVE',
            is_public=True
        ).count()
        
        # Progression par défi
        challenges_progress = []
        for challenge in SavingsChallenge.objects.filter(status='ACTIVE', is_public=True)[:5]:
            participants = ChallengeParticipation.objects.filter(
                challenge=challenge,
                status='ACTIVE'
            )
            
            total_saved_challenge = participants.aggregate(
                total=Sum('total_saved')
            )['total'] or 0
            
            progress_percentage = 0
            if challenge.target_amount > 0:
                progress_percentage = min(100, (total_saved_challenge / challenge.target_amount) * 100)
            
            challenges_progress.append({
                'id': str(challenge.id),
                'title': challenge.title,
                'description': challenge.description,
                'target_amount': float(challenge.target_amount),
                'current_amount': float(total_saved_challenge),
                'progress_percentage': round(progress_percentage, 2),
                'participants_count': participants.count(),
                'end_date': challenge.end_date.isoformat() if challenge.end_date else None
            })
        
        # Top participants (anonymisés)
        top_participants = []
        participations = ChallengeParticipation.objects.filter(
            status='ACTIVE'
        ).order_by('-total_saved')[:10]
        
        for i, participation in enumerate(participations, 1):
            top_participants.append({
                'rank': i,
                'username': f"Épargnant #{i}",
                'total_saved': float(participation.total_saved),
                'challenge': participation.challenge.title,
                'progress_percentage': round(participation.progress_percentage, 2)
            })
        
        # Calculer le niveau de la communauté basé sur le montant total
        community_level = min(5, max(1, int(total_saved / 10000000)))  # 1 niveau par 10M FCFA
        next_level_target = (community_level + 1) * 10000000
        progress_to_next = (total_saved / next_level_target) * 100 if next_level_target > 0 else 0
        
        # Adapter la structure pour correspondre au frontend - utiliser les comptes d'épargne
        top_savers = []
        for i, account in enumerate(SavingsAccount.objects.filter(status='ACTIVE').order_by('-balance')[:10], 1):
            # Calculer la progression basée sur l'objectif du défi
            participation = ChallengeParticipation.objects.filter(
                user=account.user,
                status='ACTIVE'
            ).first()
            progress = 0
            if participation and participation.personal_target > 0:
                progress = (account.balance / participation.personal_target) * 100
            
            top_savers.append({
                'id': str(account.user.id),
                'display_name': f"Épargnant #{i}",
                'amount': float(account.balance),
                'is_current_user': account.user.email == "test@xamila.com",  # Pour le test
                'level': min(5, max(1, int(account.balance / 100000))),  # 1 niveau par 100K FCFA
                'progress': round(progress, 2),
                'rank': i
            })
        
        # Utilisateur actuel - utiliser le compte d'épargne
        current_user_account = SavingsAccount.objects.filter(
            user__email="test@xamila.com",
            status='ACTIVE'
        ).first()
        
        current_user = None
        if current_user_account:
            user_rank = list(SavingsAccount.objects.filter(
                status='ACTIVE'
            ).order_by('-balance').values_list('user__id', flat=True)).index(current_user_account.user.id) + 1
            
            # Calculer la progression
            participation = ChallengeParticipation.objects.filter(
                user=current_user_account.user,
                status='ACTIVE'
            ).first()
            progress = 0
            if participation and participation.personal_target > 0:
                progress = (current_user_account.balance / participation.personal_target) * 100
            
            current_user = {
                'id': str(current_user_account.user.id),
                'display_name': f"{current_user_account.user.first_name} {current_user_account.user.last_name}",
                'amount': float(current_user_account.balance),
                'is_current_user': True,
                'level': min(5, max(1, int(current_user_account.balance / 100000))),
                'progress': round(progress, 2),
                'rank': user_rank
            }
        
        response_data = {
            'community_stats': {
                'total_participants': total_participants,
                'total_saved': float(total_saved),
                'community_level': community_level,
                'next_level_target': next_level_target,
                'progress_to_next': round(progress_to_next, 2)
            },
            'top_savers': top_savers,
            'current_user': current_user
        }
        
        logger.info("Collective progress data retrieved successfully")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving collective progress: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'error': f'Erreur lors de la récupération de la progression collective: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

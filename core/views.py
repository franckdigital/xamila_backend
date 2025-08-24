from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import logging

from .models import (
    SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification, AdminDashboardEntry
)
from .serializers import (
    SGISerializer, SGIListSerializer, ClientInvestmentProfileSerializer,
    ClientInvestmentProfileCreateSerializer, SGIMatchingRequestSerializer,
    SGIMatchingResultSerializer, ClientSGIInteractionSerializer,
    ClientSGIInteractionCreateSerializer, EmailNotificationSerializer,
    AdminDashboardEntrySerializer, MatchingCriteriaSerializer,
    SGISelectionSerializer, SGIStatisticsSerializer, ClientStatisticsSerializer
)
from .services import SGIMatchingService, EmailNotificationService

logger = logging.getLogger(__name__)


class SGIListView(generics.ListAPIView):
    """
    Liste de toutes les SGI actives
    """
    queryset = SGI.objects.filter(is_active=True)
    serializer_class = SGIListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par critères
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        objective = self.request.query_params.get('objective')
        risk_level = self.request.query_params.get('risk_level')
        horizon = self.request.query_params.get('horizon')
        verified_only = self.request.query_params.get('verified_only')
        
        if min_amount:
            queryset = queryset.filter(min_investment_amount__lte=min_amount)
        
        if max_amount:
            queryset = queryset.filter(
                Q(max_investment_amount__gte=max_amount) | 
                Q(max_investment_amount__isnull=True)
            )
        
        # TODO: Réactiver après ajout des champs supported_objectives, supported_risk_levels, supported_horizons
        # if objective:
        #     queryset = queryset.filter(supported_objectives__contains=[objective])
        # 
        # if risk_level:
        #     queryset = queryset.filter(supported_risk_levels__contains=[risk_level])
        # 
        # if horizon:
        #     queryset = queryset.filter(supported_horizons__contains=[horizon])
        
        if verified_only == 'true':
            queryset = queryset.filter(is_verified=True)
        
        return queryset.order_by('-historical_performance', 'management_fees')


class SGIDetailView(generics.RetrieveAPIView):
    """
    Détails d'une SGI spécifique
    """
    queryset = SGI.objects.filter(is_active=True)
    serializer_class = SGISerializer
    permission_classes = [permissions.IsAuthenticated]


class ClientInvestmentProfileView(generics.RetrieveUpdateAPIView):
    """
    Profil d'investissement du client connecté
    """
    serializer_class = ClientInvestmentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = ClientInvestmentProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class ClientInvestmentProfileCreateView(generics.CreateAPIView):
    """
    Création du profil d'investissement client
    """
    serializer_class = ClientInvestmentProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # Supprimer l'ancien profil s'il existe
        ClientInvestmentProfile.objects.filter(user=self.request.user).delete()
        serializer.save()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def matching_criteria_view(request):
    """
    Retourne les critères de matching disponibles
    """
    criteria = {
        'investment_objectives': SGI.INVESTMENT_OBJECTIVES,
        'risk_levels': SGI.RISK_LEVELS,
        'investment_horizons': SGI.INVESTMENT_HORIZONS,
        'experience_levels': ClientInvestmentProfile.EXPERIENCE_LEVELS
    }
    
    serializer = MatchingCriteriaSerializer(criteria)
    return Response(serializer.data)


class SGIMatchingView(APIView):
    """
    Lancement d'une demande de matching SGI
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            # Vérifier que le client a un profil complet
            try:
                client_profile = request.user.investment_profile
                if not client_profile.is_complete:
                    return Response(
                        {'error': 'Profil d\'investissement incomplet'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ClientInvestmentProfile.DoesNotExist:
                return Response(
                    {'error': 'Profil d\'investissement non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Créer la demande de matching
            matching_request = SGIMatchingRequest.objects.create(
                client_profile=client_profile,
                status='PROCESSING'
            )
            
            # Lancer le service de matching
            matching_service = SGIMatchingService()
            results = matching_service.find_matching_sgis(client_profile)
            
            # Mettre à jour la demande avec les résultats
            matching_request.matched_sgis = results
            matching_request.total_matches = len([r for r in results if r['matching_score'] >= 50])
            matching_request.status = 'COMPLETED'
            matching_request.completed_at = timezone.now()
            matching_request.save()
            
            # Préparer la réponse
            response_data = {
                'matching_request_id': matching_request.id,
                'total_matches': matching_request.total_matches,
                'matched_sgis': results,
                'has_matches': matching_request.total_matches > 0,
                'fallback_message': None
            }
            
            if matching_request.total_matches == 0:
                response_data['fallback_message'] = (
                    "Aucune SGI ne correspond parfaitement à vos critères. "
                    "Vous pouvez consulter toutes les SGI disponibles pour faire votre choix."
                )
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur lors du matching SGI: {str(e)}")
            
            # Marquer la demande comme échouée si elle existe
            if 'matching_request' in locals():
                matching_request.status = 'FAILED'
                matching_request.save()
            
            return Response(
                {'error': 'Erreur interne lors du matching'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SGIMatchingResultsView(generics.RetrieveAPIView):
    """
    Récupération des résultats d'une demande de matching
    """
    queryset = SGIMatchingRequest.objects.all()
    serializer_class = SGIMatchingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset().filter(
            client_profile__user=self.request.user
        )


class SGISelectionView(APIView):
    """
    Sélection d'une SGI par le client
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SGISelectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Récupérer le profil client
            try:
                client_profile = request.user.investment_profile
            except ClientInvestmentProfile.DoesNotExist:
                return Response(
                    {'error': 'Profil d\'investissement non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Récupérer la SGI
            sgi = get_object_or_404(SGI, id=serializer.validated_data['sgi_id'], is_active=True)
            
            # Créer l'interaction de sélection
            interaction = ClientSGIInteraction.objects.create(
                client_profile=client_profile,
                sgi=sgi,
                interaction_type='SELECTION',
                matching_score=serializer.validated_data['matching_score'],
                notes=serializer.validated_data.get('notes', ''),
                status='INITIATED'
            )
            
            # Créer l'entrée dashboard admin
            AdminDashboardEntry.objects.create(
                client_interaction=interaction
            )
            
            # Envoyer les notifications email
            email_service = EmailNotificationService()
            email_service.send_sgi_selection_notifications(interaction)
            
            # Préparer la réponse
            interaction_serializer = ClientSGIInteractionSerializer(interaction)
            
            return Response({
                'message': 'Sélection SGI enregistrée avec succès',
                'interaction': interaction_serializer.data,
                'next_steps': [
                    'Le manager de la SGI a été notifié de votre intérêt',
                    'Vous recevrez un email de confirmation',
                    'La SGI vous contactera dans les 48h',
                    'Vous pouvez suivre l\'évolution dans votre espace client'
                ]
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sélection SGI: {str(e)}")
            return Response(
                {'error': 'Erreur interne lors de la sélection'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ClientInteractionsView(generics.ListAPIView):
    """
    Liste des interactions du client connecté
    """
    serializer_class = ClientSGIInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            client_profile = self.request.user.investment_profile
            return ClientSGIInteraction.objects.filter(
                client_profile=client_profile
            ).order_by('-created_at')
        except ClientInvestmentProfile.DoesNotExist:
            return ClientSGIInteraction.objects.none()


class AdminDashboardView(generics.ListAPIView):
    """
    Dashboard admin pour le suivi des interactions SGI
    """
    queryset = AdminDashboardEntry.objects.all()
    serializer_class = AdminDashboardEntrySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(follow_up_status=status_filter)
        
        # Filtrage par priorité
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filtrage par assignation
        assigned_filter = self.request.query_params.get('assigned_to_me')
        if assigned_filter == 'true':
            queryset = queryset.filter(assigned_to=self.request.user)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def sgi_statistics_view(request):
    """
    Statistiques générales des SGI
    """
    stats = {
        'total_sgis': SGI.objects.count(),
        'active_sgis': SGI.objects.filter(is_active=True).count(),
        'verified_sgis': SGI.objects.filter(is_verified=True).count(),
        'total_matching_requests': SGIMatchingRequest.objects.count(),
        'successful_matches': SGIMatchingRequest.objects.filter(
            total_matches__gt=0
        ).count(),
        'total_interactions': ClientSGIInteraction.objects.count(),
        'average_matching_score': ClientSGIInteraction.objects.aggregate(
            avg_score=Avg('matching_score')
        )['avg_score'] or 0
    }
    
    serializer = SGIStatisticsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def client_statistics_view(request):
    """
    Statistiques des clients
    """
    profiles = ClientInvestmentProfile.objects.all()
    
    # Calculs statistiques
    total_clients = profiles.count()
    complete_profiles = profiles.filter(is_complete=True).count()
    
    investment_stats = profiles.aggregate(
        total_amount=Sum('investment_amount'),
        avg_amount=Avg('investment_amount')
    )
    
    # Objectifs les plus populaires
    objective_counts = profiles.values('investment_objective').annotate(
        count=Count('investment_objective')
    ).order_by('-count').first()
    
    risk_counts = profiles.values('risk_tolerance').annotate(
        count=Count('risk_tolerance')
    ).order_by('-count').first()
    
    horizon_counts = profiles.values('investment_horizon').annotate(
        count=Count('investment_horizon')
    ).order_by('-count').first()
    
    stats = {
        'total_clients': total_clients,
        'complete_profiles': complete_profiles,
        'total_investment_amount': investment_stats['total_amount'] or 0,
        'average_investment_amount': investment_stats['avg_amount'] or 0,
        'most_popular_objective': objective_counts['investment_objective'] if objective_counts else None,
        'most_popular_risk_level': risk_counts['risk_tolerance'] if risk_counts else None,
        'most_popular_horizon': horizon_counts['investment_horizon'] if horizon_counts else None
    }
    
    serializer = ClientStatisticsSerializer(stats)
    return Response(serializer.data)


class EmailNotificationListView(generics.ListAPIView):
    """
    Liste des notifications email (admin seulement)
    """
    queryset = EmailNotification.objects.all()
    serializer_class = EmailNotificationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrage par type
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filtrage par statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')

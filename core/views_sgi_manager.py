"""
Vues spécialisées pour les SGI_MANAGER
Gestion avancée des Sociétés de Gestion d'Investissement
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateAPIView, ListAPIView, 
    RetrieveAPIView, UpdateAPIView
)
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import logging
from datetime import timedelta, date
from decimal import Decimal

from .models import SGI, Contract, ClientInvestmentProfile
from .models_sgi_manager import (
    SGIManagerProfile, SGIPerformanceMetrics, 
    SGIClientRelationship, SGIAlert
)
from .serializers_sgi_manager import (
    SGIManagerProfileSerializer, SGIManagerProfileCreateSerializer,
    SGIPerformanceMetricsSerializer, SGIPerformanceMetricsCreateSerializer,
    SGIClientRelationshipSerializer, SGIClientRelationshipCreateSerializer,
    SGIAlertSerializer, SGIAlertCreateSerializer,
    SGIDashboardSerializer, ContractApprovalSerializer,
    SGIAnalyticsSerializer
)
from .permissions import IsSGIManager, IsSGIManagerOfSGI
from .utils_sgi_manager import SGIAnalyticsService, SGIPerformanceService

User = get_user_model()
logger = logging.getLogger(__name__)


class SGIManagerProfileView(RetrieveUpdateAPIView):
    """
    Récupération et mise à jour du profil SGI manager
    """
    serializer_class = SGIManagerProfileSerializer
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    def get_object(self):
        """Récupère le profil du manager connecté"""
        try:
            return self.request.user.sgi_manager_profile
        except SGIManagerProfile.DoesNotExist:
            return None
    
    @extend_schema(
        summary="Récupérer le profil SGI manager",
        description="Récupère le profil du manager SGI connecté",
        responses={200: SGIManagerProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if not profile:
            return Response(
                {"detail": "Profil SGI manager non trouvé."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Mettre à jour le profil SGI manager",
        description="Met à jour le profil du manager SGI connecté",
        request=SGIManagerProfileSerializer,
        responses={200: SGIManagerProfileSerializer}
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class SGIManagerProfileCreateView(CreateAPIView):
    """
    Création du profil SGI manager
    """
    serializer_class = SGIManagerProfileCreateSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Créer un profil SGI manager",
        description="Crée un profil manager pour l'utilisateur SGI_MANAGER connecté",
        request=SGIManagerProfileCreateSerializer,
        responses={201: SGIManagerProfileSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Enregistre le profil avec l'utilisateur connecté"""
        serializer.save()
        
        # Log de création
        logger.info(
            f"Profil SGI manager créé pour {self.request.user.username} "
            f"- SGI: {serializer.instance.sgi.name}"
        )


class SGIManagerDashboardView(APIView):
    """
    Dashboard principal pour les managers SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Dashboard SGI manager",
        description="Récupère les données du dashboard pour le manager SGI connecté",
        responses={200: SGIDashboardSerializer}
    )
    def get(self, request):
        """Récupère les données du dashboard"""
        try:
            manager_profile = request.user.sgi_manager_profile
            sgi = manager_profile.sgi
            
            # Métriques de base
            total_clients = ClientInvestmentProfile.objects.filter(
                sgi_interactions__sgi=sgi
            ).distinct().count()
            
            active_contracts = Contract.objects.filter(
                sgi=sgi, 
                status='APPROVED'
            ).count()
            
            pending_contracts = Contract.objects.filter(
                sgi=sgi, 
                status='PENDING'
            ).count()
            
            total_assets = Contract.objects.filter(
                sgi=sgi, 
                status='APPROVED'
            ).aggregate(
                total=Sum('investment_amount')
            )['total'] or Decimal('0.00')
            
            # Performance récente
            now = timezone.now()
            monthly_metrics = SGIPerformanceMetrics.objects.filter(
                sgi=sgi,
                period_type='MONTHLY',
                period_start__gte=now - timedelta(days=30)
            ).first()
            
            quarterly_metrics = SGIPerformanceMetrics.objects.filter(
                sgi=sgi,
                period_type='QUARTERLY',
                period_start__gte=now - timedelta(days=90)
            ).first()
            
            yearly_metrics = SGIPerformanceMetrics.objects.filter(
                sgi=sgi,
                period_type='YEARLY',
                period_start__gte=now - timedelta(days=365)
            ).first()
            
            # Alertes
            unread_alerts = SGIAlert.objects.filter(
                manager=request.user,
                status='UNREAD'
            ).count()
            
            critical_alerts = SGIAlert.objects.filter(
                manager=request.user,
                priority='CRITICAL',
                status__in=['UNREAD', 'READ']
            ).count()
            
            # Activité récente
            recent_contracts = Contract.objects.filter(
                sgi=sgi
            ).order_by('-created_at')[:5].values(
                'id', 'contract_number', 'investment_amount', 
                'status', 'created_at', 'customer__first_name', 
                'customer__last_name'
            )
            
            recent_clients = ClientInvestmentProfile.objects.filter(
                sgi_interactions__sgi=sgi
            ).order_by('-created_at')[:5].values(
                'id', 'full_name', 'investment_amount', 
                'investment_objective', 'created_at'
            )
            
            # Objectifs mensuels (exemple)
            monthly_target = sgi.total_assets_under_management * Decimal('0.1')  # 10% de croissance
            monthly_progress = Decimal('0.00')
            if monthly_metrics:
                monthly_progress = (monthly_metrics.total_investments / monthly_target) * 100
            
            dashboard_data = {
                'sgi_info': sgi,
                'manager_profile': manager_profile,
                'total_clients': total_clients,
                'active_contracts': active_contracts,
                'pending_contracts': pending_contracts,
                'total_assets': total_assets,
                'monthly_performance': monthly_metrics.portfolio_return if monthly_metrics else Decimal('0.00'),
                'quarterly_performance': quarterly_metrics.portfolio_return if quarterly_metrics else Decimal('0.00'),
                'yearly_performance': yearly_metrics.portfolio_return if yearly_metrics else Decimal('0.00'),
                'unread_alerts': unread_alerts,
                'critical_alerts': critical_alerts,
                'recent_contracts': list(recent_contracts),
                'recent_clients': list(recent_clients),
                'monthly_target': monthly_target,
                'monthly_progress': monthly_progress,
            }
            
            serializer = SGIDashboardSerializer(dashboard_data)
            return Response(serializer.data)
            
        except SGIManagerProfile.DoesNotExist:
            return Response(
                {"detail": "Profil SGI manager requis."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erreur dashboard SGI manager: {str(e)}")
            return Response(
                {"detail": "Erreur lors du chargement du dashboard."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractManagementView(APIView):
    """
    Gestion des contrats par les managers SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Liste des contrats SGI",
        description="Récupère la liste des contrats de la SGI du manager",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filtrer par statut'),
            OpenApiParameter('page', OpenApiTypes.INT, description='Numéro de page'),
        ],
        responses={200: "Liste des contrats"}
    )
    def get(self, request):
        """Liste des contrats de la SGI"""
        try:
            manager_profile = request.user.sgi_manager_profile
            sgi = manager_profile.sgi
            
            # Filtres
            status_filter = request.query_params.get('status')
            search = request.query_params.get('search')
            
            contracts = Contract.objects.filter(sgi=sgi)
            
            if status_filter:
                contracts = contracts.filter(status=status_filter)
            
            if search:
                contracts = contracts.filter(
                    Q(contract_number__icontains=search) |
                    Q(customer__first_name__icontains=search) |
                    Q(customer__last_name__icontains=search) |
                    Q(customer__email__icontains=search)
                )
            
            contracts = contracts.select_related('customer', 'sgi').order_by('-created_at')
            
            # Pagination simple
            page_size = 20
            page = int(request.query_params.get('page', 1))
            start = (page - 1) * page_size
            end = start + page_size
            
            contracts_data = []
            for contract in contracts[start:end]:
                contracts_data.append({
                    'id': contract.id,
                    'contract_number': contract.contract_number,
                    'customer_name': contract.customer.get_full_name(),
                    'customer_email': contract.customer.email,
                    'investment_amount': contract.investment_amount,
                    'funding_source': contract.funding_source,
                    'status': contract.status,
                    'created_at': contract.created_at,
                    'can_approve': manager_profile.can_approve_amount(contract.investment_amount),
                })
            
            return Response({
                'contracts': contracts_data,
                'total': contracts.count(),
                'page': page,
                'page_size': page_size,
            })
            
        except SGIManagerProfile.DoesNotExist:
            return Response(
                {"detail": "Profil SGI manager requis."},
                status=status.HTTP_404_NOT_FOUND
            )


class ContractApprovalView(APIView):
    """
    Approbation/rejet de contrats par les managers SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Approuver/rejeter un contrat",
        description="Permet au manager SGI d'approuver ou rejeter un contrat",
        request=ContractApprovalSerializer,
        responses={200: "Contrat traité avec succès"}
    )
    def post(self, request):
        """Traite l'approbation/rejet d'un contrat"""
        serializer = ContractApprovalSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            contract_id = serializer.validated_data['contract_id']
            action = serializer.validated_data['action']
            notes = serializer.validated_data.get('notes', '')
            
            try:
                contract = Contract.objects.get(id=contract_id)
                manager = request.user
                
                if action == 'approve':
                    contract.approve(manager)
                    message = f"Contrat {contract.contract_number} approuvé avec succès."
                    
                    # Créer une alerte pour le client
                    SGIAlert.objects.create(
                        manager=manager,
                        sgi=contract.sgi,
                        alert_type='CONTRACT_PENDING',
                        priority='MEDIUM',
                        title='Contrat approuvé',
                        message=f'Le contrat {contract.contract_number} a été approuvé.',
                        related_object_type='Contract',
                        related_object_id=contract.id
                    )
                    
                elif action == 'reject':
                    contract.reject(manager, notes)
                    message = f"Contrat {contract.contract_number} rejeté."
                    
                    # Créer une alerte pour le client
                    SGIAlert.objects.create(
                        manager=manager,
                        sgi=contract.sgi,
                        alert_type='CONTRACT_PENDING',
                        priority='HIGH',
                        title='Contrat rejeté',
                        message=f'Le contrat {contract.contract_number} a été rejeté. Raison: {notes}',
                        related_object_type='Contract',
                        related_object_id=contract.id
                    )
                
                logger.info(
                    f"Contrat {contract.contract_number} {action} par {manager.username}"
                )
                
                return Response({
                    'message': message,
                    'contract_id': contract.id,
                    'new_status': contract.status
                })
                
            except Contract.DoesNotExist:
                return Response(
                    {"detail": "Contrat introuvable."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Erreur approbation contrat: {str(e)}")
                return Response(
                    {"detail": "Erreur lors du traitement du contrat."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientManagementView(APIView):
    """
    Gestion des clients par les managers SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Liste des clients SGI",
        description="Récupère la liste des clients de la SGI du manager",
        responses={200: "Liste des clients"}
    )
    def get(self, request):
        """Liste des clients de la SGI"""
        try:
            manager_profile = request.user.sgi_manager_profile
            
            if not manager_profile.can_manage_clients:
                return Response(
                    {"detail": "Permission de gestion client requise."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            sgi = manager_profile.sgi
            
            # Récupérer les relations client-manager
            relationships = SGIClientRelationship.objects.filter(
                sgi=sgi,
                status='ACTIVE'
            ).select_related('client', 'manager').order_by('-created_at')
            
            clients_data = []
            for rel in relationships:
                client = rel.client
                
                # Statistiques du client
                client_contracts = Contract.objects.filter(
                    customer=client, 
                    sgi=sgi
                )
                total_invested = client_contracts.filter(
                    status='APPROVED'
                ).aggregate(
                    total=Sum('investment_amount')
                )['total'] or Decimal('0.00')
                
                clients_data.append({
                    'relationship_id': rel.id,
                    'client_id': client.id,
                    'client_name': client.get_full_name(),
                    'client_email': client.email,
                    'client_phone': client.phone,
                    'relationship_type': rel.relationship_type,
                    'start_date': rel.start_date,
                    'last_contact': rel.last_contact,
                    'days_since_contact': rel.days_since_last_contact(),
                    'total_invested': total_invested,
                    'active_contracts': client_contracts.filter(status='APPROVED').count(),
                    'pending_contracts': client_contracts.filter(status='PENDING').count(),
                })
            
            return Response({
                'clients': clients_data,
                'total': len(clients_data)
            })
            
        except SGIManagerProfile.DoesNotExist:
            return Response(
                {"detail": "Profil SGI manager requis."},
                status=status.HTTP_404_NOT_FOUND
            )


class SGIPerformanceView(APIView):
    """
    Métriques de performance SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Métriques de performance SGI",
        description="Récupère les métriques de performance de la SGI",
        parameters=[
            OpenApiParameter('period', OpenApiTypes.STR, description='Période (MONTHLY, QUARTERLY, YEARLY)'),
            OpenApiParameter('limit', OpenApiTypes.INT, description='Nombre de périodes à récupérer'),
        ],
        responses={200: SGIPerformanceMetricsSerializer(many=True)}
    )
    def get(self, request):
        """Récupère les métriques de performance"""
        try:
            manager_profile = request.user.sgi_manager_profile
            sgi = manager_profile.sgi
            
            period = request.query_params.get('period', 'MONTHLY')
            limit = int(request.query_params.get('limit', 12))
            
            metrics = SGIPerformanceMetrics.objects.filter(
                sgi=sgi,
                period_type=period
            ).order_by('-period_start')[:limit]
            
            serializer = SGIPerformanceMetricsSerializer(metrics, many=True)
            return Response(serializer.data)
            
        except SGIManagerProfile.DoesNotExist:
            return Response(
                {"detail": "Profil SGI manager requis."},
                status=status.HTTP_404_NOT_FOUND
            )


class SGIAlertsView(ListAPIView):
    """
    Gestion des alertes SGI
    """
    serializer_class = SGIAlertSerializer
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    def get_queryset(self):
        """Filtre les alertes du manager connecté"""
        return SGIAlert.objects.filter(
            manager=self.request.user
        ).order_by('-created_at')
    
    @extend_schema(
        summary="Liste des alertes SGI",
        description="Récupère les alertes du manager SGI connecté",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, description='Filtrer par statut'),
            OpenApiParameter('priority', OpenApiTypes.STR, description='Filtrer par priorité'),
        ],
        responses={200: SGIAlertSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SGIAlertActionView(APIView):
    """
    Actions sur les alertes SGI (marquer comme lu, accuser réception)
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Action sur une alerte",
        description="Marque une alerte comme lue ou accuse réception",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'action': {'type': 'string', 'enum': ['read', 'acknowledge', 'dismiss']},
                },
                'required': ['action']
            }
        },
        responses={200: "Action effectuée avec succès"}
    )
    def post(self, request, alert_id):
        """Effectue une action sur une alerte"""
        try:
            alert = SGIAlert.objects.get(
                id=alert_id,
                manager=request.user
            )
            
            action = request.data.get('action')
            
            if action == 'read':
                alert.mark_as_read()
                message = "Alerte marquée comme lue."
            elif action == 'acknowledge':
                alert.acknowledge()
                message = "Accusé de réception enregistré."
            elif action == 'dismiss':
                alert.status = 'DISMISSED'
                alert.save(update_fields=['status'])
                message = "Alerte ignorée."
            else:
                return Response(
                    {"detail": "Action non valide."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({"message": message})
            
        except SGIAlert.DoesNotExist:
            return Response(
                {"detail": "Alerte introuvable."},
                status=status.HTTP_404_NOT_FOUND
            )


class SGIAnalyticsView(APIView):
    """
    Analytics avancées pour les managers SGI
    """
    permission_classes = [IsAuthenticated, IsSGIManager]
    
    @extend_schema(
        summary="Analytics SGI avancées",
        description="Génère des analytics avancées pour la SGI",
        request=SGIAnalyticsSerializer,
        responses={200: SGIAnalyticsSerializer}
    )
    def post(self, request):
        """Génère des analytics pour la période spécifiée"""
        serializer = SGIAnalyticsSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                manager_profile = request.user.sgi_manager_profile
                sgi = manager_profile.sgi
                
                period_start = serializer.validated_data['period_start']
                period_end = serializer.validated_data['period_end']
                
                # Utiliser le service d'analytics
                analytics_service = SGIAnalyticsService(sgi, period_start, period_end)
                analytics_data = analytics_service.generate_full_analytics()
                
                response_data = serializer.validated_data.copy()
                response_data.update(analytics_data)
                
                response_serializer = SGIAnalyticsSerializer(response_data)
                return Response(response_serializer.data)
                
            except SGIManagerProfile.DoesNotExist:
                return Response(
                    {"detail": "Profil SGI manager requis."},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(f"Erreur analytics SGI: {str(e)}")
                return Response(
                    {"detail": "Erreur lors de la génération des analytics."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSGIManager])
def sgi_manager_statistics(request):
    """
    Statistiques rapides pour le manager SGI
    """
    try:
        manager_profile = request.user.sgi_manager_profile
        sgi = manager_profile.sgi
        
        # Statistiques de base
        stats = {
            'sgi_name': sgi.name,
            'manager_type': manager_profile.manager_type,
            'total_clients': ClientInvestmentProfile.objects.filter(
                sgi_interactions__sgi=sgi
            ).distinct().count(),
            'pending_approvals': Contract.objects.filter(
                sgi=sgi, 
                status='PENDING'
            ).count(),
            'monthly_approvals': manager_profile.get_daily_approvals_count(),
            'approval_limit': manager_profile.max_daily_approvals,
            'unread_alerts': SGIAlert.objects.filter(
                manager=request.user,
                status='UNREAD'
            ).count(),
        }
        
        return Response(stats)
        
    except SGIManagerProfile.DoesNotExist:
        return Response(
            {"detail": "Profil SGI manager requis."},
            status=status.HTTP_404_NOT_FOUND
        )

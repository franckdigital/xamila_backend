"""
Services utilitaires pour les SGI_MANAGER
Logique métier avancée et analytics
"""

from django.db.models import Q, Count, Sum, Avg, F, Max, Min
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta, date
import logging
from typing import Dict, List, Optional, Tuple

from .models import SGI, Contract, ClientInvestmentProfile
from .models_sgi_manager import (
    SGIManagerProfile, SGIPerformanceMetrics, 
    SGIClientRelationship, SGIAlert
)

User = get_user_model()
logger = logging.getLogger(__name__)


class SGIAnalyticsService:
    """
    Service d'analytics avancées pour les SGI
    """
    
    def __init__(self, sgi: SGI, period_start: timezone.datetime, period_end: timezone.datetime):
        self.sgi = sgi
        self.period_start = period_start
        self.period_end = period_end
    
    def generate_full_analytics(self) -> Dict:
        """Génère un rapport d'analytics complet"""
        return {
            'client_acquisition': self.get_client_acquisition_analytics(),
            'client_retention': self.get_client_retention_analytics(),
            'revenue_breakdown': self.get_revenue_breakdown(),
            'portfolio_performance': self.get_portfolio_performance(),
            'contract_analytics': self.get_contract_analytics(),
        }
    
    def get_client_acquisition_analytics(self) -> Dict:
        """Analytics d'acquisition client"""
        contracts = Contract.objects.filter(
            sgi=self.sgi,
            created_at__range=[self.period_start, self.period_end]
        )
        
        # Nouveaux clients par mois
        monthly_acquisition = contracts.extra(
            select={'month': "DATE_TRUNC('month', created_at)"}
        ).values('month').annotate(
            new_clients=Count('customer', distinct=True),
            total_amount=Sum('investment_amount')
        ).order_by('month')
        
        return {
            'monthly_acquisition': list(monthly_acquisition),
            'total_new_clients': contracts.values('customer').distinct().count(),
        }
    
    def get_client_retention_analytics(self) -> Dict:
        """Analytics de rétention client"""
        active_clients = SGIClientRelationship.objects.filter(
            sgi=self.sgi,
            status='ACTIVE'
        ).count()
        
        churned_clients = SGIClientRelationship.objects.filter(
            sgi=self.sgi,
            status='TERMINATED',
            end_date__range=[self.period_start, self.period_end]
        ).count()
        
        return {
            'active_clients': active_clients,
            'churned_clients': churned_clients,
            'retention_rate': (active_clients / (active_clients + churned_clients)) * 100 if (active_clients + churned_clients) > 0 else 0,
        }
    
    def get_revenue_breakdown(self) -> Dict:
        """Analyse détaillée des revenus"""
        contracts = Contract.objects.filter(
            sgi=self.sgi,
            status='APPROVED',
            approved_at__range=[self.period_start, self.period_end]
        )
        
        total_investments = contracts.aggregate(
            total=Sum('investment_amount')
        )['total'] or Decimal('0.00')
        
        management_fees = total_investments * (self.sgi.management_fees / 100)
        entry_fees = total_investments * (self.sgi.entry_fees / 100)
        
        return {
            'total_investments': total_investments,
            'management_fees': management_fees,
            'entry_fees': entry_fees,
            'total_revenue': management_fees + entry_fees,
        }
    
    def get_portfolio_performance(self) -> Dict:
        """Analyse de performance du portefeuille"""
        metrics = SGIPerformanceMetrics.objects.filter(
            sgi=self.sgi,
            period_start__range=[self.period_start, self.period_end]
        ).order_by('period_start')
        
        if not metrics.exists():
            return {'message': 'Données de performance insuffisantes'}
        
        returns = [float(m.portfolio_return) for m in metrics]
        
        return {
            'average_return': sum(returns) / len(returns) if returns else 0,
            'best_month': max(returns) if returns else 0,
            'worst_month': min(returns) if returns else 0,
            'total_months': len(returns),
        }
    
    def get_contract_analytics(self) -> Dict:
        """Analytics des contrats"""
        contracts = Contract.objects.filter(
            sgi=self.sgi,
            created_at__range=[self.period_start, self.period_end]
        )
        
        total_contracts = contracts.count()
        approved_contracts = contracts.filter(status='APPROVED').count()
        rejected_contracts = contracts.filter(status='REJECTED').count()
        
        return {
            'total_contracts': total_contracts,
            'approval_rate': (approved_contracts / total_contracts) * 100 if total_contracts > 0 else 0,
            'rejection_rate': (rejected_contracts / total_contracts) * 100 if total_contracts > 0 else 0,
        }


class SGIPerformanceService:
    """
    Service de gestion des performances SGI
    """
    
    @staticmethod
    def calculate_monthly_metrics(sgi: SGI, year: int, month: int) -> SGIPerformanceMetrics:
        """Calcule les métriques mensuelles pour une SGI"""
        from calendar import monthrange
        
        # Période du mois
        period_start = timezone.datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
        last_day = monthrange(year, month)[1]
        period_end = timezone.datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.get_current_timezone())
        
        # Calculs des métriques
        contracts_in_period = Contract.objects.filter(
            sgi=sgi,
            created_at__range=[period_start, period_end]
        )
        
        new_clients = contracts_in_period.values('customer').distinct().count()
        contracts_signed = contracts_in_period.filter(status='APPROVED').count()
        contracts_pending = contracts_in_period.filter(status='PENDING').count()
        contracts_rejected = contracts_in_period.filter(status='REJECTED').count()
        
        total_investments = contracts_in_period.filter(status='APPROVED').aggregate(
            total=Sum('investment_amount')
        )['total'] or Decimal('0.00')
        
        # Créer ou mettre à jour les métriques
        metrics, created = SGIPerformanceMetrics.objects.get_or_create(
            sgi=sgi,
            period_type='MONTHLY',
            period_start=period_start,
            defaults={
                'period_end': period_end,
                'new_clients': new_clients,
                'contracts_signed': contracts_signed,
                'contracts_pending': contracts_pending,
                'contracts_rejected': contracts_rejected,
                'total_investments': total_investments,
                'portfolio_return': Decimal('0.00'),
                'benchmark_return': Decimal('0.00'),
            }
        )
        
        return metrics


class SGIAlertService:
    """
    Service de gestion des alertes SGI
    """
    
    @staticmethod
    def create_contract_alert(contract: Contract, alert_type: str = 'CONTRACT_PENDING'):
        """Crée une alerte pour un nouveau contrat"""
        sgi = contract.sgi
        managers = User.objects.filter(
            sgi_manager_profile__sgi=sgi,
            sgi_manager_profile__is_active=True,
            sgi_manager_profile__can_approve_contracts=True
        )
        
        for manager in managers:
            if manager.sgi_manager_profile.can_approve_amount(contract.investment_amount):
                SGIAlert.objects.create(
                    manager=manager,
                    sgi=sgi,
                    alert_type=alert_type,
                    priority='MEDIUM',
                    title=f'Nouveau contrat - {contract.contract_number}',
                    message=f'Contrat de {contract.investment_amount} FCFA à approuver.',
                    action_required=True,
                    related_object_type='Contract',
                    related_object_id=contract.id,
                    expires_at=timezone.now() + timedelta(days=7)
                )
    
    @staticmethod
    def create_performance_alert(sgi: SGI, performance_data: Dict):
        """Crée une alerte de performance"""
        managers = User.objects.filter(
            sgi_manager_profile__sgi=sgi,
            sgi_manager_profile__is_active=True
        )
        
        if performance_data.get('return', 0) < -5:
            priority = 'HIGH'
            title = 'Performance faible détectée'
        elif performance_data.get('return', 0) < 0:
            priority = 'MEDIUM'
            title = 'Performance négative'
        else:
            return
        
        for manager in managers:
            SGIAlert.objects.create(
                manager=manager,
                sgi=sgi,
                alert_type='PERFORMANCE_LOW',
                priority=priority,
                title=title,
                message=f'Performance de {performance_data.get("return", 0)}% détectée.',
                action_required=True
            )

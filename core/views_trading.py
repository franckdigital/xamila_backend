"""
Vues API pour le module Trading
Endpoints REST pour la simulation de trading et gestion de portefeuilles
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models_trading import (
    StockExtended, Portfolio, Holding, TradingOrder, Transaction,
    PriceHistory, TradingCompetition, CompetitionParticipant
)
from .serializers_trading import (
    StockExtendedSerializer, PortfolioSerializer, HoldingSerializer,
    TradingOrderSerializer, TransactionSerializer, PriceHistorySerializer,
    TradingCompetitionSerializer, CompetitionParticipantSerializer,
    PortfolioCreateSerializer, OrderCreateSerializer, CompetitionCreateSerializer
)


class StockListView(generics.ListAPIView):
    """
    Liste des actions disponibles pour le trading
    """
    serializer_class = StockExtendedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = StockExtended.objects.filter(is_active=True, is_tradeable=True)
        
        # Filtres
        category = self.request.query_params.get('category')
        sector = self.request.query_params.get('sector')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(category=category)
        if sector:
            queryset = queryset.filter(sector__icontains=sector)
        if search:
            queryset = queryset.filter(
                Q(symbol__icontains=search) | 
                Q(company_name__icontains=search)
            )
        
        # Tri
        ordering = self.request.query_params.get('ordering', 'symbol')
        if ordering in ['symbol', 'company_name', 'current_price', 'volume', 'market_cap']:
            queryset = queryset.order_by(ordering)
        
        return queryset


class StockDetailView(generics.RetrieveAPIView):
    """
    Détails d'une action spécifique
    """
    queryset = StockExtended.objects.filter(is_active=True)
    serializer_class = StockExtendedSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_price_history(request, stock_id):
    """
    Historique des prix d'une action
    """
    try:
        stock = StockExtended.objects.get(id=stock_id, is_active=True)
    except StockExtended.DoesNotExist:
        return Response(
            {'error': 'Action introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Paramètres de filtrage
    timeframe = request.query_params.get('timeframe', '1DAY')
    days = int(request.query_params.get('days', 30))
    
    # Récupérer l'historique
    start_date = timezone.now() - timedelta(days=days)
    price_history = PriceHistory.objects.filter(
        stock=stock,
        timeframe=timeframe,
        timestamp__gte=start_date
    ).order_by('timestamp')
    
    serializer = PriceHistorySerializer(price_history, many=True)
    return Response({
        'stock': StockExtendedSerializer(stock).data,
        'price_history': serializer.data,
        'timeframe': timeframe,
        'period_days': days
    })


class PortfolioListView(generics.ListCreateAPIView):
    """
    Portefeuilles de l'utilisateur
    GET: Liste des portefeuilles
    POST: Créer un nouveau portefeuille
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PortfolioCreateSerializer
        return PortfolioSerializer
    
    def get_queryset(self):
        return Portfolio.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        # Créer le portefeuille avec le capital initial en cash
        portfolio = serializer.save(
            user=self.request.user,
            current_cash=serializer.validated_data['initial_capital'],
            total_value=serializer.validated_data['initial_capital']
        )
        
        # Créer une transaction initiale de dépôt
        Transaction.objects.create(
            portfolio=portfolio,
            transaction_type='DEPOSIT',
            quantity=1,
            price=portfolio.initial_capital,
            total_amount=portfolio.initial_capital,
            notes="Dépôt initial du portefeuille"
        )


class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un portefeuille spécifique
    """
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)
    
    def get_object(self):
        portfolio = super().get_object()
        
        # Mettre à jour la valeur totale
        portfolio.total_value = portfolio.calculate_total_value()
        portfolio.save()
        
        return portfolio


class PortfolioHoldingsView(generics.ListAPIView):
    """
    Positions détenues dans un portefeuille
    """
    serializer_class = HoldingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        portfolio_id = self.kwargs['portfolio_id']
        return Holding.objects.filter(
            portfolio_id=portfolio_id,
            portfolio__user=self.request.user
        ).select_related('stock', 'portfolio').order_by('-current_value')


class TradingOrderListView(generics.ListCreateAPIView):
    """
    Ordres de trading
    GET: Liste des ordres de l'utilisateur
    POST: Créer un nouvel ordre
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return TradingOrderSerializer
    
    def get_queryset(self):
        portfolio_id = self.request.query_params.get('portfolio')
        queryset = TradingOrder.objects.filter(
            portfolio__user=self.request.user
        ).select_related('stock', 'portfolio')
        
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        
        # Filtres de statut
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        portfolio_id = self.request.data.get('portfolio')
        
        try:
            portfolio = Portfolio.objects.get(
                id=portfolio_id,
                user=self.request.user,
                status='ACTIVE'
            )
        except Portfolio.DoesNotExist:
            raise serializers.ValidationError("Portefeuille introuvable ou inactif")
        
        # Vérifications de fonds pour les ordres d'achat
        order_data = serializer.validated_data
        if order_data['side'] == 'BUY':
            stock = order_data['stock']
            quantity = order_data['quantity']
            
            if order_data['order_type'] == 'MARKET':
                estimated_cost = stock.current_price * quantity
            else:
                estimated_cost = order_data['limit_price'] * quantity
            
            if portfolio.current_cash < estimated_cost:
                raise serializers.ValidationError(
                    "Fonds insuffisants pour cet ordre"
                )
        
        serializer.save(portfolio=portfolio)


class TradingOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un ordre de trading
    """
    serializer_class = TradingOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TradingOrder.objects.filter(
            portfolio__user=self.request.user
        ).select_related('stock', 'portfolio')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def execute_order(request, order_id):
    """
    Exécuter un ordre de trading (simulation)
    """
    try:
        order = TradingOrder.objects.get(
            id=order_id,
            portfolio__user=request.user,
            status='PENDING'
        )
    except TradingOrder.DoesNotExist:
        return Response(
            {'error': 'Ordre introuvable ou déjà exécuté'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Simulation d'exécution
    stock = order.stock
    execution_price = stock.current_price
    
    # Vérifier les conditions d'exécution pour les ordres à cours limité
    if order.order_type == 'LIMIT':
        if order.side == 'BUY' and execution_price > order.limit_price:
            return Response(
                {'error': 'Prix trop élevé pour l\'ordre limite'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif order.side == 'SELL' and execution_price < order.limit_price:
            return Response(
                {'error': 'Prix trop bas pour l\'ordre limite'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Calculer les frais (0.1% de commission)
    total_amount = execution_price * order.quantity
    commission = total_amount * Decimal('0.001')
    
    # Exécuter l'ordre
    if order.side == 'BUY':
        # Vérifier les fonds
        total_cost = total_amount + commission
        if order.portfolio.current_cash < total_cost:
            return Response(
                {'error': 'Fonds insuffisants'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Débiter le cash
        order.portfolio.current_cash -= total_cost
        
        # Créer ou mettre à jour la position
        holding, created = Holding.objects.get_or_create(
            portfolio=order.portfolio,
            stock=stock,
            defaults={
                'quantity': order.quantity,
                'average_cost': execution_price,
                'total_cost': total_amount,
                'current_value': total_amount,
                'first_purchase_date': timezone.now(),
                'last_transaction_date': timezone.now()
            }
        )
        
        if not created:
            # Mettre à jour la position existante
            total_quantity = holding.quantity + order.quantity
            total_cost = holding.total_cost + total_amount
            holding.average_cost = total_cost / total_quantity
            holding.quantity = total_quantity
            holding.total_cost = total_cost
            holding.current_value = total_quantity * stock.current_price
            holding.last_transaction_date = timezone.now()
            holding.save()
    
    else:  # SELL
        # Vérifier la position
        try:
            holding = Holding.objects.get(
                portfolio=order.portfolio,
                stock=stock
            )
        except Holding.DoesNotExist:
            return Response(
                {'error': 'Aucune position à vendre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if holding.quantity < order.quantity:
            return Response(
                {'error': 'Quantité insuffisante à vendre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créditer le cash
        net_proceeds = total_amount - commission
        order.portfolio.current_cash += net_proceeds
        
        # Mettre à jour la position
        holding.quantity -= order.quantity
        if holding.quantity == 0:
            holding.delete()
        else:
            holding.total_cost -= (holding.average_cost * order.quantity)
            holding.current_value = holding.quantity * stock.current_price
            holding.last_transaction_date = timezone.now()
            holding.save()
    
    # Mettre à jour l'ordre
    order.status = 'FILLED'
    order.filled_quantity = order.quantity
    order.average_fill_price = execution_price
    order.filled_at = timezone.now()
    order.save()
    
    # Sauvegarder le portefeuille
    order.portfolio.save()
    
    # Créer la transaction
    transaction = Transaction.objects.create(
        portfolio=order.portfolio,
        stock=stock,
        order=order,
        transaction_type=order.side,
        quantity=order.quantity,
        price=execution_price,
        total_amount=total_amount,
        commission=commission
    )
    
    return Response({
        'message': 'Ordre exécuté avec succès',
        'order': TradingOrderSerializer(order).data,
        'transaction': TransactionSerializer(transaction).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_order(request, order_id):
    """
    Annuler un ordre de trading
    """
    try:
        order = TradingOrder.objects.get(
            id=order_id,
            portfolio__user=request.user,
            status='PENDING'
        )
    except TradingOrder.DoesNotExist:
        return Response(
            {'error': 'Ordre introuvable ou déjà exécuté'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    order.status = 'CANCELLED'
    order.save()
    
    return Response({
        'message': 'Ordre annulé avec succès',
        'order': TradingOrderSerializer(order).data
    })


class TransactionListView(generics.ListAPIView):
    """
    Historique des transactions
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        portfolio_id = self.request.query_params.get('portfolio')
        queryset = Transaction.objects.filter(
            portfolio__user=self.request.user
        ).select_related('stock', 'portfolio', 'order')
        
        if portfolio_id:
            queryset = queryset.filter(portfolio_id=portfolio_id)
        
        return queryset.order_by('-executed_at')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def portfolio_performance(request, portfolio_id):
    """
    Performance d'un portefeuille
    """
    try:
        portfolio = Portfolio.objects.get(
            id=portfolio_id,
            user=request.user
        )
    except Portfolio.DoesNotExist:
        return Response(
            {'error': 'Portefeuille introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Calculer les métriques de performance
    holdings = portfolio.holdings.all()
    total_invested = sum(h.total_cost for h in holdings)
    current_value = sum(h.current_value for h in holdings)
    
    # Transactions récentes
    recent_transactions = Transaction.objects.filter(
        portfolio=portfolio
    ).order_by('-executed_at')[:10]
    
    # Performance par action
    holdings_performance = []
    for holding in holdings:
        holdings_performance.append({
            'stock': StockExtendedSerializer(holding.stock).data,
            'holding': HoldingSerializer(holding).data,
            'weight': (holding.current_value / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
        })
    
    performance_data = {
        'portfolio': PortfolioSerializer(portfolio).data,
        'summary': {
            'total_value': portfolio.total_value,
            'cash_balance': portfolio.current_cash,
            'invested_amount': total_invested,
            'total_return': portfolio.total_return,
            'total_return_percent': portfolio.total_return_percent,
            'holdings_count': holdings.count(),
        },
        'holdings_performance': holdings_performance,
        'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
    }
    
    return Response(performance_data)


# Vues pour les compétitions de trading

class TradingCompetitionListView(generics.ListCreateAPIView):
    """
    Compétitions de trading
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompetitionCreateSerializer
        return TradingCompetitionSerializer
    
    def get_queryset(self):
        queryset = TradingCompetition.objects.all()
        
        # Filtres
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Seuls les admins peuvent créer des compétitions
        if not self.request.user.role in ['ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les administrateurs peuvent créer des compétitions"
            )
        
        serializer.save(created_by=self.request.user)


class TradingCompetitionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'une compétition de trading
    """
    queryset = TradingCompetition.objects.all()
    serializer_class = TradingCompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_competition(request, competition_id):
    """
    Rejoindre une compétition de trading
    """
    try:
        competition = TradingCompetition.objects.get(
            id=competition_id,
            status='ACTIVE'
        )
    except TradingCompetition.DoesNotExist:
        return Response(
            {'error': 'Compétition introuvable ou inactive'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si l'utilisateur participe déjà
    if CompetitionParticipant.objects.filter(
        competition=competition,
        user=request.user
    ).exists():
        return Response(
            {'error': 'Vous participez déjà à cette compétition'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier les limites
    if competition.max_participants:
        current_participants = competition.participants.filter(
            status='ACTIVE'
        ).count()
        
        if current_participants >= competition.max_participants:
            return Response(
                {'error': 'Nombre maximum de participants atteint'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Créer un portefeuille pour la compétition
    portfolio = Portfolio.objects.create(
        user=request.user,
        name=f"Compétition - {competition.name}",
        description=f"Portefeuille pour la compétition {competition.name}",
        portfolio_type='COMPETITION',
        initial_capital=competition.initial_capital,
        current_cash=competition.initial_capital,
        total_value=competition.initial_capital
    )
    
    # Créer la participation
    participant = CompetitionParticipant.objects.create(
        competition=competition,
        user=request.user,
        portfolio=portfolio,
        status='ACTIVE'
    )
    
    return Response({
        'message': 'Inscription réussie à la compétition',
        'participant': CompetitionParticipantSerializer(participant).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def competition_leaderboard(request, competition_id):
    """
    Classement d'une compétition
    """
    try:
        competition = TradingCompetition.objects.get(id=competition_id)
    except TradingCompetition.DoesNotExist:
        return Response(
            {'error': 'Compétition introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Récupérer les participants classés par performance
    participants = CompetitionParticipant.objects.filter(
        competition=competition,
        status='ACTIVE'
    ).select_related('user', 'portfolio').annotate(
        portfolio_return=F('portfolio__total_value') - F('portfolio__initial_capital')
    ).order_by('-portfolio_return')
    
    # Mettre à jour les rangs
    for rank, participant in enumerate(participants, 1):
        participant.current_rank = rank
        participant.save()
    
    serializer = CompetitionParticipantSerializer(participants, many=True)
    return Response({
        'competition': TradingCompetitionSerializer(competition).data,
        'leaderboard': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def trading_dashboard(request):
    """
    Dashboard de trading de l'utilisateur
    """
    user = request.user
    
    # Statistiques des portefeuilles
    portfolios = Portfolio.objects.filter(user=user, status='ACTIVE')
    total_value = sum(p.total_value for p in portfolios)
    total_invested = sum(p.initial_capital for p in portfolios)
    total_return = total_value - total_invested
    
    # Positions actives
    holdings = Holding.objects.filter(
        portfolio__user=user,
        portfolio__status='ACTIVE'
    ).select_related('stock', 'portfolio')
    
    # Ordres en attente
    pending_orders = TradingOrder.objects.filter(
        portfolio__user=user,
        status='PENDING'
    ).select_related('stock', 'portfolio')
    
    # Transactions récentes
    recent_transactions = Transaction.objects.filter(
        portfolio__user=user
    ).select_related('stock', 'portfolio').order_by('-executed_at')[:10]
    
    # Compétitions actives
    active_competitions = CompetitionParticipant.objects.filter(
        user=user,
        status='ACTIVE',
        competition__status='ACTIVE'
    ).select_related('competition', 'portfolio')
    
    dashboard_data = {
        'summary': {
            'total_portfolios': portfolios.count(),
            'total_value': total_value,
            'total_invested': total_invested,
            'total_return': total_return,
            'total_return_percent': (total_return / total_invested * 100) if total_invested > 0 else 0,
            'active_holdings': holdings.count(),
            'pending_orders': pending_orders.count(),
        },
        'portfolios': PortfolioSerializer(portfolios, many=True).data,
        'top_holdings': HoldingSerializer(
            holdings.order_by('-current_value')[:5], many=True
        ).data,
        'pending_orders': TradingOrderSerializer(pending_orders, many=True).data,
        'recent_transactions': TransactionSerializer(recent_transactions, many=True).data,
        'active_competitions': CompetitionParticipantSerializer(
            active_competitions, many=True
        ).data,
    }
    
    return Response(dashboard_data)

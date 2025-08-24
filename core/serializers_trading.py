"""
Serializers pour le module Trading
Sérialisation des données pour l'API REST de trading et simulation boursière
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

from .models_trading import (
    StockExtended, Portfolio, Holding, TradingOrder, Transaction,
    PriceHistory, TradingCompetition, CompetitionParticipant
)

User = get_user_model()


class StockExtendedSerializer(serializers.ModelSerializer):
    """
    Serializer pour les actions étendues
    """
    
    # Champs calculés
    price_change = serializers.ReadOnlyField()
    price_change_percent = serializers.ReadOnlyField()
    
    # Informations de marché
    market_status_display = serializers.CharField(
        source='get_market_status_display', read_only=True
    )
    category_display = serializers.CharField(
        source='get_category_display', read_only=True
    )
    
    class Meta:
        model = StockExtended
        fields = [
            'id', 'symbol', 'company_name', 'sector', 'industry', 'category',
            'market_cap', 'shares_outstanding', 'pe_ratio', 'dividend_yield', 'beta',
            'current_price', 'opening_price', 'high_price', 'low_price', 'previous_close',
            'volume', 'average_volume', 'market_status', 'is_tradeable', 'is_active',
            'created_at', 'updated_at', 'last_price_update',
            'price_change', 'price_change_percent', 'market_status_display', 'category_display'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_price_update',
            'price_change', 'price_change_percent'
        ]
    
    def validate_current_price(self, value):
        """Validation du prix actuel"""
        if value <= 0:
            raise serializers.ValidationError("Le prix doit être positif")
        return value


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer pour les portefeuilles
    """
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    
    # Champs calculés
    total_return = serializers.ReadOnlyField()
    total_return_percent = serializers.ReadOnlyField()
    holdings_count = serializers.SerializerMethodField()
    
    # Informations de performance
    portfolio_type_display = serializers.CharField(
        source='get_portfolio_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'name', 'description', 'portfolio_type',
            'initial_capital', 'current_cash', 'total_value', 'status',
            'allow_short_selling', 'allow_margin_trading',
            'created_at', 'updated_at', 'last_rebalance',
            'user_name', 'total_return', 'total_return_percent',
            'holdings_count', 'portfolio_type_display', 'status_display'
        ]
        read_only_fields = [
            'id', 'total_value', 'total_return', 'total_return_percent',
            'created_at', 'updated_at', 'last_rebalance'
        ]
    
    def get_holdings_count(self, obj):
        """Nombre de positions dans le portefeuille"""
        return obj.holdings.count()
    
    def validate_initial_capital(self, value):
        """Validation du capital initial"""
        if value < Decimal('1000'):
            raise serializers.ValidationError(
                "Le capital initial minimum est de 1,000 FCFA"
            )
        return value


class HoldingSerializer(serializers.ModelSerializer):
    """
    Serializer pour les positions détenues
    """
    
    # Informations du stock
    stock_symbol = serializers.CharField(
        source='stock.symbol', read_only=True
    )
    stock_name = serializers.CharField(
        source='stock.company_name', read_only=True
    )
    current_stock_price = serializers.DecimalField(
        source='stock.current_price', max_digits=10, decimal_places=2, read_only=True
    )
    
    # Informations du portefeuille
    portfolio_name = serializers.CharField(
        source='portfolio.name', read_only=True
    )
    
    # Champs calculés
    unrealized_gain_loss = serializers.ReadOnlyField()
    unrealized_gain_loss_percent = serializers.ReadOnlyField()
    
    class Meta:
        model = Holding
        fields = [
            'id', 'portfolio', 'stock', 'quantity', 'average_cost',
            'total_cost', 'current_value', 'first_purchase_date',
            'last_transaction_date', 'created_at', 'updated_at',
            'stock_symbol', 'stock_name', 'current_stock_price',
            'portfolio_name', 'unrealized_gain_loss', 'unrealized_gain_loss_percent'
        ]
        read_only_fields = [
            'id', 'total_cost', 'current_value', 'first_purchase_date',
            'last_transaction_date', 'created_at', 'updated_at',
            'unrealized_gain_loss', 'unrealized_gain_loss_percent'
        ]


class TradingOrderSerializer(serializers.ModelSerializer):
    """
    Serializer pour les ordres de trading
    """
    
    # Informations du stock
    stock_symbol = serializers.CharField(
        source='stock.symbol', read_only=True
    )
    stock_name = serializers.CharField(
        source='stock.company_name', read_only=True
    )
    current_stock_price = serializers.DecimalField(
        source='stock.current_price', max_digits=10, decimal_places=2, read_only=True
    )
    
    # Informations du portefeuille
    portfolio_name = serializers.CharField(
        source='portfolio.name', read_only=True
    )
    
    # Champs calculés
    remaining_quantity = serializers.ReadOnlyField()
    is_expired = serializers.SerializerMethodField()
    
    # Affichage des choix
    order_type_display = serializers.CharField(
        source='get_order_type_display', read_only=True
    )
    side_display = serializers.CharField(
        source='get_side_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = TradingOrder
        fields = [
            'id', 'portfolio', 'stock', 'order_type', 'side', 'quantity',
            'limit_price', 'stop_price', 'status', 'filled_quantity',
            'average_fill_price', 'time_in_force', 'created_at', 'updated_at',
            'filled_at', 'expires_at',
            'stock_symbol', 'stock_name', 'current_stock_price',
            'portfolio_name', 'remaining_quantity', 'is_expired',
            'order_type_display', 'side_display', 'status_display'
        ]
        read_only_fields = [
            'id', 'status', 'filled_quantity', 'average_fill_price',
            'created_at', 'updated_at', 'filled_at', 'remaining_quantity'
        ]
    
    def get_is_expired(self, obj):
        """Vérifie si l'ordre a expiré"""
        return obj.is_expired()
    
    def validate(self, data):
        """Validation des données de l'ordre"""
        order_type = data.get('order_type')
        limit_price = data.get('limit_price')
        stop_price = data.get('stop_price')
        
        if order_type in ['LIMIT', 'STOP_LIMIT'] and not limit_price:
            raise serializers.ValidationError(
                "Le prix limite est requis pour ce type d'ordre"
            )
        
        if order_type in ['STOP', 'STOP_LIMIT'] and not stop_price:
            raise serializers.ValidationError(
                "Le prix stop est requis pour ce type d'ordre"
            )
        
        return data


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les transactions
    """
    
    # Informations du stock
    stock_symbol = serializers.CharField(
        source='stock.symbol', read_only=True
    )
    stock_name = serializers.CharField(
        source='stock.company_name', read_only=True
    )
    
    # Informations du portefeuille
    portfolio_name = serializers.CharField(
        source='portfolio.name', read_only=True
    )
    
    # Informations de l'ordre
    order_id = serializers.CharField(
        source='order.id', read_only=True
    )
    
    # Affichage des choix
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display', read_only=True
    )
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'portfolio', 'stock', 'order', 'transaction_type',
            'quantity', 'price', 'total_amount', 'commission', 'fees',
            'executed_at', 'notes',
            'stock_symbol', 'stock_name', 'portfolio_name', 'order_id',
            'transaction_type_display'
        ]
        read_only_fields = ['id', 'executed_at']


class PriceHistorySerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des prix
    """
    
    # Informations du stock
    stock_symbol = serializers.CharField(
        source='stock.symbol', read_only=True
    )
    
    # Affichage des choix
    timeframe_display = serializers.CharField(
        source='get_timeframe_display', read_only=True
    )
    
    class Meta:
        model = PriceHistory
        fields = [
            'id', 'stock', 'timestamp', 'timeframe', 'open_price',
            'high_price', 'low_price', 'close_price', 'volume',
            'created_at', 'stock_symbol', 'timeframe_display'
        ]
        read_only_fields = ['id', 'created_at']


class TradingCompetitionSerializer(serializers.ModelSerializer):
    """
    Serializer pour les compétitions de trading
    """
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Statistiques
    participants_count = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = TradingCompetition
        fields = [
            'id', 'name', 'description', 'initial_capital', 'max_participants',
            'registration_start', 'registration_end', 'start_date', 'end_date',
            'status', 'prizes', 'created_at', 'updated_at',
            'created_by_name', 'participants_count', 'days_remaining', 'status_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_participants_count(self, obj):
        """Nombre de participants"""
        return obj.participants.filter(status='ACTIVE').count()
    
    def get_days_remaining(self, obj):
        """Jours restants"""
        if obj.end_date:
            delta = obj.end_date - date.today()
            return max(0, delta.days)
        return 0


class CompetitionParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer pour les participants aux compétitions
    """
    
    # Informations utilisateur
    user_name = serializers.CharField(
        source='user.full_name', read_only=True
    )
    user_email = serializers.CharField(
        source='user.email', read_only=True
    )
    
    # Informations de la compétition
    competition_name = serializers.CharField(
        source='competition.name', read_only=True
    )
    
    # Informations du portefeuille
    portfolio_name = serializers.CharField(
        source='portfolio.name', read_only=True
    )
    portfolio_value = serializers.DecimalField(
        source='portfolio.total_value', max_digits=15, decimal_places=2, read_only=True
    )
    portfolio_return = serializers.DecimalField(
        source='portfolio.total_return_percent', max_digits=5, decimal_places=2, read_only=True
    )
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = CompetitionParticipant
        fields = [
            'id', 'competition', 'user', 'portfolio', 'status',
            'current_rank', 'final_rank', 'registered_at', 'last_activity',
            'user_name', 'user_email', 'competition_name',
            'portfolio_name', 'portfolio_value', 'portfolio_return', 'status_display'
        ]
        read_only_fields = [
            'id', 'current_rank', 'final_rank', 'registered_at', 'last_activity'
        ]


# Serializers pour la création et mise à jour

class PortfolioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de portefeuilles
    """
    
    class Meta:
        model = Portfolio
        fields = [
            'name', 'description', 'portfolio_type', 'initial_capital',
            'allow_short_selling', 'allow_margin_trading'
        ]
    
    def validate_initial_capital(self, value):
        """Validation du capital initial"""
        if value < Decimal('1000'):
            raise serializers.ValidationError(
                "Le capital initial minimum est de 1,000 FCFA"
            )
        if value > Decimal('100000000'):  # 100M FCFA
            raise serializers.ValidationError(
                "Le capital initial maximum est de 100,000,000 FCFA"
            )
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'ordres
    """
    
    class Meta:
        model = TradingOrder
        fields = [
            'stock', 'order_type', 'side', 'quantity',
            'limit_price', 'stop_price', 'time_in_force'
        ]
    
    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive")
        return value
    
    def validate(self, data):
        """Validation croisée des données"""
        order_type = data.get('order_type')
        limit_price = data.get('limit_price')
        stop_price = data.get('stop_price')
        
        if order_type in ['LIMIT', 'STOP_LIMIT'] and not limit_price:
            raise serializers.ValidationError(
                "Le prix limite est requis pour ce type d'ordre"
            )
        
        if order_type in ['STOP', 'STOP_LIMIT'] and not stop_price:
            raise serializers.ValidationError(
                "Le prix stop est requis pour ce type d'ordre"
            )
        
        if limit_price and limit_price <= 0:
            raise serializers.ValidationError(
                "Le prix limite doit être positif"
            )
        
        if stop_price and stop_price <= 0:
            raise serializers.ValidationError(
                "Le prix stop doit être positif"
            )
        
        return data


class CompetitionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de compétitions
    """
    
    class Meta:
        model = TradingCompetition
        fields = [
            'name', 'description', 'initial_capital', 'max_participants',
            'registration_start', 'registration_end', 'start_date', 'end_date',
            'prizes'
        ]
    
    def validate(self, data):
        """Validation des dates"""
        registration_start = data.get('registration_start')
        registration_end = data.get('registration_end')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if registration_start and registration_end:
            if registration_start >= registration_end:
                raise serializers.ValidationError(
                    "La fin des inscriptions doit être après le début"
                )
        
        if start_date and end_date:
            if start_date >= end_date:
                raise serializers.ValidationError(
                    "La date de fin doit être après la date de début"
                )
        
        if registration_end and start_date:
            if registration_end > start_date:
                raise serializers.ValidationError(
                    "Les inscriptions doivent se terminer avant le début de la compétition"
                )
        
        return data

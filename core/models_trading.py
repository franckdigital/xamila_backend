"""
Modèles spécialisés pour le trading et la simulation boursière
Portefeuilles virtuels, ordres, historiques de prix
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class StockExtended(models.Model):
    """
    Extension du modèle Stock avec données avancées
    """
    
    STOCK_CATEGORIES = [
        ('BLUE_CHIP', 'Blue Chip'),
        ('GROWTH', 'Croissance'),
        ('VALUE', 'Valeur'),
        ('DIVIDEND', 'Dividende'),
        ('TECH', 'Technologie'),
        ('FINANCE', 'Finance'),
        ('HEALTHCARE', 'Santé'),
        ('ENERGY', 'Énergie'),
        ('CONSUMER', 'Consommation'),
        ('INDUSTRIAL', 'Industriel'),
    ]
    
    MARKET_STATUS = [
        ('OPEN', 'Marché ouvert'),
        ('CLOSED', 'Marché fermé'),
        ('PRE_MARKET', 'Pré-marché'),
        ('AFTER_HOURS', 'Après bourse'),
        ('SUSPENDED', 'Suspendu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation avec le stock de base (si on garde la compatibilité)
    base_stock = models.OneToOneField(
        'Stock', on_delete=models.CASCADE, blank=True, null=True,
        related_name='extended_stock'
    )
    
    # Informations étendues
    symbol = models.CharField(
        max_length=10, unique=True, db_index=True,
        verbose_name="Symbole"
    )
    company_name = models.CharField(max_length=200, verbose_name="Nom de l'entreprise")
    sector = models.CharField(max_length=100, verbose_name="Secteur")
    industry = models.CharField(max_length=100, verbose_name="Industrie")
    category = models.CharField(
        max_length=20, choices=STOCK_CATEGORIES,
        verbose_name="Catégorie"
    )
    
    # Données financières avancées
    market_cap = models.DecimalField(
        max_digits=20, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Capitalisation boursière"
    )
    shares_outstanding = models.BigIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Actions en circulation"
    )
    
    # Ratios financiers
    pe_ratio = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        verbose_name="Ratio P/E"
    )
    dividend_yield = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Rendement dividende (%)"
    )
    beta = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True,
        verbose_name="Coefficient Beta"
    )
    
    # Prix et variations
    current_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix actuel"
    )
    opening_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix d'ouverture"
    )
    high_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Plus haut"
    )
    low_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Plus bas"
    )
    previous_close = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Clôture précédente"
    )
    
    # Volume et liquidité
    volume = models.BigIntegerField(
        default=0, validators=[MinValueValidator(0)],
        verbose_name="Volume"
    )
    average_volume = models.BigIntegerField(
        default=0, validators=[MinValueValidator(0)],
        verbose_name="Volume moyen"
    )
    
    # Statut du marché
    market_status = models.CharField(
        max_length=20, choices=MARKET_STATUS,
        default='CLOSED', verbose_name="Statut du marché"
    )
    
    # Configuration
    is_tradeable = models.BooleanField(
        default=True, verbose_name="Négociable"
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Actif"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_price_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Action étendue"
        verbose_name_plural = "Actions étendues"
        ordering = ['symbol']
    
    def __str__(self):
        return f"{self.symbol} - {self.company_name}"
    
    @property
    def price_change(self):
        """Calcule la variation de prix"""
        return self.current_price - self.previous_close
    
    @property
    def price_change_percent(self):
        """Calcule la variation de prix en pourcentage"""
        if self.previous_close > 0:
            return ((self.current_price - self.previous_close) / self.previous_close) * 100
        return Decimal('0.00')


class Portfolio(models.Model):
    """
    Portefeuilles virtuels des utilisateurs
    """
    
    PORTFOLIO_TYPES = [
        ('PRACTICE', 'Entraînement'),
        ('COMPETITION', 'Compétition'),
        ('EDUCATION', 'Éducation'),
        ('SIMULATION', 'Simulation'),
    ]
    
    PORTFOLIO_STATUS = [
        ('ACTIVE', 'Actif'),
        ('INACTIVE', 'Inactif'),
        ('FROZEN', 'Gelé'),
        ('CLOSED', 'Fermé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='portfolios'
    )
    
    # Informations du portefeuille
    name = models.CharField(max_length=200, verbose_name="Nom du portefeuille")
    description = models.TextField(blank=True, verbose_name="Description")
    portfolio_type = models.CharField(
        max_length=20, choices=PORTFOLIO_TYPES,
        verbose_name="Type de portefeuille"
    )
    
    # Capital et performance
    initial_capital = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Capital initial"
    )
    current_cash = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Liquidités actuelles"
    )
    total_value = models.DecimalField(
        max_digits=15, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valeur totale"
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=PORTFOLIO_STATUS,
        default='ACTIVE', verbose_name="Statut"
    )
    
    # Configuration
    allow_short_selling = models.BooleanField(
        default=False, verbose_name="Vente à découvert autorisée"
    )
    allow_margin_trading = models.BooleanField(
        default=False, verbose_name="Trading sur marge autorisé"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_rebalance = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Portefeuille"
        verbose_name_plural = "Portefeuilles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.name}"
    
    def calculate_total_value(self):
        """Calcule la valeur totale du portefeuille"""
        holdings_value = sum(
            holding.current_value for holding in self.holdings.all()
        )
        return self.current_cash + holdings_value
    
    @property
    def total_return(self):
        """Calcule le rendement total"""
        return self.total_value - self.initial_capital
    
    @property
    def total_return_percent(self):
        """Calcule le rendement total en pourcentage"""
        if self.initial_capital > 0:
            return (self.total_return / self.initial_capital) * 100
        return Decimal('0.00')


class Holding(models.Model):
    """
    Positions détenues dans un portefeuille
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE,
        related_name='holdings'
    )
    stock = models.ForeignKey(
        StockExtended, on_delete=models.CASCADE,
        related_name='holdings'
    )
    
    # Quantité et prix
    quantity = models.DecimalField(
        max_digits=15, decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Quantité"
    )
    average_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix moyen d'achat"
    )
    
    # Valeurs calculées
    total_cost = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="Coût total"
    )
    current_value = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="Valeur actuelle"
    )
    
    # Métadonnées
    first_purchase_date = models.DateTimeField(verbose_name="Date du premier achat")
    last_transaction_date = models.DateTimeField(verbose_name="Date de la dernière transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        ordering = ['-current_value']
        unique_together = ['portfolio', 'stock']
    
    def __str__(self):
        return f"{self.portfolio.name} - {self.stock.symbol} ({self.quantity})"
    
    @property
    def unrealized_gain_loss(self):
        """Calcule la plus/moins-value latente"""
        return self.current_value - self.total_cost
    
    @property
    def unrealized_gain_loss_percent(self):
        """Calcule la plus/moins-value latente en pourcentage"""
        if self.total_cost > 0:
            return (self.unrealized_gain_loss / self.total_cost) * 100
        return Decimal('0.00')


class TradingOrder(models.Model):
    """
    Ordres de trading
    """
    
    ORDER_TYPES = [
        ('MARKET', 'Ordre au marché'),
        ('LIMIT', 'Ordre à cours limité'),
        ('STOP', 'Ordre stop'),
        ('STOP_LIMIT', 'Ordre stop-limit'),
    ]
    
    ORDER_SIDES = [
        ('BUY', 'Achat'),
        ('SELL', 'Vente'),
    ]
    
    ORDER_STATUS = [
        ('PENDING', 'En attente'),
        ('PARTIAL', 'Partiellement exécuté'),
        ('FILLED', 'Exécuté'),
        ('CANCELLED', 'Annulé'),
        ('REJECTED', 'Rejeté'),
        ('EXPIRED', 'Expiré'),
    ]
    
    TIME_IN_FORCE = [
        ('DAY', 'Jour'),
        ('GTC', 'Jusqu\'à annulation'),
        ('IOC', 'Immédiat ou annulé'),
        ('FOK', 'Tout ou rien'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE,
        related_name='orders'
    )
    stock = models.ForeignKey(
        StockExtended, on_delete=models.CASCADE,
        related_name='orders'
    )
    
    # Détails de l'ordre
    order_type = models.CharField(
        max_length=20, choices=ORDER_TYPES,
        verbose_name="Type d'ordre"
    )
    side = models.CharField(
        max_length=10, choices=ORDER_SIDES,
        verbose_name="Sens"
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Quantité"
    )
    
    # Prix
    limit_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix limite"
    )
    stop_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix stop"
    )
    
    # Exécution
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS,
        default='PENDING', verbose_name="Statut"
    )
    filled_quantity = models.DecimalField(
        max_digits=15, decimal_places=4,
        default=Decimal('0.0000'),
        verbose_name="Quantité exécutée"
    )
    average_fill_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Prix moyen d'exécution"
    )
    
    # Configuration
    time_in_force = models.CharField(
        max_length=10, choices=TIME_IN_FORCE,
        default='DAY', verbose_name="Durée de validité"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    filled_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Ordre de trading"
        verbose_name_plural = "Ordres de trading"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.side} {self.quantity} {self.stock.symbol} @ {self.limit_price or 'Market'}"
    
    @property
    def remaining_quantity(self):
        """Calcule la quantité restante à exécuter"""
        return self.quantity - self.filled_quantity
    
    def is_expired(self):
        """Vérifie si l'ordre a expiré"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class Transaction(models.Model):
    """
    Historique des transactions exécutées
    """
    
    TRANSACTION_TYPES = [
        ('BUY', 'Achat'),
        ('SELL', 'Vente'),
        ('DIVIDEND', 'Dividende'),
        ('SPLIT', 'Division d\'actions'),
        ('DEPOSIT', 'Dépôt'),
        ('WITHDRAWAL', 'Retrait'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE,
        related_name='transactions'
    )
    stock = models.ForeignKey(
        StockExtended, on_delete=models.CASCADE, blank=True, null=True,
        related_name='transactions'
    )
    order = models.ForeignKey(
        TradingOrder, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='transactions'
    )
    
    # Détails de la transaction
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES,
        verbose_name="Type de transaction"
    )
    quantity = models.DecimalField(
        max_digits=15, decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Quantité"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix"
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="Montant total"
    )
    
    # Frais
    commission = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Commission"
    )
    fees = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Frais"
    )
    
    # Métadonnées
    executed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.transaction_type} {self.quantity} {self.stock.symbol if self.stock else 'N/A'} @ {self.price}"


class PriceHistory(models.Model):
    """
    Historique des prix des actions
    """
    
    TIMEFRAMES = [
        ('1MIN', '1 minute'),
        ('5MIN', '5 minutes'),
        ('15MIN', '15 minutes'),
        ('1HOUR', '1 heure'),
        ('1DAY', '1 jour'),
        ('1WEEK', '1 semaine'),
        ('1MONTH', '1 mois'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock = models.ForeignKey(
        StockExtended, on_delete=models.CASCADE,
        related_name='price_history'
    )
    
    # Données OHLCV
    timestamp = models.DateTimeField(db_index=True, verbose_name="Horodatage")
    timeframe = models.CharField(
        max_length=10, choices=TIMEFRAMES,
        verbose_name="Période"
    )
    open_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix d'ouverture"
    )
    high_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Plus haut"
    )
    low_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Plus bas"
    )
    close_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix de clôture"
    )
    volume = models.BigIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Volume"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historique des prix"
        verbose_name_plural = "Historiques des prix"
        ordering = ['-timestamp']
        unique_together = ['stock', 'timestamp', 'timeframe']
        indexes = [
            models.Index(fields=['stock', 'timeframe', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - {self.timestamp} ({self.timeframe})"


class TradingCompetition(models.Model):
    """
    Compétitions de trading
    """
    
    COMPETITION_STATUS = [
        ('UPCOMING', 'À venir'),
        ('ACTIVE', 'En cours'),
        ('ENDED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de la compétition
    name = models.CharField(max_length=200, verbose_name="Nom de la compétition")
    description = models.TextField(verbose_name="Description")
    
    # Configuration
    initial_capital = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Capital initial"
    )
    max_participants = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name="Nombre maximum de participants"
    )
    
    # Dates
    registration_start = models.DateTimeField(verbose_name="Début des inscriptions")
    registration_end = models.DateTimeField(verbose_name="Fin des inscriptions")
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    
    # Statut
    status = models.CharField(
        max_length=20, choices=COMPETITION_STATUS,
        default='UPCOMING', verbose_name="Statut"
    )
    
    # Récompenses
    prizes = models.JSONField(
        default=list, blank=True,
        verbose_name="Prix et récompenses"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_competitions'
    )
    
    class Meta:
        verbose_name = "Compétition de trading"
        verbose_name_plural = "Compétitions de trading"
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.status})"


class CompetitionParticipant(models.Model):
    """
    Participants aux compétitions de trading
    """
    
    PARTICIPATION_STATUS = [
        ('REGISTERED', 'Inscrit'),
        ('ACTIVE', 'Actif'),
        ('DISQUALIFIED', 'Disqualifié'),
        ('WITHDRAWN', 'Retiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competition = models.ForeignKey(
        TradingCompetition, on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='competition_participations'
    )
    portfolio = models.OneToOneField(
        Portfolio, on_delete=models.CASCADE,
        related_name='competition_participation'
    )
    
    # Statut
    status = models.CharField(
        max_length=20, choices=PARTICIPATION_STATUS,
        default='REGISTERED', verbose_name="Statut"
    )
    
    # Performance
    current_rank = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name="Classement actuel"
    )
    final_rank = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name="Classement final"
    )
    
    # Dates
    registered_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Participant à la compétition"
        verbose_name_plural = "Participants aux compétitions"
        ordering = ['current_rank']
        unique_together = ['competition', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.competition.name}"

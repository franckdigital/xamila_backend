"""
URLs pour le module Trading
Endpoints REST pour la gestion des portefeuilles et du trading
"""

from django.urls import path
from . import views_trading_basic as views_trading

app_name = 'trading'

urlpatterns = [
    # === PORTFOLIOS ===
    path('portfolios/', views_trading.PortfolioListView.as_view(), name='portfolio-list'),
    path('portfolios/<uuid:pk>/', views_trading.PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('portfolios/<uuid:portfolio_id>/performance/', views_trading.portfolio_performance, name='portfolio-performance'),
    
    # === POSITIONS ===
    path('positions/', views_trading.PositionListView.as_view(), name='position-list'),
    path('positions/<uuid:pk>/', views_trading.PositionDetailView.as_view(), name='position-detail'),
    path('positions/<uuid:position_id>/close/', views_trading.close_position, name='close-position'),
    
    # === ORDERS ===
    path('orders/', views_trading.OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:pk>/', views_trading.OrderDetailView.as_view(), name='order-detail'),
    path('orders/create/', views_trading.create_order, name='create-order'),
    path('orders/<uuid:order_id>/cancel/', views_trading.cancel_order, name='cancel-order'),
    path('orders/<uuid:order_id>/execute/', views_trading.execute_order, name='execute-order'),
    
    # === TRANSACTIONS ===
    path('transactions/', views_trading.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:pk>/', views_trading.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # === HOLDINGS ===
    path('holdings/', views_trading.HoldingListView.as_view(), name='holding-list'),
    path('holdings/<uuid:pk>/', views_trading.HoldingDetailView.as_view(), name='holding-detail'),
    
    # === WATCHLISTS ===
    path('watchlists/', views_trading.WatchlistListView.as_view(), name='watchlist-list'),
    path('watchlists/<uuid:pk>/', views_trading.WatchlistDetailView.as_view(), name='watchlist-detail'),
    path('watchlists/<uuid:watchlist_id>/add-asset/', views_trading.add_to_watchlist, name='add-to-watchlist'),
    path('watchlists/<uuid:watchlist_id>/remove-asset/', views_trading.remove_from_watchlist, name='remove-from-watchlist'),
    
    # === ANALYTICS ===
    path('analytics/dashboard/', views_trading.trading_dashboard, name='trading-dashboard'),
    path('analytics/performance/', views_trading.trading_analytics, name='trading-analytics'),
    path('analytics/risk-metrics/', views_trading.risk_metrics, name='risk-metrics'),
    
    # === MARKET DATA ===
    path('market/assets/', views_trading.AssetListView.as_view(), name='asset-list'),
    path('market/assets/<uuid:pk>/', views_trading.AssetDetailView.as_view(), name='asset-detail'),
    path('market/prices/', views_trading.market_prices, name='market-prices'),
    path('market/prices/<str:symbol>/', views_trading.asset_price_history, name='asset-price-history'),
]

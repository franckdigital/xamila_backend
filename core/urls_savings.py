"""
URLs pour les APIs d'épargne Ma Caisse
"""

from django.urls import path
from . import views_savings

urlpatterns = [
    # Compte d'épargne
    path('account/', views_savings.savings_account, name='savings_account'),
    
    # Transactions
    path('transactions/', views_savings.savings_transactions, name='savings_transactions'),
    
    # Dépôts et retraits
    path('deposit/', views_savings.savings_deposit, name='savings_deposit'),
    path('withdraw/', views_savings.savings_withdraw, name='savings_withdraw'),
    
    # Statistiques
    path('stats/', views_savings.savings_stats, name='savings_stats'),
    
    # Progression collective
    path('collective-progress/', views_savings.collective_progress, name='collective_progress'),
]

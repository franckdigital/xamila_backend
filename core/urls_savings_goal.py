"""
URLs pour la gestion des objectifs d'épargne mensuels
"""

from django.urls import path
from . import views_savings_goal

urlpatterns = [
    path('monthly-goal/', views_savings_goal.monthly_savings_goal, name='monthly_savings_goal'),
    path('monthly-progress/', views_savings_goal.monthly_savings_progress, name='monthly_savings_progress'),
]

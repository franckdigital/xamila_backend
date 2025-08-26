from django.urls import path
from . import views_bilans

urlpatterns = [
    # Flux financiers
    path('flux/', views_bilans.flux_financiers_list, name='flux_financiers_list'),
    path('flux/<uuid:flux_id>/', views_bilans.flux_financier_detail, name='flux_financier_detail'),
    
    # Bilan calculé
    path('bilan/', views_bilans.bilan_calcule, name='bilan_calcule'),
    
    # Utilitaires
    path('categories/', views_bilans.categories_disponibles, name='categories_disponibles'),
]

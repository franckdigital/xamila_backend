# -*- coding: utf-8 -*-
"""
URLs pour les APIs publiques du blog XAMILA (Actualités)
Accès public pour la lecture des articles
"""

from django.urls import path
from . import views_blog_public

urlpatterns = [
    # ===== CATÉGORIES PUBLIQUES =====
    path('public/blog/categories/', 
         views_blog_public.PublicCategorieListView.as_view(), 
         name='public-categories-list'),
    
    # ===== ACTUALITÉS PUBLIQUES =====
    path('public/blog/actualites/', 
         views_blog_public.PublicActualitesListView.as_view(), 
         name='public-actualites-list'),
    
    path('public/blog/actualites/featured/', 
         views_blog_public.PublicActualitesFeaturedView.as_view(), 
         name='public-actualites-featured'),
    
    path('public/blog/actualites/<slug:slug>/', 
         views_blog_public.PublicActualitesDetailView.as_view(), 
         name='public-actualites-detail'),
    
    # ===== STATISTIQUES PUBLIQUES =====
    path('public/blog/stats/', 
         views_blog_public.public_blog_stats, 
         name='public-blog-stats'),
]

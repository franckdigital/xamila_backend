# -*- coding: utf-8 -*-
"""
URLs pour les APIs du blog XAMILA (Actualités)
Accès restreint aux administrateurs uniquement
"""

from django.urls import path
from . import views_blog

urlpatterns = [
    # ===== GESTION DES CATÉGORIES =====
    path('admin/blog/categories/', 
         views_blog.AdminCategorieListCreateView.as_view(), 
         name='admin-categories-list-create'),
    
    path('admin/blog/categories/<int:pk>/', 
         views_blog.AdminCategorieDetailView.as_view(), 
         name='admin-categories-detail'),
    
    # ===== GESTION DES SOUS-CATÉGORIES =====
    path('admin/blog/sous-categories/', 
         views_blog.AdminSousCategorieListCreateView.as_view(), 
         name='admin-sous-categories-list-create'),
    
    path('admin/blog/sous-categories/<int:pk>/', 
         views_blog.AdminSousCategorieDetailView.as_view(), 
         name='admin-sous-categories-detail'),
    
    # ===== GESTION DES BANNIÈRES =====
    path('admin/blog/bannieres/', 
         views_blog.AdminBanniereListCreateView.as_view(), 
         name='admin-bannieres-list-create'),
    
    path('admin/blog/bannieres/<int:pk>/', 
         views_blog.AdminBanniereDetailView.as_view(), 
         name='admin-bannieres-detail'),
    
    # ===== GESTION DES ACTUALITÉS =====
    path('admin/blog/actualites/', 
         views_blog.AdminActualitesListCreateView.as_view(), 
         name='admin-actualites-list-create'),
    
    path('admin/blog/actualites/<int:pk>/', 
         views_blog.AdminActualitesDetailView.as_view(), 
         name='admin-actualites-detail'),
    
    # Actions spéciales sur les articles
    path('admin/blog/actualites/<int:pk>/publish/', 
         views_blog.admin_actualites_publish, 
         name='admin-actualites-publish'),
    
    path('admin/blog/actualites/<int:pk>/archive/', 
         views_blog.admin_actualites_archive, 
         name='admin-actualites-archive'),
    
    # ===== STATISTIQUES =====
    path('admin/blog/stats/', 
         views_blog.admin_blog_stats, 
         name='admin-blog-stats'),
]

"""
URLs pour les endpoints du dashboard multi-rôles
"""

from django.urls import path
from . import views_dashboard

app_name = 'dashboard'

urlpatterns = [
    # === DASHBOARDS PAR RÔLE ===
    
    # Dashboard client/customer
    path('customer/', views_dashboard.customer_dashboard_metrics, name='customer-dashboard'),
    
    # Dashboard manager SGI
    path('sgi-manager/', views_dashboard.SGIManagerDashboardView.as_view(), name='sgi-manager-dashboard'),
    
    # Dashboard étudiant
    path('student/', views_dashboard.StudentDashboardView.as_view(), name='student-dashboard'),
    
    # Dashboard instructeur
    path('instructor/', views_dashboard.InstructorDashboardView.as_view(), name='instructor-dashboard'),
    
    # Dashboard support
    path('support/', views_dashboard.SupportDashboardView.as_view(), name='support-dashboard'),
    
    # === ENDPOINTS SPÉCIFIQUES ===
    
    # Savings & Challenges (pour CUSTOMER)
    path('savings/challenges/', views_dashboard.savings_challenges_list, name='savings-challenges'),
    path('savings/deposits/', views_dashboard.savings_deposits_list, name='savings-deposits'),
    
    # Learning & Courses (pour STUDENT et INSTRUCTOR)
    path('learning/courses/', views_dashboard.learning_courses_list, name='learning-courses'),
    path('learning/progress/', views_dashboard.learning_progress, name='learning-progress'),
    path('learning/instructor/stats/', views_dashboard.instructor_stats, name='instructor-stats'),
    path('learning/instructor/courses/', views_dashboard.instructor_courses_list, name='instructor-courses'),
    
    # Support & Tickets (pour SUPPORT)
    path('support/tickets/', views_dashboard.support_tickets_list, name='support-tickets'),
    
    # Notifications (pour tous)
    path('notifications/', views_dashboard.notifications_list, name='notifications'),
]

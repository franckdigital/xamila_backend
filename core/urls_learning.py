"""
URLs pour le module Learning
Endpoints REST pour l'e-learning et les formations
"""

from django.urls import path
from . import views_learning_basic as views_learning

app_name = 'learning'

urlpatterns = [
    # === LEARNING PATHS ===
    path('paths/', views_learning.LearningPathListView.as_view(), name='path-list'),
    path('paths/<uuid:pk>/', views_learning.LearningPathDetailView.as_view(), name='path-detail'),
    path('paths/<uuid:path_id>/enroll/', views_learning.enroll_learning_path, name='enroll-path'),
    
    # === LEARNING MODULES ===
    path('modules/', views_learning.LearningModuleListView.as_view(), name='module-list'),
    path('modules/<uuid:pk>/', views_learning.LearningModuleDetailView.as_view(), name='module-detail'),
    path('modules/<uuid:module_id>/complete/', views_learning.complete_module, name='complete-module'),
    
    # === QUIZZES ===
    path('quizzes/', views_learning.QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<uuid:pk>/', views_learning.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<uuid:quiz_id>/start/', views_learning.start_quiz, name='start-quiz'),
    path('quizzes/<uuid:quiz_id>/submit/', views_learning.submit_quiz, name='submit-quiz'),
    
    # === STUDENT PROGRESS ===
    path('progress/', views_learning.StudentProgressListView.as_view(), name='progress-list'),
    path('progress/<uuid:pk>/', views_learning.StudentProgressDetailView.as_view(), name='progress-detail'),
    
    # === DASHBOARD & ANALYTICS ===
    path('dashboard/', views_learning.student_dashboard, name='student-dashboard'),
    path('analytics/', views_learning.learning_analytics, name='learning-analytics'),
]

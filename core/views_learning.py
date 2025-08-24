"""
Vues API pour le module Learning
Endpoints REST pour l'e-learning et les formations
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models_learning import (
    LearningPath, LearningModule, QuizExtended, QuestionExtended,
    StudentProgress, ModuleCompletion, QuizAttempt, Certification
)
from .serializers_learning import (
    LearningPathSerializer, LearningModuleSerializer, QuizExtendedSerializer,
    QuestionExtendedSerializer, StudentProgressSerializer, ModuleCompletionSerializer,
    QuizAttemptSerializer, CertificationSerializer, LearningPathCreateSerializer,
    LearningModuleCreateSerializer, QuestionCreateSerializer, StudentEnrollmentSerializer
)


class LearningPathListView(generics.ListCreateAPIView):
    """
    Parcours d'apprentissage disponibles
    GET: Liste des parcours
    POST: Créer un nouveau parcours (instructeur/admin)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LearningPathCreateSerializer
        return LearningPathSerializer
    
    def get_queryset(self):
        queryset = LearningPath.objects.filter(is_active=True)
        
        # Filtres
        difficulty = self.request.query_params.get('difficulty')
        path_type = self.request.query_params.get('type')
        search = self.request.query_params.get('search')
        
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        if path_type:
            queryset = queryset.filter(path_type=path_type)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('difficulty_level', 'title')
    
    def perform_create(self, serializer):
        # Seuls les instructeurs et admins peuvent créer des parcours
        if not self.request.user.role in ['INSTRUCTOR', 'ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les instructeurs peuvent créer des parcours"
            )
        
        serializer.save(created_by=self.request.user)


class LearningPathDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un parcours d'apprentissage
    """
    queryset = LearningPath.objects.filter(is_active=True)
    serializer_class = LearningPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        path = super().get_object()
        
        # Ajouter des statistiques si l'utilisateur est inscrit
        if hasattr(self.request.user, 'learning_progress'):
            try:
                progress = StudentProgress.objects.get(
                    student=self.request.user,
                    learning_path=path
                )
                path.user_progress = progress
            except StudentProgress.DoesNotExist:
                path.user_progress = None
        
        return path


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def enroll_in_path(request, path_id):
    """
    S'inscrire à un parcours d'apprentissage
    """
    try:
        learning_path = LearningPath.objects.get(id=path_id, is_active=True)
    except LearningPath.DoesNotExist:
        return Response(
            {'error': 'Parcours d\'apprentissage introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier si l'utilisateur est déjà inscrit
    existing_progress = StudentProgress.objects.filter(
        student=request.user,
        learning_path=learning_path
    ).first()
    
    if existing_progress:
        return Response(
            {'error': 'Vous êtes déjà inscrit à ce parcours'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier les prérequis
    for prerequisite in learning_path.prerequisites.all():
        prerequisite_progress = StudentProgress.objects.filter(
            student=request.user,
            learning_path=prerequisite,
            status='COMPLETED'
        ).first()
        
        if not prerequisite_progress:
            return Response(
                {'error': f'Prérequis manquant: {prerequisite.title}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Créer la progression
    progress = StudentProgress.objects.create(
        student=request.user,
        learning_path=learning_path,
        status='IN_PROGRESS',
        started_at=timezone.now()
    )
    
    return Response({
        'message': 'Inscription réussie au parcours',
        'progress': StudentProgressSerializer(progress).data
    })


class LearningModuleListView(generics.ListCreateAPIView):
    """
    Modules d'apprentissage
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LearningModuleCreateSerializer
        return LearningModuleSerializer
    
    def get_queryset(self):
        path_id = self.request.query_params.get('path')
        queryset = LearningModule.objects.filter(is_active=True)
        
        if path_id:
            queryset = queryset.filter(learning_path_id=path_id)
        
        return queryset.order_by('learning_path', 'order')
    
    def perform_create(self, serializer):
        if not self.request.user.role in ['INSTRUCTOR', 'ADMIN', 'SUPPORT']:
            raise permissions.PermissionDenied(
                "Seuls les instructeurs peuvent créer des modules"
            )
        
        serializer.save()


class LearningModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un module d'apprentissage
    """
    queryset = LearningModule.objects.filter(is_active=True)
    serializer_class = LearningModuleSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_module(request, module_id):
    """
    Commencer un module d'apprentissage
    """
    try:
        module = LearningModule.objects.get(id=module_id, is_active=True)
    except LearningModule.DoesNotExist:
        return Response(
            {'error': 'Module introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier que l'utilisateur est inscrit au parcours
    try:
        student_progress = StudentProgress.objects.get(
            student=request.user,
            learning_path=module.learning_path,
            status__in=['IN_PROGRESS', 'COMPLETED']
        )
    except StudentProgress.DoesNotExist:
        return Response(
            {'error': 'Vous devez être inscrit au parcours'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Créer ou récupérer la completion du module
    module_completion, created = ModuleCompletion.objects.get_or_create(
        student_progress=student_progress,
        learning_module=module,
        defaults={
            'status': 'IN_PROGRESS',
            'started_at': timezone.now()
        }
    )
    
    if not created and module_completion.status == 'COMPLETED':
        return Response(
            {'error': 'Module déjà terminé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'message': 'Module commencé',
        'completion': ModuleCompletionSerializer(module_completion).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def complete_module(request, module_id):
    """
    Terminer un module d'apprentissage
    """
    try:
        module = LearningModule.objects.get(id=module_id, is_active=True)
    except LearningModule.DoesNotExist:
        return Response(
            {'error': 'Module introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Récupérer la completion du module
    try:
        student_progress = StudentProgress.objects.get(
            student=request.user,
            learning_path=module.learning_path
        )
        module_completion = ModuleCompletion.objects.get(
            student_progress=student_progress,
            learning_module=module
        )
    except (StudentProgress.DoesNotExist, ModuleCompletion.DoesNotExist):
        return Response(
            {'error': 'Module non commencé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Marquer comme terminé
    module_completion.status = 'COMPLETED'
    module_completion.completed_at = timezone.now()
    module_completion.save()
    
    # Mettre à jour la progression du parcours
    _update_student_progress(student_progress)
    
    return Response({
        'message': 'Module terminé avec succès',
        'completion': ModuleCompletionSerializer(module_completion).data
    })


class QuizExtendedListView(generics.ListCreateAPIView):
    """
    Quiz étendus
    """
    serializer_class = QuizExtendedSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        module_id = self.request.query_params.get('module')
        queryset = QuizExtended.objects.all()
        
        if module_id:
            queryset = queryset.filter(learning_module_id=module_id)
        
        return queryset.select_related('learning_module')


class QuizExtendedDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Détails d'un quiz étendu
    """
    queryset = QuizExtended.objects.all()
    serializer_class = QuizExtendedSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_quiz(request, quiz_id):
    """
    Commencer un quiz
    """
    try:
        quiz = QuizExtended.objects.get(id=quiz_id)
        module = quiz.learning_module
    except QuizExtended.DoesNotExist:
        return Response(
            {'error': 'Quiz introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Vérifier la completion du module
    try:
        student_progress = StudentProgress.objects.get(
            student=request.user,
            learning_path=module.learning_path
        )
        module_completion = ModuleCompletion.objects.get(
            student_progress=student_progress,
            learning_module=module
        )
    except (StudentProgress.DoesNotExist, ModuleCompletion.DoesNotExist):
        return Response(
            {'error': 'Module non commencé'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier le nombre de tentatives
    attempts_count = module_completion.quiz_attempts.count()
    if attempts_count >= quiz.max_attempts:
        return Response(
            {'error': 'Nombre maximum de tentatives atteint'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier la période de cooldown
    if attempts_count > 0:
        last_attempt = module_completion.quiz_attempts.order_by('-started_at').first()
        if last_attempt and quiz.cooldown_period:
            time_since_last = timezone.now() - last_attempt.started_at
            if time_since_last < quiz.cooldown_period:
                remaining_time = quiz.cooldown_period - time_since_last
                return Response(
                    {'error': f'Attendez {remaining_time} avant la prochaine tentative'},
                    status=status.HTTP_400_BAD_REQUEST
                )
    
    # Créer une nouvelle tentative
    attempt = QuizAttempt.objects.create(
        module_completion=module_completion,
        status='STARTED',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Récupérer les questions
    questions = quiz.questions.filter(is_active=True)
    if quiz.randomize_questions:
        questions = questions.order_by('?')
    else:
        questions = questions.order_by('order')
    
    # Préparer les questions pour l'affichage
    questions_data = []
    for question in questions:
        question_data = QuestionExtendedSerializer(question).data
        
        # Masquer les réponses correctes
        question_data.pop('correct_answers', None)
        
        # Mélanger les options si nécessaire
        if quiz.randomize_answers and question.options:
            import random
            question_data['options'] = random.sample(
                question_data['options'], 
                len(question_data['options'])
            )
        
        questions_data.append(question_data)
    
    return Response({
        'attempt_id': attempt.id,
        'quiz': QuizExtendedSerializer(quiz).data,
        'questions': questions_data,
        'time_limit': quiz.time_limit.total_seconds() if quiz.time_limit else None
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_quiz(request, attempt_id):
    """
    Soumettre les réponses d'un quiz
    """
    try:
        attempt = QuizAttempt.objects.get(
            id=attempt_id,
            module_completion__student_progress__student=request.user,
            status='STARTED'
        )
    except QuizAttempt.DoesNotExist:
        return Response(
            {'error': 'Tentative de quiz introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    answers = request.data.get('answers', {})
    
    # Calculer le score
    quiz = attempt.module_completion.learning_module.quiz_extended
    questions = quiz.questions.filter(is_active=True)
    
    total_points = sum(q.points for q in questions)
    earned_points = Decimal('0.00')
    correct_answers = 0
    
    for question in questions:
        question_id = str(question.id)
        user_answer = answers.get(question_id)
        
        if user_answer and _check_answer(question, user_answer):
            earned_points += question.points
            correct_answers += 1
    
    # Calculer le pourcentage
    score = (earned_points / total_points * 100) if total_points > 0 else Decimal('0.00')
    
    # Mettre à jour la tentative
    attempt.status = 'SUBMITTED'
    attempt.answers = answers
    attempt.score = score
    attempt.total_points = total_points
    attempt.earned_points = earned_points
    attempt.total_questions = questions.count()
    attempt.correct_answers = correct_answers
    attempt.submitted_at = timezone.now()
    attempt.graded_at = timezone.now()
    attempt.status = 'GRADED'
    attempt.save()
    
    # Mettre à jour la completion du module
    module_completion = attempt.module_completion
    module_completion.attempts_count += 1
    module_completion.last_attempt_at = timezone.now()
    
    # Vérifier si le score est suffisant
    passing_score = module_completion.learning_module.passing_score
    if score >= passing_score:
        module_completion.status = 'PASSED'
        module_completion.score = score
        module_completion.completed_at = timezone.now()
    else:
        module_completion.status = 'FAILED'
    
    module_completion.save()
    
    # Mettre à jour la progression du parcours
    _update_student_progress(module_completion.student_progress)
    
    return Response({
        'attempt': QuizAttemptSerializer(attempt).data,
        'passed': score >= passing_score,
        'score': score,
        'passing_score': passing_score
    })


class StudentProgressListView(generics.ListAPIView):
    """
    Progression de l'étudiant connecté
    """
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StudentProgress.objects.filter(
            student=self.request.user
        ).select_related('learning_path').order_by('-last_activity_at')


class StudentProgressDetailView(generics.RetrieveAPIView):
    """
    Détails de progression d'un parcours
    """
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return StudentProgress.objects.filter(student=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def learning_dashboard(request):
    """
    Dashboard d'apprentissage de l'utilisateur
    """
    user = request.user
    
    # Progressions actives
    active_progress = StudentProgress.objects.filter(
        student=user,
        status='IN_PROGRESS'
    ).select_related('learning_path')
    
    # Certifications obtenues
    certifications = Certification.objects.filter(
        student=user,
        status='ACTIVE'
    ).select_related('learning_path')
    
    # Statistiques générales
    total_progress = StudentProgress.objects.filter(student=user)
    completed_paths = total_progress.filter(status='COMPLETED').count()
    
    # Modules récemment terminés
    recent_completions = ModuleCompletion.objects.filter(
        student_progress__student=user,
        status='COMPLETED'
    ).select_related('learning_module').order_by('-completed_at')[:5]
    
    # Prochains modules recommandés
    next_modules = []
    for progress in active_progress:
        next_module = progress.learning_path.modules.filter(
            is_active=True
        ).exclude(
            completions__student_progress=progress,
            completions__status='COMPLETED'
        ).order_by('order').first()
        
        if next_module:
            next_modules.append({
                'module': LearningModuleSerializer(next_module).data,
                'progress': StudentProgressSerializer(progress).data
            })
    
    dashboard_data = {
        'summary': {
            'active_paths': active_progress.count(),
            'completed_paths': completed_paths,
            'total_certifications': certifications.count(),
            'total_progress': total_progress.count(),
        },
        'active_progress': StudentProgressSerializer(active_progress, many=True).data,
        'certifications': CertificationSerializer(certifications, many=True).data,
        'recent_completions': ModuleCompletionSerializer(recent_completions, many=True).data,
        'next_modules': next_modules,
    }
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def learning_analytics(request):
    """
    Analytics d'apprentissage pour l'utilisateur
    """
    user = request.user
    
    # Période d'analyse
    days = int(request.query_params.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Activité par jour
    daily_activity = ModuleCompletion.objects.filter(
        student_progress__student=user,
        completed_at__gte=start_date,
        status='COMPLETED'
    ).extra(
        select={'day': 'DATE(completed_at)'}
    ).values('day').annotate(
        modules_completed=Count('id'),
        time_spent=Sum('time_spent')
    ).order_by('day')
    
    # Performance par difficulté
    difficulty_performance = StudentProgress.objects.filter(
        student=user,
        status='COMPLETED'
    ).values(
        'learning_path__difficulty_level'
    ).annotate(
        count=Count('id'),
        avg_score=Avg('overall_score')
    )
    
    # Temps d'apprentissage par type de parcours
    path_type_time = StudentProgress.objects.filter(
        student=user
    ).values(
        'learning_path__path_type'
    ).annotate(
        total_time=Sum('total_time_spent'),
        count=Count('id')
    )
    
    analytics_data = {
        'period_days': days,
        'daily_activity': list(daily_activity),
        'difficulty_performance': list(difficulty_performance),
        'path_type_time': list(path_type_time),
        'total_time_period': sum(
            d['time_spent'].total_seconds() if d['time_spent'] else 0 
            for d in daily_activity
        ) / 3600,  # en heures
    }
    
    return Response(analytics_data)


# Fonctions utilitaires

def _check_answer(question, user_answer):
    """
    Vérifier si une réponse est correcte
    """
    correct_answers = question.correct_answers
    
    if question.question_type == 'SINGLE_CHOICE':
        return user_answer in correct_answers
    
    elif question.question_type == 'MULTIPLE_CHOICE':
        if isinstance(user_answer, list):
            return set(user_answer) == set(correct_answers)
        return False
    
    elif question.question_type == 'TRUE_FALSE':
        return str(user_answer).lower() in [str(ans).lower() for ans in correct_answers]
    
    elif question.question_type in ['TEXT_INPUT', 'NUMERIC']:
        user_text = str(user_answer).lower().strip()
        return any(
            str(ans).lower().strip() == user_text 
            for ans in correct_answers
        )
    
    return False


def _update_student_progress(student_progress):
    """
    Mettre à jour la progression globale d'un étudiant
    """
    total_modules = student_progress.learning_path.modules.filter(is_active=True).count()
    completed_modules = student_progress.module_completions.filter(
        status='COMPLETED'
    ).count()
    
    if total_modules > 0:
        completion_percentage = (completed_modules / total_modules) * 100
        student_progress.completion_percentage = Decimal(str(completion_percentage))
        
        # Calculer le score global
        completed_completions = student_progress.module_completions.filter(
            status='COMPLETED',
            score__isnull=False
        )
        
        if completed_completions.exists():
            avg_score = completed_completions.aggregate(
                avg=Avg('score')
            )['avg']
            student_progress.overall_score = avg_score or Decimal('0.00')
        
        # Vérifier si le parcours est terminé
        if completed_modules == total_modules:
            student_progress.status = 'COMPLETED'
            student_progress.completed_at = timezone.now()
        
        student_progress.last_activity_at = timezone.now()
        student_progress.save()

"""
Serializers pour le module Learning
Sérialisation des données pour l'API REST d'e-learning et formations
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models_learning import (
    LearningPath, LearningModule, QuizExtended, QuestionExtended,
    StudentProgress, ModuleCompletion, QuizAttempt, Certification
)

User = get_user_model()


class LearningPathSerializer(serializers.ModelSerializer):
    """
    Serializer pour les parcours d'apprentissage
    """
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Statistiques
    modules_count = serializers.SerializerMethodField()
    enrolled_students = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    
    # Affichage des choix
    difficulty_level_display = serializers.CharField(
        source='get_difficulty_level_display', read_only=True
    )
    path_type_display = serializers.CharField(
        source='get_path_type_display', read_only=True
    )
    
    class Meta:
        model = LearningPath
        fields = [
            'id', 'title', 'description', 'path_type', 'difficulty_level',
            'estimated_duration', 'is_mandatory', 'is_active',
            'created_at', 'updated_at', 'created_by_name',
            'modules_count', 'enrolled_students', 'completion_rate',
            'difficulty_level_display', 'path_type_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_modules_count(self, obj):
        """Nombre de modules dans le parcours"""
        return obj.modules.count()
    
    def get_enrolled_students(self, obj):
        """Nombre d'étudiants inscrits"""
        return obj.student_progress.filter(status__in=['IN_PROGRESS', 'COMPLETED']).count()
    
    def get_completion_rate(self, obj):
        """Taux de completion du parcours"""
        total_students = obj.student_progress.count()
        if total_students == 0:
            return 0
        completed_students = obj.student_progress.filter(status='COMPLETED').count()
        return (completed_students / total_students) * 100


class LearningModuleSerializer(serializers.ModelSerializer):
    """
    Serializer pour les modules d'apprentissage
    """
    
    # Informations du parcours
    learning_path_title = serializers.CharField(
        source='learning_path.title', read_only=True
    )
    
    # Statistiques
    completions_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    
    # Affichage des choix
    module_type_display = serializers.CharField(
        source='get_module_type_display', read_only=True
    )
    
    class Meta:
        model = LearningModule
        fields = [
            'id', 'learning_path', 'title', 'description', 'module_type',
            'content_url', 'video_id', 'content_data', 'order',
            'estimated_duration', 'is_mandatory', 'passing_score', 'is_active',
            'created_at', 'updated_at', 'learning_path_title',
            'completions_count', 'average_score', 'module_type_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_completions_count(self, obj):
        """Nombre de completions du module"""
        return obj.completions.filter(status='COMPLETED').count()
    
    def get_average_score(self, obj):
        """Score moyen du module"""
        completions = obj.completions.filter(status='COMPLETED', score__isnull=False)
        if not completions.exists():
            return None
        return completions.aggregate(avg_score=serializers.models.Avg('score'))['avg_score']


class QuizExtendedSerializer(serializers.ModelSerializer):
    """
    Serializer pour les quiz étendus
    """
    
    # Informations du module
    module_title = serializers.CharField(
        source='learning_module.title', read_only=True
    )
    
    # Statistiques
    questions_count = serializers.SerializerMethodField()
    attempts_count = serializers.SerializerMethodField()
    average_score = serializers.SerializerMethodField()
    
    # Affichage des choix
    quiz_type_display = serializers.CharField(
        source='get_quiz_type_display', read_only=True
    )
    
    class Meta:
        model = QuizExtended
        fields = [
            'id', 'learning_module', 'quiz_type', 'time_limit', 'show_timer',
            'max_attempts', 'cooldown_period', 'randomize_questions',
            'randomize_answers', 'show_results_immediately', 'show_correct_answers',
            'allow_review', 'weighted_scoring', 'created_at', 'updated_at',
            'module_title', 'questions_count', 'attempts_count', 'average_score',
            'quiz_type_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_questions_count(self, obj):
        """Nombre de questions dans le quiz"""
        return obj.questions.filter(is_active=True).count()
    
    def get_attempts_count(self, obj):
        """Nombre total de tentatives"""
        return QuizAttempt.objects.filter(
            module_completion__learning_module__quiz_extended=obj
        ).count()
    
    def get_average_score(self, obj):
        """Score moyen du quiz"""
        attempts = QuizAttempt.objects.filter(
            module_completion__learning_module__quiz_extended=obj,
            status='GRADED',
            score__isnull=False
        )
        if not attempts.exists():
            return None
        return attempts.aggregate(avg_score=serializers.models.Avg('score'))['avg_score']


class QuestionExtendedSerializer(serializers.ModelSerializer):
    """
    Serializer pour les questions étendues
    """
    
    # Informations du quiz
    quiz_title = serializers.CharField(
        source='quiz.learning_module.title', read_only=True
    )
    
    # Informations du créateur
    created_by_name = serializers.CharField(
        source='created_by.full_name', read_only=True
    )
    
    # Affichage des choix
    question_type_display = serializers.CharField(
        source='get_question_type_display', read_only=True
    )
    difficulty_level_display = serializers.CharField(
        source='get_difficulty_level_display', read_only=True
    )
    
    class Meta:
        model = QuestionExtended
        fields = [
            'id', 'quiz', 'question_text', 'question_type', 'difficulty_level',
            'options', 'correct_answers', 'explanation', 'hint', 'points',
            'time_limit', 'order', 'image', 'audio', 'is_active',
            'created_at', 'updated_at', 'quiz_title', 'created_by_name',
            'question_type_display', 'difficulty_level_display'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_options(self, value):
        """Validation des options de réponse"""
        question_type = self.initial_data.get('question_type')
        
        if question_type in ['MULTIPLE_CHOICE', 'SINGLE_CHOICE'] and len(value) < 2:
            raise serializers.ValidationError(
                "Au moins 2 options sont requises pour ce type de question"
            )
        
        return value
    
    def validate_correct_answers(self, value):
        """Validation des réponses correctes"""
        question_type = self.initial_data.get('question_type')
        
        if question_type == 'SINGLE_CHOICE' and len(value) != 1:
            raise serializers.ValidationError(
                "Une seule réponse correcte est autorisée pour ce type de question"
            )
        
        return value


class StudentProgressSerializer(serializers.ModelSerializer):
    """
    Serializer pour le progrès des étudiants
    """
    
    # Informations de l'étudiant
    student_name = serializers.CharField(
        source='student.full_name', read_only=True
    )
    student_email = serializers.CharField(
        source='student.email', read_only=True
    )
    
    # Informations du parcours
    learning_path_title = serializers.CharField(
        source='learning_path.title', read_only=True
    )
    learning_path_modules = serializers.IntegerField(
        source='learning_path.modules.count', read_only=True
    )
    
    # Statistiques
    completed_modules = serializers.SerializerMethodField()
    remaining_modules = serializers.SerializerMethodField()
    estimated_completion_date = serializers.SerializerMethodField()
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'student', 'learning_path', 'status', 'completion_percentage',
            'overall_score', 'total_time_spent', 'started_at', 'completed_at',
            'last_activity_at', 'created_at', 'updated_at',
            'student_name', 'student_email', 'learning_path_title',
            'learning_path_modules', 'completed_modules', 'remaining_modules',
            'estimated_completion_date', 'status_display'
        ]
        read_only_fields = [
            'id', 'completion_percentage', 'overall_score', 'total_time_spent',
            'started_at', 'completed_at', 'last_activity_at', 'created_at', 'updated_at'
        ]
    
    def get_completed_modules(self, obj):
        """Nombre de modules terminés"""
        return obj.module_completions.filter(status='COMPLETED').count()
    
    def get_remaining_modules(self, obj):
        """Nombre de modules restants"""
        total_modules = obj.learning_path.modules.count()
        completed_modules = self.get_completed_modules(obj)
        return total_modules - completed_modules
    
    def get_estimated_completion_date(self, obj):
        """Date estimée de completion"""
        if obj.status == 'COMPLETED':
            return obj.completed_at
        
        # Calcul basé sur la progression actuelle et le temps moyen par module
        remaining = self.get_remaining_modules(obj)
        if remaining == 0:
            return None
        
        # Estimation simple basée sur le temps déjà passé
        if obj.total_time_spent.total_seconds() > 0:
            completed = self.get_completed_modules(obj)
            if completed > 0:
                avg_time_per_module = obj.total_time_spent / completed
                estimated_remaining_time = avg_time_per_module * remaining
                from datetime import timedelta
                return obj.last_activity_at + estimated_remaining_time
        
        return None


class ModuleCompletionSerializer(serializers.ModelSerializer):
    """
    Serializer pour la completion des modules
    """
    
    # Informations de l'étudiant
    student_name = serializers.CharField(
        source='student_progress.student.full_name', read_only=True
    )
    
    # Informations du module
    module_title = serializers.CharField(
        source='learning_module.title', read_only=True
    )
    module_type = serializers.CharField(
        source='learning_module.module_type', read_only=True
    )
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = ModuleCompletion
        fields = [
            'id', 'student_progress', 'learning_module', 'status', 'score',
            'attempts_count', 'time_spent', 'started_at', 'completed_at',
            'last_attempt_at', 'created_at', 'updated_at',
            'student_name', 'module_title', 'module_type', 'status_display'
        ]
        read_only_fields = [
            'id', 'attempts_count', 'time_spent', 'started_at', 'completed_at',
            'last_attempt_at', 'created_at', 'updated_at'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer pour les tentatives de quiz
    """
    
    # Informations de l'étudiant
    student_name = serializers.CharField(
        source='module_completion.student_progress.student.full_name', read_only=True
    )
    
    # Informations du module/quiz
    module_title = serializers.CharField(
        source='module_completion.learning_module.title', read_only=True
    )
    
    # Statistiques calculées
    success_rate = serializers.SerializerMethodField()
    
    # Affichage des choix
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'module_completion', 'status', 'answers', 'score',
            'total_points', 'earned_points', 'total_questions', 'correct_answers',
            'time_spent', 'started_at', 'submitted_at', 'graded_at',
            'ip_address', 'user_agent', 'student_name', 'module_title',
            'success_rate', 'status_display'
        ]
        read_only_fields = [
            'id', 'score', 'total_points', 'earned_points', 'total_questions',
            'correct_answers', 'time_spent', 'started_at', 'submitted_at',
            'graded_at', 'ip_address', 'user_agent'
        ]
    
    def get_success_rate(self, obj):
        """Taux de réussite de la tentative"""
        if obj.total_questions > 0:
            return (obj.correct_answers / obj.total_questions) * 100
        return 0


class CertificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour les certifications
    """
    
    # Informations de l'étudiant
    student_name = serializers.CharField(
        source='student.full_name', read_only=True
    )
    student_email = serializers.CharField(
        source='student.email', read_only=True
    )
    
    # Informations du parcours
    learning_path_title = serializers.CharField(
        source='learning_path.title', read_only=True
    )
    
    # Informations de l'émetteur
    issued_by_name = serializers.CharField(
        source='issued_by.full_name', read_only=True
    )
    
    # Validation
    is_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    # Affichage des choix
    certification_type_display = serializers.CharField(
        source='get_certification_type_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = Certification
        fields = [
            'id', 'student', 'learning_path', 'certificate_number',
            'certification_type', 'status', 'final_score', 'issued_at',
            'expires_at', 'issued_by', 'student_name', 'student_email',
            'learning_path_title', 'issued_by_name', 'is_valid',
            'days_until_expiry', 'certification_type_display', 'status_display'
        ]
        read_only_fields = [
            'id', 'certificate_number', 'issued_at', 'is_valid', 'days_until_expiry'
        ]
    
    def get_is_valid(self, obj):
        """Vérifie si la certification est valide"""
        return obj.is_valid()
    
    def get_days_until_expiry(self, obj):
        """Jours jusqu'à expiration"""
        if obj.expires_at:
            from datetime import date
            delta = obj.expires_at.date() - date.today()
            return max(0, delta.days)
        return None


# Serializers pour la création et mise à jour

class LearningPathCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de parcours d'apprentissage
    """
    
    class Meta:
        model = LearningPath
        fields = [
            'title', 'description', 'path_type', 'difficulty_level',
            'estimated_duration', 'is_mandatory'
        ]
    
    def validate_title(self, value):
        """Validation du titre"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Le titre doit contenir au moins 5 caractères"
            )
        return value.strip()


class LearningModuleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de modules d'apprentissage
    """
    
    class Meta:
        model = LearningModule
        fields = [
            'learning_path', 'title', 'description', 'module_type',
            'content_url', 'video_id', 'content_data', 'estimated_duration',
            'is_mandatory', 'passing_score'
        ]
    
    def validate_passing_score(self, value):
        """Validation du score minimum"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Le score doit être entre 0 et 100"
            )
        return value


class QuestionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de questions
    """
    
    class Meta:
        model = QuestionExtended
        fields = [
            'quiz', 'question_text', 'question_type', 'difficulty_level',
            'options', 'correct_answers', 'explanation', 'hint', 'points',
            'time_limit', 'order', 'image', 'audio'
        ]
    
    def validate(self, data):
        """Validation croisée des données"""
        question_type = data.get('question_type')
        options = data.get('options', [])
        correct_answers = data.get('correct_answers', [])
        
        # Validation des options pour les questions à choix multiples
        if question_type in ['MULTIPLE_CHOICE', 'SINGLE_CHOICE']:
            if len(options) < 2:
                raise serializers.ValidationError(
                    "Au moins 2 options sont requises"
                )
            
            # Vérifier que les réponses correctes sont dans les options
            for answer in correct_answers:
                if answer not in options:
                    raise serializers.ValidationError(
                        f"La réponse '{answer}' n'est pas dans les options"
                    )
        
        # Validation pour les questions vrai/faux
        if question_type == 'TRUE_FALSE':
            if len(correct_answers) != 1 or correct_answers[0] not in ['true', 'false']:
                raise serializers.ValidationError(
                    "Une réponse 'true' ou 'false' est requise"
                )
        
        return data


class StudentEnrollmentSerializer(serializers.Serializer):
    """
    Serializer pour l'inscription d'étudiants
    """
    
    learning_path_id = serializers.UUIDField()
    personal_target = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True
    )
    
    def validate_learning_path_id(self, value):
        """Validation de l'existence du parcours"""
        try:
            LearningPath.objects.get(id=value, is_active=True)
        except LearningPath.DoesNotExist:
            raise serializers.ValidationError("Parcours d'apprentissage introuvable")
        return value

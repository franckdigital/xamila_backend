"""
Modèles spécialisés pour l'e-learning et la formation
Quiz avancés, parcours d'apprentissage, certifications
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
from datetime import timedelta

User = get_user_model()


class LearningPath(models.Model):
    """
    Parcours d'apprentissage structurés
    """
    
    DIFFICULTY_LEVELS = [
        ('BEGINNER', 'Débutant'),
        ('INTERMEDIATE', 'Intermédiaire'),
        ('ADVANCED', 'Avancé'),
        ('EXPERT', 'Expert'),
    ]
    
    PATH_TYPES = [
        ('FINANCIAL_BASICS', 'Bases financières'),
        ('INVESTMENT_STRATEGY', 'Stratégies d\'investissement'),
        ('RISK_MANAGEMENT', 'Gestion des risques'),
        ('PORTFOLIO_MANAGEMENT', 'Gestion de portefeuille'),
        ('REGULATORY_COMPLIANCE', 'Conformité réglementaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre du parcours")
    description = models.TextField(verbose_name="Description")
    path_type = models.CharField(
        max_length=30, choices=PATH_TYPES,
        verbose_name="Type de parcours"
    )
    difficulty_level = models.CharField(
        max_length=20, choices=DIFFICULTY_LEVELS,
        verbose_name="Niveau de difficulté"
    )
    
    # Configuration
    estimated_duration = models.DurationField(
        verbose_name="Durée estimée",
        help_text="Temps estimé pour compléter le parcours"
    )
    is_mandatory = models.BooleanField(
        default=False, verbose_name="Parcours obligatoire"
    )
    is_active = models.BooleanField(default=True, verbose_name="Parcours actif")
    
    # Prérequis
    prerequisites = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        related_name='unlocks',
        verbose_name="Prérequis"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_learning_paths'
    )
    
    class Meta:
        verbose_name = "Parcours d'apprentissage"
        verbose_name_plural = "Parcours d'apprentissage"
        ordering = ['difficulty_level', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_level_display()})"


class LearningModule(models.Model):
    """
    Modules d'apprentissage dans un parcours
    """
    
    MODULE_TYPES = [
        ('VIDEO', 'Vidéo'),
        ('QUIZ', 'Quiz'),
        ('READING', 'Lecture'),
        ('INTERACTIVE', 'Interactif'),
        ('ASSIGNMENT', 'Devoir'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE,
        related_name='modules'
    )
    
    # Informations du module
    title = models.CharField(max_length=200, verbose_name="Titre du module")
    description = models.TextField(verbose_name="Description")
    module_type = models.CharField(
        max_length=20, choices=MODULE_TYPES,
        verbose_name="Type de module"
    )
    
    # Contenu
    content_url = models.URLField(
        blank=True, null=True,
        verbose_name="URL du contenu"
    )
    video_id = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name="ID de la vidéo"
    )
    content_data = models.JSONField(
        default=dict, blank=True,
        verbose_name="Données du contenu"
    )
    
    # Configuration
    order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre dans le parcours"
    )
    estimated_duration = models.DurationField(
        blank=True, null=True,
        verbose_name="Durée estimée"
    )
    is_mandatory = models.BooleanField(
        default=True, verbose_name="Module obligatoire"
    )
    passing_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('70.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score minimum requis (%)"
    )
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Module actif")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Module d'apprentissage"
        verbose_name_plural = "Modules d'apprentissage"
        ordering = ['learning_path', 'order']
        unique_together = ['learning_path', 'order']
    
    def __str__(self):
        return f"{self.learning_path.title} - {self.title}"


class QuizExtended(models.Model):
    """
    Extension du modèle Quiz avec fonctionnalités avancées
    """
    
    QUIZ_TYPES = [
        ('ASSESSMENT', 'Évaluation'),
        ('PRACTICE', 'Entraînement'),
        ('CERTIFICATION', 'Certification'),
        ('DIAGNOSTIC', 'Diagnostic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learning_module = models.OneToOneField(
        LearningModule, on_delete=models.CASCADE,
        related_name='quiz_extended'
    )
    
    # Configuration avancée
    quiz_type = models.CharField(
        max_length=20, choices=QUIZ_TYPES,
        default='ASSESSMENT', verbose_name="Type de quiz"
    )
    
    # Paramètres de temps
    time_limit = models.DurationField(
        blank=True, null=True,
        verbose_name="Limite de temps"
    )
    show_timer = models.BooleanField(
        default=True, verbose_name="Afficher le chronomètre"
    )
    
    # Paramètres de tentatives
    max_attempts = models.PositiveIntegerField(
        default=3, verbose_name="Nombre maximum de tentatives"
    )
    cooldown_period = models.DurationField(
        default=timedelta(hours=24),
        verbose_name="Période d'attente entre tentatives"
    )
    
    # Paramètres d'affichage
    randomize_questions = models.BooleanField(
        default=True, verbose_name="Mélanger les questions"
    )
    randomize_answers = models.BooleanField(
        default=True, verbose_name="Mélanger les réponses"
    )
    show_results_immediately = models.BooleanField(
        default=False, verbose_name="Afficher les résultats immédiatement"
    )
    show_correct_answers = models.BooleanField(
        default=True, verbose_name="Afficher les bonnes réponses"
    )
    
    # Paramètres de notation
    allow_review = models.BooleanField(
        default=True, verbose_name="Permettre la révision"
    )
    weighted_scoring = models.BooleanField(
        default=False, verbose_name="Notation pondérée"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Quiz étendu"
        verbose_name_plural = "Quiz étendus"
    
    def __str__(self):
        return f"Quiz - {self.learning_module.title}"


class QuestionExtended(models.Model):
    """
    Extension des questions avec fonctionnalités avancées
    """
    
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Choix multiple'),
        ('SINGLE_CHOICE', 'Choix unique'),
        ('TRUE_FALSE', 'Vrai/Faux'),
        ('TEXT_INPUT', 'Saisie de texte'),
        ('NUMERIC', 'Numérique'),
        ('MATCHING', 'Appariement'),
        ('ORDERING', 'Classement'),
        ('FILL_BLANKS', 'Texte à trous'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('EASY', 'Facile'),
        ('MEDIUM', 'Moyen'),
        ('HARD', 'Difficile'),
        ('EXPERT', 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        QuizExtended, on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Contenu de la question
    question_text = models.TextField(verbose_name="Texte de la question")
    question_type = models.CharField(
        max_length=20, choices=QUESTION_TYPES,
        verbose_name="Type de question"
    )
    difficulty_level = models.CharField(
        max_length=10, choices=DIFFICULTY_LEVELS,
        default='MEDIUM', verbose_name="Niveau de difficulté"
    )
    
    # Options et réponses
    options = models.JSONField(
        default=list, verbose_name="Options de réponse"
    )
    correct_answers = models.JSONField(
        verbose_name="Réponses correctes"
    )
    
    # Explications et feedback
    explanation = models.TextField(
        blank=True, verbose_name="Explication"
    )
    hint = models.TextField(
        blank=True, verbose_name="Indice"
    )
    
    # Configuration
    points = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name="Points"
    )
    time_limit = models.DurationField(
        blank=True, null=True,
        verbose_name="Limite de temps pour cette question"
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name="Ordre"
    )
    
    # Médias associés
    image = models.ImageField(
        upload_to='quiz_images/', blank=True, null=True,
        verbose_name="Image"
    )
    audio = models.FileField(
        upload_to='quiz_audio/', blank=True, null=True,
        verbose_name="Audio"
    )
    
    # Statut
    is_active = models.BooleanField(default=True, verbose_name="Question active")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='created_questions_extended'
    )
    
    class Meta:
        verbose_name = "Question étendue"
        verbose_name_plural = "Questions étendues"
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.learning_module.title} - Q{self.order}"


class StudentProgress(models.Model):
    """
    Suivi du progrès des étudiants
    """
    
    PROGRESS_STATUS = [
        ('NOT_STARTED', 'Non commencé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('PASSED', 'Réussi'),
        ('FAILED', 'Échoué'),
        ('EXPIRED', 'Expiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='learning_progress'
    )
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE,
        related_name='student_progress'
    )
    
    # Statut et progression
    status = models.CharField(
        max_length=20, choices=PROGRESS_STATUS,
        default='NOT_STARTED', verbose_name="Statut"
    )
    completion_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Pourcentage de completion (%)"
    )
    
    # Scores et résultats
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score global (%)"
    )
    
    # Temps passé
    total_time_spent = models.DurationField(
        default=timedelta(0),
        verbose_name="Temps total passé"
    )
    
    # Dates importantes
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Progrès étudiant"
        verbose_name_plural = "Progrès étudiants"
        ordering = ['-last_activity_at']
        unique_together = ['student', 'learning_path']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.learning_path.title} ({self.completion_percentage}%)"


class ModuleCompletion(models.Model):
    """
    Completion des modules individuels
    """
    
    COMPLETION_STATUS = [
        ('NOT_STARTED', 'Non commencé'),
        ('IN_PROGRESS', 'En cours'),
        ('COMPLETED', 'Terminé'),
        ('PASSED', 'Réussi'),
        ('FAILED', 'Échoué'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_progress = models.ForeignKey(
        StudentProgress, on_delete=models.CASCADE,
        related_name='module_completions'
    )
    learning_module = models.ForeignKey(
        LearningModule, on_delete=models.CASCADE,
        related_name='completions'
    )
    
    # Statut et résultats
    status = models.CharField(
        max_length=20, choices=COMPLETION_STATUS,
        default='NOT_STARTED', verbose_name="Statut"
    )
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score (%)"
    )
    
    # Tentatives
    attempts_count = models.PositiveIntegerField(
        default=0, verbose_name="Nombre de tentatives"
    )
    
    # Temps
    time_spent = models.DurationField(
        default=timedelta(0),
        verbose_name="Temps passé"
    )
    
    # Dates
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Completion de module"
        verbose_name_plural = "Completions de modules"
        ordering = ['student_progress', 'learning_module__order']
        unique_together = ['student_progress', 'learning_module']
    
    def __str__(self):
        return f"{self.student_progress.student.full_name} - {self.learning_module.title}"


class QuizAttempt(models.Model):
    """
    Tentatives de quiz avec détails complets
    """
    
    ATTEMPT_STATUS = [
        ('STARTED', 'Commencé'),
        ('IN_PROGRESS', 'En cours'),
        ('SUBMITTED', 'Soumis'),
        ('GRADED', 'Noté'),
        ('ABANDONED', 'Abandonné'),
        ('EXPIRED', 'Expiré'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_completion = models.ForeignKey(
        ModuleCompletion, on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    
    # Statut de la tentative
    status = models.CharField(
        max_length=20, choices=ATTEMPT_STATUS,
        default='STARTED', verbose_name="Statut"
    )
    
    # Réponses et résultats
    answers = models.JSONField(
        default=dict, verbose_name="Réponses"
    )
    score = models.DecimalField(
        max_digits=5, decimal_places=2,
        blank=True, null=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score (%)"
    )
    total_points = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Points totaux"
    )
    earned_points = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Points obtenus"
    )
    
    # Statistiques
    total_questions = models.PositiveIntegerField(
        default=0, verbose_name="Nombre total de questions"
    )
    correct_answers = models.PositiveIntegerField(
        default=0, verbose_name="Réponses correctes"
    )
    
    # Temps
    time_spent = models.DurationField(
        blank=True, null=True,
        verbose_name="Temps passé"
    )
    
    # Dates
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    graded_at = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Tentative de quiz"
        verbose_name_plural = "Tentatives de quiz"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Tentative {self.id} - {self.status} - {self.score}%"


class Certification(models.Model):
    """
    Certifications obtenues par les étudiants
    """
    
    CERTIFICATION_TYPES = [
        ('COMPLETION', 'Certificat de completion'),
        ('ACHIEVEMENT', 'Certificat de réussite'),
        ('MASTERY', 'Certificat de maîtrise'),
        ('PROFESSIONAL', 'Certification professionnelle'),
    ]
    
    CERTIFICATION_STATUS = [
        ('ACTIVE', 'Actif'),
        ('EXPIRED', 'Expiré'),
        ('REVOKED', 'Révoqué'),
        ('SUSPENDED', 'Suspendu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='certifications'
    )
    learning_path = models.ForeignKey(
        LearningPath, on_delete=models.CASCADE,
        related_name='certifications'
    )
    
    # Informations du certificat
    certificate_number = models.CharField(
        max_length=50, unique=True,
        verbose_name="Numéro de certificat"
    )
    certification_type = models.CharField(
        max_length=20, choices=CERTIFICATION_TYPES,
        verbose_name="Type de certification"
    )
    
    # Statut et validité
    status = models.CharField(
        max_length=20, choices=CERTIFICATION_STATUS,
        default='ACTIVE', verbose_name="Statut"
    )
    
    # Scores et résultats
    final_score = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score final (%)"
    )
    
    # Dates
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        blank=True, null=True,
        verbose_name="Date d'expiration"
    )
    
    # Métadonnées
    issued_by = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='issued_certifications'
    )
    
    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ['-issued_at']
        unique_together = ['student', 'learning_path']
    
    def __str__(self):
        return f"{self.certificate_number} - {self.student.full_name}"
    
    def is_valid(self):
        """Vérifie si la certification est encore valide"""
        if self.status != 'ACTIVE':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

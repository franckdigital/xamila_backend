"""
Modèles Django consolidés pour la plateforme XAMILA
Architecture modulaire avec imports centralisés
"""

# Import all models from specialized modules
from .models_core import *
from .models_sgi import *
from .models_sgi_manager import *
from .models_learning import *
from .models_trading import *
from .models_notifications import *

# Ensure all models are available for Django
__all__ = [
    # Core models
    'User', 'UserProfile', 'KYC', 'RefreshToken', 'OTP', 'AuditLog',
    
    # SGI models
    'SGI', 'SGIProfile', 'SGIService', 'SGIDocument', 'SGIRating',
    'ClientSGIInteraction', 'SGIContract', 'ContractTemplate',
    'ContractClause', 'ContractSignature', 'ContractAmendment',
    
    # SGI Manager models
    'SGIManager', 'SGIManagerProfile', 'SGIManagerPermission',
    'SGIClientAssignment', 'SGIPerformanceMetric', 'SGICommission',
    'SGILeadManagement', 'SGIReporting', 'SGIAnalytics',
    
    # Learning models
    'LearningPath', 'LearningModule', 'QuizExtended', 'QuestionExtended',
    'StudentProgress', 'ModuleCompletion', 'QuizAttempt', 'Certification',
    
    # Trading models
    'StockExtended', 'Portfolio', 'Holding', 'TradingOrder', 'Transaction',
    'PriceHistory', 'TradingCompetition', 'CompetitionParticipant',
    
    # Notification models
    'NotificationTemplate', 'NotificationCampaign', 'Notification',
    'NotificationPreference', 'NotificationLog', 'WebhookEndpoint',
    'NotificationQueue',
]

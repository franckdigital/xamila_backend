# ================================
# DJANGO REST FRAMEWORK CONFIGURATION
# Configuration complète pour l'API Xamila Backend
# ================================

from datetime import timedelta

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key-here',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# API Documentation with drf-spectacular
SPECTACULAR_SETTINGS = {
    'TITLE': 'Xamila Backend API',
    'DESCRIPTION': 'API pour la plateforme fintech unifiée avec système de matching SGI intelligent',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'ENUM_NAME_OVERRIDES': {
        'ValidationErrorEnum': 'drf_spectacular.types.ErrorResponse',
    },
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums'
    ],
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': 'https://api.xamila.com', 'description': 'Production server'},
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'Endpoints d\'authentification'},
        {'name': 'Users', 'description': 'Gestion des utilisateurs'},
        {'name': 'SGI Matching', 'description': 'Système de matching SGI intelligent'},
        {'name': 'Transactions', 'description': 'Gestion des transactions financières'},
        {'name': 'KYC', 'description': 'Vérification d\'identité'},
        {'name': 'Notifications', 'description': 'Système de notifications'},
    ]
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development
    "http://127.0.0.1:3000",
    "http://localhost:19006", # Expo development
    "http://127.0.0.1:19006",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Database Configuration for Production
DATABASES_PRODUCTION = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'xamila_backend',
        'USER': 'xamila_user',
        'PASSWORD': 'your_password_here',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'charset': 'utf8',
        },
    }
}

# Redis Configuration
REDIS_URL = 'redis://localhost:6379/0'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Xamila Platform <noreply@xamila.com>'

# Xamila Specific Settings
XAMILA_CONTACT_EMAIL = 'contact@xamila.com'
XAMILA_ADMIN_EMAIL = 'admin@xamila.com'
XAMILA_SUPPORT_EMAIL = 'support@xamila.com'
PLATFORM_URL = 'https://app.xamila.com'

# Mobile Money Configuration
MOBILE_MONEY_PROVIDERS = {
    'MTN': {
        'api_url': 'https://api.mtn.com/v1/',
        'api_key': 'your-mtn-api-key',
        'secret_key': 'your-mtn-secret-key',
    },
    'ORANGE': {
        'api_url': 'https://api.orange.com/v1/',
        'api_key': 'your-orange-api-key',
        'secret_key': 'your-orange-secret-key',
    },
    'WAVE': {
        'api_url': 'https://api.wave.com/v1/',
        'api_key': 'your-wave-api-key',
        'secret_key': 'your-wave-secret-key',
    }
}

# ADEC API Configuration
ADEC_API_CONFIG = {
    'base_url': 'https://api.adec.sn/v1/',
    'api_key': 'your-adec-api-key',
    'secret_key': 'your-adec-secret-key',
    'timeout': 30,
}

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'xamila_backend.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'xamila': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

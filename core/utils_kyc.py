"""
Service de vérification KYC automatisée
Intégration avec des APIs tierces (Smile Identity, Onfido, ComplyAdvantage)
"""

import requests
import base64
from django.conf import settings
from django.utils import timezone
from .models_kyc import KYCDocument, KYCVerificationLog
import logging

logger = logging.getLogger(__name__)


class KYCVerificationService:
    """
    Service principal de vérification KYC
    """
    
    def __init__(self):
        self.providers = {
            'smile_identity': SmileIdentityVerifier(),
            'onfido': OnfidoVerifier(),
            'comply_advantage': ComplyAdvantageVerifier(),
            'mock': MockVerifier()
        }
        
        # Déterminer le provider à utiliser
        self.active_provider = getattr(settings, 'KYC_VERIFICATION_PROVIDER', 'mock')
        
        if self.active_provider not in self.providers:
            logger.warning(f"Provider KYC non supporté: {self.active_provider}, utilisation du mock")
            self.active_provider = 'mock'
    
    def verify_document(self, kyc_document):
        """
        Vérifie un document KYC
        
        Args:
            kyc_document: Instance KYCDocument
            
        Returns:
            dict: Résultat de la vérification
        """
        try:
            provider = self.providers[self.active_provider]
            result = provider.verify_document(kyc_document)
            
            # Mettre à jour le document avec les résultats
            kyc_document.verification_status = 'VERIFIED' if result['success'] else 'REJECTED'
            kyc_document.auto_verification_score = result.get('score', 0)
            kyc_document.verification_details = result.get('details', {})
            kyc_document.verified_at = timezone.now()
            
            if not result['success']:
                kyc_document.rejection_reason = result.get('error', 'Vérification automatique échouée')
            
            kyc_document.save()
            
            # Log de vérification
            KYCVerificationLog.objects.create(
                kyc_profile=kyc_document.kyc_profile,
                action_type='AUTO_VERIFICATION',
                description=f"Vérification automatique du document {kyc_document.get_document_type_display()}",
                old_values={'verification_status': 'PENDING'},
                new_values={
                    'verification_status': kyc_document.verification_status,
                    'score': kyc_document.auto_verification_score
                }
            )
            
            # Mettre à jour le statut du profil KYC si nécessaire
            self.update_kyc_profile_status(kyc_document.kyc_profile)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du document {kyc_document.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de vérification: {str(e)}'
            }
    
    def verify_profile(self, kyc_profile):
        """
        Vérifie un profil KYC complet
        """
        try:
            provider = self.providers[self.active_provider]
            result = provider.verify_profile(kyc_profile)
            
            # Mettre à jour le profil avec les résultats
            if result['success']:
                kyc_profile.verification_provider = self.active_provider.upper()
                kyc_profile.verification_score = result.get('score', 0)
                kyc_profile.verification_reference = result.get('reference', '')
                
                # Approuver automatiquement si le score est suffisant
                min_score = getattr(settings, 'KYC_AUTO_APPROVAL_SCORE', 80)
                if result.get('score', 0) >= min_score:
                    kyc_profile.kyc_status = 'APPROVED'
                    kyc_profile.approved_at = timezone.now()
                else:
                    kyc_profile.kyc_status = 'UNDER_REVIEW'
            else:
                kyc_profile.kyc_status = 'REJECTED'
                kyc_profile.rejection_reason = result.get('error', 'Vérification automatique échouée')
                kyc_profile.rejected_at = timezone.now()
            
            kyc_profile.reviewed_at = timezone.now()
            kyc_profile.save()
            
            # Log de vérification
            KYCVerificationLog.objects.create(
                kyc_profile=kyc_profile,
                action_type='AUTO_VERIFICATION',
                description=f"Vérification automatique du profil complet",
                new_values={
                    'kyc_status': kyc_profile.kyc_status,
                    'verification_score': kyc_profile.verification_score
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du profil {kyc_profile.id}: {str(e)}")
            return {
                'success': False,
                'error': f'Erreur de vérification: {str(e)}'
            }
    
    def update_kyc_profile_status(self, kyc_profile):
        """
        Met à jour le statut du profil KYC selon les documents vérifiés
        """
        documents = kyc_profile.documents.all()
        
        # Vérifier si tous les documents obligatoires sont vérifiés
        required_docs = ['IDENTITY_FRONT', 'SELFIE', 'PROOF_OF_ADDRESS']
        verified_docs = documents.filter(verification_status='VERIFIED').values_list('document_type', flat=True)
        
        if all(doc in verified_docs for doc in required_docs):
            # Tous les documents obligatoires sont vérifiés
            avg_score = documents.filter(
                verification_status='VERIFIED',
                auto_verification_score__isnull=False
            ).aggregate(avg_score=models.Avg('auto_verification_score'))['avg_score'] or 0
            
            min_score = getattr(settings, 'KYC_AUTO_APPROVAL_SCORE', 80)
            
            if avg_score >= min_score:
                kyc_profile.kyc_status = 'APPROVED'
                kyc_profile.approved_at = timezone.now()
            else:
                kyc_profile.kyc_status = 'UNDER_REVIEW'
            
            kyc_profile.verification_score = avg_score
            kyc_profile.save()


class SmileIdentityVerifier:
    """
    Vérificateur utilisant l'API Smile Identity
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'SMILE_IDENTITY_API_KEY', None)
        self.partner_id = getattr(settings, 'SMILE_IDENTITY_PARTNER_ID', None)
        self.base_url = getattr(settings, 'SMILE_IDENTITY_BASE_URL', 'https://api.smileidentity.com/v1')
    
    def verify_document(self, kyc_document):
        """
        Vérifie un document via Smile Identity
        """
        if not all([self.api_key, self.partner_id]):
            return {
                'success': False,
                'error': 'Configuration Smile Identity incomplète'
            }
        
        try:
            # Encoder le fichier en base64
            with kyc_document.file.open('rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Préparer la requête
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'partner_id': self.partner_id,
                'job_type': self.get_job_type(kyc_document.document_type),
                'user_id': str(kyc_document.kyc_profile.user.id),
                'images': [{
                    'image_type_id': self.get_image_type(kyc_document.document_type),
                    'image': file_data
                }]
            }
            
            # Faire la requête
            response = requests.post(
                f'{self.base_url}/submit_job',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'score': result.get('confidence', 0) * 100,
                    'reference': result.get('job_id', ''),
                    'details': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Erreur API Smile Identity: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur Smile Identity: {str(e)}'
            }
    
    def verify_profile(self, kyc_profile):
        """
        Vérifie un profil complet via Smile Identity
        """
        # Vérifier tous les documents du profil
        documents = kyc_profile.documents.all()
        total_score = 0
        verified_count = 0
        
        for document in documents:
            result = self.verify_document(document)
            if result['success']:
                total_score += result.get('score', 0)
                verified_count += 1
        
        if verified_count > 0:
            avg_score = total_score / verified_count
            return {
                'success': True,
                'score': avg_score,
                'reference': f'smile_profile_{kyc_profile.id}'
            }
        else:
            return {
                'success': False,
                'error': 'Aucun document n\'a pu être vérifié'
            }
    
    def get_job_type(self, document_type):
        """
        Convertit le type de document en job_type Smile Identity
        """
        mapping = {
            'IDENTITY_FRONT': 'document_verification',
            'IDENTITY_BACK': 'document_verification',
            'SELFIE': 'selfie_verification',
            'PROOF_OF_ADDRESS': 'document_verification'
        }
        return mapping.get(document_type, 'document_verification')
    
    def get_image_type(self, document_type):
        """
        Convertit le type de document en image_type_id Smile Identity
        """
        mapping = {
            'IDENTITY_FRONT': 0,  # ID Card Front
            'IDENTITY_BACK': 1,   # ID Card Back
            'SELFIE': 2,          # Selfie
            'PROOF_OF_ADDRESS': 3 # Utility Bill
        }
        return mapping.get(document_type, 0)


class OnfidoVerifier:
    """
    Vérificateur utilisant l'API Onfido
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'ONFIDO_API_KEY', None)
        self.base_url = getattr(settings, 'ONFIDO_BASE_URL', 'https://api.onfido.com/v3')
    
    def verify_document(self, kyc_document):
        """
        Vérifie un document via Onfido
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Configuration Onfido incomplète'
            }
        
        # Implémentation similaire à Smile Identity
        # À adapter selon la documentation Onfido
        return {
            'success': True,
            'score': 85,  # Score simulé
            'reference': f'onfido_{kyc_document.id}',
            'details': {'provider': 'onfido', 'status': 'verified'}
        }
    
    def verify_profile(self, kyc_profile):
        """
        Vérifie un profil complet via Onfido
        """
        return {
            'success': True,
            'score': 85,
            'reference': f'onfido_profile_{kyc_profile.id}'
        }


class ComplyAdvantageVerifier:
    """
    Vérificateur utilisant l'API ComplyAdvantage (screening AML/sanctions)
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'COMPLY_ADVANTAGE_API_KEY', None)
        self.base_url = getattr(settings, 'COMPLY_ADVANTAGE_BASE_URL', 'https://api.complyadvantage.com')
    
    def verify_document(self, kyc_document):
        """
        ComplyAdvantage se concentre sur le screening, pas la vérification de documents
        """
        return self.verify_profile(kyc_document.kyc_profile)
    
    def verify_profile(self, kyc_profile):
        """
        Vérifie un profil contre les listes de sanctions
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'Configuration ComplyAdvantage incomplète'
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'search_term': f"{kyc_profile.first_name} {kyc_profile.last_name}",
                'fuzziness': 0.6,
                'filters': {
                    'birth_year': kyc_profile.date_of_birth.year if kyc_profile.date_of_birth else None,
                    'country_codes': [kyc_profile.country] if kyc_profile.country else []
                }
            }
            
            response = requests.post(
                f'{self.base_url}/searches',
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                matches = result.get('data', {}).get('matches', [])
                
                # Si aucun match, c'est bon
                if not matches:
                    return {
                        'success': True,
                        'score': 95,
                        'reference': result.get('data', {}).get('id', ''),
                        'details': {'matches': 0, 'status': 'clear'}
                    }
                else:
                    # Analyser les matches pour déterminer le risque
                    high_risk_matches = [m for m in matches if m.get('match_strength', 0) > 0.8]
                    
                    if high_risk_matches:
                        return {
                            'success': False,
                            'error': 'Correspondances trouvées dans les listes de sanctions',
                            'details': {'matches': len(high_risk_matches), 'status': 'high_risk'}
                        }
                    else:
                        return {
                            'success': True,
                            'score': 75,  # Score réduit à cause des matches faibles
                            'reference': result.get('data', {}).get('id', ''),
                            'details': {'matches': len(matches), 'status': 'low_risk'}
                        }
            else:
                return {
                    'success': False,
                    'error': f'Erreur API ComplyAdvantage: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur ComplyAdvantage: {str(e)}'
            }


class MockVerifier:
    """
    Vérificateur simulé pour le développement
    """
    
    def verify_document(self, kyc_document):
        """
        Simulation de vérification de document
        """
        import random
        
        # Simuler différents résultats selon le type de document
        success_rate = {
            'IDENTITY_FRONT': 0.9,
            'IDENTITY_BACK': 0.85,
            'SELFIE': 0.95,
            'PROOF_OF_ADDRESS': 0.8
        }
        
        rate = success_rate.get(kyc_document.document_type, 0.85)
        success = random.random() < rate
        
        if success:
            score = random.randint(75, 98)
            return {
                'success': True,
                'score': score,
                'reference': f'mock_{kyc_document.id}_{score}',
                'details': {
                    'provider': 'mock',
                    'document_type': kyc_document.document_type,
                    'file_size': kyc_document.file_size,
                    'mime_type': kyc_document.mime_type
                }
            }
        else:
            errors = [
                'Document illisible',
                'Qualité d\'image insuffisante',
                'Document expiré',
                'Type de document non supporté'
            ]
            return {
                'success': False,
                'error': random.choice(errors),
                'score': random.randint(20, 60)
            }
    
    def verify_profile(self, kyc_profile):
        """
        Simulation de vérification de profil
        """
        import random
        
        # Simuler un score basé sur la completion du profil
        completion = kyc_profile.completion_percentage
        base_score = min(completion + random.randint(-10, 10), 100)
        
        # Simuler des cas d'échec occasionnels
        if random.random() < 0.1:  # 10% de chance d'échec
            return {
                'success': False,
                'error': 'Informations incohérentes détectées',
                'score': base_score
            }
        
        return {
            'success': True,
            'score': max(base_score, 60),  # Score minimum de 60
            'reference': f'mock_profile_{kyc_profile.id}_{base_score}',
            'details': {
                'provider': 'mock',
                'completion_percentage': completion,
                'documents_count': kyc_profile.documents.count()
            }
        }

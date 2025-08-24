from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
import logging
from typing import List, Dict, Any

from .models import (
    SGI, ClientInvestmentProfile, SGIMatchingRequest,
    ClientSGIInteraction, EmailNotification
)

logger = logging.getLogger(__name__)


class SGIMatchingService:
    """
    Service pour le matching intelligent entre clients et SGI
    """
    
    def __init__(self):
        self.minimum_score_threshold = 50
    
    def find_matching_sgis(self, client_profile: ClientInvestmentProfile) -> List[Dict[str, Any]]:
        """
        Trouve les SGI compatibles avec le profil client
        
        Args:
            client_profile: Profil d'investissement du client
            
        Returns:
            Liste des SGI avec leurs scores de compatibilité
        """
        try:
            # Récupérer toutes les SGI actives
            sgis = SGI.objects.filter(is_active=True)
            
            results = []
            
            for sgi in sgis:
                # Calculer le score de compatibilité
                score = sgi.calculate_matching_score(client_profile)
                
                # Préparer les données de la SGI
                sgi_data = {
                    'sgi_id': str(sgi.id),
                    'sgi_name': sgi.name,
                    'sgi_description': sgi.description,
                    'manager_name': sgi.manager_name,
                    'manager_email': sgi.manager_email,
                    'matching_score': score,
                    'min_investment_amount': float(sgi.min_investment_amount),
                    'max_investment_amount': float(sgi.max_investment_amount) if sgi.max_investment_amount else None,
                    'historical_performance': float(sgi.historical_performance),
                    'management_fees': float(sgi.management_fees),
                    'entry_fees': float(sgi.entry_fees),
                    'logo': sgi.logo.url if sgi.logo else None,
                    'website': sgi.website,
                    'is_verified': sgi.is_verified,
                    'total_clients': sgi.total_clients,
                    'total_assets_under_management': float(sgi.total_assets_under_management)
                }
                
                results.append(sgi_data)
            
            # Trier par score décroissant
            results.sort(key=lambda x: x['matching_score'], reverse=True)
            
            logger.info(f"Matching terminé pour {client_profile.full_name}: {len(results)} SGI évaluées")
            
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors du matching SGI: {str(e)}")
            raise
    
    def get_matching_explanation(self, sgi: SGI, client_profile: ClientInvestmentProfile) -> Dict[str, Any]:
        """
        Génère une explication détaillée du score de matching
        
        Args:
            sgi: SGI évaluée
            client_profile: Profil client
            
        Returns:
            Dictionnaire avec les détails du scoring
        """
        explanation = {
            'total_score': 0,
            'criteria_breakdown': [],
            'recommendations': []
        }
        
        # Objectif d'investissement (30 points)
        # TODO: Réactiver après ajout du champ supported_objectives
        # objective_match = client_profile.investment_objective in sgi.supported_objectives
        objective_score = 20  # Score par défaut temporaire
        explanation['total_score'] += objective_score
        explanation['criteria_breakdown'].append({
            'criterion': 'Objectif d\'investissement',
            'client_value': client_profile.get_investment_objective_display(),
            'sgi_supports': objective_match,
            'score': objective_score,
            'max_score': 30
        })
        
        # Tolérance au risque (25 points)
        risk_match = client_profile.risk_tolerance in sgi.supported_risk_levels
        risk_score = 25 if risk_match else 0
        explanation['total_score'] += risk_score
        explanation['criteria_breakdown'].append({
            'criterion': 'Tolérance au risque',
            'client_value': client_profile.get_risk_tolerance_display(),
            'sgi_supports': risk_match,
            'score': risk_score,
            'max_score': 25
        })
        
        # Horizon d'investissement (20 points)
        horizon_match = client_profile.investment_horizon in sgi.supported_horizons
        horizon_score = 20 if horizon_match else 0
        explanation['total_score'] += horizon_score
        explanation['criteria_breakdown'].append({
            'criterion': 'Horizon d\'investissement',
            'client_value': client_profile.get_investment_horizon_display(),
            'sgi_supports': horizon_match,
            'score': horizon_score,
            'max_score': 20
        })
        
        # Montant d'investissement (15 points)
        amount_compatible = (
            client_profile.investment_amount >= sgi.min_investment_amount and
            (sgi.max_investment_amount is None or 
             client_profile.investment_amount <= sgi.max_investment_amount)
        )
        amount_score = 15 if amount_compatible else 0
        explanation['total_score'] += amount_score
        explanation['criteria_breakdown'].append({
            'criterion': 'Montant d\'investissement',
            'client_value': f"{client_profile.investment_amount:,.0f} FCFA",
            'sgi_supports': amount_compatible,
            'score': amount_score,
            'max_score': 15
        })
        
        # Performance historique (10 points)
        performance_score = 10 if sgi.historical_performance >= 5 else (5 if sgi.historical_performance >= 0 else 0)
        explanation['total_score'] += performance_score
        explanation['criteria_breakdown'].append({
            'criterion': 'Performance historique',
            'client_value': 'Recherche de performance',
            'sgi_supports': sgi.historical_performance >= 0,
            'score': performance_score,
            'max_score': 10,
            'sgi_performance': f"{sgi.historical_performance}%"
        })
        
        # Générer des recommandations
        if explanation['total_score'] >= 80:
            explanation['recommendations'].append("Excellente compatibilité - Fortement recommandé")
        elif explanation['total_score'] >= 60:
            explanation['recommendations'].append("Bonne compatibilité - Recommandé")
        elif explanation['total_score'] >= 40:
            explanation['recommendations'].append("Compatibilité modérée - À considérer")
        else:
            explanation['recommendations'].append("Faible compatibilité - Autres options recommandées")
        
        return explanation


class EmailNotificationService:
    """
    Service pour l'envoi des notifications email
    """
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@xamila.com')
        self.xamila_email = getattr(settings, 'XAMILA_CONTACT_EMAIL', 'contact@xamila.com')
    
    def send_sgi_selection_notifications(self, interaction: ClientSGIInteraction) -> Dict[str, bool]:
        """
        Envoie toutes les notifications lors de la sélection d'une SGI
        
        Args:
            interaction: Interaction Client-SGI créée
            
        Returns:
            Dictionnaire avec le statut d'envoi de chaque email
        """
        results = {
            'manager_notification': False,
            'client_confirmation': False,
            'xamila_notification': False
        }
        
        try:
            # 1. Notification au manager SGI
            results['manager_notification'] = self._send_manager_notification(interaction)
            
            # 2. Confirmation au client
            results['client_confirmation'] = self._send_client_confirmation(interaction)
            
            # 3. Notification à l'équipe Xamila
            results['xamila_notification'] = self._send_xamila_notification(interaction)
            
            logger.info(f"Notifications envoyées pour l'interaction {interaction.id}: {results}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des notifications: {str(e)}")
        
        return results
    
    def _send_manager_notification(self, interaction: ClientSGIInteraction) -> bool:
        """
        Envoie une notification au manager de la SGI
        """
        try:
            client = interaction.client_profile
            sgi = interaction.sgi
            
            subject = f"Nouveau client intéressé - {client.full_name}"
            
            # Contexte pour le template
            context = {
                'client_name': client.full_name,
                'client_email': client.user.email,
                'client_phone': client.phone,
                'client_profession': client.profession,
                'investment_amount': client.investment_amount,
                'investment_objective': client.get_investment_objective_display(),
                'risk_tolerance': client.get_risk_tolerance_display(),
                'investment_horizon': client.get_investment_horizon_display(),
                'matching_score': interaction.matching_score,
                'sgi_name': sgi.name,
                'manager_name': sgi.manager_name,
                'interaction_date': interaction.created_at,
                'notes': interaction.notes
            }
            
            # Générer le message
            message = self._generate_manager_email_content(context)
            html_message = self._generate_manager_email_html(context)
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[sgi.manager_email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Enregistrer la notification
            EmailNotification.objects.create(
                to_email=sgi.manager_email,
                from_email=self.from_email,
                subject=subject,
                message=message,
                html_message=html_message,
                notification_type='SGI_MANAGER',
                client_interaction=interaction,
                status='SENT' if success else 'FAILED',
                sent_at=timezone.now() if success else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur envoi notification manager: {str(e)}")
            
            # Enregistrer l'erreur
            EmailNotification.objects.create(
                to_email=interaction.sgi.manager_email,
                from_email=self.from_email,
                subject=f"Nouveau client intéressé - {interaction.client_profile.full_name}",
                message="Erreur lors de la génération du message",
                notification_type='SGI_MANAGER',
                client_interaction=interaction,
                status='FAILED',
                error_message=str(e)
            )
            
            return False
    
    def _send_client_confirmation(self, interaction: ClientSGIInteraction) -> bool:
        """
        Envoie une confirmation au client
        """
        try:
            client = interaction.client_profile
            sgi = interaction.sgi
            
            subject = f"Confirmation de votre intérêt pour {sgi.name}"
            
            # Contexte pour le template
            context = {
                'client_name': client.full_name,
                'sgi_name': sgi.name,
                'sgi_description': sgi.description,
                'manager_name': sgi.manager_name,
                'manager_email': sgi.manager_email,
                'matching_score': interaction.matching_score,
                'investment_amount': client.investment_amount,
                'interaction_date': interaction.created_at,
                'next_steps': [
                    'Le manager de la SGI a été notifié de votre intérêt',
                    'Vous serez contacté dans les 48 heures',
                    'Préparez vos documents d\'identité et justificatifs de revenus',
                    'Vous pouvez suivre l\'évolution dans votre espace client'
                ]
            }
            
            # Générer le message
            message = self._generate_client_email_content(context)
            html_message = self._generate_client_email_html(context)
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[client.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            # Enregistrer la notification
            EmailNotification.objects.create(
                to_email=client.user.email,
                from_email=self.from_email,
                subject=subject,
                message=message,
                html_message=html_message,
                notification_type='CLIENT_CONFIRMATION',
                client_interaction=interaction,
                status='SENT' if success else 'FAILED',
                sent_at=timezone.now() if success else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur envoi confirmation client: {str(e)}")
            
            # Enregistrer l'erreur
            EmailNotification.objects.create(
                to_email=interaction.client_profile.user.email,
                from_email=self.from_email,
                subject=f"Confirmation de votre intérêt pour {interaction.sgi.name}",
                message="Erreur lors de la génération du message",
                notification_type='CLIENT_CONFIRMATION',
                client_interaction=interaction,
                status='FAILED',
                error_message=str(e)
            )
            
            return False
    
    def _send_xamila_notification(self, interaction: ClientSGIInteraction) -> bool:
        """
        Envoie une notification à l'équipe Xamila
        """
        try:
            client = interaction.client_profile
            sgi = interaction.sgi
            
            subject = f"Nouvelle sélection SGI - {client.full_name} → {sgi.name}"
            
            # Contexte pour le template
            context = {
                'client_name': client.full_name,
                'client_email': client.user.email,
                'client_phone': client.phone,
                'investment_amount': client.investment_amount,
                'sgi_name': sgi.name,
                'manager_name': sgi.manager_name,
                'manager_email': sgi.manager_email,
                'matching_score': interaction.matching_score,
                'interaction_date': interaction.created_at,
                'priority': self._calculate_priority(client.investment_amount)
            }
            
            # Générer le message
            message = self._generate_xamila_email_content(context)
            
            # Envoyer l'email
            success = send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[self.xamila_email],
                fail_silently=False
            )
            
            # Enregistrer la notification
            EmailNotification.objects.create(
                to_email=self.xamila_email,
                from_email=self.from_email,
                subject=subject,
                message=message,
                notification_type='XAMILA_NOTIFICATION',
                client_interaction=interaction,
                status='SENT' if success else 'FAILED',
                sent_at=timezone.now() if success else None
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Erreur envoi notification Xamila: {str(e)}")
            
            # Enregistrer l'erreur
            EmailNotification.objects.create(
                to_email=self.xamila_email,
                from_email=self.from_email,
                subject=f"Nouvelle sélection SGI - {interaction.client_profile.full_name}",
                message="Erreur lors de la génération du message",
                notification_type='XAMILA_NOTIFICATION',
                client_interaction=interaction,
                status='FAILED',
                error_message=str(e)
            )
            
            return False
    
    def _calculate_priority(self, investment_amount) -> str:
        """Calcule la priorité basée sur le montant d'investissement"""
        if investment_amount >= 50000000:  # 50M FCFA
            return 'CRITIQUE'
        elif investment_amount >= 10000000:  # 10M FCFA
            return 'ÉLEVÉE'
        elif investment_amount >= 1000000:  # 1M FCFA
            return 'MOYENNE'
        else:
            return 'FAIBLE'
    
    def _generate_manager_email_content(self, context) -> str:
        """Génère le contenu email pour le manager SGI"""
        return f"""
Bonjour {context['manager_name']},

Un nouveau client a manifesté son intérêt pour votre SGI "{context['sgi_name']}" via la plateforme Xamila.

INFORMATIONS CLIENT:
- Nom: {context['client_name']}
- Email: {context['client_email']}
- Téléphone: {context['client_phone']}
- Profession: {context['client_profession']}

PROFIL D'INVESTISSEMENT:
- Montant à investir: {context['investment_amount']:,.0f} FCFA
- Objectif: {context['investment_objective']}
- Tolérance au risque: {context['risk_tolerance']}
- Horizon: {context['investment_horizon']}

COMPATIBILITÉ:
- Score de matching: {context['matching_score']}/100

{f"Notes du client: {context['notes']}" if context['notes'] else ""}

Nous vous recommandons de contacter ce client dans les 48 heures pour maintenir un excellent niveau de service.

Cordialement,
L'équipe Xamila
"""
    
    def _generate_manager_email_html(self, context) -> str:
        """Génère le contenu HTML pour le manager SGI"""
        # Ici, vous pourriez utiliser un template HTML plus sophistiqué
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Nouveau client intéressé</h2>
        
        <p>Bonjour <strong>{context['manager_name']}</strong>,</p>
        
        <p>Un nouveau client a manifesté son intérêt pour votre SGI "<strong>{context['sgi_name']}</strong>" via la plateforme Xamila.</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #495057; margin-top: 0;">Informations Client</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Nom:</strong> {context['client_name']}</li>
                <li><strong>Email:</strong> {context['client_email']}</li>
                <li><strong>Téléphone:</strong> {context['client_phone']}</li>
                <li><strong>Profession:</strong> {context['client_profession']}</li>
            </ul>
        </div>
        
        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #28a745; margin-top: 0;">Profil d'Investissement</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Montant à investir:</strong> {context['investment_amount']:,.0f} FCFA</li>
                <li><strong>Objectif:</strong> {context['investment_objective']}</li>
                <li><strong>Tolérance au risque:</strong> {context['risk_tolerance']}</li>
                <li><strong>Horizon:</strong> {context['investment_horizon']}</li>
            </ul>
        </div>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #856404; margin-top: 0;">Score de Compatibilité</h3>
            <p style="font-size: 24px; font-weight: bold; color: #28a745; margin: 0;">
                {context['matching_score']}/100
            </p>
        </div>
        
        <p style="background: #d1ecf1; padding: 10px; border-radius: 5px; color: #0c5460;">
            <strong>Recommandation:</strong> Contactez ce client dans les 48 heures pour maintenir un excellent niveau de service.
        </p>
        
        <hr style="margin: 30px 0;">
        <p style="color: #6c757d; font-size: 14px;">
            Cordialement,<br>
            L'équipe Xamila
        </p>
    </div>
</body>
</html>
"""
    
    def _generate_client_email_content(self, context) -> str:
        """Génère le contenu email pour le client"""
        return f"""
Bonjour {context['client_name']},

Nous avons bien enregistré votre intérêt pour la SGI "{context['sgi_name']}".

DÉTAILS DE VOTRE SÉLECTION:
- SGI sélectionnée: {context['sgi_name']}
- Manager: {context['manager_name']}
- Score de compatibilité: {context['matching_score']}/100
- Montant d'investissement: {context['investment_amount']:,.0f} FCFA

PROCHAINES ÉTAPES:
{chr(10).join(f"• {step}" for step in context['next_steps'])}

Le manager de la SGI ({context['manager_email']}) a été notifié et vous contactera prochainement.

Vous pouvez suivre l'évolution de votre demande dans votre espace client sur la plateforme Xamila.

Cordialement,
L'équipe Xamila
"""
    
    def _generate_client_email_html(self, context) -> str:
        """Génère le contenu HTML pour le client"""
        return f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Confirmation de votre sélection SGI</h2>
        
        <p>Bonjour <strong>{context['client_name']}</strong>,</p>
        
        <p>Nous avons bien enregistré votre intérêt pour la SGI "<strong>{context['sgi_name']}</strong>".</p>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #495057; margin-top: 0;">Détails de votre sélection</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>SGI sélectionnée:</strong> {context['sgi_name']}</li>
                <li><strong>Manager:</strong> {context['manager_name']}</li>
                <li><strong>Score de compatibilité:</strong> <span style="color: #28a745; font-weight: bold;">{context['matching_score']}/100</span></li>
                <li><strong>Montant d'investissement:</strong> {context['investment_amount']:,.0f} FCFA</li>
            </ul>
        </div>
        
        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="color: #28a745; margin-top: 0;">Prochaines étapes</h3>
            <ul>
                {chr(10).join(f"<li>{step}</li>" for step in context['next_steps'])}
            </ul>
        </div>
        
        <p style="background: #d1ecf1; padding: 10px; border-radius: 5px; color: #0c5460;">
            Le manager de la SGI (<strong>{context['manager_email']}</strong>) a été notifié et vous contactera prochainement.
        </p>
        
        <hr style="margin: 30px 0;">
        <p style="color: #6c757d; font-size: 14px;">
            Cordialement,<br>
            L'équipe Xamila
        </p>
    </div>
</body>
</html>
"""
    
    def _generate_xamila_email_content(self, context) -> str:
        """Génère le contenu email pour l'équipe Xamila"""
        return f"""
NOUVELLE SÉLECTION SGI - PRIORITÉ {context['priority']}

CLIENT:
- Nom: {context['client_name']}
- Email: {context['client_email']}
- Téléphone: {context['client_phone']}
- Montant: {context['investment_amount']:,.0f} FCFA

SGI SÉLECTIONNÉE:
- Nom: {context['sgi_name']}
- Manager: {context['manager_name']} ({context['manager_email']})
- Score: {context['matching_score']}/100

Date: {context['interaction_date'].strftime('%d/%m/%Y %H:%M')}

Action requise: Suivi dans le dashboard admin
"""

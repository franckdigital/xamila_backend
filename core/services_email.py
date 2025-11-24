"""
Service d'envoi d'emails pour les contrats d'ouverture de compte.
Envoie le contrat et les annexes au client, au manager SGI et à l'équipe Xamila.
"""
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class ContractEmailService:
    """
    Service pour envoyer les emails de contrat avec pièces jointes.
    """
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.xamila_team_email = getattr(settings, 'XAMILA_TEAM_EMAIL', 'xamila.developer@gmail.com')
    
    def send_contract_emails(
        self,
        aor,
        contract_pdf: bytes,
        annexes_pdf: bytes,
        sgi_manager_email: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ) -> dict:
        """
        Envoie les emails avec le contrat, les annexes, la photo et la CNI.
        
        Args:
            aor: AccountOpeningRequest instance
            contract_pdf: Contenu du PDF du contrat principal
            annexes_pdf: Contenu du PDF des annexes
            sgi_manager_email: Email du manager SGI (optionnel)
            admin_emails: Liste des emails admin (optionnel)
            
        Returns:
            dict avec les résultats d'envoi
        """
        results = {
            'client': False,
            'sgi_manager': False,
            'xamila_team': False,
            'admin': False,
            'errors': []
        }
        
        # Email du client
        client_email = aor.email
        if client_email:
            try:
                self._send_client_email(aor, client_email, contract_pdf, annexes_pdf)
                results['client'] = True
                logger.info(f"Email envoyé au client: {client_email}")
            except Exception as e:
                error_msg = f"Erreur envoi email client: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Email du manager SGI
        if sgi_manager_email:
            try:
                self._send_sgi_manager_email(aor, sgi_manager_email, contract_pdf, annexes_pdf)
                results['sgi_manager'] = True
                logger.info(f"Email envoyé au manager SGI: {sgi_manager_email}")
            except Exception as e:
                error_msg = f"Erreur envoi email manager SGI: {e}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # Email de l'équipe Xamila
        try:
            self._send_xamila_team_email(aor, contract_pdf, annexes_pdf)
            results['xamila_team'] = True
            logger.info(f"Email envoyé à l'équipe Xamila: {self.xamila_team_email}")
        except Exception as e:
            error_msg = f"Erreur envoi email équipe Xamila: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Email des admins
        if admin_emails:
            for admin_email in admin_emails:
                try:
                    self._send_admin_email(aor, admin_email, contract_pdf, annexes_pdf)
                    results['admin'] = True
                    logger.info(f"Email envoyé à l'admin: {admin_email}")
                except Exception as e:
                    error_msg = f"Erreur envoi email admin {admin_email}: {e}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        return results
    
    def _send_client_email(self, aor, to_email: str, contract_pdf: bytes, annexes_pdf: bytes):
        """Envoie l'email au client"""
        subject = f"Votre demande d'ouverture de compte-titres - {aor.sgi.name if aor.sgi else 'SGI'}"
        
        # Contexte pour le template
        context = {
            'client_name': aor.full_name,
            'sgi_name': aor.sgi.name if aor.sgi else 'la SGI',
            'request_id': aor.id,
        }
        
        # Corps de l'email en HTML
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1976d2;">Demande d'ouverture de compte-titres</h2>
                
                <p>Bonjour <strong>{aor.full_name}</strong>,</p>
                
                <p>Nous avons bien reçu votre demande d'ouverture de compte-titres auprès de <strong>{aor.sgi.name if aor.sgi else 'la SGI'}</strong>.</p>
                
                <p>Vous trouverez en pièces jointes :</p>
                <ul>
                    <li><strong>Contrat principal</strong> : Convention d'ouverture de compte-titres</li>
                    <li><strong>Annexes</strong> : Formulaires complétés avec vos informations</li>
                    <li><strong>Photo d'identité</strong> : Votre photo</li>
                    <li><strong>Pièce d'identité</strong> : Scan de votre CNI/Passeport</li>
                </ul>
                
                <p><strong>Prochaines étapes :</strong></p>
                <ol>
                    <li>Vérifiez attentivement les informations dans les annexes</li>
                    <li>Imprimez et signez les documents</li>
                    <li>Retournez-nous les documents signés avec les pièces justificatives</li>
                </ol>
                
                <p style="background-color: #e3f2fd; padding: 15px; border-left: 4px solid #1976d2; margin: 20px 0;">
                    <strong>📋 Numéro de demande :</strong> {aor.id}<br>
                    <strong>📧 Email :</strong> {aor.email}<br>
                    <strong>📞 Téléphone :</strong> {aor.phone}
                </p>
                
                <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
                
                <p>Cordialement,<br>
                <strong>L'équipe Xamila</strong></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                <p style="font-size: 12px; color: #666;">
                    Cet email a été envoyé automatiquement. Merci de ne pas y répondre directement.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Créer l'email
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=self.from_email,
            to=[to_email],
        )
        email.content_subtype = "html"
        
        # Ajouter les pièces jointes
        sgi_name = aor.sgi.name.replace(' ', '_') if aor.sgi else 'SGI'
        client_name = aor.full_name.replace(" ", "_")
        
        email.attach(
            f'Contrat_{sgi_name}_{client_name}.pdf',
            contract_pdf,
            'application/pdf'
        )
        email.attach(
            f'Annexes_{sgi_name}_{client_name}.pdf',
            annexes_pdf,
            'application/pdf'
        )
        
        # Ajouter la photo si disponible
        if aor.photo:
            try:
                photo_content = aor.photo.read()
                aor.photo.seek(0)  # Reset file pointer
                email.attach(
                    f'Photo_{client_name}.{aor.photo.name.split(".")[-1]}',
                    photo_content,
                    f'image/{aor.photo.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la photo: {e}")
        
        # Ajouter la CNI si disponible
        if aor.id_card_scan:
            try:
                id_content = aor.id_card_scan.read()
                aor.id_card_scan.seek(0)  # Reset file pointer
                email.attach(
                    f'CNI_{client_name}.{aor.id_card_scan.name.split(".")[-1]}',
                    id_content,
                    'application/pdf' if aor.id_card_scan.name.endswith('.pdf') else f'image/{aor.id_card_scan.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la CNI: {e}")
        
        # Envoyer
        email.send()
    
    def _send_sgi_manager_email(self, aor, to_email: str, contract_pdf: bytes, annexes_pdf: bytes):
        """Envoie l'email au manager de la SGI"""
        subject = f"Nouvelle demande d'ouverture de compte - {aor.full_name}"
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #00a651;">Nouvelle demande d'ouverture de compte</h2>
                
                <p>Bonjour,</p>
                
                <p>Une nouvelle demande d'ouverture de compte-titres a été soumise via Xamila.</p>
                
                <p><strong>Informations du client :</strong></p>
                <ul>
                    <li><strong>Nom complet :</strong> {aor.full_name}</li>
                    <li><strong>Email :</strong> {aor.email}</li>
                    <li><strong>Téléphone :</strong> {aor.phone}</li>
                    <li><strong>Pays :</strong> {aor.country_of_residence}</li>
                    <li><strong>Nationalité :</strong> {aor.nationality}</li>
                </ul>
                
                <p><strong>Profil investisseur :</strong> {aor.investor_profile}</p>
                
                <p style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff6b00; margin: 20px 0;">
                    <strong>📋 Numéro de demande :</strong> {aor.id}<br>
                    <strong>📅 Date de soumission :</strong> {aor.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(aor, 'created_at') else 'N/A'}
                </p>
                
                <p>Vous trouverez en pièces jointes le contrat et les annexes complétés.</p>
                
                <p>Cordialement,<br>
                <strong>Plateforme Xamila</strong></p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=self.from_email,
            to=[to_email],
        )
        email.content_subtype = "html"
        
        client_name = aor.full_name.replace(" ", "_")
        
        email.attach(
            f'Contrat_{client_name}.pdf',
            contract_pdf,
            'application/pdf'
        )
        email.attach(
            f'Annexes_{client_name}.pdf',
            annexes_pdf,
            'application/pdf'
        )
        
        # Ajouter la photo si disponible
        if aor.photo:
            try:
                photo_content = aor.photo.read()
                aor.photo.seek(0)
                email.attach(
                    f'Photo_{client_name}.{aor.photo.name.split(".")[-1]}',
                    photo_content,
                    f'image/{aor.photo.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la photo: {e}")
        
        # Ajouter la CNI si disponible
        if aor.id_card_scan:
            try:
                id_content = aor.id_card_scan.read()
                aor.id_card_scan.seek(0)
                email.attach(
                    f'CNI_{client_name}.{aor.id_card_scan.name.split(".")[-1]}',
                    id_content,
                    'application/pdf' if aor.id_card_scan.name.endswith('.pdf') else f'image/{aor.id_card_scan.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la CNI: {e}")
        
        email.send()
    
    def _send_xamila_team_email(self, aor, contract_pdf: bytes, annexes_pdf: bytes):
        """Envoie l'email à l'équipe Xamila"""
        subject = f"[NOUVELLE DEMANDE] {aor.full_name} - {aor.sgi.name if aor.sgi else 'SGI'}"
        
        html_message = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #9c27b0;">📋 Nouvelle demande d'ouverture de compte</h2>
                
                <p><strong>Client :</strong> {aor.full_name}</p>
                <p><strong>SGI :</strong> {aor.sgi.name if aor.sgi else 'N/A'}</p>
                <p><strong>Email :</strong> {aor.email}</p>
                <p><strong>Téléphone :</strong> {aor.phone}</p>
                
                <p style="background-color: #f3e5f5; padding: 15px; border-left: 4px solid #9c27b0; margin: 20px 0;">
                    <strong>ID Demande :</strong> {aor.id}<br>
                    <strong>Profil :</strong> {aor.investor_profile}<br>
                    <strong>Pays :</strong> {aor.country_of_residence}
                </p>
                
                <p><strong>Méthodes de financement :</strong></p>
                <ul>
                    {'<li>VISA</li>' if aor.funding_by_visa else ''}
                    {'<li>Mobile Money</li>' if aor.funding_by_mobile_money else ''}
                    {'<li>Virement bancaire</li>' if aor.funding_by_bank_transfer else ''}
                    {'<li>Intermédiaire</li>' if aor.funding_by_intermediary else ''}
                    {'<li>WU/MG/RIA</li>' if aor.funding_by_wu_mg_ria else ''}
                </ul>
                
                <p>Documents en pièces jointes.</p>
                
                <p><strong>L'équipe Xamila</strong></p>
            </div>
        </body>
        </html>
        """
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=self.from_email,
            to=[self.xamila_team_email],
        )
        email.content_subtype = "html"
        
        client_name = aor.full_name.replace(" ", "_")
        
        email.attach(
            f'Contrat_{aor.id}.pdf',
            contract_pdf,
            'application/pdf'
        )
        email.attach(
            f'Annexes_{aor.id}.pdf',
            annexes_pdf,
            'application/pdf'
        )
        
        # Ajouter la photo si disponible
        if aor.photo:
            try:
                photo_content = aor.photo.read()
                aor.photo.seek(0)
                email.attach(
                    f'Photo_{client_name}.{aor.photo.name.split(".")[-1]}',
                    photo_content,
                    f'image/{aor.photo.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la photo: {e}")
        
        # Ajouter la CNI si disponible
        if aor.id_card_scan:
            try:
                id_content = aor.id_card_scan.read()
                aor.id_card_scan.seek(0)
                email.attach(
                    f'CNI_{client_name}.{aor.id_card_scan.name.split(".")[-1]}',
                    id_content,
                    'application/pdf' if aor.id_card_scan.name.endswith('.pdf') else f'image/{aor.id_card_scan.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la CNI: {e}")
        
        email.send()
    
    def _send_admin_email(self, aor, to_email: str, contract_pdf: bytes, annexes_pdf: bytes):
        ""Envoie l'email � un administrateur""
        subject = f"[ADMIN] Nouvelle demande - {aor.full_name} - {aor.sgi.name if aor.sgi else 'SGI'}"
        
        html_message = f""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #d32f2f;">?? Nouvelle demande d'ouverture de compte (ADMIN)</h2>
                
                <p><strong>Client :</strong> {aor.full_name}</p>
                <p><strong>SGI :</strong> {aor.sgi.name if aor.sgi else 'N/A'}</p>
                <p><strong>Email :</strong> {aor.email}</p>
                <p><strong>T�l�phone :</strong> {aor.phone}</p>
                
                <p style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
                    <strong>ID Demande :</strong> {aor.id}<br>
                    <strong>Profil :</strong> {aor.investor_profile}<br>
                    <strong>Pays :</strong> {aor.country_of_residence}<br>
                    <strong>Nationalit� :</strong> {aor.nationality}
                </p>
                
                <p><strong>Pr�f�rences :</strong></p>
                <ul>
                    <li>Ouverture digitale : {'Oui' if aor.wants_digital_opening else 'Non'}</li>
                    <li>Ouverture en personne : {'Oui' if aor.wants_in_person_opening else 'Non'}</li>
                    <li>Xamila+ : {'Oui' if aor.wants_xamila_plus else 'Non'}</li>
                </ul>
                
                <p><strong>Documents en pi�ces jointes :</strong></p>
                <ul>
                    <li>Contrat complet</li>
                    <li>Annexes pr�-remplies</li>
                    <li>Photo d'identit�</li>
                    <li>Pi�ce d'identit� (CNI/Passeport)</li>
                </ul>
                
                <p><strong>Administration Xamila</strong></p>
            </div>
        </body>
        </html>
        ""
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=self.from_email,
            to=[to_email],
        )
        email.content_subtype = "html"
        
        client_name = aor.full_name.replace(" ", "_")
        
        email.attach(
            f'Contrat_{aor.id}.pdf',
            contract_pdf,
            'application/pdf'
        )
        email.attach(
            f'Annexes_{aor.id}.pdf',
            annexes_pdf,
            'application/pdf'
        )
        
        # Ajouter la photo si disponible
        if aor.photo:
            try:
                photo_content = aor.photo.read()
                aor.photo.seek(0)
                email.attach(
                    f'Photo_{client_name}.{aor.photo.name.split(".")[-1]}',
                    photo_content,
                    f'image/{aor.photo.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la photo: {e}")
        
        # Ajouter la CNI si disponible
        if aor.id_card_scan:
            try:
                id_content = aor.id_card_scan.read()
                aor.id_card_scan.seek(0)
                email.attach(
                    f'CNI_{client_name}.{aor.id_card_scan.name.split(".")[-1]}',
                    id_content,
                    'application/pdf' if aor.id_card_scan.name.endswith('.pdf') else f'image/{aor.id_card_scan.name.split(".")[-1]}'
                )
            except Exception as e:
                logger.warning(f"Impossible d'attacher la CNI: {e}")
        
        email.send()

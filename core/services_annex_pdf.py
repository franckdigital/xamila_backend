"""
Service pour générer les annexes du contrat en PDF séparé.
Les annexes contiennent les données dynamiques du client.
Le contrat principal reste statique.
"""
from io import BytesIO
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfWriter
from django.conf import settings
import os

logger = logging.getLogger(__name__)


class AnnexPDFService:
    """
    Génère un PDF contenant uniquement les annexes (pages 21, 22, 23, 26)
    avec les données dynamiques du client.
    """
    
    def __init__(self):
        self.font_name = "Helvetica"
        self.font_size = 10
    
    def generate_annexes_pdf(self, aor, annex_data: dict) -> BytesIO:
        """
        Génère un PDF avec les 4 pages d'annexes remplies.
        
        Args:
            aor: AccountOpeningRequest instance
            annex_data: Dict contenant page21, page22, page23, page26
            
        Returns:
            BytesIO contenant le PDF des annexes
        """
        writer = PdfWriter()
        
        # Générer chaque page d'annexe
        pages = [
            ('Page 21 - Texte légal et signatures', self._generate_page21),
            ('Page 22 - Formulaire d\'ouverture', self._generate_page22),
            ('Page 23 - Caractéristiques du compte', self._generate_page23),
            ('Page 26 - Procuration', self._generate_page26),
        ]
        
        for title, generator_func in pages:
            try:
                page_buffer = generator_func(aor, annex_data)
                if page_buffer:
                    from pypdf import PdfReader
                    reader = PdfReader(page_buffer)
                    for page in reader.pages:
                        writer.add_page(page)
            except Exception as e:
                logger.error(f"Erreur génération {title}: {e}")
        
        # Écrire le PDF final
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return output
    
    def _generate_page21(self, aor, annex_data: dict) -> BytesIO:
        """Génère la page 21 - Fin du contrat (Articles 30 et 34)"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p21 = annex_data.get('page21', {})
        
        # Pas de titre - continuation du contrat
        y = height - 30*mm
        
        # Article 30 : Élection de domicile
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Article 30 : Élection de domicile")
        y -= 7*mm
        
        c.setFont("Helvetica", 9)
        legal_text_art30 = [
            "Pour l'exécution de la Convention, les Parties font élection de domicile en leur siège social et domicile respectifs, tels qu'indiqués",
            "en tête des présentes.",
            "",
            "Tout changement de siège ou de domicile devra être notifié à l'autre Partie dans un délai de huit (8) jours calendaires, à compter de",
            "la survenance dudit changement effectif.",
            "",
            "Sauf stipulation contraire, toute notification ou communication à laquelle pourrait donner lieu la Convention devra être adressée",
            "par lettre recommandée avec accusé de réception, remise en main propre contre décharge ou par huissier. Chaque notification ou",
            "communication aura effet dès sa réception. Les notifications par lettre recommandée seront considérées avoir été reçues à la date",
            "de première présentation de la lettre recommandée, si l'avis de réception, si l'avis de réception a été signé ou si la lettre a été",
            "retournée avec quelque mention que ce soit, telles que 'inconnu à l'adresse', 'parti sans laisser d'adresse', 'non retiré', 'locaux fermés', etc.",
            "",
        ]
        
        for line in legal_text_art30:
            c.drawString(30*mm, y, line)
            y -= 5*mm
        
        # Article 34 : Langue
        y -= 3*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Article 34 : Langue")
        y -= 7*mm
        
        c.setFont("Helvetica", 9)
        legal_text_art34 = [
            "Le texte de la présente Convention est en français et, s'il est traduit dans une autre langue, seule la version française prévaudra.",
            "",
        ]
        
        for line in legal_text_art34:
            c.drawString(30*mm, y, line)
            y -= 5*mm
        
        # Fait à / Le
        y -= 5*mm
        c.setFont("Helvetica", 10)
        place = p21.get('place', 'Abidjan')
        date = p21.get('date', '')
        c.drawString(30*mm, y, f"Fait en deux exemplaires à {place}, le {date}")
        
        # Zones de signature
        y -= 20*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "LE(S) TITULAIRE(S) (1)")
        # SGI label dynamique: utilise le nom de la SGI sélectionnée
        sgi_label = "SGI"
        try:
            sgi = getattr(aor, "sgi", None)
            if sgi and getattr(sgi, "name", None):
                name = sgi.name.strip()
                upper = name.upper()
                if "NSIA" in upper:
                    sgi_label = "NSIA FINANCES"
                elif "GEK" in upper:
                    sgi_label = "GEK CAPITAL"
                else:
                    sgi_label = name
        except Exception:
            pass
        c.drawString(120*mm, y, sgi_label)
        
        y -= 5*mm
        c.setFont("Helvetica", 8)
        c.drawString(30*mm, y, '(1) Signature précédée de la mention manuscrite "Lu et approuvé"')
        
        # Dessiner des rectangles pour les zones de signature
        y -= 25*mm
        c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        c.rect(120*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        
        # Afficher les signatures si présentes (base64 -> image)
        sig_titulaire = p21.get('signature_titulaire')
        sig_sgi = p21.get('signature_sgi') or p21.get('signature_gek')  # Compatibilité
        
        if sig_titulaire:
            y -= 30*mm
            c.drawString(30*mm, y, "[Signature titulaire présente]")
        
        if sig_sgi:
            c.drawString(120*mm, y, f"[Signature {sgi_label} présente]")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    
    def _generate_page22(self, aor, annex_data: dict) -> BytesIO:
        """Génère la page 22 - Formulaire d'ouverture"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p22 = annex_data.get('page22', {})
        
        # En-tête Annexe 1
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30*mm, height - 20*mm, "Annexe 1 : Formulaire d'ouverture de compte-titres")
        
        # Note IMPORTANT
        y = height - 30*mm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(30*mm, y, "IMPORTANT : En cas de pluralité de titulaires")
        y -= 4*mm
        c.setFont("Helvetica", 8)
        c.drawString(30*mm, y, "(compte joint de titres, compte en indivision ou compte usufrui nue-propriété), merci de photocopier cette")
        y -= 4*mm
        c.drawString(30*mm, y, "page en autant d'exemplaires qu'il y a de co-titulaires du compte, de la compléter et de la joindre à votre envoi")
        y -= 4*mm
        c.drawString(30*mm, y, "(un exemplaire par co-titulaire accompagné des pièces justificatives).")
        
        # Numéro de compte-titres
        y = height - 50*mm
        c.setFont("Helvetica", 9)
        account_number = p22.get('account_number', '...........................................................................')
        c.drawString(30*mm, y, f"Numéro de compte-titres : {account_number}")
        y -= 10*mm
        
        # TITULAIRE PERSONNE PHYSIQUE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70*mm, y, "TITULAIRE PERSONNE PHYSIQUE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        # Civilité
        civility = p22.get('civility', 'Monsieur')
        c.drawString(30*mm, y, f"Civilité : {civility}")
        y -= 5*mm
        
        # Nom
        last_name = p22.get('last_name', '................................................................................................................................................................')
        c.drawString(30*mm, y, f"Nom : {last_name}")
        y -= 5*mm
        
        # Nom de jeune fille (pour les femmes mariées)
        maiden_name = p22.get('maiden_name', '.....................................................................................................................................................................')
        c.drawString(30*mm, y, f"Nom de jeune fille (pour les femmes mariées) : {maiden_name}")
        y -= 5*mm
        
        # Prénom(s)
        first_names = p22.get('first_names', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Prénom(s) : {first_names}")
        y -= 5*mm
        
        # Date et lieu de naissance
        birth_date = p22.get('birth_date', '.............................')
        birth_place = p22.get('birth_place', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Date de naissance (jj/mm/aaaa) : {birth_date}    Lieu de naissance : {birth_place}")
        y -= 5*mm
        
        # Nationalité
        nationality = p22.get('nationality', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Nationalité : {nationality}")
        y -= 5*mm
        
        # Type de pièce d'identité
        id_type = p22.get('id_type', '.............................')
        id_number = p22.get('id_number', '.............................')
        id_validity = p22.get('id_validity', '.................................')
        c.drawString(30*mm, y, f"Type de pièce d'identité : {id_type}  Numéro : {id_number}  Date de validité : {id_validity}")
        y -= 8*mm
        
        # TITULAIRE PERSONNE MORALE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70*mm, y, "TITULAIRE PERSONNE MORALE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        company_name = p22.get('company_name', '.................................................................................................................................................................')
        rccm_number = p22.get('rccm_number', '.................................')
        c.drawString(30*mm, y, f"Nom de la société : {company_name}    Numéro RCCM : {rccm_number}")
        y -= 5*mm
        
        # Numéro Compte contribuable
        tax_number = p22.get('tax_number', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Numéro Compte contribuable : {tax_number}")
        y -= 5*mm
        
        # Représentée par
        representative_name = p22.get('representative_name', '.................................................................................................................................................................')
        representative_first_names = p22.get('representative_first_names', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Représentée par Nom : {representative_name}    Prénom(s) : {representative_first_names}")
        y -= 5*mm
        
        # Date de naissance représentant
        rep_birth_date = p22.get('rep_birth_date', '.............................')
        rep_birth_place = p22.get('rep_birth_place', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Date de naissance (jj/mm/aaaa) : {rep_birth_date}    Lieu de naissance : {rep_birth_place}")
        y -= 5*mm
        
        # Titulaire de la pièce d'identité
        rep_id_type = p22.get('rep_id_type', '.............................')
        rep_id_number = p22.get('rep_id_number', '.............................')
        rep_id_validity = p22.get('rep_id_validity', '.................................')
        c.drawString(30*mm, y, f"Titulaire de la pièce d'identité : {rep_id_type}  N° : {rep_id_number}  Valide jusqu'au : {rep_id_validity}")
        y -= 5*mm
        
        # Nationalité représentant
        rep_nationality = p22.get('rep_nationality', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Nationalité : {rep_nationality}")
        y -= 5*mm
        
        # Fonction
        rep_function = p22.get('rep_function', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Fonction : {rep_function}")
        y -= 8*mm
        
        # ADRESSE FISCALE DU TITULAIRE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "ADRESSE FISCALE DU TITULAIRE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        fiscal_address = p22.get('fiscal_address', '.................................................................................................................................................................')
        fiscal_building = p22.get('fiscal_building', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Résidence, Bâtiment : {fiscal_address}    N° de rue : {fiscal_building}")
        y -= 5*mm
        
        fiscal_postal_code = p22.get('fiscal_postal_code', '.............................')
        fiscal_city = p22.get('fiscal_city', '.................................................................................................................................................................')
        fiscal_country = p22.get('fiscal_country', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Code postal : {fiscal_postal_code}    Ville : {fiscal_city}    Pays : {fiscal_country}")
        y -= 8*mm
        
        # ADRESSE POSTALE DU TITULAIRE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "ADRESSE POSTALE DU TITULAIRE (si différente de l'adresse fiscale)")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        postal_address = p22.get('postal_address', '.................................................................................................................................................................')
        postal_building = p22.get('postal_building', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Résidence, Bâtiment : {postal_address}    N° de rue : {postal_building}")
        y -= 5*mm
        
        postal_code = p22.get('postal_code', '.............................')
        postal_city = p22.get('postal_city', '.................................................................................................................................................................')
        postal_country = p22.get('postal_country', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Code postal : {postal_code}    Ville : {postal_city}    Pays : {postal_country}")
        y -= 8*mm
        
        # Cases à cocher
        c.setFont("Helvetica", 9)
        is_fiscal_resident = p22.get('is_fiscal_resident', False)
        is_cedeao_member = p22.get('is_cedeao_member', False)
        is_outside_cedeao = p22.get('is_outside_cedeao', False)
        
        marker_fiscal = "☑" if is_fiscal_resident else "☐"
        marker_cedeao = "☑" if is_cedeao_member else "☐"
        marker_outside = "☑" if is_outside_cedeao else "☐"
        
        c.drawString(30*mm, y, f"{marker_fiscal} Résident fiscal ivoirien    {marker_cedeao} Membre de la CEDEAO    {marker_outside} Pays hors CEDEAO")
        y -= 8*mm
        
        # COORDONNÉES DU TITULAIRE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "COORDONNÉES DU TITULAIRE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        phone_portable = p22.get('phone_portable', '.................................................................................................................................................................')
        phone_domicile = p22.get('phone_domicile', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Tél Portable : {phone_portable}    Tél Domicile : {phone_domicile}")
        y -= 5*mm
        
        email = p22.get('email', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Email : {email}")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    
    def _generate_page23(self, aor, annex_data: dict) -> BytesIO:
        """Génère la page 23 - Caractéristiques du compte"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p23 = annex_data.get('page23', {})
        
        # Continuation de l'Annexe 1
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30*mm, height - 20*mm, "Annexe 1 : Formulaire d'ouverture de compte-titres (suite)")
        
        y = height - 35*mm
        
        # CARACTÉRISTIQUES DU COMPTE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "CARACTÉRISTIQUES DU COMPTE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        
        # Type de compte
        account_individual = p23.get('account_individual', True)
        account_joint = p23.get('account_joint', False)
        account_indivision = p23.get('account_indivision', False)
        account_usufruit = p23.get('account_usufruit', False)
        
        marker = "☑" if account_individual else "☐"
        c.drawString(30*mm, y, f"{marker} Compte individuel pleine propriété")
        y -= 5*mm
        
        marker = "☑" if account_joint else "☐"
        c.drawString(30*mm, y, f"{marker} Compte joint de Titres")
        y -= 5*mm
        
        marker = "☑" if account_indivision else "☐"
        indivision_names = p23.get('indivision_names', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"{marker} Compte en indivision entre : {indivision_names}")
        y -= 5*mm
        
        marker = "☑" if account_usufruit else "☐"
        usufruit_name = p23.get('usufruit_name', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"{marker} Compte usufrui nue-propriété Usufruitier : {usufruit_name}")
        y -= 5*mm
        
        nue_propriete_name = p23.get('nue_propriete_name', '.................................................................................................................................................................')
        c.drawString(40*mm, y, f"Nu-propriétaire : {nue_propriete_name}")
        y -= 8*mm
        
        # PERSONNE DÉSIGNÉE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "PERSONNE DÉSIGNÉE POUR RECEVOIR LES CORRESPONDANCES")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        designated_person_name = p23.get('designated_person_name', '.................................................................................................................................................................')
        designated_person_first_names = p23.get('designated_person_first_names', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Nom : {designated_person_name}    Prénom(s) : {designated_person_first_names}")
        y -= 5*mm
        
        designated_person_address = p23.get('designated_person_address', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Adresse : {designated_person_address}")
        y -= 5*mm
        
        designated_person_phone = p23.get('designated_person_phone', '.................................................................................................................................................................')
        designated_person_email = p23.get('designated_person_email', '.................................................................................................................................................................')
        c.drawString(30*mm, y, f"Téléphone : {designated_person_phone}    Email : {designated_person_email}")
        y -= 8*mm
        
        # MODALITÉS DE FONCTIONNEMENT DU COMPTE
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "MODALITÉS DE FONCTIONNEMENT DU COMPTE")
        y -= 8*mm
        
        c.setFont("Helvetica", 9)
        c.drawString(30*mm, y, "En cas de pluralité de titulaires, le compte fonctionne sous la signature :")
        y -= 5*mm
        
        signature_conjointe = p23.get('signature_conjointe', False)
        signature_separee = p23.get('signature_separee', False)
        
        marker_conjointe = "☑" if signature_conjointe else "☐"
        marker_separee = "☑" if signature_separee else "☐"
        
        c.drawString(30*mm, y, f"{marker_conjointe} Conjointe de tous les titulaires    {marker_separee} Séparée de chacun des titulaires")
        y -= 8*mm
        
        # DÉCLARATION
        c.setFont("Helvetica", 8)
        c.drawString(30*mm, y, "Par le présent, je déclare (nous déclarons) avoir pris connaissance et adhérer à l'intégralité des dispositions de la convention")
        y -= 4*mm
        c.drawString(30*mm, y, "d'ouverture et de tenue de compte-titres ci-annexée et m'engage (nous nous engageons) à respecter les obligations qui en découlent.")
        y -= 4*mm
        c.drawString(30*mm, y, "Je reconnais (nous reconnaissons) avoir reçu un exemplaire de ladite convention.")
        y -= 8*mm
        
        # Fait à / Le
        place = p23.get('place', 'Abidjan')
        date = p23.get('date', '.............................')
        c.setFont("Helvetica", 9)
        c.drawString(30*mm, y, f"Fait à {place}, le {date}, en deux exemplaires originaux.")
        y -= 12*mm
        
        # Zone de signature
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Signature du titulaire")
        y -= 5*mm
        c.setFont("Helvetica", 8)
        c.drawString(30*mm, y, '(précédée de "Lu et approuvé")')
        
        # Rectangle pour la signature
        y -= 25*mm
        c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        
        signature = p23.get('signature')
        if signature:
            c.setFont("Helvetica", 8)
            c.drawString(35*mm, y + 10*mm, "[Signature présente]")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    
    def _generate_page26(self, aor, annex_data: dict) -> BytesIO:
        """Génère la page 26 - Procuration"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p26 = annex_data.get('page26', {})
        
        # Titre Annexe 4
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30*mm, height - 20*mm, "Annexe 4 : Procuration")
        
        y = height - 50*mm
        
        # Vérifier si procuration
        has_procuration = p26.get('has_procuration', False)
        
        if not has_procuration:
            c.setFont("Helvetica", 10)
            c.drawString(30*mm, y, "Pas de procuration demandée")
        else:
            # Mandant
            c.setFont("Helvetica-Bold", 11)
            c.drawString(30*mm, y, "JE SOUSSIGNÉ(E) - MANDANT")
            y -= 8*mm
            
            c.setFont("Helvetica", 10)
            mandant_name = p26.get('mandant_name', '')
            mandant_first_names = p26.get('mandant_first_names', '')
            mandant_address = p26.get('mandant_address', '')
            
            c.drawString(30*mm, y, f"Nom: {mandant_name}")
            y -= 6*mm
            c.drawString(30*mm, y, f"Prénoms: {mandant_first_names}")
            y -= 6*mm
            c.drawString(30*mm, y, f"Adresse: {mandant_address}")
            y -= 10*mm
            
            # Mandataire
            c.setFont("Helvetica-Bold", 11)
            c.drawString(30*mm, y, "DONNE POUVOIR À - MANDATAIRE")
            y -= 8*mm
            
            c.setFont("Helvetica", 10)
            mandataire_name = p26.get('mandataire_name', '')
            mandataire_first_names = p26.get('mandataire_first_names', '')
            mandataire_address = p26.get('mandataire_address', '')
            
            c.drawString(30*mm, y, f"Nom: {mandataire_name}")
            y -= 6*mm
            c.drawString(30*mm, y, f"Prénoms: {mandataire_first_names}")
            y -= 6*mm
            c.drawString(30*mm, y, f"Adresse: {mandataire_address}")
            y -= 10*mm
            
            # Signatures
            c.setFont("Helvetica-Bold", 10)
            c.drawString(30*mm, y, "Signature du mandant")
            c.drawString(120*mm, y, "Signature du mandataire")
            y -= 5*mm
            
            c.setFont("Helvetica", 8)
            c.drawString(30*mm, y, '"Bon pour pouvoir"')
            c.drawString(120*mm, y, '"Bon pour accord"')
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

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
        """Génère la page 21 - Texte légal et signatures"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p21 = annex_data.get('page21', {})
        
        # Titre
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - 30*mm, "PAGE 21 - TEXTE LÉGAL ET SIGNATURES")
        
        # Texte légal (simplifié pour l'exemple)
        c.setFont("Helvetica", 9)
        y = height - 50*mm
        legal_text = [
            "En cas de litige relatif notamment, à la validité, l'interprétation ou l'exécution",
            "de la Convention, les Parties conviennent de suivre la procédure prévue par",
            "l'Instruction n°50/2016 portant procédure de traitement des plaintes...",
            "",
            "Article 30 : Élection de domicile",
            "Pour l'exécution de la Convention, les Parties font élection de domicile...",
        ]
        
        for line in legal_text:
            c.drawString(30*mm, y, line)
            y -= 5*mm
        
        # Fait à / Le
        y -= 10*mm
        c.setFont("Helvetica", 10)
        place = p21.get('place', 'Abidjan')
        date = p21.get('date', '')
        c.drawString(30*mm, y, f"Fait à: {place}")
        c.drawString(120*mm, y, f"Le: {date}")
        
        # Zones de signature
        y -= 20*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "LE(S) TITULAIRE(S)")
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
        c.drawString(30*mm, y, 'Signature précédée de "Lu et approuvé"')
        c.drawString(120*mm, y, 'Signature précédée de "Lu et approuvé"')
        
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
        
        # Titre
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - 30*mm, "PAGE 22 - FORMULAIRE D'OUVERTURE")
        
        y = height - 50*mm
        c.setFont("Helvetica", 10)
        
        # Numéro de compte
        account_number = p22.get('account_number', '')
        if account_number:
            c.drawString(30*mm, y, f"Numéro de compte-titres: {account_number}")
            y -= 10*mm
        
        # Identité personne physique
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y, "IDENTITÉ DE LA PERSONNE PHYSIQUE")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        civility = p22.get('civility', 'Monsieur')
        last_name = p22.get('last_name', '')
        first_names = p22.get('first_names', '')
        
        c.drawString(30*mm, y, f"Civilité: {civility}")
        y -= 6*mm
        c.drawString(30*mm, y, f"Nom: {last_name}")
        y -= 6*mm
        c.drawString(30*mm, y, f"Prénoms: {first_names}")
        y -= 6*mm
        
        # Date et lieu de naissance
        birth_date = p22.get('birth_date', '')
        birth_place = p22.get('birth_place', '')
        c.drawString(30*mm, y, f"Né(e) le: {birth_date}")
        c.drawString(100*mm, y, f"À: {birth_place}")
        y -= 6*mm
        
        # Nationalité
        nationality = p22.get('nationality', '')
        c.drawString(30*mm, y, f"Nationalité: {nationality}")
        y -= 10*mm
        
        # Adresse fiscale
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y, "ADRESSE FISCALE")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        fiscal_address = p22.get('fiscal_address', '')
        fiscal_city = p22.get('fiscal_city', '')
        fiscal_country = p22.get('fiscal_country', '')
        
        c.drawString(30*mm, y, fiscal_address)
        y -= 6*mm
        c.drawString(30*mm, y, f"{fiscal_city}, {fiscal_country}")
        y -= 10*mm
        
        # Coordonnées
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y, "COORDONNÉES")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        phone = p22.get('phone', '')
        email = p22.get('email', '')
        
        c.drawString(30*mm, y, f"Téléphone: {phone}")
        y -= 6*mm
        c.drawString(30*mm, y, f"Email: {email}")
        
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
        
        # Titre
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - 30*mm, "PAGE 23 - CARACTÉRISTIQUES DU COMPTE")
        
        y = height - 50*mm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y, "TYPE DE COMPTE")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        
        # Type de compte
        account_individual = p23.get('account_individual', True)
        account_joint = p23.get('account_joint', False)
        account_indivision = p23.get('account_indivision', False)
        
        marker = "☑" if account_individual else "☐"
        c.drawString(30*mm, y, f"{marker} Compte individuel pleine propriété")
        y -= 6*mm
        
        marker = "☑" if account_joint else "☐"
        c.drawString(30*mm, y, f"{marker} Compte joint de Titres")
        y -= 6*mm
        
        marker = "☑" if account_indivision else "☐"
        c.drawString(30*mm, y, f"{marker} Compte en indivision entre:")
        y -= 10*mm
        
        # Personne désignée
        c.setFont("Helvetica-Bold", 11)
        c.drawString(30*mm, y, "PERSONNE DÉSIGNÉE")
        y -= 8*mm
        
        c.setFont("Helvetica", 10)
        designated_person = p23.get('designated_person_name', '')
        c.drawString(30*mm, y, designated_person)
        y -= 10*mm
        
        # Déclaration
        c.setFont("Helvetica", 9)
        c.drawString(30*mm, y, "Par le présent, je déclare (nous déclarons) avoir pris connaissance")
        y -= 5*mm
        c.drawString(30*mm, y, "et adhérer à l'intégralité des dispositions de la convention...")
        y -= 10*mm
        
        # Fait à / Le
        place = p23.get('place', 'Abidjan')
        date = p23.get('date', '')
        c.setFont("Helvetica", 10)
        c.drawString(30*mm, y, f"Fait à: {place}")
        c.drawString(100*mm, y, f"Le: {date}")
        y -= 10*mm
        
        # Signature
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Signature du titulaire")
        y -= 5*mm
        
        signature = p23.get('signature')
        if signature:
            c.setFont("Helvetica", 8)
            c.drawString(30*mm, y, "[Signature présente]")
        
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
        
        # Titre
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30*mm, height - 30*mm, "PAGE 26 - PROCURATION (ANNEXE 4)")
        
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

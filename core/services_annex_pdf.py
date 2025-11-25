"""
Service pour générer les annexes du contrat en PDF séparé.
Les annexes contiennent les données dynamiques du client.
Le contrat principal reste statique.
"""
from io import BytesIO
import logging
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from pypdf import PdfWriter
from django.conf import settings
import os
from PIL import Image

logger = logging.getLogger(__name__)


class AnnexPDFService:
    """
    Génère un PDF contenant uniquement les annexes (pages 21, 22, 23, 26)
    avec les données dynamiques du client.
    """
    
    def __init__(self):
        self.font_name = "Helvetica"
        self.font_size = 10
        # Couleurs du design original
        self.blue_header = HexColor('#1E3A8A')  # Bleu foncé pour les en-têtes
        self.blue_border = HexColor('#3B82F6')  # Bleu pour les bordures
        self.gray_bg = HexColor('#F3F4F6')      # Gris clair pour les fonds
        self.black_text = colors.black
    
    def _format_date(self, date_string):
        """
        Convertit une date du format YYYY-MM-DD ou ISO en format jj/mm/aaaa.
        
        Args:
            date_string: Date au format YYYY-MM-DD, ISO ou déjà formatée
        
        Returns:
            Date au format jj/mm/aaaa
        """
        if not date_string or date_string == '.............................':
            return '.............................'
        
        try:
            from datetime import datetime
            # Essayer différents formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(date_string.split('+')[0].split('Z')[0], fmt)
                    return dt.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            # Si déjà au bon format ou format inconnu, retourner tel quel
            return date_string
        except Exception as e:
            logger.warning(f"Erreur formatage date {date_string}: {e}")
            return date_string
    
    def _base64_to_image(self, base64_string):
        """
        Convertit une chaîne base64 en objet ImageReader utilisable par ReportLab.
        
        Args:
            base64_string: Chaîne base64 (avec ou sans préfixe data:image/png;base64,)
        
        Returns:
            ImageReader object ou None si erreur
        """
        try:
            # Supprimer le préfixe data:image/png;base64, si présent
            if ',' in base64_string:
                base64_string = base64_string.split(',', 1)[1]
            
            # Décoder le base64
            image_data = base64.b64decode(base64_string)
            
            # Créer un objet Image PIL
            image = Image.open(BytesIO(image_data))
            
            # Convertir en ImageReader pour ReportLab
            image_buffer = BytesIO()
            image.save(image_buffer, format='PNG')
            image_buffer.seek(0)
            
            return ImageReader(image_buffer)
        except Exception as e:
            logger.error(f"Erreur conversion base64 vers image: {e}")
            return None
    
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
                logger.info(f"Génération de {title}...")
                page_buffer = generator_func(aor, annex_data)
                if page_buffer:
                    from pypdf import PdfReader
                    reader = PdfReader(page_buffer)
                    for page in reader.pages:
                        writer.add_page(page)
                    logger.info(f"✅ {title} générée avec succès")
                else:
                    logger.warning(f"⚠️ {title} - buffer vide")
            except Exception as e:
                logger.error(f"❌ Erreur génération {title}: {e}", exc_info=True)
        
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
        y = height - 20*mm
        
        # Texte sur le règlement des litiges (avant Article 30)
        c.setFont("Helvetica", 8)
        
        litige_text = [
            "En cas de litige relatif notamment, à la validité, l'interprétation ou l'exécution de la Convention, les Parties   conviennent de suivre",
            "la procédure prévue par l'instruction n°50/2016 portant procédure de traitement des plaintes et/ou réclamations sur le marché",
            "financier régional de l'UMOA.",
            "",
            "Conformément à ladite instruction, le traitement des différends entre la SGI et ses Clients se déroulera ainsi qu'il suit :",
            "",
            "Le Titulaire adressera sa plainte ou sa réclamation au service   commercial par tout moyen écrit permettant de justifier de sa date",
            "(courrier, courriel etc.). Les plaintes doivent porter sur des faits survenus dans un délai maximum d'un an.   Ledit département",
            "accusera réception de la plainte et la mettra immédiatement en traitement avec les organes internes compétents de la SGI.   Le",
            "Titulaire sera tenu informé par courriel du déroulement du traitement de sa plainte dans les cinq (5) jours ouvrables à compter de",
            "la date de la saisine. En tout état de cause, la SGI répondra aux demandes d'informations du Titulaire   sur le déroulement du",
            "traitement de sa plainte. Afin de faciliter les échanges, Le Titulaire consent à communiquer une adresse email lors de la transmission",
            "de sa réclamation ou plainte.",
            "",
            "La plainte ou réclamation sera traitée dans un délai maximum de dix (10) jours à compter de sa réception par le service susvisé. A",
            "l'expiration du délai sus indiqué, la SGI adressera, au Titulaire, un courrier ou un courriel, si Le Titulaire a choisi ce mode de",
            "communication. En cas de rejet ou refus de faire droit en totalité ou partiellement à la réclamation, la SGI indiquera au Titulaire",
            "qu'il a le droit de saisir l'association professionnelle des sociétés de gestion et d'intermédiation (APSGI).",
            "",
            "Si le litige persiste à l'issue de l'intervention de l'association professionnelle des sociétés de gestion et d'intermédiation (APSGI), le",
            "traitement du litige sera porté devant l'Autorité des marchés (AMF-UMOA) qui interviendra en qualité de médiateur ou de",
            "conciliateur, conformément à l'instruction n°50/2016.",
            "",
            "La partie insatisfaite à l'issue du traitement du litige par l'Autorité des marchés (AMF-UMOA) pourra saisir le tribunal compétent.",
            "",
            "Cette clause de règlement des litiges sera interprétée et appliquée conformément à l'instruction n°50/2016 et à toute autre",
            "réglementation pertinente en vigueur à la date de signature du contrat.",
            "",
        ]
        
        for line in litige_text:
            c.drawString(30*mm, y, line)
            y -= 4*mm
        
        # Article 30 : Élection de domicile
        y -= 2*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Article 30 : Élection de domicile")
        y -= 7*mm
        
        c.setFont("Helvetica", 8)
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
            "de première présentation de la lettre recommandée ou du courrier exprès telle qu'indiquée sur l'avis de réception. Les Parties",
            "conviennent que toute notification adressée à l'une des Parties à son adresse telle que prévue ci-dessus est réputée valable, régulière",
            "et opérante quand bien même le pli correspondant est retourné à l'autre Partie avec quelque mention que ce soit, telles que 'inconnu",
            "à l'adresse', 'parti sans laisser d'adresse', 'non retiré', 'locaux fermés', etc.",
            "",
        ]
        
        for line in legal_text_art30:
            c.drawString(30*mm, y, line)
            y -= 5*mm
        
        # Article 34 : Langue
        y -= 2*mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30*mm, y, "Article 34 : Langue")
        y -= 7*mm
        
        c.setFont("Helvetica", 8)
        legal_text_art34 = [
            "Le texte de la présente Convention est en français et, s'il est traduit dans une autre langue, seule la version française prévaudra.",
            "",
        ]
        
        for line in legal_text_art34:
            c.drawString(30*mm, y, line)
            y -= 4*mm
        
        # Fait à / Le
        y -= 8*mm
        c.setFont("Helvetica", 9)
        place = p21.get('place', 'Abidjan')
        date = self._format_date(p21.get('date', '.............................'))
        c.drawString(width/2 - 50*mm, y, f"Fait en deux exemplaires à {place}, le {date}")
        
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
        sig_y = y  # Sauvegarder la position Y pour les signatures
        c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        c.rect(120*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        
        # Afficher les signatures si présentes (base64 -> image)
        sig_titulaire = p21.get('signature_titulaire')
        sig_sgi = p21.get('signature_sgi') or p21.get('signature_gek')  # Compatibilité
        
        # Afficher la signature du titulaire
        if sig_titulaire:
            try:
                img = self._base64_to_image(sig_titulaire)
                if img:
                    # Dessiner l'image dans le rectangle (ajuster la taille)
                    c.drawImage(img, 32*mm, sig_y + 2*mm, width=56*mm, height=16*mm, 
                               preserveAspectRatio=True, mask='auto')
                else:
                    c.setFont("Helvetica", 8)
                    c.drawString(35*mm, sig_y + 8*mm, "[Signature présente]")
            except Exception as e:
                logger.error(f"Erreur affichage signature titulaire: {e}")
                c.setFont("Helvetica", 8)
                c.drawString(35*mm, sig_y + 8*mm, "[Erreur signature]")
        
        # Afficher la signature SGI
        if sig_sgi:
            try:
                img = self._base64_to_image(sig_sgi)
                if img:
                    # Dessiner l'image dans le rectangle (ajuster la taille)
                    c.drawImage(img, 122*mm, sig_y + 2*mm, width=56*mm, height=16*mm, 
                               preserveAspectRatio=True, mask='auto')
                else:
                    c.setFont("Helvetica", 8)
                    c.drawString(125*mm, sig_y + 8*mm, f"[Signature présente]")
            except Exception as e:
                logger.error(f"Erreur affichage signature SGI: {e}")
                c.setFont("Helvetica", 8)
                c.drawString(125*mm, sig_y + 8*mm, "[Erreur signature]")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    
    def _generate_page22(self, aor, annex_data: dict) -> BytesIO:
        """Génère la page 22 - Formulaire d'ouverture avec design exact"""
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p22 = annex_data.get('page22', {})
        
        # Titre centré
        c.setFont("Helvetica-Bold", 11)
        title = "Annexe 1 : Formulaire d'ouverture de compte-titres"
        title_width = c.stringWidth(title, "Helvetica-Bold", 11)
        c.drawString((width - title_width) / 2, height - 15*mm, title)
        
        y = height - 25*mm
        
        # Encadré IMPORTANT avec fond bleu
        important_box_y = y
        c.setFillColor(self.blue_header)
        c.rect(20*mm, important_box_y - 15*mm, width - 40*mm, 15*mm, fill=1, stroke=0)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(22*mm, important_box_y - 5*mm, "IMPORTANT : En cas de pluralité de titulaires (compte joint de titres, compte en indivision ou compte usufrui nue-propriété), merci de photocopier cette")
        c.drawString(22*mm, important_box_y - 9*mm, "page en autant d'exemplaires qu'il y a de co-titulaires du compte, de la compléter et de la joindre à votre envoi (un exemplaire par co-titulaire accompagné des")
        c.drawString(22*mm, important_box_y - 13*mm, "pièces justificatives).")
        
        c.setFillColor(self.black_text)
        y = important_box_y - 20*mm
        
        # Numéro de compte-titres avec bordure
        y = height - 50*mm
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(1.5)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=0, stroke=1)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        
        c.setFont("Helvetica", 9)
        account_number = p22.get('account_number', '...........................................................................')
        c.drawString(22*mm, y, f"Numéro de compte-titres : {account_number}")
        y -= 15*mm
        
        # TITULAIRE PERSONNE PHYSIQUE - Encadré bleu
        section_start_y = y
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(2)
        c.setFillColor(self.blue_header)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(22*mm, y - 1*mm, "TITULAIRE PERSONNE PHYSIQUE")
        
        c.setFillColor(self.black_text)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        y -= 12*mm
        
        # Cadre avec photo à droite
        photo_box_x = width - 50*mm
        photo_box_y = y
        c.rect(photo_box_x, photo_box_y - 35*mm, 30*mm, 40*mm, fill=0, stroke=1)
        
        # Ajouter la photo si disponible
        logger.info(f"Vérification photo - aor: {aor is not None}, hasattr photo: {hasattr(aor, 'photo') if aor else False}, photo value: {aor.photo if (aor and hasattr(aor, 'photo')) else 'N/A'}")
        
        # Essayer d'abord de charger depuis le fichier uploadé
        photo_img = None
        photo_source = None
        
        if aor and hasattr(aor, 'photo') and aor.photo:
            try:
                logger.info(f"Tentative de chargement depuis fichier: {aor.photo.name}")
                aor.photo.seek(0)
                photo_img = Image.open(aor.photo)
                photo_source = "file"
                logger.info(f"✅ Photo chargée depuis fichier: {photo_img.size[0]}x{photo_img.size[1]} pixels")
            except Exception as e:
                logger.warning(f"Impossible de charger depuis fichier: {e}")
        
        # Si pas de photo depuis fichier, essayer depuis base64 dans annex_data
        if not photo_img and annex_data:
            try:
                # Chercher la photo base64 dans annex_data
                photo_base64 = None
                
                # Vérifier dans page22
                if 'page22' in annex_data and 'photo_base64' in annex_data['page22']:
                    photo_base64 = annex_data['page22']['photo_base64']
                # Vérifier à la racine
                elif 'photo_base64' in annex_data:
                    photo_base64 = annex_data['photo_base64']
                
                if photo_base64:
                    logger.info("Tentative de chargement depuis base64...")
                    # Supprimer le préfixe data:image si présent
                    if ',' in photo_base64:
                        photo_base64 = photo_base64.split(',', 1)[1]
                    
                    # Décoder le base64
                    import base64
                    photo_bytes = base64.b64decode(photo_base64)
                    photo_buffer = BytesIO(photo_bytes)
                    photo_img = Image.open(photo_buffer)
                    photo_source = "base64"
                    logger.info(f"✅ Photo chargée depuis base64: {photo_img.size[0]}x{photo_img.size[1]} pixels")
            except Exception as e:
                logger.warning(f"Impossible de charger depuis base64: {e}")
        
        if photo_img:
            try:
                logger.info(f"Ajout de la photo sur page 22 (source: {photo_source})")
                
                # Calculer les dimensions pour ajuster dans le cadre (30mm x 40mm)
                photo_width_mm = 28  # Légère marge
                photo_height_mm = 38  # Légère marge
                
                # Convertir en points ReportLab
                photo_width_pt = photo_width_mm * mm
                photo_height_pt = photo_height_mm * mm
                
                # Calculer le ratio pour maintenir les proportions
                img_width, img_height = photo_img.size
                img_ratio = img_width / img_height
                box_ratio = photo_width_pt / photo_height_pt
                
                if img_ratio > box_ratio:
                    # Image plus large, ajuster sur la largeur
                    final_width = photo_width_pt
                    final_height = photo_width_pt / img_ratio
                else:
                    # Image plus haute, ajuster sur la hauteur
                    final_height = photo_height_pt
                    final_width = photo_height_pt * img_ratio
                
                logger.info(f"Dimensions finales: {final_width}pt x {final_height}pt")
                
                # Centrer la photo dans le cadre
                photo_x = photo_box_x + (30*mm - final_width) / 2
                photo_y = photo_box_y - 35*mm + (40*mm - final_height) / 2
                
                # Créer un ImageReader depuis PIL Image
                # Convertir PIL Image en buffer pour ImageReader
                img_buffer = BytesIO()
                photo_img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                photo_reader = ImageReader(img_buffer)
                
                # Dessiner la photo
                c.drawImage(photo_reader, photo_x, photo_y, width=final_width, height=final_height, preserveAspectRatio=True)
                
                logger.info(f"✅ Photo ajoutée sur l'annexe page 22 à la position ({photo_x}, {photo_y})")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'ajout de la photo sur page 22: {e}", exc_info=True)
                # Continuer sans la photo - le cadre vide sera visible
        else:
            logger.info("Aucune photo disponible pour la page 22")
        
        c.setFont("Helvetica", 8)
        # Civilité
        civility = p22.get('civility', 'Monsieur')
        c.drawString(22*mm, y, f"Civilité : {civility}")
        y -= 5*mm
        
        # Nom
        last_name = p22.get('last_name', '................................................................................................................................................................')
        c.drawString(22*mm, y, f"Nom : {last_name}")
        y -= 5*mm
        
        # Nom de jeune fille
        maiden_name = p22.get('maiden_name', '.....................................................................................................................................................................')
        c.drawString(22*mm, y, f"Nom de jeune fille (pour les femmes mariées) : {maiden_name}")
        y -= 5*mm
        
        # Prénom(s)
        first_names = p22.get('first_names', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Prénom(s) : {first_names}")
        y -= 5*mm
        
        # Date et lieu de naissance
        birth_date = self._format_date(p22.get('birth_date', '.............................'))
        birth_place = p22.get('birth_place', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Date de naissance (jj/mm/aaaa) : {birth_date}    Lieu de naissance : {birth_place}")
        y -= 5*mm
        
        # Nationalité
        nationality = p22.get('nationality', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Nationalité : {nationality}")
        y -= 5*mm
        
        # Type de pièce d'identité
        id_type = p22.get('id_type', '.............................')
        id_number = p22.get('id_number', '.............................')
        id_validity = self._format_date(p22.get('id_validity', '.................................'))
        c.drawString(22*mm, y, f"Type de pièce d'identité : {id_type}  Numéro : {id_number}  ...date de validité : {id_validity}")
        y -= 8*mm
        
        # TITULAIRE PERSONNE MORALE - Encadré bleu
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(2)
        c.setFillColor(self.blue_header)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(22*mm, y - 1*mm, "TITULAIRE PERSONNE MORALE")
        
        c.setFillColor(self.black_text)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        y -= 12*mm
        
        c.setFont("Helvetica", 8)
        company_name = p22.get('company_name', '.................................................................................................................................................................')
        rccm_number = p22.get('rccm_number', '.................................')
        c.drawString(22*mm, y, f"Nom de la société : {company_name}    Numéro RCCM : {rccm_number}")
        y -= 5*mm
        
        # Numéro Compte contribuable
        tax_number = p22.get('tax_number', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Numéro Compte contribuable : {tax_number}")
        y -= 5*mm
        
        # Représentant
        c.setFont("Helvetica-Bold", 8)
        c.drawString(22*mm, y, "Représenté par :")
        y -= 5*mm
        
        c.setFont("Helvetica", 8)
        rep_last_name = p22.get('rep_last_name', '.................................................................................................................................................................')
        rep_first_names = p22.get('rep_first_names', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Nom : {rep_last_name}    Prénom(s) : {rep_first_names}")
        y -= 5*mm
        
        # Date et lieu de naissance représentant
        rep_birth_date = self._format_date(p22.get('rep_birth_date', '.............................'))
        rep_birth_place = p22.get('rep_birth_place', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Date de naissance (jj/mm/aaaa) : {rep_birth_date}    Lieu de naissance : {rep_birth_place}")
        y -= 5*mm
        
        # Pièce d'identité représentant
        rep_id_type = p22.get('rep_id_type', '.............................')
        rep_id_number = p22.get('rep_id_number', '.............................')
        rep_id_validity = self._format_date(p22.get('rep_id_validity', '.................................'))
        c.drawString(22*mm, y, f"Titulaire de la pièce d'identité : {rep_id_type}  N° : {rep_id_number}  Valide jusqu'au : {rep_id_validity}")
        y -= 5*mm
        
        # Nationalité représentant
        rep_nationality = p22.get('rep_nationality', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Nationalité : {rep_nationality}")
        y -= 5*mm
        
        # Fonction
        rep_function = p22.get('rep_function', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Fonction : {rep_function}")
        y -= 8*mm
        
        # ADRESSE FISCALE DU TITULAIRE - Encadré bleu
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(2)
        c.setFillColor(self.blue_header)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(22*mm, y - 1*mm, "ADRESSE FISCALE DU TITULAIRE")
        
        c.setFillColor(self.black_text)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        y -= 12*mm
        
        c.setFont("Helvetica", 8)
        fiscal_address = p22.get('fiscal_address', '.................................................................................................................................................................')
        fiscal_building = p22.get('fiscal_building', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Résidence, Bâtiment : {fiscal_address}    N° de rue : {fiscal_building}")
        y -= 5*mm
        
        fiscal_postal_code = p22.get('fiscal_postal_code', '.............................')
        fiscal_city = p22.get('fiscal_city', '.................................................................................................................................................................')
        fiscal_country = p22.get('fiscal_country', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Code postal : {fiscal_postal_code}    Ville : {fiscal_city}    Pays : {fiscal_country}")
        y -= 8*mm
        
        # ADRESSE POSTALE DU TITULAIRE - Encadré bleu
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(2)
        c.setFillColor(self.blue_header)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(22*mm, y - 1*mm, "ADRESSE POSTALE DU TITULAIRE (si différente de l'adresse fiscale)")
        
        c.setFillColor(self.black_text)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        y -= 12*mm
        
        c.setFont("Helvetica", 8)
        postal_address = p22.get('postal_address', '.................................................................................................................................................................')
        postal_building = p22.get('postal_building', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Résidence, Bâtiment : {postal_address}    N° de rue : {postal_building}")
        y -= 5*mm
        
        postal_code = p22.get('postal_code', '.............................')
        postal_city = p22.get('postal_city', '.................................................................................................................................................................')
        postal_country = p22.get('postal_country', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Code postal : {postal_code}    Ville : {postal_city}    Pays : {postal_country}")
        y -= 8*mm
        
        # Cases à cocher avec bordure
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(1)
        c.rect(20*mm, y - 8*mm, width - 40*mm, 10*mm, fill=0, stroke=1)
        c.setStrokeColor(self.black_text)
        
        c.setFont("Helvetica", 8)
        is_fiscal_resident = p22.get('is_fiscal_resident', False)
        is_cedeao_member = p22.get('is_cedeao_member', False)
        is_outside_cedeao = p22.get('is_outside_cedeao', False)
        
        marker_fiscal = "☑" if is_fiscal_resident else "☐"
        marker_cedeao = "☑" if is_cedeao_member else "☐"
        marker_outside = "☑" if is_outside_cedeao else "☐"
        
        c.drawString(22*mm, y - 3*mm, f"{marker_fiscal} Résident fiscal ivoirien    {marker_cedeao} Membre de la CEDEAO    {marker_outside} Pays hors CEDEAO")
        y -= 12*mm
        
        # COORDONNÉES DU TITULAIRE - Encadré bleu
        c.setStrokeColor(self.blue_border)
        c.setLineWidth(2)
        c.setFillColor(self.blue_header)
        c.rect(20*mm, y - 5*mm, width - 40*mm, 8*mm, fill=1, stroke=1)
        
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(22*mm, y - 1*mm, "COORDONNÉES DU TITULAIRE")
        
        c.setFillColor(self.black_text)
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        y -= 12*mm
        
        c.setFont("Helvetica", 8)
        phone_portable = p22.get('phone_portable', '.................................................................................................................................................................')
        phone_domicile = p22.get('phone_domicile', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Tél Portable : {phone_portable}    Tél Domicile : {phone_domicile}")
        y -= 5*mm
        
        email = p22.get('email', '.................................................................................................................................................................')
        c.drawString(22*mm, y, f"Email : {email}")
        
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
        
        # Titre centré
        c.setFont("Helvetica-Bold", 11)
        title = "CARACTÉRISTIQUES DU COMPTE (cocher la case correspondante)"
        title_width = c.stringWidth(title, "Helvetica-Bold", 11)
        c.drawString((width - title_width) / 2, height - 15*mm, title)
        
        y = height - 30*mm
        
        # Section avec fond gris clair
        section_height = 70*mm
        c.setFillColor(self.gray_bg)
        c.rect(20*mm, y - section_height, width - 40*mm, section_height, fill=1, stroke=0)
        
        # Bordure noire autour de la section
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1.5)
        c.rect(20*mm, y - section_height, width - 40*mm, section_height, fill=0, stroke=1)
        
        c.setFillColor(self.black_text)
        c.setFont("Helvetica", 9)
        
        y -= 10*mm
        
        # Type de compte avec cases à cocher
        account_individual = p23.get('account_individual', True)
        account_joint = p23.get('account_joint', False)
        account_indivision = p23.get('account_indivision', False)
        account_usufruit = p23.get('account_usufruit', False)
        
        marker = "☑" if account_individual else "☐"
        c.drawString(25*mm, y, f"{marker} Compte individuel pleine propriété (cas général)")
        y -= 8*mm
        
        # Ligne de séparation
        c.setLineWidth(0.5)
        c.line(25*mm, y + 2*mm, width - 25*mm, y + 2*mm)
        y -= 3*mm
        
        marker = "☑" if account_joint else "☐"
        c.drawString(25*mm, y, f"{marker} Compte joint de Titres")
        y -= 5*mm
        
        # Titulaires A et B
        c.setFont("Helvetica", 8)
        titulaire_a_nom = p23.get('titulaire_a_nom', '.............................')
        titulaire_a_prenom = p23.get('titulaire_a_prenom', '.............................')
        titulaire_a_birth = self._format_date(p23.get('titulaire_a_birth', '.............................'))
        c.drawString(30*mm, y, f"Titulaire A : Nom : {titulaire_a_nom}    Prénoms : {titulaire_a_prenom}    Date de naissance : {titulaire_a_birth}")
        y -= 5*mm
        
        titulaire_b_nom = p23.get('titulaire_b_nom', '.............................')
        titulaire_b_prenom = p23.get('titulaire_b_prenom', '.............................')
        titulaire_b_birth = self._format_date(p23.get('titulaire_b_birth', '.............................'))
        c.drawString(30*mm, y, f"Titulaire B : Nom : {titulaire_b_nom}    Prénoms : {titulaire_b_prenom}    Date de naissance : {titulaire_b_birth}")
        y -= 8*mm
        
        # Ligne de séparation
        c.line(25*mm, y + 2*mm, width - 25*mm, y + 2*mm)
        y -= 3*mm
        
        c.setFont("Helvetica", 9)
        marker = "☑" if account_indivision else "☐"
        c.drawString(25*mm, y, f"{marker} Compte en indivision entre:")
        y -= 5*mm
        
        # Titulaires A, B, C, D pour indivision
        c.setFont("Helvetica", 8)
        for letter in ['A', 'B', 'C', 'D']:
            nom_key = f'titulaire_{letter.lower()}_nom'
            prenom_key = f'titulaire_{letter.lower()}_prenom'
            nom = p23.get(nom_key, '.............................')
            prenom = p23.get(prenom_key, '.............................')
            c.drawString(30*mm, y, f"Titulaire {letter} : Nom : {nom}    Prénoms : {prenom}")
            y -= 4*mm
        
        y -= 3*mm
        c.setFont("Helvetica", 8)
        designated_person = p23.get('designated_person_name', '.................................................................................................................................................................')
        c.drawString(25*mm, y, f"Nom et prénoms de la personne désignée pour faire fonctionner le compte : {designated_person}")
        y -= 8*mm
        
        # Déclaration avec bordure
        y -= 5*mm
        c.setStrokeColor(self.black_text)
        c.setLineWidth(1)
        declaration_height = 25*mm
        c.rect(20*mm, y - declaration_height, width - 40*mm, declaration_height, fill=0, stroke=1)
        
        y -= 5*mm
        c.setFont("Helvetica", 8)
        c.drawString(22*mm, y, "Par le présent, je déclare (nous déclarons) avoir pris connaissance et adhérer à l'intégralité des dispositions de la convention")
        y -= 4*mm
        c.drawString(22*mm, y, "d'ouverture de compte laquelle se compose du présent formulaire, ainsi que des conditions générales.")
        y -= 12*mm
        
        # Fait à / Le
        place = p23.get('place', 'Abidjan')
        date = self._format_date(p23.get('date', '.............................'))
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
        sig_y = y  # Sauvegarder la position Y
        c.rect(30*mm, y, 60*mm, 20*mm, stroke=1, fill=0)
        
        signature = p23.get('signature')
        if signature:
            try:
                img = self._base64_to_image(signature)
                if img:
                    # Dessiner l'image dans le rectangle
                    c.drawImage(img, 32*mm, sig_y + 2*mm, width=56*mm, height=16*mm, 
                               preserveAspectRatio=True, mask='auto')
                else:
                    c.setFont("Helvetica", 8)
                    c.drawString(35*mm, sig_y + 10*mm, "[Signature présente]")
            except Exception as e:
                logger.error(f"Erreur affichage signature page 23: {e}")
                c.setFont("Helvetica", 8)
                c.drawString(35*mm, sig_y + 10*mm, "[Erreur signature]")
        
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
        
        # Titre centré
        c.setFont("Helvetica-Bold", 12)
        title = "Annexe 4 : Formulaire de Procuration"
        title_width = c.stringWidth(title, "Helvetica-Bold", 12)
        c.drawString((width - title_width) / 2, height - 20*mm, title)
        
        y = height - 40*mm
        
        # Vérifier si procuration
        has_procuration = p26.get('has_procuration', False)
        
        if not has_procuration:
            c.setFont("Helvetica", 10)
            c.drawString(30*mm, y, "Pas de procuration demandée")
        else:
            # Section Je, soussigné(e)
            c.setFont("Helvetica", 10)
            c.drawString(20*mm, y, "Je, soussigné(e) :")
            y -= 10*mm
            
            # Civilité
            mandant_civility = p26.get('mandant_civility', 'Madame, Mademoiselle, Monsieur')
            c.setFont("Helvetica", 9)
            c.drawString(25*mm, y, f"Civilité : {mandant_civility}")
            y -= 6*mm
            
            # Nom
            mandant_name = p26.get('mandant_name', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Nom : {mandant_name}")
            y -= 6*mm
            
            # Prénom(s)
            mandant_first_names = p26.get('mandant_first_names', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Prénom(s) : {mandant_first_names}")
            y -= 6*mm
            
            # Adresse
            mandant_address = p26.get('mandant_address', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Adresse : {mandant_address}")
            y -= 6*mm
            
            # Code Postal, Ville, Pays
            mandant_postal = p26.get('mandant_postal', '.............................')
            mandant_city = p26.get('mandant_city', '.............................')
            mandant_country = p26.get('mandant_country', '.............................')
            c.drawString(25*mm, y, f"Code Postal : {mandant_postal}    Ville : {mandant_city}    Pays : {mandant_country}")
            y -= 8*mm
            
            # Titulaire du compte-titres
            account_number = p26.get('account_number', '.............................')
            sgi_name = p26.get('sgi_name', 'GEK CAPITAL')
            c.drawString(20*mm, y, f"Titulaire du compte-titres n° : {account_number} ouvert(s) dans les livres de {sgi_name}")
            y -= 10*mm
            
            # donne pouvoir à
            c.setFont("Helvetica-Bold", 10)
            c.drawString(20*mm, y, "donne pouvoir à :")
            y -= 10*mm
            
            # Civilité mandataire
            mandataire_civility = p26.get('mandataire_civility', 'Madame, Mademoiselle, Monsieur')
            c.setFont("Helvetica", 9)
            c.drawString(25*mm, y, f"Civilité : {mandataire_civility}")
            y -= 6*mm
            
            # Nom mandataire
            mandataire_name = p26.get('mandataire_name', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Nom : {mandataire_name}")
            y -= 6*mm
            
            # Prénom(s) mandataire
            mandataire_first_names = p26.get('mandataire_first_names', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Prénom(s) : {mandataire_first_names}")
            y -= 6*mm
            
            # Adresse mandataire
            mandataire_address = p26.get('mandataire_address', '.................................................................................................................................................................')
            c.drawString(25*mm, y, f"Adresse : {mandataire_address}")
            y -= 6*mm
            
            # Code Postal mandataire
            mandataire_postal = p26.get('mandataire_postal', '.............................')
            mandataire_city = p26.get('mandataire_city', '.............................')
            mandataire_country = p26.get('mandataire_country', '.............................')
            c.drawString(25*mm, y, f"Code Postal : {mandataire_postal}    Ville : {mandataire_city}    Pays : {mandataire_country}")
            y -= 10*mm
            
            # Texte de la procuration
            c.setFont("Helvetica", 9)
            c.drawString(20*mm, y, "dont la signature est reprise ci-dessous, afin d'effectuer en mon nom et pour mon compte toutes les opérations sur titres,")
            y -= 5*mm
            c.drawString(20*mm, y, "notamment pour procéder à l'achat et à la vente de titres.")
            y -= 10*mm
            
            c.drawString(20*mm, y, f"Par la présente, j'autorise donc {sgi_name}, à procéder à ces opérations conformément aux conditions générales de la")
            y -= 5*mm
            c.drawString(20*mm, y, "convention d'ouverture de compte signée par mes soins.")
            y -= 10*mm
            
            c.drawString(20*mm, y, f"La présente procuration restera valable jusqu'à dénonciation adressée par mes soins par lettre simple à {sgi_name},")
            y -= 5*mm
            c.drawString(20*mm, y, "sauf à considérer les dispositions légales en vigueur.")
            y -= 15*mm
            
            # Fait à / Le
            place = p26.get('place', '.............................')
            date = self._format_date(p26.get('date', '.............................'))
            c.setFont("Helvetica", 9)
            c.drawString(20*mm, y, f"Fait à {place}, le {date}")
            y -= 20*mm
            
            # Signatures côte à côte
            c.setFont("Helvetica-Bold", 10)
            c.drawString(30*mm, y, "Signature du mandant, précédée de la")
            c.drawString(120*mm, y, "Signature de la mandataire précédée de la")
            y -= 5*mm
            
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(30*mm, y, 'mention manuscrite "Bon pour pouvoir"')
            c.drawString(120*mm, y, 'mention manuscrite "Bon pour accord"')
            y -= 15*mm
            
            # Rectangles pour signatures
            c.setStrokeColor(self.black_text)
            c.setLineWidth(1)
            sig_y = y - 20*mm  # Position Y pour les signatures
            c.rect(30*mm, sig_y, 50*mm, 25*mm, fill=0, stroke=1)
            c.rect(120*mm, sig_y, 50*mm, 25*mm, fill=0, stroke=1)
            
            # Afficher les signatures si présentes
            sig_mandant = p26.get('signature_mandant')
            sig_mandataire = p26.get('signature_mandataire')
            
            # Signature du mandant
            if sig_mandant:
                try:
                    img = self._base64_to_image(sig_mandant)
                    if img:
                        c.drawImage(img, 32*mm, sig_y + 2*mm, width=46*mm, height=21*mm, 
                                   preserveAspectRatio=True, mask='auto')
                    else:
                        c.setFont("Helvetica", 8)
                        c.drawString(35*mm, sig_y + 12*mm, "[Signature présente]")
                except Exception as e:
                    logger.error(f"Erreur affichage signature mandant: {e}")
                    c.setFont("Helvetica", 8)
                    c.drawString(35*mm, sig_y + 12*mm, "[Erreur signature]")
            
            # Signature du mandataire
            if sig_mandataire:
                try:
                    img = self._base64_to_image(sig_mandataire)
                    if img:
                        c.drawImage(img, 122*mm, sig_y + 2*mm, width=46*mm, height=21*mm, 
                                   preserveAspectRatio=True, mask='auto')
                    else:
                        c.setFont("Helvetica", 8)
                        c.drawString(125*mm, sig_y + 12*mm, "[Signature présente]")
                except Exception as e:
                    logger.error(f"Erreur affichage signature mandataire: {e}")
                    c.setFont("Helvetica", 8)
                    c.drawString(125*mm, sig_y + 12*mm, "[Erreur signature]")
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

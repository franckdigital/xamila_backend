"""
NSIA FINANCE PDF Template with custom field mappings.
Different positions and layout from GEK CAPITAL.
"""
import os
from typing import Dict, Any
from django.conf import settings
from reportlab.lib.units import mm
from .base import BasePDFTemplate


class NSIATemplate(BasePDFTemplate):
    """
    PDF Template for NSIA FINANCE contract.
    Uses different field positions and layout compared to GEK CAPITAL.
    """
    
    def get_template_path(self) -> str:
        """Return path to NSIA FINANCE PDF template."""
        return os.path.join(
            settings.BASE_DIR,
            'contracts',
            'NSIA_Convention_Compte_Titres.pdf'
        )
    
    def fill_page(self, canvas_obj, page_index: int, context: Dict[str, Any]):
        """
        Fill specific pages with data for NSIA template.
        NSIA has a different page structure than GEK.
        
        Args:
            canvas_obj: ReportLab canvas object
            page_index: 0-based page index
            context: Dictionary with aor, annex, sgi data
        """
        annex = self.get_annex_data(context)
        aor = self.get_aor_data(context)
        
        # NSIA template structure (adjust based on actual template)
        # Page 1 (index 0): Cover page
        if page_index == 0:
            self._fill_page_1_cover(canvas_obj, annex, aor)
        
        # Page 15 (index 14): Identity form (example - adjust to actual NSIA page)
        elif page_index == 14:
            self._fill_page_15_identity(canvas_obj, annex, aor)
        
        # Page 16 (index 15): Contact and address
        elif page_index == 15:
            self._fill_page_16_contact(canvas_obj, annex, aor)
        
        # Page 18 (index 17): Account characteristics
        elif page_index == 17:
            self._fill_page_18_account(canvas_obj, annex, aor)
    
    def _fill_page_1_cover(self, c, annex: Dict, aor):
        """
        Fill NSIA cover page.
        NSIA uses different positions than GEK.
        """
        c.setFont("Helvetica-Bold", 12)
        
        # Client name (different position for NSIA)
        x, y = 40 * mm, 240 * mm
        self.draw_text(c, x, y, getattr(aor, 'full_name', ''))
        
        # Contact info
        y -= 10 * mm
        c.setFont("Helvetica", 10)
        p22 = annex.get('page22', {})
        email = self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        phone = self.safe_get(p22, 'phone') or getattr(aor, 'phone', '')
        
        self.draw_text(c, x, y, f"Email: {email}")
        y -= 6 * mm
        self.draw_text(c, x, y, f"Tél: {phone}")
        
        # Country
        y -= 6 * mm
        country = getattr(aor, 'country_of_residence', '')
        self.draw_text(c, x, y, f"Pays: {country}")
        
        # Date
        from django.utils import timezone
        y -= 10 * mm
        self.draw_text(c, x, y, f"Date: {timezone.now().strftime('%d/%m/%Y')}")
    
    def _fill_page_15_identity(self, c, annex: Dict, aor):
        """
        Fill NSIA identity page (page 15).
        Complete identity information with NSIA-specific positions.
        """
        p22 = annex.get('page22', {})
        
        # NSIA uses different layout - fields are more spread out
        
        # === PERSONNE PHYSIQUE ===
        if not self.safe_get(p22, 'is_company', 'false').lower() == 'true':
            # Civilité (NSIA format - different positions)
            civility = self.safe_get(p22, 'civility', 'Monsieur')
            y_civ = 255 * mm
            if civility == 'Monsieur':
                self.draw_checkbox(c, 30 * mm, y_civ, True)
            elif civility == 'Madame':
                self.draw_checkbox(c, 60 * mm, y_civ, True)
            elif civility == 'Mademoiselle':
                self.draw_checkbox(c, 90 * mm, y_civ, True)
            
            # Nom et prénoms (NSIA positions)
            parts = (getattr(aor, 'full_name', '') or '').split()
            nom = self.safe_get(p22, 'last_name') or (parts[-1] if parts else '')
            prenoms = self.safe_get(p22, 'first_names') or (' '.join(parts[:-1]) if len(parts) > 1 else '')
            
            self.draw_text(c, 40 * mm, 245 * mm, f"Nom: {nom}")
            self.draw_text(c, 40 * mm, 238 * mm, f"Prénoms: {prenoms}")
            
            # Nom de jeune fille
            maiden_name = self.safe_get(p22, 'maiden_name')
            if maiden_name:
                self.draw_text(c, 40 * mm, 231 * mm, f"Nom de jeune fille: {maiden_name}")
            
            # Date et lieu de naissance
            birth_date = self.format_date(self.safe_get(p22, 'birth_date'))
            birth_place = self.safe_get(p22, 'birth_place')
            self.draw_text(c, 40 * mm, 224 * mm, f"Né(e) le: {birth_date}")
            self.draw_text(c, 40 * mm, 217 * mm, f"À: {birth_place}")
            
            # Nationalité
            nationality = self.safe_get(p22, 'nationality') or getattr(aor, 'nationality', '')
            self.draw_text(c, 40 * mm, 210 * mm, f"Nationalité: {nationality}")
            
            # Pièce d'identité
            id_type = self.safe_get(p22, 'id_type', 'Carte d\'identité')
            id_number = self.safe_get(p22, 'id_number')
            id_valid = self.format_date(self.safe_get(p22, 'id_valid_until'))
            
            y_id = 200 * mm
            self.draw_text(c, 40 * mm, y_id, f"Type: {id_type}")
            self.draw_text(c, 40 * mm, y_id - 7 * mm, f"N°: {id_number}")
            self.draw_text(c, 40 * mm, y_id - 14 * mm, f"Valide jusqu'au: {id_valid}")
        
        # === PERSONNE MORALE ===
        else:
            company_name = self.safe_get(p22, 'company_name')
            company_ncc = self.safe_get(p22, 'company_ncc')
            company_rccm = self.safe_get(p22, 'company_rccm')
            
            self.draw_text(c, 40 * mm, 245 * mm, f"Raison sociale: {company_name}")
            self.draw_text(c, 40 * mm, 238 * mm, f"NCC: {company_ncc}")
            self.draw_text(c, 40 * mm, 231 * mm, f"RCCM: {company_rccm}")
            
            # Représentant
            rep_name = self.safe_get(p22, 'representative_name')
            rep_first = self.safe_get(p22, 'representative_first_names')
            rep_function = self.safe_get(p22, 'representative_function')
            
            y_rep = 220 * mm
            self.draw_text(c, 40 * mm, y_rep, f"Représenté par: {rep_name} {rep_first}")
            self.draw_text(c, 40 * mm, y_rep - 7 * mm, f"Fonction: {rep_function}")
        
        # === RESTRICTIONS ===
        is_minor = self.safe_get(p22, 'is_minor', 'false').lower() == 'true'
        is_protected = self.safe_get(p22, 'is_protected_adult', 'false').lower() == 'true'
        
        y_restrict = 170 * mm
        self.draw_checkbox(c, 40 * mm, y_restrict, is_minor)
        self.draw_text(c, 50 * mm, y_restrict, "Mineur")
        
        self.draw_checkbox(c, 40 * mm, y_restrict - 7 * mm, is_protected)
        self.draw_text(c, 50 * mm, y_restrict - 7 * mm, "Majeur protégé")
        
        # === REPRÉSENTANT LÉGAL (si applicable) ===
        if is_minor or is_protected:
            guardian_name = self.safe_get(p22, 'guardian_name')
            guardian_first = self.safe_get(p22, 'guardian_first_names')
            guardian_nationality = self.safe_get(p22, 'guardian_nationality')
            
            y_guard = 150 * mm
            self.draw_text(c, 40 * mm, y_guard, f"Représentant légal: {guardian_name} {guardian_first}")
            self.draw_text(c, 40 * mm, y_guard - 7 * mm, f"Nationalité: {guardian_nationality}")
    
    def _fill_page_16_contact(self, c, annex: Dict, aor):
        """
        Fill NSIA contact and address page (page 16).
        """
        p22 = annex.get('page22', {})
        
        # === ADRESSE FISCALE ===
        fiscal_address = self.safe_get(p22, 'fiscal_address')
        fiscal_street = self.safe_get(p22, 'fiscal_street_number')
        fiscal_postal = self.safe_get(p22, 'fiscal_postal_code')
        fiscal_city = self.safe_get(p22, 'fiscal_city')
        fiscal_country = self.safe_get(p22, 'fiscal_country') or getattr(aor, 'country_of_residence', '')
        
        y_fiscal = 240 * mm
        self.draw_text(c, 40 * mm, y_fiscal, "ADRESSE FISCALE")
        self.draw_text(c, 40 * mm, y_fiscal - 8 * mm, fiscal_address)
        self.draw_text(c, 40 * mm, y_fiscal - 15 * mm, f"{fiscal_street}, {fiscal_postal}")
        self.draw_text(c, 40 * mm, y_fiscal - 22 * mm, f"{fiscal_city}, {fiscal_country}")
        
        # Résidence fiscale
        is_ivory = self.safe_get(p22, 'is_fiscal_resident_ivory', 'false').lower() == 'true'
        is_cedeao = self.safe_get(p22, 'is_cedeao_member', 'false').lower() == 'true'
        is_outside = self.safe_get(p22, 'is_outside_cedeao', 'false').lower() == 'true'
        
        y_res = 200 * mm
        self.draw_checkbox(c, 40 * mm, y_res, is_ivory)
        self.draw_text(c, 50 * mm, y_res, "Résident fiscal ivoirien")
        
        self.draw_checkbox(c, 40 * mm, y_res - 7 * mm, is_cedeao)
        self.draw_text(c, 50 * mm, y_res - 7 * mm, "Membre CEDEAO")
        
        self.draw_checkbox(c, 40 * mm, y_res - 14 * mm, is_outside)
        self.draw_text(c, 50 * mm, y_res - 14 * mm, "Hors CEDEAO")
        
        # === ADRESSE POSTALE ===
        postal_address = self.safe_get(p22, 'postal_address')
        if postal_address:
            postal_city = self.safe_get(p22, 'postal_city')
            postal_country = self.safe_get(p22, 'postal_country')
            
            y_postal = 170 * mm
            self.draw_text(c, 40 * mm, y_postal, "ADRESSE POSTALE (si différente)")
            self.draw_text(c, 40 * mm, y_postal - 8 * mm, postal_address)
            self.draw_text(c, 40 * mm, y_postal - 15 * mm, f"{postal_city}, {postal_country}")
        
        # === COORDONNÉES ===
        phone = self.safe_get(p22, 'phone') or getattr(aor, 'phone', '')
        home_phone = self.safe_get(p22, 'home_phone')
        email = self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        
        y_contact = 130 * mm
        self.draw_text(c, 40 * mm, y_contact, "COORDONNÉES")
        self.draw_text(c, 40 * mm, y_contact - 8 * mm, f"Tél portable: {phone}")
        if home_phone:
            self.draw_text(c, 40 * mm, y_contact - 15 * mm, f"Tél domicile: {home_phone}")
        self.draw_text(c, 40 * mm, y_contact - 22 * mm, f"Email: {email}")
        
        # === CONVOCATION ÉLECTRONIQUE ===
        p23 = annex.get('page23', {})
        consent_email = self.safe_get(p23, 'consent_email', 'true').lower() == 'true'
        consent_electronic = self.safe_get(p22, 'consent_electronic', 'true').lower() == 'true'
        
        y_consent = 90 * mm
        self.draw_checkbox(c, 40 * mm, y_consent, consent_electronic)
        self.draw_text(c, 50 * mm, y_consent, "J'accepte la convocation électronique")
        
        self.draw_checkbox(c, 40 * mm, y_consent - 7 * mm, consent_email)
        self.draw_text(c, 50 * mm, y_consent - 7 * mm, "J'accepte les communications par email")
    
    def _fill_page_18_account(self, c, annex: Dict, aor):
        """
        Fill NSIA account characteristics page (page 18).
        """
        p26 = annex.get('page26', {})
        
        # === TYPE DE COMPTE ===
        account_individual = self.safe_get(p26, 'account_individual', 'true').lower() == 'true'
        account_joint = self.safe_get(p26, 'account_joint', 'false').lower() == 'true'
        account_indivision = self.safe_get(p26, 'account_indivision', 'false').lower() == 'true'
        
        y_type = 250 * mm
        self.draw_text(c, 40 * mm, y_type, "TYPE DE COMPTE")
        
        self.draw_checkbox(c, 40 * mm, y_type - 10 * mm, account_individual)
        self.draw_text(c, 50 * mm, y_type - 10 * mm, "Compte individuel")
        
        self.draw_checkbox(c, 40 * mm, y_type - 17 * mm, account_joint)
        self.draw_text(c, 50 * mm, y_type - 17 * mm, "Compte joint")
        
        self.draw_checkbox(c, 40 * mm, y_type - 24 * mm, account_indivision)
        self.draw_text(c, 50 * mm, y_type - 24 * mm, "Compte en indivision")
        
        # === CO-TITULAIRES (si compte joint) ===
        if account_joint:
            joint_a_name = self.safe_get(p26, 'joint_holder_a_name')
            joint_a_first = self.safe_get(p26, 'joint_holder_a_first_names')
            joint_b_name = self.safe_get(p26, 'joint_holder_b_name')
            joint_b_first = self.safe_get(p26, 'joint_holder_b_first_names')
            
            y_joint = 210 * mm
            self.draw_text(c, 40 * mm, y_joint, "CO-TITULAIRES")
            self.draw_text(c, 40 * mm, y_joint - 8 * mm, f"Titulaire A: {joint_a_name} {joint_a_first}")
            self.draw_text(c, 40 * mm, y_joint - 15 * mm, f"Titulaire B: {joint_b_name} {joint_b_first}")
        
        # === PERSONNE DÉSIGNÉE ===
        designated_name = self.safe_get(p26, 'designated_operator_name') or getattr(aor, 'full_name', '')
        y_desig = 180 * mm
        self.draw_text(c, 40 * mm, y_desig, "PERSONNE DÉSIGNÉE")
        self.draw_text(c, 40 * mm, y_desig - 8 * mm, designated_name)
        
        # === PROCURATION ===
        has_procuration = self.safe_get(p26, 'has_procuration', 'false').lower() == 'true'
        
        y_proc = 150 * mm
        self.draw_checkbox(c, 40 * mm, y_proc, has_procuration)
        self.draw_text(c, 50 * mm, y_proc, "Procuration")
        
        if has_procuration:
            mandataire_name = self.safe_get(p26, 'mandataire_name')
            mandataire_first = self.safe_get(p26, 'mandataire_first_names')
            
            self.draw_text(c, 40 * mm, y_proc - 10 * mm, f"Mandataire: {mandataire_name} {mandataire_first}")
        
        # === SIGNATURE ===
        place = self.safe_get(p26, 'place') or getattr(aor, 'country_of_residence', '')
        date = self.safe_get(p26, 'date')
        if not date:
            from django.utils import timezone
            date = timezone.now().strftime('%d/%m/%Y')
        else:
            date = self.format_date(date)
        
        y_sign = 60 * mm
        self.draw_text(c, 40 * mm, y_sign, f"Fait à {place}, le {date}")
        self.draw_text(c, 40 * mm, y_sign - 10 * mm, "Signature du titulaire:")

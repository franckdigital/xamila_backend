"""
NSIA FINANCE PDF Template with complete field mappings for all 95 annex fields.
Identical structure to GEK CAPITAL but uses NSIA PDF template.
"""
import os
from typing import Dict, Any
from django.conf import settings
from reportlab.lib.units import mm
from .base import BasePDFTemplate


class NSIATemplate(BasePDFTemplate):
    """
    PDF Template for NSIA FINANCE contract.
    Handles all 95 annex fields across pages 22, 23, and 26.
    Identical structure to GEK CAPITAL.
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
        Fill specific pages with data for NSIA FINANCE template.
        
        Args:
            canvas_obj: ReportLab canvas object
            page_index: 0-based page index
            context: Dictionary with aor, annex, sgi data
        """
        annex = self.get_annex_data(context)
        aor = self.get_aor_data(context)
        
        # Page 1 (index 0): Cover/Summary page
        if page_index == 0:
            self._fill_page_1_cover(canvas_obj, annex, aor)
        
        # Page 2 (index 1): Initial form page
        elif page_index == 1:
            self._fill_page_2_initial_form(canvas_obj, annex, aor)
        
        # Page 22 (index 21): Annexe 1 - Complete identity form
        elif page_index == 21:
            self._fill_page_22_annex1(canvas_obj, annex, aor)
        
        # Page 23 (index 22): Communication and restrictions
        elif page_index == 22:
            self._fill_page_23_communication(canvas_obj, annex, aor)
        
        # Page 26 (index 25): Account characteristics
        elif page_index == 25:
            self._fill_page_26_account_characteristics(canvas_obj, annex, aor)
    
    def _fill_page_1_cover(self, c, annex: Dict, aor):
        """Fill page 1 (cover/summary)."""
        c.setFont("Helvetica-Bold", 11)
        
        # Client name
        x, y = 25 * mm, 250 * mm
        self.draw_text(c, x, y, getattr(aor, 'full_name', ''))
        
        # Contact info
        y -= 7 * mm
        c.setFont("Helvetica", 10)
        p22 = annex.get('page22', {})
        email = self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        phone = self.safe_get(p22, 'phone') or getattr(aor, 'phone', '')
        self.draw_text(c, x, y, f"{email} | {phone}")
        
        # Country and nationality
        y -= 7 * mm
        country = getattr(aor, 'country_of_residence', '')
        nationality = self.safe_get(p22, 'nationality') or getattr(aor, 'nationality', '')
        self.draw_text(c, x, y, f"{country} / {nationality}")
        
        # Funding methods
        y -= 10 * mm
        methods = []
        if getattr(aor, 'funding_by_visa', False): methods.append('VISA')
        if getattr(aor, 'funding_by_mobile_money', False): methods.append('MOBILE MONEY')
        if getattr(aor, 'funding_by_bank_transfer', False): methods.append('VIREMENT')
        if getattr(aor, 'funding_by_intermediary', False): methods.append('INTERMEDIAIRE')
        if getattr(aor, 'funding_by_wu_mg_ria', False): methods.append('WU/MG/RIA')
        self.draw_text(c, x, y, f"Méthodes: {', '.join(methods) or '—'}")
        
        # Account type checkbox (individual by default)
        p26 = annex.get('page26', {})
        self.draw_checkbox(c, 17 * mm, 262 * mm, self.safe_get(p26, 'account_individual', 'true').lower() == 'true')
        
        # Signature
        self.draw_text(c, 35 * mm, 35 * mm, self.safe_get(p26, 'place') or country)
        
        from django.utils import timezone
        date = self.safe_get(p26, 'date') or timezone.now().strftime('%d/%m/%Y')
        self.draw_text(c, 120 * mm, 35 * mm, self.format_date(date))
    
    def _fill_page_2_initial_form(self, c, annex: Dict, aor):
        """Fill page 2 (initial form)."""
        p22 = annex.get('page22', {})
        
        # Name fields
        x1, y1 = 52 * mm, 238 * mm
        parts = (getattr(aor, 'full_name', '') or '').split()
        nom = parts[-1] if parts else ''
        prenoms = ' '.join(parts[:-1]) if len(parts) > 1 else ''
        
        # Override with annex data if available
        nom = self.safe_get(p22, 'last_name') or nom
        prenoms = self.safe_get(p22, 'first_names') or prenoms
        
        self.draw_text(c, x1, y1, nom)
        self.draw_text(c, 140 * mm, y1, prenoms)
        
        # Nationality
        y2 = 230 * mm
        nationality = self.safe_get(p22, 'nationality') or getattr(aor, 'nationality', '')
        self.draw_text(c, 52 * mm, y2, nationality)
        
        # Contact info
        self.draw_text(c, 30 * mm, 128 * mm, self.safe_get(p22, 'phone') or getattr(aor, 'phone', ''))
        self.draw_text(c, 30 * mm, 120 * mm, self.safe_get(p22, 'email') or getattr(aor, 'email', ''))
    
    def _fill_page_22_annex1(self, c, annex: Dict, aor):
        """
        Fill page 22 (Annexe 1) - Complete identity form with ALL 55 fields.
        This is the most detailed page with personal/company information.
        """
        p22 = annex.get('page22', {})
        
        # === SECTION 1: PERSONNE PHYSIQUE (11 fields) ===
        if not self.safe_get(p22, 'is_company', 'false').lower() == 'true':
            # Civilité (checkbox or text) - Position depends on template
            civility = self.safe_get(p22, 'civility', 'Monsieur')
            if civility == 'Monsieur':
                self.draw_checkbox(c, 20 * mm, 260 * mm, True)
            elif civility == 'Madame':
                self.draw_checkbox(c, 40 * mm, 260 * mm, True)
            elif civility == 'Mademoiselle':
                self.draw_checkbox(c, 60 * mm, 260 * mm, True)
            
            # Nom / Nom de jeune fille / Prénoms
            parts = (getattr(aor, 'full_name', '') or '').split()
            nom = self.safe_get(p22, 'last_name') or (parts[-1] if parts else '')
            prenoms = self.safe_get(p22, 'first_names') or (' '.join(parts[:-1]) if len(parts) > 1 else '')
            
            self.draw_text(c, 52 * mm, 238 * mm, nom)
            self.draw_text(c, 140 * mm, 238 * mm, prenoms)
            
            maiden_name = self.safe_get(p22, 'maiden_name')
            if maiden_name:
                self.draw_text(c, 52 * mm, 232 * mm, maiden_name)
            
            # Date et lieu de naissance
            birth_date = self.format_date(self.safe_get(p22, 'birth_date'))
            birth_place = self.safe_get(p22, 'birth_place')
            self.draw_text(c, 30 * mm, 225 * mm, birth_date)
            self.draw_text(c, 80 * mm, 225 * mm, birth_place)
            
            # Nationalité
            nationality = self.safe_get(p22, 'nationality') or getattr(aor, 'nationality', '')
            self.draw_text(c, 52 * mm, 230 * mm, nationality)
            
            # Pièce d'identité
            id_type = self.safe_get(p22, 'id_type', 'Carte d\'identité')
            id_number = self.safe_get(p22, 'id_number')
            id_valid = self.format_date(self.safe_get(p22, 'id_valid_until'))
            
            # Type de pièce (checkboxes)
            if 'carte' in id_type.lower():
                self.draw_checkbox(c, 20 * mm, 218 * mm, True)
            elif 'passeport' in id_type.lower():
                self.draw_checkbox(c, 60 * mm, 218 * mm, True)
            elif 'permis' in id_type.lower():
                self.draw_checkbox(c, 100 * mm, 218 * mm, True)
            
            self.draw_text(c, 30 * mm, 212 * mm, id_number)
            self.draw_text(c, 100 * mm, 212 * mm, id_valid)
        
        # === SECTION 2: PERSONNE MORALE (10 fields) ===
        else:
            company_name = self.safe_get(p22, 'company_name')
            company_ncc = self.safe_get(p22, 'company_ncc')
            company_rccm = self.safe_get(p22, 'company_rccm')
            
            self.draw_text(c, 30 * mm, 250 * mm, company_name)
            self.draw_text(c, 30 * mm, 244 * mm, f"NCC: {company_ncc}")
            self.draw_text(c, 100 * mm, 244 * mm, f"RCCM: {company_rccm}")
            
            # Représentant légal
            rep_name = self.safe_get(p22, 'representative_name')
            rep_first = self.safe_get(p22, 'representative_first_names')
            rep_birth_date = self.format_date(self.safe_get(p22, 'representative_birth_date'))
            rep_birth_place = self.safe_get(p22, 'representative_birth_place')
            rep_nationality = self.safe_get(p22, 'representative_nationality')
            rep_function = self.safe_get(p22, 'representative_function')
            
            self.draw_text(c, 30 * mm, 235 * mm, f"{rep_name} {rep_first}")
            self.draw_text(c, 30 * mm, 230 * mm, f"Né(e) le {rep_birth_date} à {rep_birth_place}")
            self.draw_text(c, 30 * mm, 225 * mm, f"Nationalité: {rep_nationality}")
            self.draw_text(c, 30 * mm, 220 * mm, f"Fonction: {rep_function}")
        
        # === SECTION 3: ADRESSE FISCALE (8 fields) ===
        fiscal_address = self.safe_get(p22, 'fiscal_address')
        fiscal_street = self.safe_get(p22, 'fiscal_street_number')
        fiscal_postal = self.safe_get(p22, 'fiscal_postal_code')
        fiscal_city = self.safe_get(p22, 'fiscal_city')
        fiscal_country = self.safe_get(p22, 'fiscal_country') or getattr(aor, 'country_of_residence', '')
        
        y_fiscal = 195 * mm
        self.draw_text(c, 30 * mm, y_fiscal, fiscal_address)
        self.draw_text(c, 30 * mm, y_fiscal - 5 * mm, f"{fiscal_street} - {fiscal_postal}")
        self.draw_text(c, 30 * mm, y_fiscal - 10 * mm, fiscal_city)
        self.draw_text(c, 30 * mm, 176 * mm, fiscal_country)
        
        # Résidence fiscale (checkboxes)
        is_ivory = self.safe_get(p22, 'is_fiscal_resident_ivory', 'false').lower() == 'true'
        is_cedeao = self.safe_get(p22, 'is_cedeao_member', 'false').lower() == 'true'
        is_outside = self.safe_get(p22, 'is_outside_cedeao', 'false').lower() == 'true'
        
        self.draw_checkbox(c, 20 * mm, 170 * mm, is_ivory)
        self.draw_checkbox(c, 70 * mm, 170 * mm, is_cedeao)
        self.draw_checkbox(c, 120 * mm, 170 * mm, is_outside)
        
        # === SECTION 4: ADRESSE POSTALE (5 fields) ===
        postal_address = self.safe_get(p22, 'postal_address')
        if postal_address:  # Only if different from fiscal
            postal_door = self.safe_get(p22, 'postal_door_number')
            postal_code = self.safe_get(p22, 'postal_code')
            postal_city = self.safe_get(p22, 'postal_city')
            postal_country = self.safe_get(p22, 'postal_country')
            
            y_postal = 155 * mm
            self.draw_text(c, 30 * mm, y_postal, postal_address)
            self.draw_text(c, 30 * mm, y_postal - 5 * mm, f"Porte {postal_door} - {postal_code}")
            self.draw_text(c, 30 * mm, y_postal - 10 * mm, f"{postal_city}, {postal_country}")
        
        # === SECTION 5: COORDONNÉES (4 fields) ===
        phone = self.safe_get(p22, 'phone') or getattr(aor, 'phone', '')
        home_phone = self.safe_get(p22, 'home_phone')
        email = self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        email_confirm = self.safe_get(p22, 'email_confirm')
        
        self.draw_text(c, 30 * mm, 128 * mm, phone)
        self.draw_text(c, 120 * mm, 128 * mm, home_phone)
        self.draw_text(c, 30 * mm, 120 * mm, email)
        
        # === SECTION 6: RESTRICTIONS (6 fields) ===
        is_minor = self.safe_get(p22, 'is_minor', 'false').lower() == 'true'
        minor_legal = self.safe_get(p22, 'minor_legal_admin', 'false').lower() == 'true'
        minor_tutelle = self.safe_get(p22, 'minor_tutelle', 'false').lower() == 'true'
        is_protected = self.safe_get(p22, 'is_protected_adult', 'false').lower() == 'true'
        protected_curatelle = self.safe_get(p22, 'protected_curatelle', 'false').lower() == 'true'
        protected_tutelle = self.safe_get(p22, 'protected_tutelle', 'false').lower() == 'true'
        
        y_restrict = 105 * mm
        self.draw_checkbox(c, 20 * mm, y_restrict, is_minor)
        if is_minor:
            self.draw_checkbox(c, 40 * mm, y_restrict - 5 * mm, minor_legal)
            self.draw_checkbox(c, 80 * mm, y_restrict - 5 * mm, minor_tutelle)
        
        self.draw_checkbox(c, 20 * mm, y_restrict - 12 * mm, is_protected)
        if is_protected:
            self.draw_checkbox(c, 40 * mm, y_restrict - 17 * mm, protected_curatelle)
            self.draw_checkbox(c, 80 * mm, y_restrict - 17 * mm, protected_tutelle)
        
        # === SECTION 7: REPRÉSENTANT LÉGAL (9 fields) ===
        if is_minor or is_protected:
            guardian_name = self.safe_get(p22, 'guardian_name')
            guardian_first = self.safe_get(p22, 'guardian_first_names')
            guardian_birth_date = self.format_date(self.safe_get(p22, 'guardian_birth_date'))
            guardian_birth_place = self.safe_get(p22, 'guardian_birth_place')
            guardian_nationality = self.safe_get(p22, 'guardian_nationality')
            guardian_geo = self.safe_get(p22, 'guardian_geo_address')
            guardian_postal = self.safe_get(p22, 'guardian_postal_address')
            guardian_city = self.safe_get(p22, 'guardian_city')
            guardian_country = self.safe_get(p22, 'guardian_country')
            
            y_guard = 75 * mm
            self.draw_text(c, 30 * mm, y_guard, f"{guardian_name} {guardian_first}")
            self.draw_text(c, 30 * mm, y_guard - 5 * mm, f"Né(e) le {guardian_birth_date} à {guardian_birth_place}")
            self.draw_text(c, 30 * mm, y_guard - 10 * mm, f"Nationalité: {guardian_nationality}")
            self.draw_text(c, 30 * mm, y_guard - 15 * mm, guardian_geo)
            self.draw_text(c, 30 * mm, y_guard - 20 * mm, f"{guardian_postal}, {guardian_city}, {guardian_country}")
        
        # === SECTION 8: CONVOCATION ÉLECTRONIQUE (2 fields) ===
        consent_electronic = self.safe_get(p22, 'consent_electronic', 'true').lower() == 'true'
        consent_docs = self.safe_get(p22, 'consent_electronic_docs', 'true').lower() == 'true'
        
        self.draw_checkbox(c, 20 * mm, 45 * mm, consent_electronic)
        self.draw_checkbox(c, 20 * mm, 38 * mm, consent_docs)
    
    def _fill_page_23_communication(self, c, annex: Dict, aor):
        """
        Fill page 23 - Communication and restrictions (2 fields).
        """
        p23 = annex.get('page23', {})
        p22 = annex.get('page22', {})
        
        # Email consent checkbox
        consent_email = self.safe_get(p23, 'consent_email', 'true').lower() == 'true'
        self.draw_checkbox(c, 26 * mm, 60 * mm, consent_email)
        
        # Email address (use p23 email or fallback to p22/aor)
        email = self.safe_get(p23, 'email') or self.safe_get(p22, 'email') or getattr(aor, 'email', '')
        self.draw_text(c, 30 * mm, 56 * mm, email)
    
    def _fill_page_26_account_characteristics(self, c, annex: Dict, aor):
        """
        Fill page 26 (Annexe 4) - Account characteristics and procuration (38 fields).
        """
        p26 = annex.get('page26', {})
        
        # === SECTION 1: TYPE DE COMPTE (19 fields) ===
        
        # Account type checkboxes
        account_individual = self.safe_get(p26, 'account_individual', 'true').lower() == 'true'
        account_joint = self.safe_get(p26, 'account_joint', 'false').lower() == 'true'
        account_indivision = self.safe_get(p26, 'account_indivision', 'false').lower() == 'true'
        
        self.draw_checkbox(c, 17 * mm, 262 * mm, account_individual)
        self.draw_checkbox(c, 17 * mm, 255 * mm, account_joint)
        self.draw_checkbox(c, 17 * mm, 248 * mm, account_indivision)
        
        # Compte joint (7 fields)
        if account_joint:
            joint_a_name = self.safe_get(p26, 'joint_holder_a_name')
            joint_a_first = self.safe_get(p26, 'joint_holder_a_first_names')
            joint_a_birth = self.format_date(self.safe_get(p26, 'joint_holder_a_birth_date'))
            joint_b_name = self.safe_get(p26, 'joint_holder_b_name')
            joint_b_first = self.safe_get(p26, 'joint_holder_b_first_names')
            joint_b_birth = self.format_date(self.safe_get(p26, 'joint_holder_b_birth_date'))
            
            y_joint = 250 * mm
            self.draw_text(c, 40 * mm, y_joint, f"A: {joint_a_name} {joint_a_first} ({joint_a_birth})")
            self.draw_text(c, 40 * mm, y_joint - 5 * mm, f"B: {joint_b_name} {joint_b_first} ({joint_b_birth})")
        
        # Compte indivision (9 fields)
        if account_indivision:
            holders = []
            for letter in ['a', 'b', 'c', 'd']:
                name = self.safe_get(p26, f'indivision_holder_{letter}_name')
                first = self.safe_get(p26, f'indivision_holder_{letter}_first_names')
                if name:
                    holders.append(f"{name} {first}")
            
            y_indiv = 243 * mm
            for i, holder in enumerate(holders):
                self.draw_text(c, 40 * mm, y_indiv - (i * 5 * mm), f"{chr(65+i)}: {holder}")
        
        # === SECTION 2: PERSONNE DÉSIGNÉE (1 field) ===
        designated_name = self.safe_get(p26, 'designated_operator_name') or getattr(aor, 'full_name', '')
        self.draw_text(c, 30 * mm, 205 * mm, designated_name)
        
        # === SECTION 3: SIGNATURE (2 fields) ===
        place = self.safe_get(p26, 'place') or getattr(aor, 'country_of_residence', '')
        date = self.safe_get(p26, 'date')
        if not date:
            from django.utils import timezone
            date = timezone.now().strftime('%d/%m/%Y')
        else:
            date = self.format_date(date)
        
        self.draw_text(c, 35 * mm, 35 * mm, place)
        self.draw_text(c, 120 * mm, 35 * mm, date)
        
        # === SECTION 4: PROCURATION (17 fields) ===
        has_procuration = self.safe_get(p26, 'has_procuration', 'false').lower() == 'true'
        
        if has_procuration:
            # Mandant (8 fields)
            mandant_civility = self.safe_get(p26, 'mandant_civility', 'Monsieur')
            mandant_name = self.safe_get(p26, 'mandant_name')
            mandant_first = self.safe_get(p26, 'mandant_first_names')
            mandant_address = self.safe_get(p26, 'mandant_address')
            mandant_postal = self.safe_get(p26, 'mandant_postal_code')
            mandant_city = self.safe_get(p26, 'mandant_city')
            mandant_country = self.safe_get(p26, 'mandant_country')
            account_number = self.safe_get(p26, 'account_number')
            
            y_mandant = 180 * mm
            self.draw_text(c, 30 * mm, y_mandant, f"{mandant_civility} {mandant_name} {mandant_first}")
            self.draw_text(c, 30 * mm, y_mandant - 5 * mm, mandant_address)
            self.draw_text(c, 30 * mm, y_mandant - 10 * mm, f"{mandant_postal} {mandant_city}, {mandant_country}")
            self.draw_text(c, 30 * mm, y_mandant - 15 * mm, f"Compte n°: {account_number}")
            
            # Mandataire (7 fields)
            mandataire_civility = self.safe_get(p26, 'mandataire_civility', 'Monsieur')
            mandataire_name = self.safe_get(p26, 'mandataire_name')
            mandataire_first = self.safe_get(p26, 'mandataire_first_names')
            mandataire_address = self.safe_get(p26, 'mandataire_address')
            mandataire_postal = self.safe_get(p26, 'mandataire_postal_code')
            mandataire_city = self.safe_get(p26, 'mandataire_city')
            mandataire_country = self.safe_get(p26, 'mandataire_country')
            
            y_mandataire = 145 * mm
            self.draw_text(c, 30 * mm, y_mandataire, f"{mandataire_civility} {mandataire_name} {mandataire_first}")
            self.draw_text(c, 30 * mm, y_mandataire - 5 * mm, mandataire_address)
            self.draw_text(c, 30 * mm, y_mandataire - 10 * mm, f"{mandataire_postal} {mandataire_city}, {mandataire_country}")
            
            # Signature procuration (2 fields)
            proc_place = self.safe_get(p26, 'procuration_place')
            proc_date = self.format_date(self.safe_get(p26, 'procuration_date'))
            
            self.draw_text(c, 30 * mm, 110 * mm, f"Fait à {proc_place}, le {proc_date}")

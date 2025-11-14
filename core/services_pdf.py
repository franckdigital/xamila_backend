from io import BytesIO
import logging
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from decimal import Decimal
from django.utils.text import slugify

try:
    # Prefer WeasyPrint for HTML->PDF
    from weasyprint import HTML, CSS  # type: ignore
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

# Optional template-based generation dependencies
try:
    from reportlab.pdfgen import canvas  # type: ignore
    from reportlab.lib.pagesizes import A4  # type: ignore
    from reportlab.lib.units import mm  # type: ignore
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

try:
    # pypdf is the new PyPDF2
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except Exception:
    try:
        from PyPDF2 import PdfReader, PdfWriter  # type: ignore
        PYPDF_AVAILABLE = True
    except Exception:
        PYPDF_AVAILABLE = False

from .models import SGI, User
from .models_sgi import AccountOpeningRequest, SGIAccountTerms


class ContractPDFService:
    """
    Génère un PDF de convention d'ouverture de compte-titres prérempli
    à partir des infos Client (AccountOpeningRequest), SGI et SGIAccountTerms.
    """

    def build_context(self, aor: AccountOpeningRequest):
        sgi = aor.sgi
        terms = getattr(sgi, 'account_terms', None) if sgi else None
        client = aor.customer

        context = {
            'generated_at': timezone.now(),
            'sgi': sgi,
            'terms': terms,
            'aor': aor,
            'client': client,
            'client_profile': getattr(client, 'investment_profile', None),
        }
        # Keep last context for template-based generator
        try:
            self._last_ctx = context
        except Exception:
            pass
        return context

    def render_html(self, context: dict) -> str:
        """Rendu du HTML en essayant d'abord le template dédié SGI puis un template par défaut.
        Fallback final: HTML inline minimaliste.
        """
        sgi = context.get('sgi')
        terms = context.get('terms')
        aor = context.get('aor')
        client_profile = context.get('client_profile')

        # 1) Template dédié par SGI
        if sgi:
            sgi_slug = slugify(sgi.name or 'sgi')
            candidate = f"contracts/{sgi_slug}/contract.html"
            try:
                return render_to_string(candidate, context)
            except TemplateDoesNotExist:
                pass

        # 2) Template par défaut
        try:
            return render_to_string("contracts/default/contract.html", context)
        except TemplateDoesNotExist:
            pass

        # 3) Fallback inline
        html = f"""
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <style>
    body {{ font-family: DejaVu Sans, Arial, sans-serif; font-size: 12px; color: #222; }}
    h1, h2, h3 {{ margin: 0; padding: 0; }}
    .section {{ margin: 16px 0; }}
    .box {{ border: 1px solid #ccc; padding: 12px; border-radius: 6px; margin-bottom: 10px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border: 1px solid #ddd; padding: 6px; vertical-align: top; }}
    .muted {{ color: #666; }}
  </style>
</head>
<body>
  <h1>Convention d'ouverture de compte-titres</h1>
  <div class="muted">Généré le {context['generated_at'].strftime('%d/%m/%Y %H:%M')}</div>

  <div class="section box">
    <h2>SGI</h2>
    <p><strong>Nom:</strong> {sgi.name if sgi else 'N/A'}</p>
    <p><strong>Adresse:</strong> {sgi.address if sgi else 'N/A'}</p>
    <p><strong>Manager:</strong> {sgi.manager_name if sgi else 'N/A'} ({sgi.manager_email if sgi else ''})</p>
  </div>

  <div class="section box">
    <h2>Client</h2>
    <p><strong>Nom:</strong> {aor.full_name}</p>
    <p><strong>Email:</strong> {aor.email}</p>
    <p><strong>Téléphone:</strong> {aor.phone}</p>
    <p><strong>Pays résidence / Nationalité:</strong> {aor.country_of_residence} / {aor.nationality}</p>
  </div>

  <div class="section box">
    <h2>Préférences d'ouverture</h2>
    <table>
      <tr><th>Ouverture 100% digitale</th><td>{'Oui' if aor.wants_digital_opening else 'Non'}</td></tr>
      <tr><th>En personne</th><td>{'Oui' if aor.wants_in_person_opening else 'Non'}</td></tr>
      <tr><th>Montant minimum disponible</th><td>{aor.available_minimum_amount or ''}</td></tr>
      <tr><th>SGI 100% digitale</th><td>{'Oui' if aor.wants_100_percent_digital_sgi else 'Non'}</td></tr>
      <tr><th>Méthodes d'alimentation</th><td>
        VISA: {'Oui' if aor.funding_by_visa else 'Non'} | 
        Mobile Money: {'Oui' if aor.funding_by_mobile_money else 'Non'} | 
        Virement: {'Oui' if aor.funding_by_bank_transfer else 'Non'} | 
        Intermédiaire: {'Oui' if aor.funding_by_intermediary else 'Non'} | 
        WU/MG/Ria: {'Oui' if aor.funding_by_wu_mg_ria else 'Non'}
      </td></tr>
      <tr><th>Sources de revenus</th><td>{aor.sources_of_income}</td></tr>
      <tr><th>Profil investisseur</th><td>{aor.investor_profile}</td></tr>
    </table>
  </div>

  <div class="section box">
    <h2>Conditions SGI</h2>
    <table>
      <tr><th>Pays</th><td>{terms.country if terms else ''}</td></tr>
      <tr><th>Ouverture digitale</th><td>{'Oui' if (terms and terms.is_digital_opening) else 'Non'}</td></tr>
      <tr><th>Montant minimum</th><td>{terms.minimum_amount_value if (terms and terms.has_minimum_amount) else 'Non'}</td></tr>
      <tr><th>Frais d'ouverture</th><td>{terms.opening_fees_amount if (terms and terms.has_opening_fees) else 'Non'}</td></tr>
      <tr><th>Frais de garde</th><td>{terms.custody_fees if terms else ''}</td></tr>
      <tr><th>Frais de tenue de compte</th><td>{terms.account_maintenance_fees if terms else ''}</td></tr>
      <tr><th>Méthodes de rachat</th><td>{', '.join(terms.redemption_methods) if (terms and terms.redemption_methods) else ''}</td></tr>
    </table>
  </div>

  <div class="section">
    <p class="muted">Ce document est généré automatiquement par Xamila à partir des informations fournies par le client et la SGI sélectionnée.</p>
  </div>
</body>
</html>
        """
        return html

    def _maybe_get_template_path(self, sgi) -> str | None:
        """Resolve a base PDF template path, either per SGI or default from settings.
        Settings candidates (first found wins):
          - SGI-specific mapping: settings.CONTRACT_TEMPLATES_BY_SGI = { 'GEK': '/path/to/gek.pdf', ... }
          - Global default: settings.DEFAULT_CONTRACT_TEMPLATE_PDF
        """
        # Per-SGI mapping by exact name key
        try:
            mapping = getattr(settings, 'CONTRACT_TEMPLATES_BY_SGI', {}) or {}
            if sgi and sgi.name in mapping:
                return mapping[sgi.name]
        except Exception:
            pass
        # Global default
        try:
            default_path = getattr(settings, 'DEFAULT_CONTRACT_TEMPLATE_PDF', None)
            return default_path
        except Exception:
            return None

    def _generate_from_template(self, context: dict) -> bytes | None:
        """Generate a PDF by overlaying text on a base template using reportlab + pypdf.
        Returns PDF bytes or None if not possible.
        """
        if not (REPORTLAB_AVAILABLE and PYPDF_AVAILABLE):
            return None
        sgi = context.get('sgi')
        aor: AccountOpeningRequest = context.get('aor')
        client = context.get('client')
        template_path = self._maybe_get_template_path(sgi)
        if not template_path:
            return None
        try:
            reader = PdfReader(template_path)
            writer = PdfWriter()

            def draw_checkbox(cvs, x, y, checked):
                size = 4 * mm
                cvs.rect(x, y, size, size, stroke=1, fill=0)
                if checked:
                    cvs.line(x, y, x + size, y + size)
                    cvs.line(x, y + size, x + size, y)

            overlays = []
            pages_count = len(reader.pages)
            for page_index in range(pages_count):
                ov = BytesIO()
                c = canvas.Canvas(ov, pagesize=A4)
                c.setFont("Helvetica", 10)

                if sgi and (sgi.name or '').strip().upper() in ('GEK', 'GEK CAPITAL', 'GEK CAPITAL SA'):
                    # Page 1 (cover/summary) – keep for context; main dynamic pages are 22, 23, 26
                    if page_index == 0:
                        x = 25 * mm
                        y = 250 * mm
                        c.setFont("Helvetica-Bold", 11)
                        c.drawString(x, y, f"{aor.full_name}")
                        y -= 7 * mm
                        c.setFont("Helvetica", 10)
                        c.drawString(x, y, f"{aor.email} | {aor.phone}")
                        y -= 7 * mm
                        c.drawString(x, y, f"{aor.country_of_residence} / {aor.nationality}")
                        y -= 10 * mm
                        m = []
                        if aor.funding_by_visa: m.append('VISA')
                        if aor.funding_by_mobile_money: m.append('MOBILE MONEY')
                        if aor.funding_by_bank_transfer: m.append('VIREMENT')
                        if aor.funding_by_intermediary: m.append('INTERMEDIAIRE')
                        if aor.funding_by_wu_mg_ria: m.append('WU/MG/RIA')
                        c.drawString(x, y, f"Méthodes d'alimentation: {', '.join(m) or '—'}")
                        # Compte individuel par défaut
                        draw_checkbox(c, 17 * mm, 262 * mm, True)
                        # Fait à / le
                        c.drawString(35 * mm, 35 * mm, aor.country_of_residence or '')
                        try:
                            from django.utils import timezone
                            c.drawString(120 * mm, 35 * mm, timezone.now().strftime('%d/%m/%Y'))
                        except Exception:
                            pass
                    # Annexe 1 – formulaire (likely early page); we keep this minimal
                    elif page_index == 1:
                        x1 = 52 * mm
                        y1 = 238 * mm
                        parts = (aor.full_name or '').split()
                        nom = parts[-1] if parts else ''
                        prenoms = ' '.join(parts[:-1]) if len(parts) > 1 else ''
                        c.drawString(x1, y1, nom)
                        c.drawString(140 * mm, y1, prenoms)
                        y2 = 230 * mm
                        c.drawString(52 * mm, y2, aor.nationality or '')
                        # Email / Téléphones
                        c.drawString(30 * mm, 128 * mm, aor.phone or '')
                        c.drawString(120 * mm, 128 * mm, '')
                        c.drawString(30 * mm, 120 * mm, aor.email or '')

                    # === GEK dynamic pages ===
                    # Page 22 (0-based 21): 'Annexe 1' section with identity and contact
                    elif page_index == 21:
                        # Basic identity fields
                        parts = (aor.full_name or '').split()
                        nom = parts[-1] if parts else ''
                        prenoms = ' '.join(parts[:-1]) if len(parts) > 1 else ''
                        # Nom / Prénoms (top area)
                        c.drawString(52 * mm, 238 * mm, nom)
                        c.drawString(140 * mm, 238 * mm, prenoms)
                        # Nationalité
                        c.drawString(52 * mm, 230 * mm, aor.nationality or '')
                        # Adresse fiscale (we only have country; placing country and phone/email lower)
                        c.drawString(30 * mm, 176 * mm, aor.country_of_residence or '')
                        # Coordonnées du titulaire
                        c.drawString(30 * mm, 128 * mm, aor.phone or '')  # Tel Portable
                        c.drawString(120 * mm, 128 * mm, '')               # Tel Domicile (unknown)
                        c.drawString(30 * mm, 120 * mm, aor.email or '')   # Email

                    # Page 23 (0-based 22): Restrictions éventuelles & coordonnées représentant, and consent email
                    elif page_index == 22:
                        # We don't know restrictions; leave unchecked. Fill coordinates of the titulaire again near the bottom if available
                        # Email consent section – pre-check opting into electronic communication
                        draw_checkbox(c, 26 * mm, 60 * mm, True)
                        c.drawString(30 * mm, 56 * mm, aor.email or '')

                    # Page 26 (0-based 25): "CARACTÉRISTIQUES DU COMPTE" and signature block
                    elif page_index == 25:
                        # Check "Compte individuel pleine propriété"
                        draw_checkbox(c, 17 * mm, 262 * mm, True)
                        # Nom et prénoms de la personne désignée pour faire fonctionner le compte – use AOR full name
                        c.drawString(30 * mm, 205 * mm, aor.full_name or '')
                        # Fait à / le
                        c.drawString(35 * mm, 35 * mm, aor.country_of_residence or '')
                        try:
                            from django.utils import timezone
                            c.drawString(120 * mm, 35 * mm, timezone.now().strftime('%d/%m/%Y'))
                        except Exception:
                            pass

                c.showPage()
                c.save()
                ov.seek(0)
                overlays.append(PdfReader(ov).pages[0])

            for i, page in enumerate(reader.pages):
                page_out = page
                if i < len(overlays):
                    try:
                        page_out.merge_page(overlays[i])
                    except Exception:
                        page_out.mergePage(overlays[i])  # type: ignore
                writer.add_page(page_out)

            out_io = BytesIO()
            writer.write(out_io)
            out_io.seek(0)
            return out_io.read()
        except Exception:
            return None

    def generate_pdf_response(self, html: str, filename: str = 'contrat.pdf') -> HttpResponse:
        # 1) Try template-based generation if configured
        # We pass context via last built context stored on the instance
        try:
            tmpl_bytes = None
            ctx = getattr(self, '_last_ctx', None)
            if isinstance(ctx, dict):
                tmpl_bytes = self._generate_from_template(ctx)
            if tmpl_bytes:
                logging.getLogger(__name__).info("ContractPDFService: using template-based generator")
                resp = HttpResponse(tmpl_bytes, content_type='application/pdf')
                resp['Content-Disposition'] = f'attachment; filename="{filename}"'
                resp['X-Contract-Generator'] = 'template'
                return resp
        except Exception:
            pass

        # 2) Fallback to WeasyPrint HTML rendering
        if not WEASYPRINT_AVAILABLE:
            return HttpResponse(
                content=("WeasyPrint non installé. Ajoutez weasyprint au projet pour la génération PDF."),
                status=501,
                content_type='text/plain'
            )

        pdf_io = BytesIO()
        HTML(string=html, base_url=getattr(settings, 'BASE_DIR', None)).write_pdf(pdf_io)
        pdf_io.seek(0)

        logging.getLogger(__name__).info("ContractPDFService: using weasyprint fallback")
        resp = HttpResponse(pdf_io.read(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        resp['X-Contract-Generator'] = 'weasyprint'
        return resp

from io import BytesIO
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
            # Read base template
            reader = PdfReader(template_path)
            writer = PdfWriter()

            # Create an overlay for the first page with key info (coordinates need tuning per template)
            overlay_io = BytesIO()
            _w, _h = A4
            c = canvas.Canvas(overlay_io, pagesize=A4)
            c.setFont("Helvetica", 10)
            # Example positions (Top-left origin from reportlab is bottom-left):
            y = 270 * mm
            x_left = 25 * mm
            # SGI
            c.drawString(x_left, y, f"SGI: {sgi.name if sgi else '—'}")
            y -= 7 * mm
            c.drawString(x_left, y, f"Adresse: {getattr(sgi, 'address', '') if sgi else ''}")
            y -= 7 * mm
            c.drawString(x_left, y, f"Manager: {getattr(sgi, 'manager_name', '') if sgi else ''} ({getattr(sgi, 'manager_email', '') if sgi else ''})")
            # Client block
            y -= 12 * mm
            c.drawString(x_left, y, f"Client: {aor.full_name}")
            y -= 7 * mm
            c.drawString(x_left, y, f"Email: {aor.email}  Tel: {aor.phone}")
            y -= 7 * mm
            c.drawString(x_left, y, f"Pays/Nationalité: {aor.country_of_residence} / {aor.nationality}")
            # Preferences
            y -= 12 * mm
            c.drawString(x_left, y, f"Montant dispo: {aor.available_minimum_amount or ''}")
            y -= 7 * mm
            methods = []
            if aor.funding_by_visa: methods.append('VISA')
            if aor.funding_by_mobile_money: methods.append('MOBILE MONEY')
            if aor.funding_by_bank_transfer: methods.append('VIREMENT')
            if aor.funding_by_intermediary: methods.append('INTERMÉDIAIRE')
            if aor.funding_by_wu_mg_ria: methods.append('WU/MG/RIA')
            c.drawString(x_left, y, f"Méthodes: {', '.join(methods) or '—'}")
            c.showPage()
            c.save()
            overlay_io.seek(0)

            # Merge overlay with first page of template; copy remaining pages as-is
            overlay_page = PdfReader(overlay_io).pages[0]
            for i, page in enumerate(reader.pages):
                page_out = page
                if i == 0:
                    try:
                        page_out.merge_page(overlay_page)
                    except Exception:
                        # Older PyPDF2 API
                        page_out.mergePage(overlay_page)  # type: ignore
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
                resp = HttpResponse(tmpl_bytes, content_type='application/pdf')
                resp['Content-Disposition'] = f'attachment; filename="{filename}"'
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

        resp = HttpResponse(pdf_io.read(), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

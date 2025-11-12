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

        return {
            'generated_at': timezone.now(),
            'sgi': sgi,
            'terms': terms,
            'aor': aor,
            'client': client,
            'client_profile': getattr(client, 'investment_profile', None),
        }

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

    def generate_pdf_response(self, html: str, filename: str = 'contrat.pdf') -> HttpResponse:
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

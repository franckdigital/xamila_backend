"""
PDF Template configurations for different SGIs.
Each SGI has its own template with specific field positions.
"""
from .base import BasePDFTemplate
from .gek_capital import GEKCapitalTemplate
from .nsia import NSIATemplate

# Registry of all available templates
TEMPLATE_REGISTRY = {
    'GEK': GEKCapitalTemplate,
    'GEK CAPITAL': GEKCapitalTemplate,
    'GEK CAPITAL SA': GEKCapitalTemplate,
    'NSIA': NSIATemplate,
    'NSIA FINANCE': NSIATemplate,
}

def get_template_for_sgi(sgi_name: str):
    """
    Get the appropriate PDF template class for a given SGI name.
    Returns BasePDFTemplate if no specific template is found.
    """
    if not sgi_name:
        return BasePDFTemplate
    
    sgi_key = sgi_name.strip().upper()
    return TEMPLATE_REGISTRY.get(sgi_key, BasePDFTemplate)

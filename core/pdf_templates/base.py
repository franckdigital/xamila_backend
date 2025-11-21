"""
Base PDF Template class that all SGI templates inherit from.
Defines the interface and common utilities.
"""
from typing import Dict, Any, Optional
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm


class BasePDFTemplate:
    """
    Base class for SGI-specific PDF templates.
    Each SGI template should inherit from this and implement:
    - get_template_path(): Return path to the PDF template file
    - fill_page_X(): Methods to fill specific pages with data
    """
    
    def __init__(self):
        self.page_size = A4
        self.font_name = "Helvetica"
        self.font_size = 10
        self.checkbox_size = 4 * mm
    
    def get_template_path(self) -> Optional[str]:
        """
        Return the path to the PDF template file for this SGI.
        Override in subclasses.
        """
        return None
    
    def get_page_count(self) -> int:
        """
        Return the expected number of pages in the template.
        Override in subclasses if different from default.
        """
        return 30  # Default
    
    def draw_checkbox(self, canvas_obj, x: float, y: float, checked: bool):
        """
        Draw a checkbox at position (x, y).
        
        Args:
            canvas_obj: ReportLab canvas object
            x: X position in mm
            y: Y position in mm
            checked: Whether the checkbox should be checked
        """
        size = self.checkbox_size
        canvas_obj.rect(x, y, size, size, stroke=1, fill=0)
        if checked:
            canvas_obj.line(x, y, x + size, y + size)
            canvas_obj.line(x, y + size, x + size, y)
    
    def draw_text(self, canvas_obj, x: float, y: float, text: str, 
                  font_name: Optional[str] = None, font_size: Optional[int] = None):
        """
        Draw text at position (x, y).
        
        Args:
            canvas_obj: ReportLab canvas object
            x: X position in mm
            y: Y position in mm
            text: Text to draw
            font_name: Font name (optional, uses default if not provided)
            font_size: Font size (optional, uses default if not provided)
        """
        if font_name or font_size:
            canvas_obj.setFont(
                font_name or self.font_name,
                font_size or self.font_size
            )
        canvas_obj.drawString(x, y, str(text))
    
    def fill_page(self, canvas_obj, page_index: int, context: Dict[str, Any]):
        """
        Fill a specific page with data from context.
        This is the main method that should be overridden in subclasses.
        
        Args:
            canvas_obj: ReportLab canvas object
            page_index: 0-based page index
            context: Dictionary containing all data (aor, annex, sgi, etc.)
        """
        # Default implementation does nothing
        # Subclasses should override this to fill their specific pages
        pass
    
    def get_annex_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract annex data from context.
        
        Args:
            context: Full context dictionary
            
        Returns:
            Dictionary with page22, page23, page26 data
        """
        annex = context.get('annex', {})
        if not isinstance(annex, dict):
            annex = {}
        return annex
    
    def get_aor_data(self, context: Dict[str, Any]) -> Any:
        """
        Extract AccountOpeningRequest object from context.
        
        Args:
            context: Full context dictionary
            
        Returns:
            AccountOpeningRequest object or None
        """
        return context.get('aor')
    
    def get_sgi_data(self, context: Dict[str, Any]) -> Any:
        """
        Extract SGI object from context.
        
        Args:
            context: Full context dictionary
            
        Returns:
            SGI object or None
        """
        return context.get('sgi')
    
    def safe_get(self, data: Dict[str, Any], key: str, default: str = '') -> str:
        """
        Safely get a value from a dictionary, returning default if not found.
        
        Args:
            data: Dictionary to get value from
            key: Key to look up
            default: Default value if key not found
            
        Returns:
            Value as string or default
        """
        value = data.get(key, default)
        return str(value) if value is not None else default
    
    def format_date(self, date_str: str) -> str:
        """
        Format a date string to DD/MM/YYYY format.
        
        Args:
            date_str: Date string in any format
            
        Returns:
            Formatted date string or original if parsing fails
        """
        if not date_str:
            return ''
        
        try:
            from datetime import datetime
            # Try parsing ISO format (YYYY-MM-DD)
            if '-' in date_str:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
                return dt.strftime('%d/%m/%Y')
            return date_str
        except Exception:
            return date_str

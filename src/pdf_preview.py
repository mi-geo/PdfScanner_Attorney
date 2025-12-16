# PDF preview utilities
import pdfplumber
from PIL import Image

def render_pdf_page(pdf_path: str, page_number: int, dpi: int = 150) -> Image.Image:
    """Render a PDF page to an image for quick visual inspection."""
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        im = page.to_image(resolution=dpi).original
        return im
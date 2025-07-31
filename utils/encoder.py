from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from ppf.datamatrix import DataMatrix
import cairosvg
import io
import base64

def encode_text_to_qr(text: str, scale: int = 3) -> str:
    """
    Encodes text into a QR code using segno and returns a Base64-encoded PNG.

    Args:
        text (str): The data to encode.

    Returns:
        str: Base64-encoded PNG string of the QR code.
    """
    svg = DataMatrix(text).svg()
    png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
    #qr = segno.make_symbol(text, symbol_type='dm')
    #buffer = io.BytesIO()
    #qr.save(buffer, kind='png', scale=scale)
    return base64.b64encode(png_bytes).decode('utf-8')

def generate_qr_pdf(payload: str, scale: int = 3) -> bytes:
    """
    Generates a PDF containing a QR code from the given payload.

    Args:
        payload (str): The text to encode as a QR code.

    Returns:
        bytes: Byte content of the generated PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Create QR code using segno and save as PNG
    svg = DataMatrix(payload).svg()
    png_bytes = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
    img_stream = io.BytesIO(png_bytes)
    dm_img = ImageReader(img_stream)

    #qr.save(qr_buffer, kind='png', scale=scale, dark='black', light='white')
    #qr_buffer.seek(0)
    #qr_img = ImageReader(qr_buffer)
    
    # Draw QR code onto PDF
    # Base size (e.g. scale 3 = small, scale 5 = medium, scale 8 = large)
    scale_size_map = {
        2: 40,    # mm
        3: 65,   # mm
        5: 85    # mm
    }

    dm_dim_mm = scale_size_map.get(scale, 100)

    c.drawImage(dm_img, x=50*mm, y=120*mm, width=qr_dim_mm*mm, height=qr_dim_mm*mm)

    #c.drawImage(qr_img, x=50*mm, y=120*mm, width=100*mm, height=100*mm)
    c.drawString(50*mm, 110*mm, "DataMatrix Payload:")
    c.drawString(50*mm, 105*mm, payload[:60] + "..." if len(payload) > 60 else payload)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

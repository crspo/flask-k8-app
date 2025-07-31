from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from ppf.datamatrix import DataMatrix
from PIL import Image
import cairosvg
import io
import base64

SCALE_SIZE_MAP_MM = {
        2: 40,   # mm
        3: 60,  # mm
        5: 120   # mm
    }

def encode_text_to_qr(text: str, scale: int = 3) -> str:
    """
    Encodes text into a DM code and returns a Base64-encoded PNG.

    Args:
        text (str): The data to encode.

    Returns:
        str: Base64-encoded PNG string of the QR code.
    """

    dm_dim_mm = SCALE_SIZE_MAP_MM.get(scale, 100)
    dm_dim_px = int(dm_dim_mm * 3.78)  # Approx. 96 dpi

    # Generate SVG
    svg = DataMatrix(text).svg()

    # Convert to PNG with dynamic resolution
    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode('utf-8'),
        output_width=dm_dim_px,
        output_height=dm_dim_px
    )

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

    """ 
        Create DM 
    """

    dm_dim_mm = SCALE_SIZE_MAP_MM.get(scale, 100)
    dm_dim_px = int(dm_dim_mm * 3.78)
    # Generate SVG and convert to PNG with specified resolution
    svg = DataMatrix(payload).svg()
    

    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode('utf-8'),
        output_width=dm_dim_px,
        output_height=dm_dim_px
    )

    with Image.open(io.BytesIO(png_bytes)) as img:
        flattened = Image.new("RGB", img.size, (255, 255, 255))
        flattened.paste(img, mask=img.getchannel("A"))

        # Convert to ImageReader before drawing
        img_stream = io.BytesIO()
        flattened.save(img_stream, format="PNG")
        img_stream.seek(0)
        dm_img = ImageReader(img_stream)
    

    c.drawImage(dm_img, x=50*mm, y=120*mm, width=dm_dim_mm*mm, height=dm_dim_mm*mm)
    #c.drawString(50*mm, 110*mm, "DataMatrix Payload:")
    #c.drawString(50*mm, 105*mm, payload[:60] + "..." if len(payload) > 60 else payload)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

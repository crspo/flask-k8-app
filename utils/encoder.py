from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from ppf.datamatrix import DataMatrix
from PIL import Image
import cairosvg
import io
import base64

'''
SCALE_SIZE_MAP_MM = {
        2: 25,   # mm
        3: 50,  # mm
        5: 100   # mm
    }
'''
def encode_text_to_qr(text: str, scale: int = 50) -> str:
    """
    Encodes text into a DM code and returns a Base64-encoded PNG.

    Args:
        text (str): The data to encode.

    Returns:
        str: Base64-encoded PNG string of the QR code.
    """

    #dm_dim_mm = SCALE_SIZE_MAP_MM.get(scale, 100)
    dm_dim_px = int(scale * 3.78)  # Approx. 96 dpi

    # Generate SVG
    svg = DataMatrix(text).svg()

    # Convert to PNG with dynamic resolution
    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode('utf-8'),
        output_width=dm_dim_px,
        output_height=dm_dim_px
    )

    return base64.b64encode(png_bytes).decode('utf-8')

def generate_qr_pdf(payload: str, scale: int = 50) -> bytes:
    """
    Generates a PDF containing tiled QR codes from the given payload.
    Displays the first serial above and the last serial below each QR code.

    Args:
        payload (str): Multiline string with each line as a separate QR code.
        scale (int): Scale factor for QR code size.

    Returns:
        bytes: Byte content of the generated PDF.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    serials = [line.strip() for line in payload.splitlines() if line.strip()]
    if not serials:
        return b''

    #qr_dim_mm = SCALE_SIZE_MAP_MM.get(scale, 60)
    qr_dim_px = int(scale * 3.78)

    page_width_mm, page_height_mm = A4[0] / mm, A4[1] / mm
    margin_mm = 10
    spacing_mm = 5
    x_mm = margin_mm
    y_mm = page_height_mm - margin_mm - scale
    max_cols = int((page_width_mm - 2 * margin_mm) // (scale + spacing_mm))
    max_rows = int((page_height_mm - 2 * margin_mm) // (scale + spacing_mm))
    qr_per_page = max_cols * max_rows

    chunk_size = 50
    chunks = [serials[i:i + chunk_size] for i in range(0, len(serials), chunk_size)]

    for i, chunk in enumerate(chunks):
        first_serial = chunk[0]
        last_serial = chunk[-1]
        chunk_payload = "\n".join(chunk)

        qr_svg = DataMatrix(chunk_payload).svg()

        grid_index = i % qr_per_page
        row = grid_index // max_cols
        col = grid_index % max_cols
        x_mm = margin_mm + col * (scale + spacing_mm)
        y_mm = page_height_mm - margin_mm - (row + 1) * (scale + spacing_mm)
        

        draw_qr(c, x_mm, y_mm, qr_svg, scale, qr_dim_px, first_serial, last_serial)
        # Start new page if grid is full
        if (i + 1) % qr_per_page == 0:
            c.showPage()
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
    
def draw_qr(c, x_mm, y_mm, qr_svg, qr_dim_mm, qr_dim_px, first_serial, last_serial):
    # Convert SVG to PNG
    png_bytes = cairosvg.svg2png(
        bytestring=qr_svg.encode('utf-8'),
        output_width=qr_dim_px,
        output_height=qr_dim_px
    )
    with Image.open(io.BytesIO(png_bytes)) as img:
        flattened = Image.new("RGB", img.size, (255, 255, 255))
        flattened.paste(img, mask=img.getchannel("A"))
        img_stream = io.BytesIO()
        flattened.save(img_stream, format="PNG")
        img_stream.seek(0)
        qr_img = ImageReader(img_stream)
        c.drawImage(qr_img, x_mm * mm, y_mm * mm, qr_dim_mm * mm, qr_dim_mm * mm)

        # Label the QR with its own first/last serials
        label_font_size = 8
        c.setFont("Helvetica", label_font_size)
        c.drawCentredString(
            (x_mm + qr_dim_mm / 2) * mm,
            (y_mm + qr_dim_mm + 2) * mm,
            first_serial
        )
        c.drawCentredString(
            (x_mm + qr_dim_mm / 2) * mm,
            (y_mm - 4) * mm,
            last_serial
        )

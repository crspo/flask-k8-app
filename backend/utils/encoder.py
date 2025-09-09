from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from ppf.datamatrix import DataMatrix
from PIL import Image
import cairosvg
import io
import base64

def encode_text_to_qr(text: str, scale: int = 50) -> str:
    """
    Encodes text into a DM code and returns a Base64-encoded PNG.
    """

    dm_dim_px = int(scale * 3.78)  # Approx. 96 dpi
    svg = DataMatrix(text).svg()
    png_bytes = cairosvg.svg2png(
        bytestring=svg.encode('utf-8'),
        output_width=dm_dim_px,
        output_height=dm_dim_px
    )

    return base64.b64encode(png_bytes).decode('utf-8')


def generate_qr_pdf(payload: str, scale: int = 50) -> bytes:
    """
    Generates a PDF containing tiled DataMatrix (DM) codes, one DM per serial.
    """

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    serials = [line.strip() for line in payload.splitlines() if line.strip()]
    if not serials:
        return b''

    qr_dim_px = int(scale * 3.78)
    page_width_mm, page_height_mm = A4[0] / mm, A4[1] / mm
    margin_mm = 10
    spacing_mm = 5

    effective_width = page_width_mm - 2 * margin_mm + spacing_mm
    effective_height = page_height_mm - 2 * margin_mm + spacing_mm
    max_cols = max(1, int(effective_width // (scale + spacing_mm)))
    max_rows = max(1, int(effective_height // (scale + spacing_mm)))
    qr_per_page = max_cols * max_rows

    for idx, serial in enumerate(serials):
        index_on_page = idx % qr_per_page
        row = index_on_page // max_cols
        col = index_on_page % max_cols

        x_mm = margin_mm + col * (scale + spacing_mm)
        y_mm = page_height_mm - margin_mm - (row + 1) * (scale + spacing_mm)

        try:
            qr_svg = DataMatrix(serial).svg()
        except Exception:
            continue

        draw_qr(c, x_mm, y_mm, qr_svg, scale, qr_dim_px, serial, serial)

        if (index_on_page + 1) == qr_per_page or idx == len(serials) - 1:
            c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_qr(c, x_mm, y_mm, qr_svg, qr_dim_mm, qr_dim_px, first_serial, last_serial):
    png_bytes = cairosvg.svg2png(
        bytestring=qr_svg.encode('utf-8'),
        output_width=qr_dim_px,
        output_height=qr_dim_px
    )

    with Image.open(io.BytesIO(png_bytes)) as img:
        if 'A' in img.getbands():
            flattened = Image.new("RGB", img.size, (255, 255, 255))
            flattened.paste(img, mask=img.getchannel("A"))
        else:
            flattened = img.convert("RGB")

        img_stream = io.BytesIO()
        flattened.save(img_stream, format="PNG")
        img_stream.seek(0)
        qr_img = ImageReader(img_stream)
        c.drawImage(qr_img, x_mm * mm, y_mm * mm, qr_dim_mm * mm, qr_dim_mm * mm)

    label_font_size = 8
    c.setFont("Helvetica", label_font_size)
    try:
        c.drawCentredString((x_mm + qr_dim_mm / 2) * mm, (y_mm + qr_dim_mm + 2) * mm, str(first_serial))
        c.drawCentredString((x_mm + qr_dim_mm / 2) * mm, (y_mm - 4) * mm, str(last_serial))
    except Exception:
        pass

from io import BytesIO
import base64
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

try:
    from ppf.datamatrix import DataMatrix
except Exception:
    DataMatrix = None


def _render_datamatrix(text: str, module_size: int = 8, border_modules: int = 2) -> Image.Image:
    """Render a DataMatrix into a PIL Image using `ppf.datamatrix.DataMatrix`.

    module_size: pixels per datamatrix module.
    border_modules: blank border modules around the symbol.
    """
    if DataMatrix is None:
        raise RuntimeError('ppf.datamatrix not available')

    dm = DataMatrix(text)
    mat = dm.matrix
    rows = len(mat)
    cols = len(mat[0])

    img_w = (cols + border_modules * 2) * module_size
    img_h = (rows + border_modules * 2) * module_size
    img = Image.new('RGB', (img_w, img_h), 'white')
    draw = ImageDraw.Draw(img)

    for y, row in enumerate(mat):
        for x, cell in enumerate(row):
            if cell:
                x0 = (x + border_modules) * module_size
                y0 = (y + border_modules) * module_size
                draw.rectangle([x0, y0, x0 + module_size - 1, y0 + module_size - 1], fill='black')

    return img


def _compute_module_size_for_target(text: str, target_mm: float, dpi: int = 300, border_modules: int = 2) -> int:
    """Compute pixels-per-module so the printed symbol width approximates target_mm at dpi."""
    if DataMatrix is None:
        raise RuntimeError('ppf.datamatrix not available')
    dm = DataMatrix(text)
    mat = dm.matrix
    cols = len(mat[0])
    total_modules = cols + border_modules * 2
    target_pixels = round((target_mm / 25.4) * dpi)
    module_size = max(1, target_pixels // total_modules)
    return module_size


def encode_text_to_qr(text: str, scale: int = 50, module_size: int | None = None, target_mm: float | None = None, dpi: int = 300) -> str:
    """Return a data-URI PNG of the datamatrix.

    Either provide `module_size` (pixels per datamatrix module) directly, or
    pass a `scale` value which will be converted into a module size
    (legacy behavior). Passing `module_size` gives explicit control over
    output symbol size.
    """
    if target_mm is not None:
        # compute module_size so printed width ~ target_mm
        module_size = _compute_module_size_for_target(text or '<empty>', target_mm=target_mm, dpi=dpi)

    if module_size is None:
        module_size = max(2, scale // 5)

    try:
        img = _render_datamatrix(text or '<empty>', module_size=module_size)
    except Exception:
        # Fallback: render human-readable preview for robustness
        # Keep minimal readable fallback similar to previous implementation
        size = max(100, min(2000, len(text or '') * scale // 2))
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, size - 1, size - 1], outline='black')
        lines = (text or '<empty>').split('\n')[:10]
        y = 10
        for line in lines:
            draw.text((10, y), line, fill='black')
            y += 12

    buf = BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # Return a ready-to-use data URI to simplify client usage
    return f"data:image/png;base64,{b64}"


def generate_qr_pdf(text: str, scale: int = 50, module_size: int | None = None, target_mm: float | None = None, dpi: int = 300) -> bytes:
    """Generate a one-page PDF embedding the DataMatrix image and return bytes.

    Accepts the same `module_size` vs `scale` options as `encode_text_to_qr`.
    """
    if target_mm is not None:
        module_size = _compute_module_size_for_target(text or '<empty>', target_mm=target_mm, dpi=dpi)

    if module_size is None:
        module_size = max(2, scale // 5)

    try:
        img = _render_datamatrix(text or '<empty>', module_size=module_size)
    except Exception:
        # Fallback to a simple preview image
        size = max(100, min(2000, len(text or '') * scale // 2))
        img = Image.new('RGB', (size, size), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, size - 1, size - 1], outline='black')
        lines = (text or '<empty>').split('\n')[:10]
        y = 10
        for line in lines:
            draw.text((10, y), line, fill='black')
            y += 12

    img_buf = BytesIO()
    img.save(img_buf, format='PNG')
    img_buf.seek(0)

    out = BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    width, height = A4

    if target_mm is not None:
        # convert target mm to PDF points (1 pt = 1/72 in)
        img_width_pts = (target_mm / 25.4) * 72
        img_height_pts = img_width_pts
        x = (width - img_width_pts) / 2
        y = (height - img_height_pts) / 2
        c.drawImage(ImageReader(img_buf), x, y, width=img_width_pts, height=img_height_pts)
    else:
        img_width = min(width - 100, img.width)
        img_height = min(height - 100, img.height)
        x = (width - img_width) / 2
        y = (height - img_height) / 2
        c.drawImage(ImageReader(img_buf), x, y, width=img_width, height=img_height)
    c.showPage()
    c.save()
    return out.getvalue()

from flask import Blueprint, request, Response, jsonify, send_file, send_from_directory
import base64
import os
from pathlib import Path

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    # Serve the SPA entrypoint
    root = Path(__file__).resolve().parents[1]
    return send_file(root / 'static' / 'index.html')


@bp.route('/static/<path:filename>')
def serve_static(filename):
    root = Path(__file__).resolve().parents[1]
    return send_from_directory(root / 'static', filename)


@bp.route('/sw.js')
def service_worker():
    # Allow disabling the service worker at runtime for debugging cached/blank pages.
    # Set environment variable DISABLE_SW=1 to make this endpoint return 204 No Content.
    if os.environ.get('DISABLE_SW', '0') == '1':
        return ('', 204)

    root = Path(__file__).resolve().parents[1]
    sw_path = root / 'static' / 'sw.js'
    if sw_path.exists():
        return send_from_directory(root / 'static', 'sw.js')
    return ('', 204)


@bp.route('/favicon.ico')
def favicon():
    root = Path(__file__).resolve().parents[1]
    ico = root / 'static' / 'favicon.ico'
    if ico.exists():
        return send_from_directory(root / 'static', 'favicon.ico')
    # Fallback: use the main logo if a proper favicon.ico is not present
    logo = root / 'static' / 'text-to-dm-logo.png'
    if logo.exists():
        return send_from_directory(root / 'static', 'text-to-dm-logo.png')
    # Last resort: return 204 No Content
    return ('', 204)


@bp.route('/api/upload', methods=['POST'])
def upload_and_export():
    """
    Handles file upload, generates QR preview, and returns JSON with base64 image and PDF.
    """
    size_map = {
        'small': 25,
        'medium': 50,
        'large': 100
    }

    selected_size = request.form.get('size', 'medium')
    qr_size = size_map.get(selected_size, 50)  # default to Medium if not recognized

    file = request.files.get('file')
    serials_input = request.form.get('serials', '').strip()
    lines = []

    # start input logic
    if file and file.filename != '':
        lines = file.stream.read().decode('utf-8').splitlines()
    elif serials_input:
        lines = serials_input.splitlines()
    else:
        return jsonify({'error': 'No file or input provided.'}), 400

    serials = [line.strip() for line in lines if line.strip()]
    payload = '\r\n'.join(serials)
    # end input logic

    # Lazily import encoder functions to avoid importing heavy native dependencies at module import time
    from backend.utils.encoder import encode_text_to_qr, generate_qr_pdf

    # Generate QR preview
    img_base64 = encode_text_to_qr(payload, scale=qr_size)

    # Generate PDF and store in memory
    pdf_bytes = generate_qr_pdf(payload, scale=qr_size)
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return jsonify({
        'img_base64': img_base64,
        'pdf_b64': pdf_b64,
    })


@bp.route('/_debug/status')
def debug_status():
    """Return quick diagnostics about the served static files.

    This endpoint is intentionally minimal and only used for local debugging
    or CI smoke-tests. It returns whether the SPA entrypoint and key assets
    exist and a small preview of `index.html` so you can confirm what the
    backend is actually serving.
    """
    root = Path(__file__).resolve().parents[1]
    static_dir = root / 'static'

    def info(p: Path):
        return {
            'exists': p.exists(),
            'size': p.stat().st_size if p.exists() else 0
        }

    index_file = static_dir / 'index.html'
    assets = [
        static_dir / 'assets' / 'index-BPrHFD5V.js',
        static_dir / 'assets' / 'index-Cos4r8-z.css',
        static_dir / 'sw.js'
    ]

    preview = ''
    if index_file.exists():
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                preview = f.read(1200)
        except Exception:
            preview = ''

    return jsonify({
        'index': info(index_file),
        'assets': {a.name: info(a) for a in assets},
        'index_preview': preview
    })

from flask import Blueprint, request, Response, jsonify, send_file, send_from_directory
import base64
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
    root = Path(__file__).resolve().parents[1]
    return send_from_directory(root / 'static', 'sw.js')


@bp.route('/favicon.ico')
def favicon():
    root = Path(__file__).resolve().parents[1]
    return send_from_directory(root / 'static', 'favicon.ico')


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

from flask import Blueprint, request, Response, jsonify, send_file, send_from_directory, current_app
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


@bp.route('/assets/<path:filename>')
def serve_assets(filename):
    # Vite builds often reference /assets/<file>; ensure those requests are served
    root = Path(__file__).resolve().parents[1]
    assets_dir = root / 'static' / 'assets'
    return send_from_directory(assets_dir, filename)


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
    # Map UI sizes to explicit DataMatrix module sizes (pixels per module).
    # Adjust these values so the rendered symbol matches the expected visual size.
    module_size_map = {
        'small': 6,
        # keep legacy explicit module_size for small/large; for medium we prefer a
        # target physical size (printed) which will be computed by the encoder.
        'medium': 8,
        'large': 12,
    }

    selected_size = request.form.get('size', 'medium')
    # For "medium" use a target physical size (in mm) so printed output is predictable.
    target_mm = None
    if selected_size == 'medium':
        target_mm = 34.0

    module_size = module_size_map.get(selected_size, 8)  # default to medium module size

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
    try:
        from backend.utils.encoder import encode_text_to_qr, generate_qr_pdf
    except Exception as e:
        # Import failed; log full exception and return a clear error to the caller
        current_app.logger.exception('Failed to import encoder module')
        return jsonify({'error': f'Encoder module import error: {e}'}), 500

    # Generate QR preview using explicit module size
    # Prefer target_mm when provided; encoder will compute an appropriate module_size.
    img_base64 = encode_text_to_qr(payload, module_size=module_size, target_mm=target_mm, dpi=300)

    # Ensure we return a ready-to-use data URI for clients and keep the raw base64
    if isinstance(img_base64, str) and img_base64.startswith('data:'):
        img_src = img_base64
        # strip data: prefix to keep img_base64 as raw base64 for backwards compatibility
        try:
            _, b64 = img_base64.split(',', 1)
            img_b64_raw = b64
        except Exception:
            img_b64_raw = img_base64
    else:
        img_b64_raw = img_base64 or ''
        img_src = f"data:image/png;base64,{img_b64_raw}"

    # Generate PDF and store in memory
    pdf_bytes = generate_qr_pdf(payload, module_size=module_size, target_mm=target_mm, dpi=300)
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    return jsonify({
        'img_base64': img_b64_raw,
        'img_src': img_src,
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


@bp.route('/_debug/bundle')
def debug_bundle():
    """Return a truncated preview of the main JS bundle to help diagnose runtime errors."""
    root = Path(__file__).resolve().parents[1]
    bundle = root / 'static' / 'assets' / 'index-BPrHFD5V.js'
    if not bundle.exists():
        return jsonify({'error': 'bundle not found'}), 404
    try:
        with open(bundle, 'r', encoding='utf-8') as f:
            content = f.read(4000)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return Response(content, mimetype='text/javascript')


@bp.route('/client-error', methods=['POST'])
def client_error():
    """Accept client-side error reports (console logs) and write to server logs.

    Expected JSON: { 'message': string, 'stack': string, 'userAgent': string }
    """
    data = request.get_json(silent=True) or {}
    message = data.get('message') or '<no message>'
    stack = data.get('stack') or ''
    ua = data.get('userAgent') or request.headers.get('User-Agent')
    # Log the error for developers to inspect (visible in pod logs)
    current_app.logger.error('Client error: %s\nUser-Agent: %s\nStack:\n%s', message, ua, stack)
    return ('', 204)


@bp.route('/_debug/routes')
def debug_routes():
    """Return a JSON list of registered routes for debugging."""
    try:
        from flask import current_app
        rules = []
        for rule in sorted(current_app.url_map.iter_rules(), key=lambda r: r.rule):
            # rule.methods can be a set or None; normalize to a sorted list for JSON
            methods = sorted(list(rule.methods or []))
            rules.append({'rule': rule.rule, 'endpoint': rule.endpoint, 'methods': methods})
        return jsonify({'routes': rules})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/healthz')
def healthz():
    """Simple health endpoint for Kubernetes readiness/liveness.

    Kept intentionally tiny: returns 200 OK when the app process is alive.
    Use a separate readiness/liveness path so probes are fast and predictable.
    """
    return ('', 200)

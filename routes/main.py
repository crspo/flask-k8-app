from utils.encoder import encode_text_to_qr, generate_qr_pdf
from flask import send_file, Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask import Blueprint, request, Response, render_template
import io
import base64

bp = Blueprint('main', __name__)
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/products')
def products():
    return render_template('products.html')


@bp.route('/upload', methods=['POST'])
def upload_and_export():
    """
    Handles file upload or text input, generates QR preview, and offers PDF download.
    """
    size_map = {
        'small': 25,
        'medium': 50,
        'large': 100
    }

    selected_size = request.form.get('size', 'medium')
    qr_size = size_map.get(selected_size, 50)

    file = request.files.get('file')
    serials_input = request.form.get('serials', '').strip()
    lines = []

    # 🧠 Input validation
    if file and file.filename:
        try:
            lines = file.stream.read().decode('utf-8').splitlines()
        except Exception:
            raise BadRequest("Unable to read uploaded file. Ensure it's a valid UTF-8 text file.")
    elif serials_input:
        lines = serials_input.splitlines()
    else:
        raise BadRequest("No file or serial input provided.")

    # 🧼 Clean and validate serials
    serials = [line.strip() for line in lines if line.strip()]
    if not serials:
        raise BadRequest("No valid serials found in input.")

    payload = '\r\n'.join(serials)

    # 🖼️ Generate QR preview
    img_base64 = encode_text_to_qr(payload, scale=qr_size)

    # 📄 Generate PDF
    pdf_bytes = generate_qr_pdf(payload, scale=qr_size)
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    # 🎯 Render preview page
    return render_template("preview.html", img_base64=img_base64, pdf_b64=pdf_b64)

# Decodes DM code to text and injects to decode.html
from pylibdmtx.pylibdmtx import decode
@bp.route('/decode-dm', methods=['POST'])
def decode_datamatrix():
    file = request.files.get('file')

    if not file:
        raise BadRequest("No file uploaded. Please select an image file.")

    # Validate file type if needed
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        raise BadRequest("Unsupported file format. Please upload a valid image.")
    
    # Process the image (example logic)
    try:
        img = Image.open(file.stream).convert("RGB")
        decoded_objects = decode(img)
        decoded_texts = [obj.data.decode("utf-8") for obj in decoded_objects]

    except ValueError as ve:
        raise BadRequest(f"Decoding failed: {str(ve)}")

    # Return result (could be JSON or render a template)
    return render_template("decode.html", decoded_text=decoded_text)
    
# Handle HTTP exceptions (e.g., 404, 403, etc.)
@bp.errorhandler(HTTPException)
def handle_http_exception(e):
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': e.name, 'description': e.description}), e.code
    else:
        return render_template('error.html', error=e), e.code

# Handle non-HTTP exceptions (e.g., bugs, crashes)
@bp.errorhandler(Exception)
def handle_generic_exception(e):
    bp.logger.error(f"Unhandled Exception: {e}")
    if request.accept_mimetypes.accept_json:
        return jsonify({'error': 'Internal Server Error', 'description': str(e)}), 500
    else:
        return render_template('error.html', error=e), 500

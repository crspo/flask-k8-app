from flask import send_file
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
    Handles file upload, generates QR preview, and offers PDF download link.
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
    
    #start input logic
    if file and file.filename != '':
        lines = file.stream.read().decode('utf-8').splitlines()
    elif serials_input:
        lines = serials_input.splitlines()
    else:
        return render_template("error.html", error_msg="No file or input provided.")
    
    serials = [line.strip() for line in lines if line.strip()]
    payload = '\r\n'.join(serials)
    #end input logic


    # Lazily import encoder functions to avoid importing heavy native dependencies at module import time
    from backend.utils.encoder import encode_text_to_qr, generate_qr_pdf

    # Generate QR preview
    img_base64 = encode_text_to_qr(payload, scale=qr_size)

    # Generate PDF and store in memory (base64 encoding optional if you want download link)
    pdf_bytes = generate_qr_pdf(payload, scale=qr_size)
    # Save PDF to memory for download
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

    if request.method == 'POST':
        return render_template("preview.html", img_base64=img_base64, pdf_b64=pdf_b64)

    else:
        return Response(f'''\n            <h3>QR Code Preview:</h3> <h2> Result out of bound </h2>\n            ''', content_type='text/html')

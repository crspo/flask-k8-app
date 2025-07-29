from utils.encoder import generate_qr_pdf
from flask import send_file
from flask import Blueprint, request, Response, render_template
import io

bp = Blueprint('main', __name__)
@bp.route('/')
def index():
    return render_template('index.html')
  
@bp.route('/upload', methods=['POST'])
def upload_and_export():
    """
    Handles file upload, generates QR preview, and offers PDF download link.
    """
    size_map = {
    'small': 200,
    'medium': 300,
    'large': 500
    }

    selected_size = request.form.get('size', 'medium')
    qr_size = size_map.get(selected_size, 300)  # default to Medium if not recognized

    file = request.files.get('file')
    if not file or file.filename == '':
        return render_template("error.html", error_msg="No file selected.")

    lines = file.stream.read().decode('utf-8').splitlines()
    serials = [line.strip() for line in lines if line.strip()]
    payload = '\n'.join(serials)

    # Generate QR preview
    from utils.encoder import encode_text_to_qr, generate_qr_pdf
    img_base64 = encode_text_to_qr(payload, size=qr_size)

    # Generate PDF and store in memory (base64 encoding optional if you want download link)
    pdf_bytes = generate_qr_pdf(payload)

    # Save PDF to memory for download
    import base64
    pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
    if request.method == 'POST':
        return Response(f'''
            <h3>QR Code Preview:</h3>
            <img src="data:image/png;base64,{img_base64}" alt="QR Code"/>
            <br/><button onclick="printQRCode()">Print QR Code</button>
            <br/><a download="qr-code.pdf" href="data:application/pdf;base64,{pdf_b64}">Download as PDF</a>
            <br/><a href="/">Upload Another</a>
            <script>
                function printQRCode() {{
                const w = window.open('', '', 'height=600,width=800');
                w.document.write('<html><head><title>Print</title></head><body>');
                w.document.write(document.querySelector('img').outerHTML);
                w.document.write('</body></html>');
                w.document.close();
                w.focus();
                w.print();
                w.close();
            }}
            </script>
        ''', content_type='text/html')

    else:
        return Response(f'''
            <h3>QR Code Preview:</h3> <h2> Result out of bound </h2>
            ''', content_type='text/html')

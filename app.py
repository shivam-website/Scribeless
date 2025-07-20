from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# For Windows only (ignored in production Docker)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR'

@app.route('/')
def serve():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        img = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(img)

        return jsonify({
            'success': True,from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from pyzbar.pyzbar import decode as qr_decode

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# --------- Routes to Serve Frontend --------- #
@app.route('/')
def serve():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('.', path)):
        return send_from_directory('.', path)
    else:
        return send_from_directory('.', 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

# ---------- OCR: Image to Text --------- #
@app.route('/api/ocr/image', methods=['POST'])
def ocr_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    image = Image.open(file.stream)
    text = pytesseract.image_to_string(image)

    return jsonify({'success': True, 'text': text.strip()})

# ---------- OCR: PDF to Text --------- #
@app.route('/api/ocr/pdf', methods=['POST'])
def ocr_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    text_output = ""

    try:
        pdf = fitz.open(stream=file.read(), filetype="pdf")
        for page in pdf:
            pix = page.get_pixmap(dpi=300)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            page_text = pytesseract.image_to_string(img)
            text_output += page_text + "\n"
        pdf.close()
    except Exception as e:
        return jsonify({'error': f'PDF OCR failed: {str(e)}'}), 500

    return jsonify({'success': True, 'text': text_output.strip()})

# ---------- QR Code Scanner --------- #
@app.route('/api/scan/qr', methods=['POST'])
def scan_qr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    image = Image.open(file.stream)
    decoded = qr_decode(image)

    if not decoded:
        return jsonify({'error': 'No QR code found'}), 404

    results = [d.data.decode('utf-8') for d in decoded]
    return jsonify({'success': True, 'results': results})

# ---------- Barcode Scanner --------- #
@app.route('/api/scan/barcode', methods=['POST'])
def scan_barcode():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    image = Image.open(file.stream)
    decoded = qr_decode(image)

    if not decoded:
        return jsonify({'error': 'No barcode found'}), 404

    results = [{'type': d.type, 'data': d.data.decode('utf-8')} for d in decoded]
    return jsonify({'success': True, 'results': results})

# ---------- Dummy Ping API --------- #
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})

# ---------- Run Server --------- #
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

            'text': text.strip(),
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Could not process the image. Please ensure it contains clear text.'
        }), 500

# Catch-all for SPA routing (optional)
@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

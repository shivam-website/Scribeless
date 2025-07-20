from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from pdf2image import convert_from_bytes

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- API Key system ---
ALLOWED_API_KEYS = {"abc123", "testkey123"}  # You can manage this securely in DB or env later

def check_api_key():
    api_key = request.headers.get("x-api-key")
    if api_key not in ALLOWED_API_KEYS:
        return False
    return True

# --- Serve frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path) if os.path.exists(path) else send_from_directory('.', 'index.html')

# --- API Ping Test ---
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})

# --- Image to Text API ---
@app.route('/api/image2text', methods=['POST'])
def image_to_text():
    if not check_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- PDF to Text API ---
@app.route('/api/pdf2text', methods=['POST'])
def pdf_to_text():
    if not check_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    try:
        images = convert_from_bytes(file.read())
        full_text = ""
        for img in images:
            full_text += pytesseract.image_to_string(img) + "\n"
        return jsonify({'success': True, 'text': full_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Fallback for SPA ---
@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

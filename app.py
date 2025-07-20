from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import os
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from pdf2image import convert_from_bytes
import uuid
import threading
import time

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- In-memory API key storage (replace with DB or Redis in prod) ---
API_KEYS = set([
    "abc123",
    "testkey123"
])

# Clean up old uploaded files periodically (e.g., every hour)
def cleanup_uploads():
    while True:
        now = time.time()
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                # Remove files older than 1 hour
                if now - os.path.getmtime(filepath) > 3600:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
        time.sleep(3600)

cleanup_thread = threading.Thread(target=cleanup_uploads, daemon=True)
cleanup_thread.start()

# --- Helper: API Key Check ---
def check_api_key():
    api_key = request.headers.get("x-api-key")
    if not api_key or api_key not in API_KEYS:
        return False
    return True

# --- API Key Generation Endpoint ---
@app.route('/api/generate_key', methods=['POST'])
def generate_key():
    # For security, you may want to add authentication here (admin only)
    # Example: pass an admin password in JSON body (replace this with real auth)
    data = request.get_json() or {}
    admin_pass = data.get('admin_pass')
    if admin_pass != os.environ.get('ADMIN_PASS', 'changeme'):
        return jsonify({'error': 'Unauthorized'}), 403

    new_key = str(uuid.uuid4())
    API_KEYS.add(new_key)
    return jsonify({'success': True, 'api_key': new_key})

# --- Serve frontend ---
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    else:
        return send_from_directory('.', 'index.html')

# --- API Ping ---
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'})

# --- Image to Text ---
@app.route('/api/image2text', methods=['POST'])
def image_to_text():
    if not check_api_key():
        return jsonify({'error': 'Invalid or missing API key'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        text = pytesseract.image_to_string(Image.open(filepath))
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- PDF to Text ---
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

# --- Catch-all for SPA ---
@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

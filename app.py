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
            'success': True,
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

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import os
import logging
import tempfile

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ScribelessOCR')

# Tesseract configuration for Render
TESSERACT_CMD = '/usr/bin/tesseract'
if not os.path.exists(TESSERACT_CMD):
    logger.warning(f"Tesseract not found at {TESSERACT_CMD}, falling back to system PATH")
    TESSERACT_CMD = 'tesseract'
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def serve():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Failed to serve index.html: {str(e)}")
        return jsonify({'error': 'Application failed to load'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file exists in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Validate file
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Secure file handling with tempfile
        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            file.save(tmp.name)
            
            # Check file size
            file_size = os.path.getsize(tmp.name)
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': f'File exceeds {MAX_FILE_SIZE//1024//1024}MB limit'}), 400
            
            try:
                # Open and verify image
                with Image.open(tmp.name) as img:
                    img.verify()  # Verify without loading
                
                # Reopen for processing
                with Image.open(tmp.name) as img:
                    # Convert to RGB if needed (for CMYK images)
                    if img.mode not in ('L', 'RGB'):
                        img = img.convert('RGB')
                    
                    # Perform OCR with optimized settings
                    text = pytesseract.image_to_string(
                        img,
                        config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
                    )
                    
                    return jsonify({
                        'success': True,
                        'text': text.strip(),
                        'filename': file.filename
                    })
                    
            except Image.UnidentifiedImageError:
                return jsonify({'error': 'Invalid or corrupted image'}), 400
            
    except Exception as e:
        logger.error(f"OCR Processing Error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'OCR processing failed',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(e):
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # Configure for production
    app.run(
        host='0.0.0.0',
        port=port,
        threaded=True
    )

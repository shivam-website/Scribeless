FROM python:3.10-slim

# Install Tesseract OCR and required dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy all project files to the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the port (Render sets $PORT automatically)
EXPOSE 10000

# Start the Flask app using Gunicorn
CMD gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT

FROM python:3.10-slim

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose a default port (optional for docs only — Render injects $PORT at runtime)
EXPOSE 10000

# Run the app using shell form so $PORT gets resolved properly
CMD gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT

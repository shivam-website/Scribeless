FROM python:3.10-slim

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy code to container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app using Gunicorn with 1 worker and 120s timeout
CMD ["gunicorn", "app:app", "--workers", "1", "--timeout", "120", "--bind", "0.0.0.0:${PORT}"]

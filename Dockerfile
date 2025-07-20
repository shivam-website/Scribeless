FROM python:3.10-slim

# Install Tesseract and dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy code
COPY . .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]

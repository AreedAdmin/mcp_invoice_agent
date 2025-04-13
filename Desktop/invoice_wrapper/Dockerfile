FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["streamlit", "run", "invoice_processor.py", "--server.port=8501", "--server.address=0.0.0.0"]
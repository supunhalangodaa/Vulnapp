FROM python:3.9-slim

# Install system dependencies including ImageMagick for image processing
RUN apt-get update && apt-get install -y \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads

# Create a non-root user
RUN useradd -m vulnshop
RUN chown -R vulnshop:vulnshop /app
USER vulnshop

# Initialize the database
RUN python init_db.py

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 
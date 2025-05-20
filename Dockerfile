FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create non-root user
RUN useradd -m vulnshop

# Set proper permissions
RUN chown -R vulnshop:vulnshop /app

# Switch to non-root user
USER vulnshop

# Initialize the database
RUN python init_db.py

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 
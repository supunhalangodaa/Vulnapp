FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create files directory and add secret file
RUN mkdir -p files
RUN echo "FLAG{4_d1r3ct0ry_tr4v3rs4l_1s_n0t_s3cur3}" > files/secret.txt

# Initialize the database
RUN python init_db.py

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python", "app.py"] 
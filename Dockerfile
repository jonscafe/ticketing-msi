FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Salin file requirements.txt dan install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam container
COPY . .

# Expose port 5000
EXPOSE 5000

# Perintah untuk menjalankan aplikasi
CMD ["python", "app.py"]

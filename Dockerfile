# Base Image
FROM python:3.10-slim

# Environment Configuration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Working Directory
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY src/ src/
COPY producer.py .
COPY run_app.sh .

# Permissions
RUN chmod +x run_app.sh

# Expose FastAPI Port
EXPOSE 8000

# Entry Point
CMD ["./run_app.sh"]

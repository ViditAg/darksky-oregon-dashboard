# Dockerfile for Flask Oregon Dark Sky Dashboard
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY flask_api/ ./flask_api/
COPY shared/ ./shared/
COPY flask_api/templates/ ./flask_api/templates/

# Expose Flask port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=flask_api/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# Start Flask app
CMD ["flask", "run"]

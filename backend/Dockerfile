# Backend Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\npython manage.py migrate --noinput\nexec gunicorn --bind 0.0.0.0:8000 --workers 2 smartpharmacy.wsgi:application' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run migrations and start gunicorn
CMD ["/app/entrypoint.sh"]

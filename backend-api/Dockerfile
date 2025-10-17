# backend-api/Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (opcional pero útil)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Instala requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia código
COPY . /app

# Expone el puerto del servidor Django
EXPOSE 8000

# Ejecuta el dev server (simple y suficiente para el reto)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Usamos una imagen ligera de Python
FROM python:3.11-slim

# Evitamos que Python genere archivos basura (.pyc) y buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para PostgreSQL y otros (por si acaso)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos los requerimientos primero (para aprovechar la caché de Docker)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . /app/

# Exponemos el puerto
EXPOSE 8000

# Comando por defecto al levantar el contenedor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
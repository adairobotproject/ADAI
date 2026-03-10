# Dockerfile para RobotAtlas
# Sistema de Control de Robot con Inteligencia Artificial

FROM python:3.12-slim

# Metadatos
LABEL maintainer="RobotAtlas Team"
LABEL description="RobotAtlas - Sistema de Control de Robot con IA"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:0

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Dependencias básicas
    build-essential \
    cmake \
    git \
    wget \
    curl \
    # Dependencias para OpenCV
    libopencv-dev \
    python3-opencv \
    # Dependencias para audio
    portaudio19-dev \
    libasound2-dev \
    # Dependencias para tkinter
    python3-tk \
    tk-dev \
    # Dependencias para procesamiento de imágenes
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    # Dependencias para dlib
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    # Dependencias para Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-spa \
    # Dependencias para X11 (para GUI)
    xvfb \
    x11vnc \
    fluxbox \
    # Dependencias adicionales
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requirements primero (para cache de Docker)
COPY requirements-unix.txt /app/requirements-unix.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    # Instalar paquetes base primero
    pip install --no-cache-dir numpy scipy matplotlib pillow && \
    # Instalar OpenCV
    pip install --no-cache-dir opencv-python opencv-contrib-python && \
    # Instalar resto de dependencias
    pip install --no-cache-dir -r requirements-unix.txt || true && \
    # Intentar instalar paquetes problemáticos
    pip install --no-cache-dir dlib==19.24.6 || echo "dlib falló, continuando..." && \
    pip install --no-cache-dir PyAudio==0.2.14 || echo "PyAudio falló, continuando..." && \
    pip install --no-cache-dir face-recognition==1.3.0 || echo "face_recognition falló, continuando..." && \
    pip install --no-cache-dir mediapipe==0.10.21 || echo "mediapipe falló, continuando..."

# Copiar el resto del código de la aplicación
COPY . /app/

# Crear directorios necesarios
RUN mkdir -p /app/clases /app/data /app/logs

# Configurar permisos
RUN chmod +x /app/*.sh 2>/dev/null || true

# Exponer puertos (ajustar según necesidad)
EXPOSE 8000 8080

# Script de inicio
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Punto de entrada
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "robot_gui_conmodulos.py"]


#!/bin/bash
# ============================================
# Script para configurar Python 3.12
# RobotAtlas - Sistema de Control de Robot
# ============================================

# Desactivar cualquier venv que esté activo
if [ -n "$VIRTUAL_ENV" ]; then
    echo "[INFO] Desactivando entorno virtual existente..."
    deactivate 2>/dev/null || true
fi

echo ""
echo "============================================"
echo "  Configuración de Python 3.12"
echo "============================================"
echo ""

# Verificar si Python 3.12 está instalado
if command -v python3.12 &> /dev/null; then
    echo "[OK] Python 3.12 detectado"
    python3.12 --version
else
    echo "[ERROR] Python 3.12 no está instalado"
    echo ""
    echo "Por favor ejecuta primero:"
    echo "  macOS: brew install python@3.12"
    echo "  Linux: sudo apt-get install python3.12 python3.12-venv"
    echo ""
    exit 1
fi

# Verificar e instalar dependencias del sistema (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo ""
    echo "[INFO] Verificando dependencias del sistema para macOS..."
    
    # Verificar CMake (necesario para dlib)
    if ! command -v cmake &> /dev/null; then
        echo "[INFO] CMake no está instalado. Instalando con Homebrew..."
        if command -v brew &> /dev/null; then
            brew install cmake || echo "[ADVERTENCIA] No se pudo instalar CMake. dlib puede fallar."
        else
            echo "[ADVERTENCIA] Homebrew no está instalado. Instala CMake manualmente: brew install cmake"
        fi
    else
        echo "[OK] CMake detectado: $(cmake --version | head -n1)"
    fi
    
    # Verificar PortAudio (necesario para PyAudio)
    if ! brew list portaudio &> /dev/null 2>&1; then
        echo "[INFO] PortAudio no está instalado. Instalando con Homebrew..."
        if command -v brew &> /dev/null; then
            brew install portaudio || echo "[ADVERTENCIA] No se pudo instalar PortAudio. PyAudio puede fallar."
        else
            echo "[ADVERTENCIA] Homebrew no está instalado. Instala PortAudio manualmente: brew install portaudio"
        fi
    else
        echo "[OK] PortAudio detectado"
    fi
fi

echo ""
echo "[INFO] Eliminando entorno virtual antiguo..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "[OK] Entorno virtual antiguo eliminado"
else
    echo "[INFO] No hay entorno virtual antiguo"
fi

echo ""
echo "[INFO] Creando nuevo entorno virtual con Python 3.12..."
if ! python3.12 -m venv venv; then
    echo "[ERROR] No se pudo crear el entorno virtual"
    echo "Asegúrate de que python3.12 está instalado correctamente"
    exit 1
fi

echo "[OK] Entorno virtual creado con Python 3.12"

echo ""
echo "[INFO] Activando entorno virtual..."
if [ ! -f "venv/bin/activate" ]; then
    echo "[ERROR] No se pudo encontrar el script de activación del venv"
    exit 1
fi

source venv/bin/activate

echo ""
echo "[INFO] Verificando versión de Python en el venv..."
if ! command -v python &> /dev/null; then
    echo "[ERROR] Python no está disponible en el entorno virtual"
    exit 1
fi
python --version
echo ""

# Verificar tkinter (crítico para la GUI)
echo "[INFO] Verificando soporte de tkinter..."
if ! python -c "import tkinter" 2>/dev/null; then
    echo ""
    echo "[ERROR] tkinter no está disponible en este Python"
    echo ""
    echo "En macOS, Python instalado con Homebrew no incluye tkinter por defecto."
    echo ""
    echo "Soluciones:"
    echo "  1. Instalar python-tk:"
    echo "     brew install python-tk@3.12"
    echo ""
    echo "  2. O reinstalar Python con soporte de tkinter:"
    echo "     brew uninstall python@3.12"
    echo "     brew install python@3.12 python-tk@3.12"
    echo ""
    echo "  3. O usar el Python del sistema (si está disponible):"
    echo "     /usr/bin/python3 -m venv venv"
    echo ""
    exit 1
else
    echo "[OK] tkinter está disponible"
fi
echo ""

echo "[INFO] Actualizando pip..."
pip install --upgrade pip setuptools wheel
echo ""

# Instalar dependencias en lotes
echo "[INFO] Instalando dependencias desde requirements.txt..."
echo "Esto puede tardar varios minutos..."
echo ""

# Instalar paquetes base primero
echo "[INFO] Instalando paquetes base..."
pip install numpy scipy matplotlib pillow

# Instalar OpenCV (crítico)
echo "[INFO] Instalando OpenCV..."
pip install opencv-python opencv-contrib-python

# Instalar el resto de dependencias (solo paquetes compatibles con Unix)
echo "[INFO] Instalando resto de dependencias..."
if [ -f "requirements-unix.txt" ]; then
    pip install -r requirements-unix.txt || {
        echo "[ADVERTENCIA] Algunos paquetes fallaron durante la instalación"
    }
else
    # Si no existe requirements-unix.txt, usar requirements.txt pero ignorar errores de paquetes Windows
    pip install -r requirements.txt || {
        echo "[ADVERTENCIA] Algunos paquetes fallaron (probablemente específicos de Windows)"
        echo "[INFO] Intentando instalar paquetes individualmente..."
        # Intentar instalar sin los paquetes de Windows
        pip install $(grep -v "pywin32\|pypiwin32\|comtypes" requirements.txt | tr '\n' ' ') || true
    }
fi

# Intentar instalar paquetes problemáticos después de instalar dependencias del sistema
echo ""
echo "[INFO] Intentando instalar paquetes que requieren compilación..."

# Intentar instalar dlib (requiere CMake)
if ! python -c "import dlib" 2>/dev/null; then
    echo "[INFO] Instalando dlib (puede tardar varios minutos)..."
    pip install dlib==19.24.6 || echo "[ADVERTENCIA] dlib falló. Asegúrate de tener CMake instalado."
fi

# Intentar instalar PyAudio (requiere PortAudio)
if ! python -c "import pyaudio" 2>/dev/null; then
    echo "[INFO] Instalando PyAudio..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # En macOS, intentar con las rutas de Homebrew
        pip install PyAudio==0.2.14 || {
            echo "[ADVERTENCIA] PyAudio falló. Asegúrate de tener PortAudio instalado: brew install portaudio"
        }
    else
        pip install PyAudio==0.2.14 || echo "[ADVERTENCIA] PyAudio falló."
    fi
fi

# Intentar instalar face_recognition (depende de dlib)
if ! python -c "import face_recognition" 2>/dev/null; then
    echo "[INFO] Instalando face_recognition..."
    pip install face-recognition==1.3.0 || echo "[ADVERTENCIA] face_recognition falló (requiere dlib)."
fi

# Intentar instalar mediapipe
if ! python -c "import mediapipe" 2>/dev/null; then
    echo "[INFO] Instalando mediapipe..."
    pip install mediapipe==0.10.21 || echo "[ADVERTENCIA] mediapipe falló."
fi

# Verificar instalación de paquetes críticos
echo ""
echo "[INFO] Verificando instalación de paquetes críticos..."
python -c "import cv2; print('✓ OpenCV:', cv2.__version__)" || echo "✗ OpenCV no instalado"
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" || echo "✗ NumPy no instalado"
python -c "import matplotlib; print('✓ Matplotlib:', matplotlib.__version__)" || echo "✗ Matplotlib no instalado"
python -c "import mediapipe; print('✓ MediaPipe instalado')" || echo "✗ MediaPipe no instalado"
python -c "import face_recognition; print('✓ Face Recognition instalado')" || echo "✗ Face Recognition no instalado"
python -c "import pygame; print('✓ Pygame instalado')" || echo "✗ Pygame no instalado"
python -c "import dotenv; print('✓ python-dotenv instalado')" || echo "✗ python-dotenv no instalado"
python -c "import openai; print('✓ OpenAI instalado')" || echo "✗ OpenAI no instalado"
python -c "import fitz; print('✓ PyMuPDF instalado')" || echo "✗ PyMuPDF no instalado"
python -c "import requests; print('✓ Requests instalado')" || echo "✗ Requests no instalado"

echo ""
echo "============================================"
echo "  Configuración Completada"
echo "============================================"
echo ""
echo "Para ejecutar el proyecto:"
echo "  1. Activa el entorno virtual: source venv/bin/activate"
echo "  2. Ejecuta: python robot_gui_conmodulos.py"
echo ""
echo "O usa el script run.sh"
echo ""

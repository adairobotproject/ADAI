#!/bin/bash
# ============================================
# Script para configurar Python 3.12
# RobotAtlas - Sistema de Control de Robot
# ============================================

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
    echo "[INFO] Python 3.12 no está instalado"
    echo ""
    echo "Por favor ejecuta primero:"
    echo "  brew install python@3.12"
    echo ""
    exit 1
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
python3.12 -m venv venv

if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo crear el entorno virtual"
    exit 1
fi

echo "[OK] Entorno virtual creado con Python 3.12"

echo ""
echo "[INFO] Activando entorno virtual..."
source venv/bin/activate

echo ""
echo "[INFO] Verificando versión de Python en el venv..."
python --version

echo ""
echo "[INFO] Actualizando pip..."
pip install --upgrade pip

echo ""
echo "[INFO] Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Hubo errores al instalar algunas dependencias"
    echo "Algunas dependencias pueden requerir instalación manual"
    echo ""
    echo "Intentando instalar dependencias opcionales..."
    pip install ikpy --no-deps 2>/dev/null || true
else
    echo ""
    echo "[OK] Todas las dependencias instaladas correctamente"
fi

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


#!/bin/bash
# ============================================
# Script de Ejecución para Linux/Mac
# RobotAtlas - Sistema de Control de Robot
# ============================================

# Verificar que el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "[ERROR] El entorno virtual no existe"
    echo "Ejecuta ./setup.sh primero para configurar el proyecto"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar que el archivo principal existe
if [ ! -f "robot_gui_conmodulos.py" ]; then
    echo "[ERROR] No se encuentra robot_gui_conmodulos.py"
    echo "Asegúrate de estar en el directorio correcto"
    exit 1
fi

echo ""
echo "============================================"
echo "  Iniciando RobotAtlas..."
echo "============================================"
echo ""

# Ejecutar la aplicación
python robot_gui_conmodulos.py

# Si hay error, mostrar mensaje
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] La aplicación se cerró con errores"
fi



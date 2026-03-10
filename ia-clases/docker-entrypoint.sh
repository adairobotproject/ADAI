#!/bin/bash
# Script de entrada para Docker

set -e

echo "============================================"
echo "  RobotAtlas - Iniciando en Docker"
echo "============================================"
echo ""

# Verificar que Python está disponible
if ! command -v python &> /dev/null; then
    echo "[ERROR] Python no está disponible"
    exit 1
fi

echo "[OK] Python detectado: $(python --version)"
echo ""

# Verificar paquetes críticos
echo "[INFO] Verificando paquetes instalados..."
python -c "import cv2; print('✓ OpenCV:', cv2.__version__)" || echo "✗ OpenCV no disponible"
python -c "import numpy; print('✓ NumPy:', numpy.__version__)" || echo "✗ NumPy no disponible"
python -c "import matplotlib; print('✓ Matplotlib:', matplotlib.__version__)" || echo "✗ Matplotlib no disponible"
echo ""

# Configurar X11 si es necesario
if [ -n "$DISPLAY" ] && [ "$DISPLAY" != ":99" ]; then
    echo "[INFO] Configurando display X11: $DISPLAY"
    xhost +local:docker 2>/dev/null || true
fi

# Crear directorios si no existen
mkdir -p /app/clases /app/data /app/logs /app/config

# Ejecutar el comando pasado como argumento
echo "[INFO] Ejecutando: $@"
echo ""
exec "$@"


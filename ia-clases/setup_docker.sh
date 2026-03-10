#!/bin/bash
# ============================================
# Script de Setup para Docker
# RobotAtlas - Sistema de Control de Robot
# ============================================

echo ""
echo "============================================"
echo "  RobotAtlas - Configuración con Docker"
echo "============================================"
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker no está instalado"
    echo ""
    echo "Por favor instala Docker:"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    echo "  Windows: https://docs.docker.com/desktop/install/windows-install/"
    echo ""
    exit 1
fi

echo "[OK] Docker detectado: $(docker --version)"
echo ""

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "[ERROR] Docker Compose no está instalado"
    echo ""
    echo "Por favor instala Docker Compose:"
    echo "  https://docs.docker.com/compose/install/"
    echo ""
    exit 1
fi

echo "[OK] Docker Compose detectado"
echo ""

# Verificar permisos de Docker
if ! docker ps &> /dev/null; then
    echo "[ERROR] No tienes permisos para ejecutar Docker"
    echo ""
    echo "Soluciones:"
    echo "  1. Agrega tu usuario al grupo docker:"
    echo "     sudo usermod -aG docker $USER"
    echo "     (luego cierra sesión y vuelve a entrar)"
    echo ""
    echo "  2. O ejecuta con sudo (no recomendado)"
    echo ""
    exit 1
fi

echo "[OK] Permisos de Docker verificados"
echo ""

# Detectar sistema operativo
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "[INFO] Sistema detectado: macOS"
    echo "[INFO] Para GUI, necesitarás XQuartz instalado"
    echo ""
    if ! command -v xquartz &> /dev/null && ! brew list --cask xquartz &> /dev/null 2>&1; then
        echo "[ADVERTENCIA] XQuartz no está instalado"
        echo "  Instala con: brew install --cask xquartz"
        echo "  Luego reinicia tu Mac"
        echo ""
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[INFO] Sistema detectado: Linux"
    echo "[INFO] Para GUI, asegúrate de tener X11 configurado"
    echo ""
fi

# Construir la imagen
echo "[INFO] Construyendo imagen de Docker..."
echo "Esto puede tardar varios minutos la primera vez..."
echo ""

if docker-compose build 2>/dev/null || docker compose build 2>/dev/null; then
    echo ""
    echo "[OK] Imagen construida correctamente"
else
    echo ""
    echo "[ERROR] Error al construir la imagen"
    exit 1
fi

echo ""
echo "============================================"
echo "  Configuración Completada"
echo "============================================"
echo ""
echo "Para ejecutar RobotAtlas con Docker:"
echo ""
echo "  Modo normal (con GUI):"
echo "    docker-compose up"
echo ""
echo "  Modo headless (sin GUI):"
echo "    docker-compose --profile headless up robotatlas-headless"
echo ""
echo "  Modo detached (en segundo plano):"
echo "    docker-compose up -d"
echo ""
echo "  Ver logs:"
echo "    docker-compose logs -f"
echo ""
echo "  Detener:"
echo "    docker-compose down"
echo ""
echo "Para más información, consulta DOCKER.md"
echo ""


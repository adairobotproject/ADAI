#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script para verificar por qué las clases no envían requests al ESP32
"""

import os
import sys
import traceback

# Agregar el directorio actual al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔍 DEBUG: Verificando ESP32 en clases")
print("=" * 50)

# 1. Verificar importaciones
print("\n📦 1. Verificando importaciones...")
try:
    from services.esp32_services.esp32_client import ESP32Client
    print("✅ ESP32Client importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32Client: {e}")
    sys.exit(1)

try:
    from services.esp32_services.esp32_config_binary import ESP32BinaryConfig
    print("✅ ESP32BinaryConfig importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32BinaryConfig: {e}")
    sys.exit(1)

# 2. Verificar configuración
print("\n⚙️ 2. Verificando configuración ESP32...")
try:
    config = ESP32BinaryConfig()
    config_data = config.load_config()

    if config_data:
        print(f"✅ Configuración cargada: {config_data.host}:{config_data.port}")
        host = config_data.host
        port = config_data.port
    else:
        print("⚠️ No se encontró configuración, usando valores por defecto")
        host = "192.168.1.100"
        port = 80

except Exception as e:
    print(f"❌ Error cargando configuración: {e}")
    traceback.print_exc()
    host = "192.168.1.100"
    port = 80

# 3. Probar conexión como lo hace el sequence builder
print("
🔌 3. Probando conexión (estilo sequence builder)...")
try:
    client = ESP32Client()
    client.host = host
    client.port = port

    print(f"📍 Cliente creado: {client.host}:{client.port}")

    success = client.connect()
    if success:
        print("✅ Conexión exitosa")
    else:
        print("❌ Error en conexión")
        sys.exit(1)

except Exception as e:
    print(f"❌ Error conectando: {e}")
    traceback.print_exc()
    sys.exit(1)

# 4. Probar envío de comando
print("
📡 4. Probando envío de comando...")
try:
    print("🧪 Enviando comando de test...")
    response = client.send_movement(10, 40, 80, 90, 80, 80, 45)

    if response:
        print("✅ Comando enviado correctamente")
    else:
        print("❌ Error enviando comando")

except Exception as e:
    print(f"❌ Error enviando comando: {e}")
    traceback.print_exc()

# 5. Comparar con el patrón de clases
print("
🏫 5. Probando patrón de clases (conectar/desconectar)...")
try:
    # Crear nuevo cliente como lo hace main.py
    test_client = ESP32Client()
    test_client.host = host
    test_client.port = port

    print("🔌 Conectando nuevo cliente...")
    success = test_client.connect()

    if success:
        print("✅ Nuevo cliente conectado")

        # Enviar comando
        print("📡 Enviando comando desde nuevo cliente...")
        response = test_client.send_movement(10, 40, 80, 90, 80, 80, 45)

        if response:
            print("✅ Comando enviado correctamente desde nuevo cliente")
        else:
            print("❌ Error enviando comando desde nuevo cliente")

        # Desconectar
        print("🔌 Desconectando nuevo cliente...")
        test_client.disconnect()
        print("✅ Nuevo cliente desconectado")

    else:
        print("❌ Error conectando nuevo cliente")

except Exception as e:
    print(f"❌ Error en patrón de clases: {e}")
    traceback.print_exc()

# 6. Verificar secuencias disponibles
print("
📋 6. Verificando secuencias disponibles...")
sequences_dir = os.path.join(current_dir, "sequences")

if os.path.exists(sequences_dir):
    sequences = []
    for file in os.listdir(sequences_dir):
        if file.endswith('.json'):
            sequences.append(file)

    print(f"📂 Secuencias encontradas: {len(sequences)}")
    for seq in sequences:
        print(f"  📄 {seq}")
else:
    print(f"❌ Directorio de secuencias no encontrado: {sequences_dir}")

# 7. Limpiar
print("
🧹 7. Limpiando...")
try:
    client.disconnect()
    print("✅ Cliente desconectado")
except Exception as e:
    print(f"⚠️ Error desconectando: {e}")

print("
🎯 RESULTADO DEL DEBUG:")
print("-" * 30)
print("Si ves ✅ en todos los pasos anteriores, el problema está en:")
print("1. La llamada a execute_esp32_sequence() desde las clases")
print("2. La configuración de rutas en main.py")
print("3. Los archivos de secuencia JSON")
print("4. La configuración del ESP32 (host/port)")
print("\nSi hay algún ❌, ese es el problema principal.")

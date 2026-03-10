#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para ESP32 connection
"""

import os
import sys

# Agregar servicios al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, "services", "esp32_services"))

print("🧪 Test simple de ESP32")

try:
    from esp32_client import ESP32Client
    print("✅ ESP32Client importado correctamente")

    # Crear instancia
    client = ESP32Client()
    print(f"📍 Cliente creado: {client.host}:{client.port}")

    # Intentar conectar
    print("🔌 Intentando conectar...")
    success = client.connect()

    if success:
        print("✅ ¡Conexión exitosa!")
    else:
        print("❌ Error en conexión")

    # Probar comando simple
    print("🧪 Probando comando...")
    response = client.send_movement(0, 0, 0, 0, 0, 0, 0)

    if response:
        print("✅ Comando enviado correctamente")
    else:
        print("❌ Error enviando comando")

    # Desconectar
    client.disconnect()
    print("🔌 Desconectado")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

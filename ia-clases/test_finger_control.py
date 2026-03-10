#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para control de dedos en ESP32
"""

import os
import sys

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from services.esp32_services.esp32_client import ESP32Client
    print("✅ ESP32Client importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32Client: {e}")
    sys.exit(1)

def test_finger_control():
    """Probar control de dedos"""

    print("🧪 Probando control de dedos...")

    # Crear cliente ESP32
    client = ESP32Client()

    # Configurar host/port (usar valores por defecto si no hay configuración)
    config_path = os.path.join(current_dir, "services", "esp32_services", "esp32_config_binary.py")
    if os.path.exists(config_path):
        try:
            from services.esp32_services.esp32_config_binary import ESP32BinaryConfig
            config = ESP32BinaryConfig()
            config_data = config.load_config()
            if config_data:
                client.host = config_data.host
                client.port = config_data.port
                print(f"✅ Configuración cargada: {client.host}:{client.port}")
            else:
                print("⚠️ Usando configuración por defecto")
        except:
            print("⚠️ Error cargando configuración, usando valores por defecto")

    # Intentar conectar
    print(f"🔌 Conectando a ESP32 en {client.host}:{client.port}...")
    success = client.connect()

    if not success:
        print("❌ No se pudo conectar al ESP32")
        print("💡 Asegúrate de que:")
        print("   - El ESP32 esté encendido")
        print("   - Esté conectado a la misma red WiFi")
        print(f"   - La IP del ESP32 sea {client.host}")
        return

    print("✅ Conexión exitosa")

    # Probar diferentes dedos y posiciones
    test_cases = [
        ("izquierda", "pulgar", 90),
        ("izquierda", "indice", 45),
        ("derecha", "medio", 120),
        ("derecha", "anular", 60),
        ("izquierda", "menique", 30),
        ("derecha", "pulgar", 0),
        ("derecha", "indice", 180),
    ]

    print("\n👐 Probando control de dedos:")
    print("-" * 50)

    for hand, finger, angle in test_cases:
        print(f"🤖 Probando: Mano={hand}, Dedo={finger}, Ángulo={angle}°")

        try:
            success = client.send_finger_control(hand, finger, angle)

            if success:
                print(f"   ✅ Comando enviado correctamente")
            else:
                print(f"   ❌ Error enviando comando")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Pequeña pausa entre comandos
        import time
        time.sleep(0.5)

    print("-" * 50)
    print("🎯 Test de dedos completado")

    # Desconectar
    client.disconnect()
    print("🔌 Desconectado del ESP32")

if __name__ == "__main__":
    test_finger_control()

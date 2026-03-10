#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar la cadena completa de comunicación de dedos:
Python → ESP32 → Mega → Uno → Servo
"""

import os
import sys
import time

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from services.esp32_services.esp32_client import ESP32Client
    print("✅ ESP32Client importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32Client: {e}")
    sys.exit(1)

def test_finger_chain():
    """Probar la cadena completa de comunicación de dedos"""

    print("🔍 DIAGNÓSTICO DE CADENA DE DEDOS")
    print("=" * 50)

    # Crear cliente ESP32
    client = ESP32Client()

    # Configurar host/port desde configuración
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
        print("⚠️ Error cargando configuración")

    print("\n📋 PRUEBA 1: Conexión básica al ESP32")
    print("-" * 40)

    success = client.connect()
    if not success:
        print("❌ No se pudo conectar al ESP32")
        print("💡 Verifica que:")
        print("   - El ESP32 esté encendido")
        print("   - Esté en la misma red WiFi")
        print(f"   - La IP del ESP32 sea {client.host}")
        return

    print("✅ Conexión exitosa")

    print("\n📋 PRUEBA 2: Comando básico al ESP32")
    print("-" * 40)

    # Probar un comando básico primero
    response = client.send_movement(10, 40, 80, 90, 80, 80, 45)
    if response:
        print("✅ Comando básico funciona")
    else:
        print("❌ Comando básico falla")
        return

    print("\n📋 PRUEBA 3: Comando de dedo individual")
    print("-" * 40)

    print("👐 Probando dedo: Mano derecha, Pulgar, 90°")
    success = client.send_finger_control("derecha", "pulgar", 90)

    if success:
        print("✅ Comando de dedo enviado correctamente")
        print("💡 Si el dedo NO se mueve, el problema está en:")
        print("   1. ESP32 → Mega (UART1)")
        print("   2. Mega → Uno (Serial1)")
        print("   3. Uno procesando comando")
        print("   4. Servo conectado correctamente")
    else:
        print("❌ Comando de dedo falló")
        print("💡 El problema está en la comunicación Python → ESP32")

    print("\n📋 PRUEBA 4: Múltiples dedos")
    print("-" * 40)

    test_fingers = [
        ("izquierda", "indice", 45),
        ("derecha", "medio", 120),
        ("izquierda", "anular", 60),
    ]

    for hand, finger, angle in test_fingers:
        print(f"👐 Probando {hand} {finger} → {angle}°")
        success = client.send_finger_control(hand, finger, angle)
        if success:
            print("   ✅ Comando enviado")
        else:
            print("   ❌ Comando falló")

        time.sleep(1)  # Pausa entre comandos

    print("\n📋 PRUEBA 5: Verificación de respuestas")
    print("-" * 40)

    print("🔍 Verifica en los monitores serie:")
    print("   - ESP32: Debe mostrar '[TX MEGA] DEDO M=... D=... ANG=...'")
    print("   - Mega: Debe mostrar '[UNO TX] DEDO M=... D=... ANG=...'")
    print("   - Uno: Debe mostrar 'UNO:Dedo ... movido a ...°'")
    print("   - Si no ves estos mensajes, hay un problema de comunicación")

    print("\n🎯 RESUMEN DEL DIAGNÓSTICO:")
    print("-" * 40)
    print("1. ✅ Python → ESP32: Si llega aquí, funciona")
    print("2. 🔍 ESP32 → Mega: Verificar logs del ESP32")
    print("3. 🔍 Mega → Uno: Verificar logs del Mega")
    print("4. 🔍 Uno → Servo: Verificar logs del Uno")

    # Desconectar
    client.disconnect()
    print("\n🔌 Desconectado del ESP32")

if __name__ == "__main__":
    test_finger_chain()

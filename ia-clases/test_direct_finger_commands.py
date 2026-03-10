#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test directo de comandos de dedos para diagnosticar problemas en ESP32 → Mega → Uno
"""

import os
import sys
import time
import requests

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_direct_finger_commands():
    """Enviar comandos directos de dedos al ESP32 para probar la cadena completa"""

    print("🔧 TEST DIRECTO DE COMANDOS DE DEDOS")
    print("=" * 50)

    # Configuración del ESP32
    esp32_host = "10.71.47.237"  # Cambiar si es diferente
    esp32_port = 80
    base_url = f"http://{esp32_host}:{esp32_port}"

    print(f"📡 Conectando a ESP32: {base_url}")

    # Verificar conexión básica
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ ESP32 responde correctamente")
        else:
            print(f"❌ ESP32 responde con código: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error conectando a ESP32: {e}")
        return

    print("\n🧪 ENVIANDO COMANDOS DE DEDOS DIRECTOS:")
    print("-" * 50)

    # Lista de comandos de dedos para probar
    finger_commands = [
        {"mano": "derecha", "dedo": "pulgar", "angulo": "90"},
        {"mano": "izquierda", "dedo": "indice", "angulo": "45"},
        {"mano": "derecha", "dedo": "medio", "angulo": "120"},
        {"mano": "izquierda", "dedo": "anular", "angulo": "60"},
        {"mano": "derecha", "dedo": "menique", "angulo": "30"},
    ]

    for i, cmd in enumerate(finger_commands, 1):
        mano = cmd["mano"]
        dedo = cmd["dedo"]
        angulo = cmd["angulo"]

        print(f"\n👐 Comando {i}: {mano} {dedo} → {angulo}°")

        try:
            # Enviar comando al endpoint de dedos
            url = f"{base_url}/manos/dedo"
            data = {
                "mano": mano,
                "dedo": dedo,
                "angulo": angulo
            }

            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")

            response = requests.post(url, data=data, timeout=5)

            if response.status_code == 200:
                print(f"   ✅ Respuesta ESP32: {response.text.strip()}")
            else:
                print(f"   ❌ Código HTTP: {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Pausa entre comandos
        time.sleep(1)

    print("\n🔍 INSTRUCCIONES DE DIAGNÓSTICO:")
    print("-" * 50)
    print("1. Abre el Monitor Serie del ESP32 (Arduino IDE)")
    print("2. Busca mensajes como:")
    print("   - [TX MEGA] DEDO M=derecha D=pulgar ANG=90")
    print("3. Si NO ves estos mensajes → Problema: ESP32 → Mega (UART)")
    print("")
    print("4. Abre el Monitor Serie del Mega (Arduino IDE)")
    print("5. Busca mensajes como:")
    print("   - [UNO TX] DEDO M=derecha D=pulgar ANG=90")
    print("6. Si NO ves estos mensajes → Problema: Mega → Uno (Serial1)")
    print("")
    print("7. Abre el Monitor Serie del Uno (Arduino IDE)")
    print("8. Busca mensajes como:")
    print("   - UNO:Dedo pulgar de mano derecha movido a 90°")
    print("9. Si NO ves estos mensajes → Problema: Uno procesando comando")
    print("")
    print("10. Si ves todos los mensajes pero el dedo no se mueve:")
    print("    → Problema: Servo desconectado o sin alimentación")

    print("\n🎯 POSIBLES SOLUCIONES:")
    print("-" * 50)
    print("• Verificar cables UART entre ESP32 y Mega")
    print("• Verificar cables Serial entre Mega y Uno")
    print("• Verificar alimentación de servos (5V)")
    print("• Verificar conexiones de servos a pines correctos")
    print("• Verificar configuración de pines en Uno.ino")

if __name__ == "__main__":
    test_direct_finger_commands()

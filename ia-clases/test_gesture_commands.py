#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que los comandos de gestos funcionan correctamente
"""

import os
import sys
import time
import requests

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_gesture_commands():
    """Probar comandos de gestos que estaban fallando"""

    print("👐 TEST DE COMANDOS DE GESTOS")
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

    print("\n🧪 Probando comandos de gestos que fallaban:")

    # Lista de gestos problemáticos
    gestures_to_test = [
        {"mano": "ambas", "gesto": "ABRIR"},
        {"mano": "ambas", "gesto": "CERRAR"},
        {"mano": "derecha", "gesto": "abrir"},
        {"mano": "izquierda", "gesto": "cerrar"},
        {"mano": "derecha", "gesto": "PAZ"},
        {"mano": "izquierda", "gesto": "ROCK"},
    ]

    for i, gesture in enumerate(gestures_to_test, 1):
        mano = gesture["mano"]
        gesto = gesture["gesto"]

        print(f"\n👐 Test {i}: {mano} {gesto}")

        try:
            # Probar endpoint /manos/gesto
            url = f"{base_url}/manos/gesto"
            data = {
                "mano": mano,
                "gesto": gesto
            }

            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")

            response = requests.post(url, data=data, timeout=5)

            if response.status_code == 200:
                print(f"   ✅ Respuesta ESP32: {response.text.strip()}")
                print("   💡 El comando debería llegar al Uno como:")
                print(f"      MANO M={mano} A={gesto.lower()}")
            else:
                print(f"   ❌ Código HTTP: {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        time.sleep(2)  # Pausa entre comandos

    print("\n🔍 MONITOREO ESP32:")
    print("-" * 40)
    print("Abre el Monitor Serie del ESP32 y deberías ver:")
    print("   [TX MEGA] MANO M=ambas A=abrir")
    print("   [TX MEGA] MANO M=ambas A=cerrar")
    print("   (y otros gestos)")

    print("\n🔍 MONITOREO UNO:")
    print("-" * 40)
    print("Abre el Monitor Serie del Uno y deberías ver:")
    print("   UNO:Mano ambas abierta")
    print("   UNO:Mano ambas cerrada")
    print("   UNO:Gesto de paz con mano derecha")
    print("   (etc.)")

    print("\n🎯 RESULTADO ESPERADO:")
    print("-" * 40)
    print("✅ Si ves todos los mensajes, los gestos funcionan")
    print("❌ Si ves 'Acción no reconocida', aún hay problemas")
    print("🤖 Si los mensajes llegan pero los dedos no se mueven:")
    print("   → Verificar conexiones de servos y alimentación")

if __name__ == "__main__":
    test_gesture_commands()

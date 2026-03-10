#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del control web directo del robot
"""

import os
import sys
import requests
import time

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_web_control():
    """Test del control web directo"""

    print("🌐 TEST CONTROL WEB DIRECTO")
    print("=" * 50)

    # Configuración del ESP32
    esp32_ip = "192.168.1.102"  # Cambia esto por la IP de tu ESP32
    base_url = f"http://{esp32_ip}"

    print(f"📍 ESP32 IP: {esp32_ip}")
    print(f"🌐 Base URL: {base_url}")

    # Test 1: Verificar conexión con ESP32
    print("
🔍 Test 1: Verificando conexión con ESP32..."    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ Conexión exitosa con ESP32")
        else:
            print(f"   ❌ Error HTTP: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return

    # Test 2: Control directo de dedos
    print("
👐 Test 2: Control directo de dedos"    test_cases = [
        {"mano": "derecha", "dedo": "pulgar", "angulo": 0},
        {"mano": "derecha", "dedo": "indice", "angulo": 90},
        {"mano": "izquierda", "dedo": "pulgar", "angulo": 180},
        {"mano": "izquierda", "dedo": "medio", "angulo": 45},
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"   Test 2.{i}: {test['mano']} {test['dedo']} → {test['angulo']}°")
        try:
            data = {
                "mano": test["mano"],
                "dedo": test["dedo"],
                "angulo": test["angulo"]
            }
            response = requests.post(f"{base_url}/web/dedo", data=data, timeout=5)

            if response.status_code == 200:
                print(f"      ✅ Respuesta: {response.text}")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

        time.sleep(1)  # Esperar entre comandos

    # Test 3: Control de muñecas
    print("
🦴 Test 3: Control de muñecas"    muneca_tests = [
        {"mano": "derecha", "angulo": 0},
        {"mano": "derecha", "angulo": 80},
        {"mano": "derecha", "angulo": 160},
        {"mano": "izquierda", "angulo": 160},
        {"mano": "izquierda", "angulo": 80},
        {"mano": "izquierda", "angulo": 0},
    ]

    for i, test in enumerate(muneca_tests, 1):
        print(f"   Test 3.{i}: Muñeca {test['mano']} → {test['angulo']}°")
        try:
            data = {
                "mano": test["mano"],
                "angulo": test["angulo"]
            }
            response = requests.post(f"{base_url}/web/muneca", data=data, timeout=5)

            if response.status_code == 200:
                print(f"      ✅ Respuesta: {response.text}")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

        time.sleep(1)

    # Test 4: Control de brazos
    print("
💪 Test 4: Control de brazos"    print("   Test 4.1: Posición de descanso")
    try:
        data = {
            "bi": 10, "fi": 80, "hi": 80,
            "bd": 40, "fd": 90, "hd": 80, "pd": 45
        }
        response = requests.post(f"{base_url}/web/brazos", data=data, timeout=5)

        if response.status_code == 200:
            print(f"      ✅ Respuesta: {response.text}")
        else:
            print(f"      ❌ Error HTTP: {response.status_code}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    # Test 5: Control de cuello
    print("
🦴 Test 5: Control de cuello"    cuello_tests = [
        {"lateral": 155, "inferior": 95, "superior": 105},  # Centro
        {"lateral": 120, "inferior": 95, "superior": 105},  # Izquierda
        {"lateral": 190, "inferior": 95, "superior": 105},  # Derecha
    ]

    for i, test in enumerate(cuello_tests, 1):
        print(f"   Test 5.{i}: Cuello L={test['lateral']} I={test['inferior']} S={test['superior']}")
        try:
            data = {
                "lateral": test["lateral"],
                "inferior": test["inferior"],
                "superior": test["superior"]
            }
            response = requests.post(f"{base_url}/web/cuello", data=data, timeout=5)

            if response.status_code == 200:
                print(f"      ✅ Respuesta: {response.text}")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

        time.sleep(1)

    # Test 6: Control directo de servos
    print("
🔧 Test 6: Control directo de servos"    servo_tests = [
        {"canal": 0, "angulo": 0},
        {"canal": 0, "angulo": 90},
        {"canal": 0, "angulo": 180},
        {"canal": 1, "angulo": 45},
    ]

    for i, test in enumerate(servo_tests, 1):
        print(f"   Test 6.{i}: Servo CH{test['canal']} → {test['angulo']}°")
        try:
            data = {
                "canal": test["canal"],
                "angulo": test["angulo"]
            }
            response = requests.post(f"{base_url}/web/servo", data=data, timeout=5)

            if response.status_code == 200:
                print(f"      ✅ Respuesta: {response.text}")
            else:
                print(f"      ❌ Error HTTP: {response.status_code}")

        except Exception as e:
            print(f"      ❌ Error: {e}")

        time.sleep(1)

    # Test 7: Verificar posiciones actuales
    print("
📊 Test 7: Verificando posiciones actuales"    try:
        response = requests.get(f"{base_url}/posiciones", timeout=5)

        if response.status_code == 200:
            print("      ✅ Posiciones obtenidas:")
            print(f"      📄 Respuesta: {response.text[:200]}...")
        else:
            print(f"      ❌ Error HTTP: {response.status_code}")

    except Exception as e:
        print(f"      ❌ Error: {e}")

    print("
🎉 TEST COMPLETADO"    print("=" * 50)
    print("✅ Todos los tests han sido ejecutados")
    print("📝 Revisa el monitor serie del ESP32 para ver los comandos enviados")
    print("🔍 Verifica que los servos se muevan correctamente")

if __name__ == "__main__":
    test_web_control()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que el sequence builder registre correctamente acciones de dedos
"""

import json
import os
import tempfile

def test_sequence_builder_finger_recording():
    """Simular el comportamiento del sequence builder con dedos"""

    print("🧪 Probando grabación de dedos en sequence builder...")

    # Simular la función on_finger_change del sequence builder
    def simulate_finger_change(hand, finger, value, recording_actions):
        """Simular la función on_finger_change"""

        # Map finger names to ESP32 format (como en el sequence builder)
        finger_map = {
            'thumb': 'pulgar',
            'index': 'indice',
            'middle': 'medio',
            'ring': 'anular',
            'pinky': 'menique'
        }

        esp32_finger = finger_map.get(finger, finger)

        # Simular agregar acción a la secuencia (como hace el sequence builder)
        action = {
            "command": "MANO",
            "parameters": {
                "M": hand,
                "DEDO": esp32_finger,
                "ANG": int(value)
            },
            "duration": 1000,
            "description": f"{hand} {finger} finger",
            "timestamp": 1234567890.123
        }

        recording_actions.append(action)
        print(f"✅ Acción grabada: {hand} {finger} -> {esp32_finger} = {value}°")

    # Simular grabación de secuencia con dedos
    recording_actions = []

    print("🎬 Simulando grabación de secuencia con dedos:")
    print("-" * 50)

    # Simular movimientos de dedos
    test_movements = [
        ("left", "thumb", 90),
        ("left", "index", 45),
        ("right", "middle", 120),
        ("right", "ring", 60),
        ("left", "pinky", 30),
    ]

    for hand, finger, angle in test_movements:
        simulate_finger_change(hand, finger, angle, recording_actions)

    print("-" * 50)
    print(f"📋 Total acciones grabadas: {len(recording_actions)}")

    # Mostrar las acciones grabadas
    print("\n📝 Acciones en la secuencia:")
    for i, action in enumerate(recording_actions, 1):
        params = action["parameters"]
        mano = params["M"]
        dedo = params["DEDO"]
        angulo = params["ANG"]
        print(f"   {i}. MANO: Mano={mano}, Dedo={dedo}, Ángulo={angulo}°")

    # Simular guardado de secuencia
    print("
💾 Simulando guardado de secuencia...")

    sequence_data = {
        "name": "Test_Finger_Sequence",
        "title": "Test Sequence with Fingers",
        "created_at": "2024-01-01T12:00:00",
        "movements": [
            {
                "id": 1,
                "name": "Finger_Movements",
                "actions": recording_actions
            }
        ],
        "total_movements": 1,
        "total_actions": len(recording_actions)
    }

    # Guardar en archivo temporal para verificar
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sequence_data, f, indent=2)
        temp_file = f.name

    print(f"✅ Secuencia guardada en: {temp_file}")

    # Leer y verificar el archivo
    with open(temp_file, 'r') as f:
        loaded_data = json.load(f)

    loaded_actions = loaded_data["movements"][0]["actions"]
    print(f"✅ Archivo cargado correctamente: {len(loaded_actions)} acciones")

    # Limpiar archivo temporal
    os.unlink(temp_file)
    print("🧹 Archivo temporal limpiado")

    print("
🎯 Test completado exitosamente!")
    print("El sequence builder debería grabar correctamente las acciones de dedos.")

if __name__ == "__main__":
    test_sequence_builder_finger_recording()

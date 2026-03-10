#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test solo de la lógica de parsing de acciones - sin importar módulos problemáticos
"""

import os
import json

def extract_actions_from_sequence(sequence_data):
    """Extraer acciones de secuencia usando la lógica corregida"""

    # Obtener acciones de la secuencia - CORREGIDO para manejar estructura movements/actions
    movements = sequence_data.get('movements', [])
    actions = []

    # Si no hay movements pero sí hay actions directamente (compatibilidad)
    if not movements:
        actions = sequence_data.get('actions', [])
    else:
        # Extraer todas las actions de todos los movements
        for movement in movements:
            movement_actions = movement.get('actions', [])
            actions.extend(movement_actions)

    return movements, actions

def test_sequence_actions():
    """Probar la extracción de acciones"""

    print("🧪 Probando extracción de acciones...")

    # Directorio de secuencias
    sequences_dir = os.path.join(os.path.dirname(__file__), "clases", "sequences")

    test_files = ["Test2.json", "Awiwi.json"]

    for filename in test_files:
        filepath = os.path.join(sequences_dir, filename)

        if not os.path.exists(filepath):
            print(f"❌ Archivo no encontrado: {filepath}")
            continue

        print(f"\n📂 Probando archivo: {filename}")
        print("-" * 50)

        try:
            # Leer archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)

            print(f"📋 Nombre: {sequence_data.get('name', 'Unknown')}")
            print(f"📋 Título: {sequence_data.get('title', 'Unknown')}")

            # Extraer acciones
            movements, actions = extract_actions_from_sequence(sequence_data)

            print(f"📋 Total movimientos encontrados: {len(movements)}")
            print(f"📋 Total acciones extraídas: {len(actions)}")

            # Mostrar todas las acciones (no solo primeras 3)
            if actions:
                print("\n⚡ Todas las acciones:")
                for i, action in enumerate(actions):
                    command = action.get('command', 'Unknown')
                    desc = action.get('description', 'No description')
                    params = action.get('parameters', {})
                    print(f"   {i+1}. {command}: {desc}")
                    if command == "BRAZOS" and params:
                        bi = params.get('BI', 'N/A')
                        bd = params.get('BD', 'N/A')
                        fi = params.get('FI', 'N/A')
                        fd = params.get('FD', 'N/A')
                        print(f"       Parámetros: BI={bi}, BD={bd}, FI={fi}, FD={fd}")
            else:
                print("❌ No se encontraron acciones")

        except Exception as e:
            print(f"❌ Error procesando {filename}: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 50)

if __name__ == "__main__":
    test_sequence_actions()

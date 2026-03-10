#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de parsing de secuencias JSON corregido
"""

import os
import sys
import json

def test_sequence_parsing():
    """Probar el parsing de secuencias con la nueva lógica"""

    print("🧪 Probando parsing de secuencias...")

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

            # Aplicar la lógica corregida
            movements = sequence_data.get('movements', [])
            actions = []

            # Si no hay movements pero sí hay actions directamente (compatibilidad)
            if not movements:
                actions = sequence_data.get('actions', [])
                print("📋 Estructura: actions directas")
            else:
                # Extraer todas las actions de todos los movements
                for movement in movements:
                    movement_actions = movement.get('actions', [])
                    actions.extend(movement_actions)
                print(f"📋 Estructura: {len(movements)} movements")

            print(f"📋 Total movimientos encontrados: {len(movements)}")
            print(f"📋 Total acciones extraídas: {len(actions)}")

            # Mostrar primeras acciones
            if actions:
                print("\n⚡ Primeras acciones:")
                for i, action in enumerate(actions[:3]):  # Solo primeras 3
                    command = action.get('command', 'Unknown')
                    desc = action.get('description', 'No description')
                    print(f"   {i+1}. {command}: {desc}")

                if len(actions) > 3:
                    print(f"   ... y {len(actions) - 3} acciones más")
            else:
                print("❌ No se encontraron acciones")

        except Exception as e:
            print(f"❌ Error procesando {filename}: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 50)

if __name__ == "__main__":
    test_sequence_parsing()

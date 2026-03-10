#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la función esp32_action_resolver corregida
"""

import os
import sys

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar la función corregida
from clases.main.main import esp32_action_resolver

def test_esp32_function():
    """Probar la función esp32_action_resolver"""
    print("🧪 Probando función esp32_action_resolver...")

    # Probar con una secuencia existente
    test_sequences = ["Awiwi", "Test2"]

    for sequence in test_sequences:
        print(f"\n🎬 Probando secuencia: {sequence}")
        print("-" * 40)

        try:
            success = esp32_action_resolver(sequence)

            if success:
                print(f"✅ Secuencia '{sequence}' ejecutada correctamente")
            else:
                print(f"❌ Error ejecutando secuencia '{sequence}'")

        except Exception as e:
            print(f"❌ Error llamando función: {e}")
            import traceback
            traceback.print_exc()

        print("-" * 40)

if __name__ == "__main__":
    test_esp32_function()

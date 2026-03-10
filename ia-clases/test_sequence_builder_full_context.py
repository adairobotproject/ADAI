#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del sequence builder en el contexto completo de la aplicación
"""

import os
import sys

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_sequence_builder_full_context():
    """Probar sequence builder en contexto completo como en la aplicación"""

    print("🎯 TEST SEQUENCE BUILDER - CONTEXTO COMPLETO")
    print("=" * 60)

    try:
        # Importar la aplicación completa
        from robot_gui import RobotGUI
        print("✅ RobotGUI importado correctamente")

        # Crear instancia de la aplicación
        app = RobotGUI()
        print("✅ RobotGUI creado correctamente")

        # Acceder directamente al sequence builder tab
        sequence_builder = app.sequence_builder_tab
        if sequence_builder:
            print("✅ Sequence Builder encontrado")
        else:
            print("❌ Sequence Builder no encontrado")
            return

        # Verificar estado del sequence builder
        print("\n📊 Estado del Sequence Builder:")
        print(f"   - ESP32 Client: {sequence_builder.esp32_client}")
        print(f"   - ESP32 Connected: {sequence_builder.esp32_connected}")
        print(f"   - Debug Mode: {sequence_builder.debug_mode}")

        # Intentar conectar ESP32 si no está conectado
        if sequence_builder.esp32_client and not sequence_builder.esp32_connected:
            print("🔌 Intentando conectar ESP32...")
            try:
                # Cargar configuración
                if hasattr(sequence_builder, 'esp32_config') and sequence_builder.esp32_config:
                    config_data = sequence_builder.esp32_config.load_config()
                    if config_data:
                        sequence_builder.esp32_client.host = config_data.host
                        sequence_builder.esp32_client.port = config_data.port
                        print(f"   ✅ Configuración: {config_data.host}:{config_data.port}")

                # Intentar conectar
                success = sequence_builder.esp32_client.connect()
                if success:
                    sequence_builder.esp32_connected = True
                    print("   ✅ Conexión exitosa")
                else:
                    print("   ❌ Error conectando")

            except Exception as e:
                print(f"   ❌ Error en conexión: {e}")

        # Probar envío de comandos de dedos
        print("\n👐 Probando comandos de dedos:")
        print("-" * 40)

        test_commands = [
            ("right", "thumb", 90),
            ("left", "index", 45),
            ("right", "middle", 120),
        ]

        for hand, finger, angle in test_commands:
            print(f"   Probando {hand} {finger} → {angle}°")

            try:
                # Llamar directamente al método on_finger_change
                sequence_builder.on_finger_change(hand, finger, angle)

                # Verificar condiciones
                can_send = sequence_builder.esp32_connected and not sequence_builder.debug_mode
                print(f"      Condiciones: Connected={sequence_builder.esp32_connected}, Debug={sequence_builder.debug_mode} → Can Send: {can_send}")

            except Exception as e:
                print(f"      ❌ Error: {e}")

        print("\n🎯 DIAGNÓSTICO:")
        print("-" * 40)

        if sequence_builder.debug_mode:
            print("❌ PROBLEMA: Debug Mode está ACTIVADO")
            print("   → Los comandos NO se envían cuando debug_mode=True")
            print("   → Solución: Desactivar debug mode en el sequence builder")
        elif not sequence_builder.esp32_connected:
            print("❌ PROBLEMA: ESP32 no está conectado")
            print("   → Los comandos NO se envían sin conexión ESP32")
            print("   → Solución: Verificar conexión ESP32")
        else:
            print("✅ TODO PARECE ESTAR BIEN")
            print("   → Si los dedos no se mueven, verificar:")
            print("      • Cables UART ESP32→Mega")
            print("      • Cables Serial Mega→Uno")
            print("      • Alimentación de servos")
            print("      • Configuración de pines en Uno.ino")

        # Mostrar estado final
        print("\n📊 Estado Final:")
        print(f"   - ESP32 Connected: {sequence_builder.esp32_connected}")
        print(f"   - Debug Mode: {sequence_builder.debug_mode}")
        print(f"   - Can Send Commands: {sequence_builder.esp32_connected and not sequence_builder.debug_mode}")

    except Exception as e:
        print(f"❌ Error en test completo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sequence_builder_full_context()

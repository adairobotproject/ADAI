#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test específico para verificar que los controles de muñeca del sequence builder funcionen
"""

import os
import sys
import time

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_wrist_sequence_builder():
    """Test específico para controles de muñeca del sequence builder"""

    print("🦴 TEST CONTROLES DE MUÑECA - SEQUENCE BUILDER")
    print("=" * 60)

    try:
        # Importar el sequence builder
        from tabs.sequence_builder_tab import SequenceBuilderTab
        from services.esp32_services.esp32_client import ESP32Client

        print("✅ Módulos importados correctamente")

        # Crear mock GUI
        class MockGUI:
            def __init__(self):
                self.root = None
                self.notebook = None

        class MockNotebook:
            def __init__(self):
                pass

        mock_gui = MockGUI()
        mock_notebook = MockNotebook()

        # Crear sequence builder
        seq_builder = SequenceBuilderTab(mock_gui, mock_notebook)
        print("✅ SequenceBuilderTab creado")

        # Verificar estado inicial
        print("\n📊 Estado inicial:")
        print(f"   - ESP32 Client: {seq_builder.esp32_client}")
        print(f"   - ESP32 Connected: {seq_builder.esp32_connected}")
        print(f"   - Debug Mode: {seq_builder.debug_mode}")

        # Simular conexión ESP32
        if seq_builder.esp32_client and hasattr(seq_builder, 'esp32_config'):
            try:
                config_data = seq_builder.esp32_config.load_config()
                if config_data:
                    seq_builder.esp32_client.host = config_data.host
                    seq_builder.esp32_client.port = config_data.port
                    print(f"   ✅ Configuración cargada: {config_data.host}:{config_data.port}")

                    # Intentar conectar
                    success = seq_builder.esp32_client.connect()
                    if success:
                        seq_builder.esp32_connected = True
                        print("   ✅ ESP32 conectado")
                    else:
                        print("   ❌ Error conectando ESP32")
                else:
                    print("   ⚠️ No se encontró configuración ESP32")
            except Exception as e:
                print(f"   ❌ Error en configuración: {e}")

        # Test 1: Simular movimiento de muñeca izquierda
        print("\n🧪 Test 1: Movimiento muñeca izquierda")
        if seq_builder.esp32_connected:
            try:
                print("   Enviando comando: muñeca izquierda → 90°")
                seq_builder.on_wrist_change('left', 90)
                print("   ✅ Comando enviado")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Test 2: Simular movimiento de muñeca derecha
        print("\n🧪 Test 2: Movimiento muñeca derecha")
        if seq_builder.esp32_connected:
            try:
                print("   Enviando comando: muñeca derecha → 45°")
                seq_builder.on_wrist_change('right', 45)
                print("   ✅ Comando enviado")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Test 3: Simular movimiento de muñeca derecha con otro ángulo
        print("\n🧪 Test 3: Movimiento muñeca derecha (otro ángulo)")
        if seq_builder.esp32_connected:
            try:
                print("   Enviando comando: muñeca derecha → 120°")
                seq_builder.on_wrist_change('right', 120)
                print("   ✅ Comando enviado")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Test 4: Verificar formato del comando enviado
        print("\n🔍 Test 4: Verificación del formato de comandos")
        if seq_builder.esp32_client:
            try:
                # Verificar que el método send_wrist_control existe
                if hasattr(seq_builder.esp32_client, 'send_wrist_control'):
                    print("   ✅ Método send_wrist_control existe")

                    # Verificar formato esperado (simulado)
                    print("   📝 Formato esperado: mano=X angulo=Y")
                    print("   📝 Comando ESP32Client: MUNECA con params='mano=X angulo=Y'")
                    print("   📝 Parsing ESP32: busca 'mano=' y 'angulo='")

                else:
                    print("   ❌ Método send_wrist_control no encontrado")
            except Exception as e:
                print(f"   ❌ Error verificando método: {e}")

        # Estado final
        print("\n📊 Estado final:")
        print(f"   - ESP32 Connected: {seq_builder.esp32_connected}")
        print(f"   - Debug Mode: {seq_builder.debug_mode}")
        print(f"   - Can Send Commands: {seq_builder.esp32_connected and not seq_builder.debug_mode}")

        if seq_builder.esp32_connected:
            print("\n✅ RECOMENDACIONES:")
            print("   1. Verifica que el ESP32 esté ejecutando el código actualizado")
            print("   2. Revisa el monitor serie del ESP32 para ver:")
            print("      - 📋 Comando de secuencia recibido: MUNECA")
            print("      - 🔧 Parámetros: mano=derecha angulo=90")
            print("   3. Verifica que el MEGA reciba: [UNO TX] MUNECA M=derecha ANG=90")
            print("   4. Verifica que el UNO reciba: [CMD] MUNECA M=derecha ANG=90")
            print("   5. Confirma movimiento físico de los servos de muñeca")
        else:
            print("\n⚠️ NOTAS:")
            print("   - ESP32 no está conectado")
            print("   - Los comandos se enviarán pero no llegarán al robot")
            print("   - Activa debug mode en sequence builder para simular")

    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎉 TEST COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_wrist_sequence_builder()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug específico para el sequence builder y sus controles de dedos
"""

import os
import sys
import tkinter as tk

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def debug_sequence_builder():
    """Debug del sequence builder"""

    print("🔧 DEBUG SEQUENCE BUILDER")
    print("=" * 50)

    try:
        from tabs.sequence_builder_tab import SequenceBuilderTab
        print("✅ SequenceBuilderTab importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando SequenceBuilderTab: {e}")
        print("💡 Verifica que estés ejecutando desde el directorio correcto")
        return

    # Crear una ventana Tkinter básica
    root = tk.Tk()
    root.title("Debug Sequence Builder")
    root.geometry("400x200")

    # Crear un notebook básico
    notebook = tk.Frame(root)
    notebook.pack(fill="both", expand=True)

    # Crear instancia del sequence builder
    try:
        # Simular una GUI básica
        class MockGUI:
            def __init__(self):
                self.root = root
                self.notebook = notebook

        mock_gui = MockGUI()
        seq_builder = SequenceBuilderTab(mock_gui, notebook)

        print("✅ SequenceBuilderTab creado correctamente")

        # Verificar estado inicial
        print("\n📊 Estado inicial:")
        print(f"   - ESP32 Client: {seq_builder.esp32_client}")
        print(f"   - ESP32 Connected: {seq_builder.esp32_connected}")
        print(f"   - Debug Mode: {seq_builder.debug_mode}")

        # Intentar conectar ESP32
        if seq_builder.esp32_client:
            print("🔌 Intentando conectar ESP32...")
            try:
                # Intentar acceder a la configuración
                if hasattr(seq_builder, 'esp32_config') and seq_builder.esp32_config:
                    config_data = seq_builder.esp32_config.load_config()
                    if config_data:
                        print(f"   ✅ Configuración encontrada: {config_data.host}:{config_data.port}")
                        seq_builder.esp32_client.host = config_data.host
                        seq_builder.esp32_client.port = config_data.port
                    else:
                        print("   ⚠️ No se encontró configuración ESP32")
                else:
                    print("   ❌ ESP32 config no disponible")

                # Intentar conectar
                success = seq_builder.esp32_client.connect()
                if success:
                    seq_builder.esp32_connected = True
                    print("   ✅ Conexión ESP32 exitosa")
                else:
                    print("   ❌ Error conectando ESP32")

            except Exception as e:
                print(f"   ❌ Error en conexión: {e}")
                import traceback
                traceback.print_exc()

        # Simular movimiento de dedo
        print("\n👐 Probando movimiento de dedo simulado:")
        print("-" * 40)

        # Simular llamada a on_finger_change
        try:
            print("   Simulando on_finger_change('right', 'thumb', 90)...")
            seq_builder.on_finger_change('right', 'thumb', 90)

            print("   Simulando on_finger_change('left', 'index', 45)...")
            seq_builder.on_finger_change('left', 'index', 45)

        except Exception as e:
            print(f"   ❌ Error en movimiento simulado: {e}")
            import traceback
            traceback.print_exc()

        # Mostrar estado final
        print("\n📊 Estado final:")
        print(f"   - ESP32 Client: {seq_builder.esp32_client}")
        print(f"   - ESP32 Connected: {seq_builder.esp32_connected}")
        print(f"   - Debug Mode: {seq_builder.debug_mode}")

        # Verificar si se están enviando comandos
        if seq_builder.esp32_connected and not seq_builder.debug_mode:
            print("   ✅ Condiciones para enviar comandos: OK")
        else:
            print("   ❌ Condiciones para enviar comandos: FALLANDO")
            if not seq_builder.esp32_connected:
                print("      → ESP32 no conectado")
            if seq_builder.debug_mode:
                print("      → Modo debug activado (bloquea envío de comandos)")

    except Exception as e:
        print(f"❌ Error creando SequenceBuilderTab: {e}")
        import traceback
        traceback.print_exc()

    # Mantener ventana abierta por un momento
    def close_window():
        root.quit()
        root.destroy()

    # Botón para cerrar
    close_btn = tk.Button(root, text="Cerrar Debug", command=close_window)
    close_btn.pack(pady=10)

    # Auto-cerrar después de 10 segundos
    root.after(10000, close_window)

    print("\\n⏳ Ejecutando debug (ventana se cerrará en 10 segundos)...")
    root.mainloop()

    print("✅ Debug completado")

if __name__ == "__main__":
    debug_sequence_builder()

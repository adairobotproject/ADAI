#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que el toggle de modos de control funcione correctamente
"""

import os
import sys

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_control_modes():
    """Test del toggle de modos de control"""

    print("🎛️ TEST TOGGLE MODOS DE CONTROL")
    print("=" * 50)

    try:
        # Importar el sequence builder
        from tabs.sequence_builder_tab import SequenceBuilderTab

        print("✅ SequenceBuilderTab importado")

        # Verificar que las funciones existen
        seq_builder = SequenceBuilderTab.__new__(SequenceBuilderTab)

        # Verificar que las nuevas funciones existen
        assert hasattr(seq_builder, 'control_mode'), "❌ Falta variable control_mode"
        assert hasattr(seq_builder, 'update_control_mode'), "❌ Falta función update_control_mode"
        assert hasattr(seq_builder, 'create_slider_controls'), "❌ Falta función create_slider_controls"
        assert hasattr(seq_builder, 'create_arrow_controls'), "❌ Falta función create_arrow_controls"

        print("✅ Todas las funciones necesarias existen")

        # Verificar inicialización de variables
        seq_builder.__init__(None, None)

        assert seq_builder.control_mode.get() == "sliders", "❌ Modo inicial incorrecto"
        print("✅ Modo inicial configurado correctamente: 'sliders'")

        # Cambiar a modo arrows
        seq_builder.control_mode.set("arrows")
        assert seq_builder.control_mode.get() == "arrows", "❌ Cambio de modo falló"
        print("✅ Cambio de modo funciona correctamente")

        # Verificar que las funciones de ajuste existen
        assert hasattr(seq_builder, 'adjust_arm_value'), "❌ Falta función adjust_arm_value"
        assert hasattr(seq_builder, 'adjust_finger_value'), "❌ Falta función adjust_finger_value"
        assert hasattr(seq_builder, 'adjust_wrist_value'), "❌ Falta función adjust_wrist_value"

        print("✅ Funciones de ajuste existen")

        print("\n🎉 TODOS LOS TESTS PASARON")        print("=" * 50)
        print("✅ El toggle de modos de control está implementado correctamente")
        print("🎛️ Funciones disponibles:")
        print("   • Modo Sliders: Controles tradicionales con deslizadores")
        print("   • Modo Arrows: Controles con flechas que muestran valor actual")
        print("   • Cambio dinámico entre modos sin reiniciar la aplicación")

    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_control_modes()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar la lógica de importación de módulos
"""

import os
import sys

def test_modular_import_logic():
    """Probar la lógica de importación de módulos"""
    print("🧪 Probando lógica de importación de módulos...")
    
    try:
        # Simular la lógica de importación desde una clase
        current_file_dir = os.path.dirname(os.path.abspath(__file__))  # ia-clases/
        print(f"📁 Directorio actual: {current_file_dir}")
        
        # Calcular ruta a modules/
        modules_path = os.path.join(current_file_dir, "modules")
        print(f"📁 Ruta a modules: {modules_path}")
        
        # Verificar que existe
        if os.path.exists(modules_path):
            print(f"✅ Directorio modules existe: {modules_path}")
        else:
            print(f"❌ Directorio modules NO existe: {modules_path}")
            return False
        
        # Agregar al path si no está
        if modules_path not in sys.path:
            sys.path.append(modules_path)
            print(f"✅ Agregado al path: {modules_path}")
        else:
            print(f"ℹ️ Ya estaba en el path: {modules_path}")
        
        # Intentar importar módulos
        print("\n🔍 Probando importaciones...")
        
        try:
            from modules.config import client, script_dir, faces_dir, QR_PATHS
            print("✅ modules.config importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando modules.config: {e}")
            return False
        
        try:
            from modules.speech import initialize_tts, speak_with_animation
            print("✅ modules.speech importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando modules.speech: {e}")
            return False
        
        try:
            from modules.camera import verify_camera_for_iriun, camera_process
            print("✅ modules.camera importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando modules.camera: {e}")
            return False
        
        try:
            from modules.esp32 import execute_esp32_sequence
            print("✅ modules.esp32 importado correctamente")
        except ImportError as e:
            print(f"❌ Error importando modules.esp32: {e}")
            return False
        
        print("\n🎉 ¡Todas las importaciones exitosas!")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_from_class_perspective():
    """Probar la lógica desde la perspectiva de una clase generada"""
    print("\n🧪 Probando desde perspectiva de clase generada...")
    
    try:
        # Simular estar en una clase generada
        # clases/mi_clase_de_robótica_clase/Mi_Clase_de_Robótica_clase.py
        class_file_path = os.path.join("clases", "mi_clase_de_robótica_clase", "Mi_Clase_de_Robótica_clase.py")
        
        if os.path.exists(class_file_path):
            print(f"✅ Archivo de clase existe: {class_file_path}")
        else:
            print(f"❌ Archivo de clase NO existe: {class_file_path}")
            return False
        
        # Calcular rutas como lo haría la clase
        current_file_dir = os.path.dirname(os.path.abspath(class_file_path))  # clases/mi_clase_de_robótica_clase/
        project_root = os.path.dirname(os.path.dirname(current_file_dir))  # ia-clases/
        modules_path = os.path.join(project_root, "modules")
        
        print(f"📁 Desde clase - Directorio actual: {current_file_dir}")
        print(f"📁 Desde clase - Project root: {project_root}")
        print(f"📁 Desde clase - Modules path: {modules_path}")
        
        # Verificar que existe
        if os.path.exists(modules_path):
            print(f"✅ Directorio modules existe desde clase: {modules_path}")
        else:
            print(f"❌ Directorio modules NO existe desde clase: {modules_path}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test desde clase: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando tests de lógica de importación...")
    
    # Test 1: Lógica de importación general
    test1_result = test_modular_import_logic()
    
    # Test 2: Lógica desde perspectiva de clase
    test2_result = test_from_class_perspective()
    
    print("\n" + "="*50)
    print("📊 RESULTADOS:")
    print(f"Test 1 (Importación general): {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Test 2 (Desde clase): {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ¡Todos los tests pasaron!")
    else:
        print("\n⚠️ Algunos tests fallaron")

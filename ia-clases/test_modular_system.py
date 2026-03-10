#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema modular de ADAI
Verifica que todos los componentes funcionen correctamente
"""

import os
import sys
import traceback

# Agregar rutas necesarias
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")
classes_dir = os.path.join(current_dir, "clases")

if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
if classes_dir not in sys.path:
    sys.path.insert(0, classes_dir)

def test_imports():
    """Prueba que todos los módulos se puedan importar correctamente"""
    print("🔍 Probando importación de módulos...")
    
    try:
        # Probar importación de módulos principales
        from modules.class_config import ClassConfigManager, get_class_config, list_available_classes
        print("✅ class_config importado correctamente")
        
        from modules.config import client, script_dir, faces_dir
        print("✅ config importado correctamente")
        
        from modules.speech import initialize_tts, speak_with_animation, listen
        print("✅ speech importado correctamente")
        
        from modules.camera import verify_camera_for_iriun, identify_users, load_known_faces
        print("✅ camera importado correctamente")
        
        from modules.qr import show_diagnostic_qr, show_final_exam_qr
        print("✅ qr importado correctamente")
        
        from modules.slides import show_pdf_page_in_opencv, extract_text_from_pdf
        print("✅ slides importado correctamente")
        
        from modules.questions import RandomQuestionManager, evaluate_student_answer
        print("✅ questions importado correctamente")
        
        from modules.esp32 import execute_esp32_sequence
        print("✅ esp32 importado correctamente")
        
        from modules.utils import summarize_text, ask_openai
        print("✅ utils importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        traceback.print_exc()
        return False

def test_class_config():
    """Prueba el sistema de configuración de clases"""
    print("\n🔍 Probando sistema de configuración de clases...")
    
    try:
        from modules.class_config import ClassConfigManager
        
        # Crear gestor de configuración
        config_manager = ClassConfigManager(classes_dir)
        
        # Listar clases disponibles
        classes = config_manager.list_classes()
        print(f"✅ Clases encontradas: {classes}")
        
        # Probar configuración de clase específica
        if "mi_clase_de_robótica_clase" in classes:
            config = config_manager.load_class_config("mi_clase_de_robótica_clase")
            print(f"✅ Configuración cargada para mi_clase_de_robótica_clase")
            print(f"   - Título: {config.get('title', 'N/A')}")
            print(f"   - Materia: {config.get('subject', 'N/A')}")
            print(f"   - Usa diagnóstico: {config.get('use_diagnostic', False)}")
            print(f"   - Usa PDF: {config.get('use_pdf', False)}")
            
            # Obtener información de la clase
            info = config_manager.get_class_info("mi_clase_de_robótica_clase")
            print(f"✅ Información de clase obtenida:")
            print(f"   - Existe: {info['exists']}")
            print(f"   - Tiene config: {info['has_config']}")
            print(f"   - Tiene archivo principal: {info['has_main_file']}")
            if info['has_main_file']:
                print(f"   - Archivo principal: {info['main_file_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración de clases: {e}")
        traceback.print_exc()
        return False

def test_class_import():
    """Prueba importar la clase específica"""
    print("\n🔍 Probando importación de clase específica...")
    
    try:
        # Buscar y importar la clase
        class_name = "mi_clase_de_robótica_clase"
        class_folder = os.path.join(classes_dir, class_name)
        
        if not os.path.exists(class_folder):
            print(f"❌ No se encontró la carpeta de clase: {class_folder}")
            return False
        
        # Buscar archivo principal
        main_file = None
        possible_names = [
            f"{class_name}.py",
            f"{class_name}_clase.py", 
            f"{class_name}_class.py",
            "main.py",
            "class.py"
        ]
        
        for name in possible_names:
            file_path = os.path.join(class_folder, name)
            if os.path.exists(file_path):
                main_file = file_path
                break
        
        if not main_file:
            print(f"❌ No se encontró archivo principal en: {class_folder}")
            return False
        
        print(f"✅ Archivo principal encontrado: {main_file}")
        
        # Agregar directorio de la clase al path
        if class_folder not in sys.path:
            sys.path.insert(0, class_folder)
        
        # Importar módulo dinámicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location(class_name, main_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        print(f"✅ Módulo {class_name} importado correctamente")
        
        # Buscar la clase principal
        class_found = False
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name != 'object' and 
                hasattr(attr, 'run_complete_class')):
                print(f"✅ Clase principal encontrada: {attr_name}")
                class_found = True
                
                # Probar crear instancia (sin ejecutar)
                try:
                    instance = attr()
                    print(f"✅ Instancia de {attr_name} creada exitosamente")
                except Exception as e:
                    print(f"⚠️ Error creando instancia: {e}")
                
                break
        
        if not class_found:
            print(f"❌ No se encontró clase con método run_complete_class()")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando clase: {e}")
        traceback.print_exc()
        return False

def test_main_modular():
    """Prueba el main modular"""
    print("\n🔍 Probando main modular...")
    
    try:
        # Importar main modular
        main_file = os.path.join(current_dir, "clases", "main", "main_modular.py")
        if not os.path.exists(main_file):
            print(f"❌ No se encontró main_modular.py: {main_file}")
            return False
        
        # Agregar directorio main al path
        main_dir = os.path.join(current_dir, "clases", "main")
        if main_dir not in sys.path:
            sys.path.insert(0, main_dir)
        
        # Importar main modular
        import main_modular
        print("✅ main_modular importado correctamente")
        
        # Probar función de listar clases
        classes = main_modular.list_available_classes()
        print(f"✅ Clases disponibles desde main_modular: {classes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando main modular: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de prueba"""
    print("="*60)
    print("🧪 PRUEBAS DEL SISTEMA MODULAR ADAI")
    print("="*60)
    
    tests = [
        ("Importación de módulos", test_imports),
        ("Sistema de configuración", test_class_config),
        ("Importación de clase", test_class_import),
        ("Main modular", test_main_modular)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name}: EXITOSO")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El sistema modular está funcionando correctamente.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error crítico en las pruebas: {e}")
        traceback.print_exc()
        sys.exit(1)

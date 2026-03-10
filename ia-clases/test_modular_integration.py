#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para verificar la integración del sistema modular
"""

import os
import sys
import tempfile
import shutil

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_modular_structure():
    """Test que la estructura modular esté en su lugar"""
    print("🔍 Verificando estructura modular...")
    
    modules_dir = os.path.join("clases", "modules")
    required_modules = [
        "__init__.py",
        "config.py",
        "speech.py", 
        "camera.py",
        "qr.py",
        "questions.py",
        "slides.py",
        "esp32.py",
        "utils.py"
    ]
    
    for module in required_modules:
        module_path = os.path.join(modules_dir, module)
        if os.path.exists(module_path):
            print(f"✅ {module}")
        else:
            print(f"❌ {module} - NO ENCONTRADO")
            return False
    
    print("✅ Estructura modular verificada")
    return True

def test_class_builder_generation():
    """Test que el ClassBuilderTab pueda generar clases modulares"""
    print("\n🔍 Verificando generación de clases modulares...")
    
    try:
        # Verificar que el archivo existe y contiene el código modular
        class_builder_path = os.path.join("tabs", "class_builder_tab.py")
        
        if not os.path.exists(class_builder_path):
            print(f"❌ Archivo no encontrado: {class_builder_path}")
            return False
        
        with open(class_builder_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que contiene imports modulares en el código generado
        modular_imports = [
            'from modules.config import',
            'from modules.speech import',
            'from modules.camera import',
            'from modules.qr import',
            'from modules.slides import',
            'from modules.questions import',
            'from modules.esp32 import',
            'from modules.utils import'
        ]
        
        for import_line in modular_imports:
            if import_line in content:
                print(f"✅ Import modular encontrado: {import_line}")
            else:
                print(f"❌ Import modular NO encontrado: {import_line}")
                return False
        
        # Verificar que contiene la estructura de clase modular
        modular_indicators = [
            'def initialize_systems(self):',
            'def run_diagnostic_phase(self):',
            'def run_class_initialization(self):',
            'def run_pdf_phase(self):',
            'def run_demo_phase(self):',
            'def run_final_exam_phase(self):',
            'def run_complete_class(self):'
        ]
        
        for indicator in modular_indicators:
            if indicator in content:
                print(f"✅ Método modular encontrado: {indicator}")
            else:
                print(f"❌ Método modular NO encontrado: {indicator}")
                return False
        
        print("✅ Generación de clases modulares verificada")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de generación: {e}")
        return False

def test_class_manager_modular_detection():
    """Test que el ClassManager pueda detectar clases modulares"""
    print("\n🔍 Verificando detección de clases modulares...")
    
    try:
        from class_manager import ClassManager
        
        # Crear un archivo temporal de clase modular
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('''
import cv2
from modules.config import client, script_dir
from modules.speech import initialize_tts, speak_with_animation
from modules.camera import verify_camera_for_iriun

class TestModularClass:
    def __init__(self):
        pass
    
    def run(self):
        pass
''')
            temp_file = f.name
        
        try:
            manager = ClassManager()
            
            # Test del método de detección
            is_modular = manager._check_if_modular_class(temp_file)
            
            if is_modular:
                print("✅ Detección de clases modulares funciona correctamente")
                return True
            else:
                print("❌ No se detectó la clase como modular")
                return False
                
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Error en test de detección: {e}")
        return False

def test_import_modules():
    """Test que los módulos se puedan importar correctamente"""
    print("\n🔍 Verificando imports de módulos...")
    
    try:
        # Agregar el directorio de clases al path
        clases_dir = os.path.join(os.getcwd(), "clases")
        
        if os.path.exists(clases_dir):
            # Agregar al path para poder importar
            if clases_dir not in sys.path:
                sys.path.insert(0, clases_dir)
            
            # Test imports
            try:
                from modules.config import client, script_dir, faces_dir
                print("✅ modules.config importado")
            except Exception as e:
                print(f"❌ Error importando modules.config: {e}")
                return False
            
            try:
                from modules.speech import initialize_tts, speak_with_animation
                print("✅ modules.speech importado")
            except Exception as e:
                print(f"❌ Error importando modules.speech: {e}")
                return False
            
            try:
                from modules.camera import verify_camera_for_iriun, camera_process
                print("✅ modules.camera importado")
            except Exception as e:
                print(f"❌ Error importando modules.camera: {e}")
                return False
            
            try:
                from modules.qr import show_diagnostic_qr, show_final_exam_qr
                print("✅ modules.qr importado")
            except Exception as e:
                print(f"❌ Error importando modules.qr: {e}")
                return False
            
            try:
                from modules.slides import show_pdf_page_in_opencv, extract_text_from_pdf
                print("✅ modules.slides importado")
            except Exception as e:
                print(f"❌ Error importando modules.slides: {e}")
                return False
            
            try:
                from modules.questions import RandomQuestionManager, evaluate_student_answer
                print("✅ modules.questions importado")
            except Exception as e:
                print(f"❌ Error importando modules.questions: {e}")
                return False
            
            try:
                from modules.esp32 import execute_esp32_sequence
                print("✅ modules.esp32 importado")
            except Exception as e:
                print(f"❌ Error importando modules.esp32: {e}")
                return False
            
            try:
                from modules.utils import summarize_text, ask_openai
                print("✅ modules.utils importado")
            except Exception as e:
                print(f"❌ Error importando modules.utils: {e}")
                return False
            
            print("✅ Todos los módulos se importaron correctamente")
            return True
        else:
            print("❌ Directorio 'clases' no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error en test de imports: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests de integración modular...")
    print("="*60)
    
    tests = [
        ("Estructura Modular", test_modular_structure),
        ("Generación de Clases", test_class_builder_generation),
        ("Detección de Clases Modulares", test_class_manager_modular_detection),
        ("Imports de Módulos", test_import_modules)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! El sistema modular está funcionando correctamente.")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar la configuración.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

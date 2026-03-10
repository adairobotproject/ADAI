#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para verificar la integración modular
"""

import os
import sys

def main():
    print("🚀 Test Simple de Integración Modular")
    print("="*50)
    
    # Test 1: Verificar estructura modular
    print("\n1. Verificando estructura modular...")
    modules_dir = os.path.join("clases", "modules")
    required_modules = ["__init__.py", "config.py", "speech.py", "camera.py", "qr.py", "questions.py", "slides.py", "esp32.py", "utils.py"]
    
    all_exist = True
    for module in required_modules:
        module_path = os.path.join(modules_dir, module)
        if os.path.exists(module_path):
            print(f"   ✅ {module}")
        else:
            print(f"   ❌ {module}")
            all_exist = False
    
    if all_exist:
        print("   ✅ Estructura modular OK")
    else:
        print("   ❌ Estructura modular incompleta")
        return False
    
    # Test 2: Verificar ClassBuilderTab
    print("\n2. Verificando ClassBuilderTab...")
    class_builder_path = os.path.join("tabs", "class_builder_tab.py")
    if os.path.exists(class_builder_path):
        with open(class_builder_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from modules.config import' in content:
            print("   ✅ ClassBuilderTab genera código modular")
        else:
            print("   ❌ ClassBuilderTab no genera código modular")
            return False
    else:
        print("   ❌ ClassBuilderTab no encontrado")
        return False
    
    # Test 3: Verificar ClassManager
    print("\n3. Verificando ClassManager...")
    class_manager_path = "class_manager.py"
    if os.path.exists(class_manager_path):
        with open(class_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '_check_if_modular_class' in content:
            print("   ✅ ClassManager detecta clases modulares")
        else:
            print("   ❌ ClassManager no detecta clases modulares")
            return False
    else:
        print("   ❌ ClassManager no encontrado")
        return False
    
    # Test 4: Verificar imports de módulos
    print("\n4. Verificando imports de módulos...")
    clases_dir = os.path.join(os.getcwd(), "clases")
    if clases_dir not in sys.path:
        sys.path.insert(0, clases_dir)
    
    try:
        from modules.config import client, script_dir
        print("   ✅ modules.config importado")
    except Exception as e:
        print(f"   ❌ Error importando modules.config: {e}")
        return False
    
    try:
        from modules.speech import initialize_tts
        print("   ✅ modules.speech importado")
    except Exception as e:
        print(f"   ❌ Error importando modules.speech: {e}")
        return False
    
    print("\n🎉 ¡Todos los tests pasaron!")
    print("✅ El sistema modular está funcionando correctamente")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

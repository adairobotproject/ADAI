#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar y verificar las importaciones del sistema modular
"""

import os
import sys
import traceback

def test_path_calculation():
    """Prueba el cálculo de rutas para los módulos"""
    print("🔍 Probando cálculo de rutas...")
    
    # Simular la estructura de directorios
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Directorio actual: {current_dir}")
    
    # Desde ia-clases/
    classes_dir = os.path.join(current_dir, "clases")
    print(f"📁 Directorio de clases: {classes_dir}")
    
    # Desde ia-clases/clases/mi_clase_de_robótica_clase/
    class_dir = os.path.join(classes_dir, "mi_clase_de_robótica_clase")
    print(f"📁 Directorio de clase: {class_dir}")
    
    # Calcular ruta a módulos
    parent_dir = os.path.dirname(class_dir)  # ia-clases/clases/
    parent_parent_dir = os.path.dirname(parent_dir)  # ia-clases/
    modules_dir = os.path.join(parent_parent_dir, "modules")  # ia-clases/modules/
    
    print(f"📁 Directorio de módulos calculado: {modules_dir}")
    print(f"📁 ¿Existe el directorio de módulos? {os.path.exists(modules_dir)}")
    
    if os.path.exists(modules_dir):
        print("✅ Ruta calculada correctamente")
        return modules_dir
    else:
        print("❌ Ruta calculada incorrectamente")
        return None

def test_module_imports():
    """Prueba la importación de módulos"""
    print("\n🔍 Probando importación de módulos...")
    
    modules_dir = test_path_calculation()
    if not modules_dir:
        return False
    
    # Agregar módulos al path
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
        print(f"✅ Agregado al path: {modules_dir}")
    
    # Probar importaciones
    modules_to_test = [
        "modules.config",
        "modules.speech", 
        "modules.camera",
        "modules.qr",
        "modules.slides",
        "modules.questions",
        "modules.esp32",
        "modules.utils",
        "modules.class_config"
    ]
    
    success_count = 0
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} importado correctamente")
            success_count += 1
        except ImportError as e:
            print(f"❌ Error importando {module_name}: {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(modules_to_test)} módulos importados")
    return success_count == len(modules_to_test)

def test_class_execution():
    """Prueba la ejecución de la clase"""
    print("\n🔍 Probando ejecución de clase...")
    
    try:
        # Agregar rutas necesarias
        current_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(current_dir, "modules")
        classes_dir = os.path.join(current_dir, "clases")
        
        if modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        if classes_dir not in sys.path:
            sys.path.insert(0, classes_dir)
        
        # Importar la clase
        class_name = "mi_clase_de_robótica_clase"
        class_folder = os.path.join(classes_dir, class_name)
        
        if class_folder not in sys.path:
            sys.path.insert(0, class_folder)
        
        # Importar módulo de la clase
        import importlib.util
        main_file = os.path.join(class_folder, f"{class_name}.py")
        if not os.path.exists(main_file):
            main_file = os.path.join(class_folder, f"{class_name}_clase.py")
        
        if not os.path.exists(main_file):
            print(f"❌ No se encontró archivo principal en {class_folder}")
            return False
        
        print(f"✅ Archivo principal encontrado: {main_file}")
        
        spec = importlib.util.spec_from_file_location(class_name, main_file)
        module = importlib.util.module_from_spec(spec)
        
        print("🔄 Ejecutando importación del módulo...")
        spec.loader.exec_module(module)
        
        print("✅ Módulo de clase importado correctamente")
        
        # Buscar la clase principal
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr_name != 'object' and 
                hasattr(attr, 'run_complete_class')):
                print(f"✅ Clase principal encontrada: {attr_name}")
                return True
        
        print("❌ No se encontró clase con método run_complete_class()")
        return False
        
    except Exception as e:
        print(f"❌ Error en ejecución de clase: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de prueba"""
    print("="*60)
    print("🧪 PRUEBAS DE IMPORTACIONES DEL SISTEMA MODULAR")
    print("="*60)
    
    tests = [
        ("Cálculo de rutas", test_path_calculation),
        ("Importación de módulos", test_module_imports),
        ("Ejecución de clase", test_class_execution)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            if test_name == "Cálculo de rutas":
                success = success is not None
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
        print("🎉 ¡Todas las pruebas pasaron!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error crítico en las pruebas: {e}")
        traceback.print_exc()
        sys.exit(1)

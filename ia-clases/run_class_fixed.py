#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para ejecutar una clase específica con manejo correcto de rutas
"""

import os
import sys
import multiprocessing
import traceback

def setup_paths():
    """Configura las rutas necesarias para el sistema modular"""
    print("🔧 Configurando rutas del sistema...")
    
    # Obtener directorio base
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Directorio base: {current_dir}")
    
    # Configurar rutas
    modules_dir = os.path.join(current_dir, "modules")
    classes_dir = os.path.join(current_dir, "clases")
    main_dir = os.path.join(classes_dir, "main")
    
    # Verificar que existan los directorios
    if not os.path.exists(modules_dir):
        print(f"❌ No se encontró directorio de módulos: {modules_dir}")
        return False
    
    if not os.path.exists(classes_dir):
        print(f"❌ No se encontró directorio de clases: {classes_dir}")
        return False
    
    print(f"✅ Módulos: {modules_dir}")
    print(f"✅ Clases: {classes_dir}")
    
    # Agregar al path
    paths_to_add = [modules_dir, classes_dir, main_dir]
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)
            print(f"✅ Agregado al path: {path}")
    
    return True

def run_class_direct(class_name):
    """
    Ejecuta una clase directamente importando su módulo
    
    Args:
        class_name (str): Nombre de la clase a ejecutar
    """
    try:
        print(f"🚀 Ejecutando clase directamente: {class_name}")
        
        # Buscar la carpeta de la clase
        current_dir = os.path.dirname(os.path.abspath(__file__))
        class_folder = os.path.join(current_dir, "clases", class_name)
        
        if not os.path.exists(class_folder):
            print(f"❌ No se encontró la carpeta de clase: {class_folder}")
            return False
        
        print(f"📁 Carpeta de clase: {class_folder}")
        
        # Buscar archivo principal
        possible_files = [
            f"{class_name}.py",
            f"{class_name}_clase.py",
            f"{class_name}_class.py",
            "main.py",
            "class.py"
        ]
        
        main_file = None
        for filename in possible_files:
            file_path = os.path.join(class_folder, filename)
            if os.path.exists(file_path):
                main_file = file_path
                break
        
        if not main_file:
            print(f"❌ No se encontró archivo principal en: {class_folder}")
            print(f"   Archivos buscados: {possible_files}")
            return False
        
        print(f"✅ Archivo principal: {main_file}")
        
        # Agregar directorio de la clase al path
        if class_folder not in sys.path:
            sys.path.insert(0, class_folder)
        
        # Importar y ejecutar el módulo
        import importlib.util
        
        # Crear especificación del módulo
        module_name = class_name.replace(" ", "_").replace("-", "_")
        spec = importlib.util.spec_from_file_location(module_name, main_file)
        
        if spec is None:
            print(f"❌ No se pudo crear especificación del módulo")
            return False
        
        # Crear y ejecutar el módulo
        module = importlib.util.module_from_spec(spec)
        
        print("🔄 Ejecutando importación del módulo...")
        spec.loader.exec_module(module)
        
        print("✅ Módulo importado correctamente")
        
        # Buscar función main o clase principal
        if hasattr(module, 'main'):
            print("🎯 Ejecutando función main()...")
            module.main()
            return True
        else:
            # Buscar clase con método run_complete_class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    attr_name != 'object' and 
                    hasattr(attr, 'run_complete_class')):
                    print(f"🎯 Ejecutando clase {attr_name}...")
                    instance = attr()
                    return instance.run_complete_class()
            
            print("❌ No se encontró función main() ni clase con run_complete_class()")
            return False
        
    except Exception as e:
        print(f"❌ Error ejecutando clase directamente: {e}")
        traceback.print_exc()
        return False

def run_class_modular(class_name):
    """
    Ejecuta una clase usando el sistema modular
    
    Args:
        class_name (str): Nombre de la clase a ejecutar
    """
    try:
        print(f"🚀 Ejecutando clase con sistema modular: {class_name}")
        
        # Importar main modular
        from clases.main.main_modular import run_class_by_name
        
        success = run_class_by_name(class_name)
        return success
        
    except Exception as e:
        print(f"❌ Error ejecutando con sistema modular: {e}")
        traceback.print_exc()
        return False

def list_available_classes():
    """Lista todas las clases disponibles"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        classes_dir = os.path.join(current_dir, "clases")
        
        if not os.path.exists(classes_dir):
            print("❌ Directorio de clases no encontrado")
            return []
        
        classes = []
        for item in os.listdir(classes_dir):
            item_path = os.path.join(classes_dir, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                classes.append(item)
        
        return sorted(classes)
        
    except Exception as e:
        print(f"❌ Error listando clases: {e}")
        return []

def main():
    """Función principal"""
    try:
        print("="*60)
        print("🤖 ADAI - EJECUTOR DE CLASES MEJORADO")
        print("="*60)
        
        # Configurar rutas
        if not setup_paths():
            print("❌ Error configurando rutas")
            return
        
        # Si se proporciona argumento, ejecutar esa clase
        if len(sys.argv) > 1:
            class_name = sys.argv[1]
            print(f"🎯 Ejecutando clase específica: {class_name}")
            
            # Intentar ejecutar directamente primero
            print("\n🔄 Intentando ejecución directa...")
            success = run_class_direct(class_name)
            
            if not success:
                print("\n🔄 Intentando ejecución modular...")
                success = run_class_modular(class_name)
            
            if success:
                print("✅ Clase completada exitosamente")
            else:
                print("❌ La clase tuvo errores")
            return
        
        # Si no hay argumentos, mostrar menú interactivo
        classes = list_available_classes()
        
        if not classes:
            print("❌ No se encontraron clases disponibles")
            return
        
        print(f"\n📚 Clases disponibles:")
        for i, class_name in enumerate(classes, 1):
            print(f"  {i}. {class_name}")
        
        print(f"\n¿Qué clase deseas ejecutar? (1-{len(classes)})")
        
        try:
            choice = input("Ingresa el número: ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(classes):
                selected_class = classes[choice_idx]
                print(f"\n🎯 Ejecutando: {selected_class}")
                
                # Intentar ejecutar directamente primero
                print("\n🔄 Intentando ejecución directa...")
                success = run_class_direct(selected_class)
                
                if not success:
                    print("\n🔄 Intentando ejecución modular...")
                    success = run_class_modular(selected_class)
                
                if success:
                    print("✅ Clase completada exitosamente")
                else:
                    print("❌ La clase tuvo errores")
            else:
                print("❌ Opción inválida")
                
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Saliendo...")
            
    except Exception as e:
        print(f"❌ Error en main: {e}")
        traceback.print_exc()
    finally:
        import cv2
        cv2.destroyAllWindows()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

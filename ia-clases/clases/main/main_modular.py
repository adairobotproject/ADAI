#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Modular - Punto de entrada principal para el sistema ADAI
Permite ejecutar clases específicas usando el sistema modular
"""

import cv2
import os
import sys
import multiprocessing
from multiprocessing import freeze_support

# Agregar el directorio de módulos al path
current_dir = os.path.dirname(os.path.abspath(__file__))  # clases/main/
project_root = os.path.dirname(os.path.dirname(current_dir))  # ia-clases/
modules_dir = os.path.join(project_root, "modules")
classes_dir = os.path.join(project_root, "clases")

if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
if classes_dir not in sys.path:
    sys.path.insert(0, classes_dir)

def run_class_by_name(class_name):
    """
    Ejecuta una clase específica por nombre
    
    Args:
        class_name (str): Nombre de la clase a ejecutar (ej: "mi_clase_de_robótica_clase")
    """
    try:
        print(f"🚀 Buscando clase: {class_name}")
        
        # Buscar la carpeta de la clase
        class_folder = os.path.join(classes_dir, class_name)
        if not os.path.exists(class_folder):
            print(f"❌ No se encontró la carpeta de clase: {class_folder}")
            return False
        
        # Buscar el archivo principal de la clase
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
            print(f"   Archivos buscados: {possible_names}")
            return False
        
        print(f"✅ Archivo encontrado: {main_file}")
        
        # Importar y ejecutar la clase
        module_name = class_name.replace(" ", "_").replace("-", "_")
        
        # Agregar el directorio de la clase al path
        if class_folder not in sys.path:
            sys.path.insert(0, class_folder)
        
        try:
            # Importar el módulo dinámicamente
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar y ejecutar la función main
            if hasattr(module, 'main'):
                print(f"🎯 Ejecutando main() de {class_name}")
                module.main()
                return True
            elif hasattr(module, 'run_complete_class'):
                # Si es una clase, crear instancia y ejecutar
                print(f"🎯 Ejecutando clase {class_name}")
                # Buscar la clase principal
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name != 'object' and 
                        hasattr(attr, 'run_complete_class')):
                        class_instance = attr()
                        return class_instance.run_complete_class()
            else:
                print(f"❌ No se encontró función main() o clase con run_complete_class()")
                return False
                
        except Exception as e:
            print(f"❌ Error importando módulo: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando clase {class_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_available_classes():
    """Lista todas las clases disponibles"""
    print("📚 Clases disponibles:")
    
    if not os.path.exists(classes_dir):
        print("❌ Directorio de clases no encontrado")
        return []
    
    classes = []
    for item in os.listdir(classes_dir):
        item_path = os.path.join(classes_dir, item)
        if os.path.isdir(item_path) and not item.startswith('.'):
            classes.append(item)
    
    for i, class_name in enumerate(classes, 1):
        print(f"  {i}. {class_name}")
    
    return classes

def main():
    """Función principal"""
    try:
        print("="*60)
        print("🤖 ADAI - SISTEMA MODULAR DE CLASES")
            print("="*60)
            
        # Si se proporciona argumento, ejecutar esa clase específica
        if len(sys.argv) > 1:
            class_name = sys.argv[1]
            print(f"🎯 Ejecutando clase específica: {class_name}")
            success = run_class_by_name(class_name)
            
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
        
        print(f"\n¿Qué clase deseas ejecutar? (1-{len(classes)})")
        
        try:
            choice = input("Ingresa el número: ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(classes):
                selected_class = classes[choice_idx]
                print(f"\n🎯 Ejecutando: {selected_class}")
                success = run_class_by_name(selected_class)
                
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
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    freeze_support()
    main()

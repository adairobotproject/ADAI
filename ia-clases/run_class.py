#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para ejecutar una clase específica
Uso: python run_class.py mi_clase_de_robótica_clase
"""

import os
import sys
import multiprocessing

# Agregar rutas necesarias
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")
classes_dir = os.path.join(current_dir, "clases")

if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
if classes_dir not in sys.path:
    sys.path.insert(0, classes_dir)

def run_class(class_name):
    """
    Ejecuta una clase específica
    
    Args:
        class_name (str): Nombre de la clase a ejecutar
    """
    try:
        print(f"🚀 Ejecutando clase: {class_name}")
        
        # Importar y ejecutar main modular
        from clases.main.main_modular import run_class_by_name
        
        success = run_class_by_name(class_name)
        
        if success:
            print("✅ Clase completada exitosamente")
            return True
        else:
            print("❌ La clase tuvo errores")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando clase: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python run_class.py <nombre_clase>")
        print("Ejemplo: python run_class.py mi_clase_de_robótica_clase")
        
        # Mostrar clases disponibles
        try:
            from clases.main.main_modular import list_available_classes
            classes = list_available_classes()
            if classes:
                print(f"\nClases disponibles:")
                for i, class_name in enumerate(classes, 1):
                    print(f"  {i}. {class_name}")
        except Exception as e:
            print(f"Error listando clases: {e}")
        
        return
    
    class_name = sys.argv[1]
    success = run_class(class_name)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

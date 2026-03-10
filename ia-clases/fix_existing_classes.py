#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir automáticamente las rutas de importación en clases existentes
"""

import os
import re
import glob

def fix_class_imports(class_file_path):
    """Corregir las rutas de importación en un archivo de clase"""
    try:
        print(f"🔧 Corrigiendo: {class_file_path}")
        
        # Leer el archivo
        with open(class_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón para encontrar la sección de importación de módulos
        old_pattern = r'# Agregar el directorio de módulos al path\nimport sys\nimport os\ncurrent_dir = os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\nmodules_dir = os\.path\.join\(current_dir, "modules"\)\nif modules_dir not in sys\.path:\n    sys\.path\.insert\(0, modules_dir\)'
        
        new_code = '''# Agregar el directorio de módulos al path
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
# Los módulos están en el directorio padre (ia-clases/modules)
parent_dir = os.path.dirname(current_dir)
modules_dir = os.path.join(parent_dir, "modules")
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)'''
        
        # Reemplazar si se encuentra el patrón
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_code, content)
            
            # Escribir el archivo corregido
            with open(class_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Corregido: {class_file_path}")
            return True
        else:
            print(f"ℹ️ No necesita corrección: {class_file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error corrigiendo {class_file_path}: {e}")
        return False

def fix_all_existing_classes():
    """Corregir todas las clases existentes"""
    print("🔧 Corrigiendo rutas de importación en clases existentes")
    print("="*60)
    
    # Buscar todos los archivos .py en las carpetas de clases
    classes_dir = "clases"
    if not os.path.exists(classes_dir):
        print(f"❌ No se encontró el directorio: {classes_dir}")
        return False
    
    # Buscar archivos .py en subdirectorios de clases
    pattern = os.path.join(classes_dir, "*", "*.py")
    class_files = glob.glob(pattern)
    
    if not class_files:
        print("ℹ️ No se encontraron archivos de clase para corregir")
        return True
    
    print(f"📁 Encontrados {len(class_files)} archivos de clase")
    
    corrected_count = 0
    for class_file in class_files:
        if fix_class_imports(class_file):
            corrected_count += 1
    
    print(f"\n✅ Corrección completada:")
    print(f"   - Archivos procesados: {len(class_files)}")
    print(f"   - Archivos corregidos: {corrected_count}")
    print(f"   - Archivos sin cambios: {len(class_files) - corrected_count}")
    
    return True

def main():
    """Función principal"""
    print("🚀 Corrector de Rutas de Importación")
    print("="*50)
    
    success = fix_all_existing_classes()
    
    if success:
        print("\n🎉 ¡Corrección completada exitosamente!")
        print("✅ Todas las clases existentes han sido corregidas")
        print("✅ Las rutas de importación apuntan a ia-clases/modules/")
    else:
        print("\n❌ Error en la corrección")
        print("⚠️ Revisar los errores mostrados arriba")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

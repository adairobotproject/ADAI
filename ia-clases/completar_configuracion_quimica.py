#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Completar Configuración de Clase de Química
==========================================

Script para completar la configuración copiando archivos PDF
"""

import os
import shutil
import json

def completar_configuracion_quimica():
    """Completar la configuración de la clase de química"""
    
    print("🧪 Completando configuración de clase de química...")
    print("="*50)
    
    # Rutas de archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clases_dir = os.path.join(script_dir, "clases")
    quimica_dir = os.path.join(clases_dir, "clase_quimica")
    clase_quimica_dir = os.path.join(clases_dir, "clase_quimica_neutralizacion")
    
    # Verificar archivos fuente
    pdf_principal = os.path.join(quimica_dir, "Clase_Neutralizacion_Bicarbonato.pdf")
    pdf_demo = os.path.join(quimica_dir, "Demo_Paso_a_Paso.pdf")
    
    if not os.path.exists(pdf_principal):
        print(f"❌ No se encontró: {pdf_principal}")
        return False
    
    if not os.path.exists(pdf_demo):
        print(f"❌ No se encontró: {pdf_demo}")
        return False
    
    print("✅ Archivos PDF fuente encontrados")
    
    # Crear directorios si no existen
    pdfs_dir = os.path.join(clase_quimica_dir, "pdfs")
    os.makedirs(pdfs_dir, exist_ok=True)
    
    # Copiar archivos PDF
    try:
        # Copiar PDF principal
        dest_principal = os.path.join(pdfs_dir, "Clase_Neutralizacion_Bicarbonato.pdf")
        shutil.copy2(pdf_principal, dest_principal)
        print(f"✅ PDF principal copiado: {dest_principal}")
        
        # Copiar PDF demo
        dest_demo = os.path.join(pdfs_dir, "Demo_Paso_a_Paso.pdf")
        shutil.copy2(pdf_demo, dest_demo)
        print(f"✅ PDF demo copiado: {dest_demo}")
        
        # Actualizar configuración de la clase
        actualizar_configuracion_clase(clase_quimica_dir, dest_principal, dest_demo)
        
        print("🎉 Configuración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error copiando archivos: {e}")
        return False

def actualizar_configuracion_clase(clase_dir, pdf_principal, pdf_demo):
    """Actualizar la configuración de la clase"""
    
    # Actualizar class_config.json
    config_file = os.path.join(clase_dir, "class_config.json")
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Actualizar rutas de PDFs
    config["pdfs"] = {
        "principal": os.path.basename(pdf_principal),
        "demo": os.path.basename(pdf_demo)
    }
    
    config["resources"] = {
        "pdfs": [
            os.path.basename(pdf_principal),
            os.path.basename(pdf_demo)
        ]
    }
    
    # Guardar configuración actualizada
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuración actualizada: {config_file}")

def crear_script_ejecucion():
    """Crear script de ejecución para la clase de química"""
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Clase de Química
===========================

Script para ejecutar la clase de química desde la línea de comandos
"""

import os
import sys

def ejecutar_clase_quimica():
    """Ejecutar la clase de química"""
    
    # Obtener ruta del script actual
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clase_dir = os.path.join(script_dir, "clases", "clase_quimica_neutralizacion")
    clase_file = os.path.join(clase_dir, "clase_quimica_neutralizacion")
    
    if not os.path.exists(clase_file):
        print(f"❌ No se encontró la clase: {clase_file}")
        return False
    
    print("🧪 Ejecutando clase de química...")
    print("="*50)
    
    try:
        # Cambiar al directorio de la clase
        original_dir = os.getcwd()
        os.chdir(clase_dir)
        
        # Ejecutar la clase
        os.system(f'python "{os.path.basename(clase_file)}"')
        
        # Volver al directorio original
        os.chdir(original_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando clase: {e}")
        return False

if __name__ == "__main__":
    ejecutar_clase_quimica()
'''
    
    # Guardar script de ejecución
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_file = os.path.join(script_dir, "ejecutar_clase_quimica.py")
    
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ Script de ejecución creado: {script_file}")

if __name__ == "__main__":
    if completar_configuracion_quimica():
        crear_script_ejecucion()
        print("\n🎉 ¡Clase de química completamente configurada!")
        print("\n📋 Para ejecutar la clase:")
        print("   python ejecutar_clase_quimica.py")
        print("\n📋 O desde el robot_gui:")
        print("   1. Ir a la pestaña 'Class Controller'")
        print("   2. Buscar 'clase_quimica_neutralizacion'")
        print("   3. Hacer clic en 'Ejecutar'")
    else:
        print("❌ Error completando la configuración")

#!/usr/bin/env python3
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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agregar Clase de Química al Metadata
====================================

Script para agregar la clase de química al archivo classes_metadata.json
"""

import os
import json
import datetime
from pathlib import Path

def agregar_clase_quimica_metadata():
    """Agregar la clase de química al metadata"""
    
    print("🧪 Agregando clase de química al metadata...")
    print("="*50)
    
    # Rutas de archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    clases_dir = os.path.join(script_dir, "clases")
    metadata_file = os.path.join(clases_dir, "classes_metadata.json")
    clase_quimica_dir = os.path.join(clases_dir, "clase_quimica_neutralizacion")
    
    # Verificar que existe la clase
    if not os.path.exists(clase_quimica_dir):
        print(f"❌ No se encontró la clase: {clase_quimica_dir}")
        return False
    
    # Verificar que existe el metadata
    if not os.path.exists(metadata_file):
        print(f"❌ No se encontró el metadata: {metadata_file}")
        return False
    
    # Cargar metadata existente
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Verificar si la clase ya existe
    clase_existente = None
    for clase in metadata["classes"]:
        if clase["name"] == "clase_quimica_neutralizacion":
            clase_existente = clase
            break
    
    if clase_existente:
        print("⚠️ La clase ya existe en el metadata, actualizando...")
        metadata["classes"].remove(clase_existente)
    
    # Obtener información de archivos
    clase_file = os.path.join(clase_quimica_dir, "clase_quimica_neutralizacion")
    config_file = os.path.join(clase_quimica_dir, "class_config.json")
    pdfs_dir = os.path.join(clase_quimica_dir, "pdfs")
    
    # Obtener tamaños y fechas de modificación
    clase_size = os.path.getsize(clase_file) if os.path.exists(clase_file) else 0
    clase_modified = datetime.datetime.fromtimestamp(os.path.getmtime(clase_file)).isoformat() if os.path.exists(clase_file) else datetime.datetime.now().isoformat()
    
    config_size = os.path.getsize(config_file) if os.path.exists(config_file) else 0
    config_modified = datetime.datetime.fromtimestamp(os.path.getmtime(config_file)).isoformat() if os.path.exists(config_file) else datetime.datetime.now().isoformat()
    
    # Obtener información de PDFs
    pdfs_info = []
    if os.path.exists(pdfs_dir):
        for pdf_file in os.listdir(pdfs_dir):
            if pdf_file.endswith('.pdf'):
                pdf_path = os.path.join(pdfs_dir, pdf_file)
                pdf_size = os.path.getsize(pdf_path)
                pdf_modified = datetime.datetime.fromtimestamp(os.path.getmtime(pdf_path)).isoformat()
                pdfs_info.append({
                    "name": pdf_file,
                    "path": f"clases\\clase_quimica_neutralizacion\\pdfs\\{pdf_file}",
                    "size": pdf_size,
                    "modified": pdf_modified
                })
    
    # Crear entrada de la clase
    nueva_clase = {
        "name": "clase_quimica_neutralizacion",
        "folder": "clase_quimica_neutralizacion",
        "file_path": f"clases\\clase_quimica_neutralizacion\\clase_quimica_neutralizacion",
        "folder_path": f"clases\\clase_quimica_neutralizacion",
        "modified": clase_modified,
        "size": clase_size,
        "title": "Neutralización con Bicarbonato de Sodio",
        "subject": "Química",
        "description": "Clase práctica sobre neutralización de ácidos usando bicarbonato de sodio. Incluye experimento completo con fases de preparación, ejecución y análisis de resultados.",
        "duration": "60 minutos",
        "created_at": "2025-08-31T10:48:30.606114",
        "resources": {
            "files": [
                {
                    "name": "clase_quimica_neutralizacion",
                    "path": f"clases\\clase_quimica_neutralizacion\\clase_quimica_neutralizacion",
                    "size": clase_size,
                    "modified": clase_modified
                }
            ],
            "images": [],
            "pdfs": pdfs_info,
            "qrs": [],
            "other": [
                {
                    "name": "class_config.json",
                    "path": f"clases\\clase_quimica_neutralizacion\\class_config.json",
                    "size": config_size,
                    "modified": config_modified
                }
            ]
        },
        "config": {
            "title": "Neutralización con Bicarbonato de Sodio",
            "subject": "Química",
            "description": "Clase práctica sobre neutralización de ácidos usando bicarbonato de sodio",
            "duration": "60 minutos",
            "created_at": "2025-08-31T10:48:30.606114",
            "main_file": "clase_quimica_neutralizacion",
            "folder_name": "clase_quimica_neutralizacion",
            "version": "1.0",
            "author": "ADAI Class Builder",
            "type": "experimental",
            "difficulty": "intermedio",
            "safety_level": "bajo",
            "tags": [
                "química",
                "experimental",
                "neutralización",
                "bicarbonato",
                "laboratorio"
            ],
            "features": [
                "Introducción al experimento",
                "Guías de seguridad",
                "Teoría de neutralización",
                "6 fases del experimento",
                "Demostración paso a paso",
                "Análisis de resultados",
                "Ventanas visuales interactivas",
                "Texto a voz con ADAI",
                "Presentación de PDFs integrada"
            ],
            "materials": [
                "Bicarbonato de sodio (NaHCO₃)",
                "Ácido cítrico (C₆H₈O₇)",
                "Agua destilada",
                "Vasos de precipitado",
                "Probetas",
                "Termómetro",
                "Papel indicador de pH"
            ],
            "learning_objectives": [
                "Comprender el concepto de neutralización",
                "Identificar reactivos ácidos y básicos",
                "Observar reacciones químicas en tiempo real",
                "Registrar observaciones científicas",
                "Aplicar medidas de seguridad en el laboratorio"
            ],
            "pdfs": {
                "principal": "Clase_Neutralizacion_Bicarbonato.pdf",
                "demo": "Demo_Paso_a_Paso.pdf"
            },
            "resources": {
                "pdfs": [
                    "Clase_Neutralizacion_Bicarbonato.pdf",
                    "Demo_Paso_a_Paso.pdf"
                ]
            }
        }
    }
    
    # Agregar la clase al inicio de la lista
    metadata["classes"].insert(0, nueva_clase)
    
    # Actualizar timestamp de último escaneo
    metadata["last_scan"] = datetime.datetime.now().isoformat()
    
    # Guardar metadata actualizado
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("✅ Clase de química agregada al metadata exitosamente!")
    print(f"📁 Archivo: {metadata_file}")
    print(f"📊 Total de clases: {len(metadata['classes'])}")
    
    # Mostrar información de la clase agregada
    print("\n📋 Información de la clase agregada:")
    print(f"   Título: {nueva_clase['title']}")
    print(f"   Materia: {nueva_clase['subject']}")
    print(f"   Duración: {nueva_clase['duration']}")
    print(f"   PDFs: {len(pdfs_info)} archivos")
    print(f"   Tamaño: {clase_size} bytes")
    
    return True

if __name__ == "__main__":
    if agregar_clase_quimica_metadata():
        print("\n🎉 ¡Clase de química agregada al metadata exitosamente!")
        print("\n📋 Ahora puedes:")
        print("   1. Ver la clase en el 'Class Controller' del robot_gui")
        print("   2. Ejecutarla desde la app móvil")
        print("   3. Buscarla en el sistema de gestión de clases")
    else:
        print("❌ Error agregando la clase al metadata")

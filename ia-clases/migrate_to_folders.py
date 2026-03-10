#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to convert existing classes to folder structure
"""

import os
import json
import shutil
import datetime

def migrate_classes_to_folders():
    """Migrar clases existentes al nuevo sistema de carpetas"""
    print("🔄 Migrando clases al nuevo sistema de carpetas...")
    print("=" * 60)
    
    clases_dir = "clases"
    if not os.path.exists(clases_dir):
        print("❌ Directorio de clases no encontrado")
        return False
    
    # Leer metadata existente
    metadata_file = os.path.join(clases_dir, "classes_metadata.json")
    if not os.path.exists(metadata_file):
        print("❌ Archivo de metadata no encontrado")
        return False
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo metadata: {e}")
        return False
    
    classes = metadata.get("classes", [])
    if not classes:
        print("⚠️ No hay clases para migrar")
        return True
    
    print(f"📚 Encontradas {len(classes)} clases para migrar")
    
    migrated_count = 0
    errors = []
    
    for class_info in classes:
        try:
            class_name = class_info['name']
            file_path = class_info['file_path']
            
            print(f"\n🔄 Migrando: {class_name}")
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                print(f"   ⚠️ Archivo no encontrado: {file_path}")
                continue
            
            # Crear nombre de carpeta
            folder_name = class_name.replace('.py', '').replace(' ', '_').lower()
            class_folder = os.path.join(clases_dir, folder_name)
            
            # Crear carpeta si no existe
            if not os.path.exists(class_folder):
                os.makedirs(class_folder)
                print(f"   ✅ Carpeta creada: {folder_name}")
            
            # Crear subcarpetas
            subfolders = ["images", "pdfs", "qrs", "resources"]
            for subfolder in subfolders:
                subfolder_path = os.path.join(class_folder, subfolder)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
            
            # Mover archivo principal
            new_file_path = os.path.join(class_folder, class_name)
            if not os.path.exists(new_file_path):
                shutil.move(file_path, new_file_path)
                print(f"   ✅ Archivo movido: {class_name}")
            else:
                print(f"   ⚠️ Archivo ya existe en destino: {class_name}")
            
            # Crear archivo de configuración
            config = {
                "title": class_info.get("title", folder_name.replace("_", " ").title()),
                "subject": class_info.get("subject", "Robótica"),
                "description": class_info.get("description", f"Clase: {folder_name}"),
                "duration": class_info.get("duration", "45 minutos"),
                "created_at": class_info.get("created_at", datetime.datetime.now().isoformat()),
                "main_file": class_name,
                "folder_name": folder_name,
                "migrated_at": datetime.datetime.now().isoformat()
            }
            
            config_file = os.path.join(class_folder, "class_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"   ✅ Configuración creada")
            migrated_count += 1
            
        except Exception as e:
            error_msg = f"Error migrando {class_name}: {e}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)
    
    # Crear nuevo metadata
    print(f"\n📝 Creando nuevo metadata...")
    
    # Escanear clases migradas
    new_classes = []
    for item in os.listdir(clases_dir):
        class_folder = os.path.join(clases_dir, item)
        
        if not os.path.isdir(class_folder):
            continue
        
        # Buscar archivo principal
        main_file = None
        for file in os.listdir(class_folder):
            if file.endswith('.py') and not file.startswith('__'):
                main_file = file
                break
        
        if not main_file:
            continue
        
        # Obtener información de la clase
        main_file_path = os.path.join(class_folder, main_file)
        stat = os.stat(main_file_path)
        
        # Leer configuración
        config_file = os.path.join(class_folder, "class_config.json")
        class_config = {}
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    class_config = json.load(f)
            except Exception as e:
                print(f"⚠️ Error leyendo config de {item}: {e}")
        
        # Escanear recursos
        resources = {
            "files": [],
            "images": [],
            "pdfs": [],
            "qrs": [],
            "other": []
        }
        
        for file in os.listdir(class_folder):
            file_path = os.path.join(class_folder, file)
            
            if os.path.isfile(file_path):
                file_info = {
                    "name": file,
                    "path": file_path,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                
                # Categorizar archivo
                if file.endswith('.py') and not file.startswith('__'):
                    resources["files"].append(file_info)
                elif file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    resources["images"].append(file_info)
                elif file.lower().endswith('.pdf'):
                    resources["pdfs"].append(file_info)
                elif 'qr' in file.lower() or 'code' in file.lower():
                    resources["qrs"].append(file_info)
                else:
                    resources["other"].append(file_info)
        
        # Crear información de la clase
        class_info = {
            "name": main_file,
            "folder": item,
            "file_path": main_file_path,
            "folder_path": class_folder,
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size": stat.st_size,
            "title": class_config.get("title", item.replace("_", " ").title()),
            "subject": class_config.get("subject", "Robótica"),
            "description": class_config.get("description", f"Clase: {item}"),
            "duration": class_config.get("duration", "45 minutos"),
            "created_at": class_config.get("created_at", datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()),
            "resources": resources,
            "config": class_config
        }
        
        new_classes.append(class_info)
    
    # Guardar nuevo metadata
    new_metadata = {
        "classes": new_classes,
        "last_scan": datetime.datetime.now().isoformat(),
        "migrated_at": datetime.datetime.now().isoformat()
    }
    
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(new_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Nuevo metadata guardado")
    
    # Resumen
    print(f"\n" + "=" * 60)
    print("📊 RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"✅ Clases migradas: {migrated_count}")
    print(f"❌ Errores: {len(errors)}")
    print(f"📁 Total de clases en nuevo formato: {len(new_classes)}")
    
    if errors:
        print(f"\n❌ Errores encontrados:")
        for error in errors:
            print(f"   - {error}")
    
    print(f"\n🎉 Migración completada!")
    print(f"📁 Las clases ahora están organizadas en carpetas individuales")
    print(f"📋 Cada clase tiene su propio archivo de configuración")
    print(f"📁 Recursos organizados en subcarpetas (images, pdfs, qrs, resources)")
    
    return True

def main():
    """Función principal"""
    print("🔄 Migración al Sistema de Carpetas Individuales")
    print("=" * 60)
    
    # Confirmar migración
    response = input("¿Deseas continuar con la migración? (s/N): ")
    if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Migración cancelada")
        return
    
    # Realizar migración
    success = migrate_classes_to_folders()
    
    if success:
        print(f"\n✅ Migración exitosa!")
        print(f"🔄 Ahora puedes usar el nuevo sistema de carpetas")
    else:
        print(f"\n❌ Error en la migración")

if __name__ == "__main__":
    main()

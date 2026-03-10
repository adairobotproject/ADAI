#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de configuración modular para clases ADAI
Maneja la configuración de clases de manera centralizada
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# Ensure paths module is importable (lives in ia-clases/)
_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _parent not in sys.path:
    sys.path.insert(0, _parent)
from paths import get_data_dir

class ClassConfigManager:
    """
    Gestor de configuración para clases ADAI
    """

    def __init__(self, classes_dir: str = None):
        """
        Inicializa el gestor de configuración

        Args:
            classes_dir (str): Directorio donde están las clases
        """
        if classes_dir is None:
            classes_dir = os.path.join(get_data_dir(), "clases")
        
        self.classes_dir = classes_dir
        self.default_config = {
            "title": "Clase ADAI",
            "subject": "Robótica",
            "description": "Una clase educativa con ADAI",
            "duration": "45 minutos",
            "created_at": "",
            "main_file": "main.py",
            "folder_name": "",
            "use_diagnostic": True,
            "use_pdf": True,
            "use_demo": False,
            "use_final_exam": True,
            "diagnostic_qr": "",
            "pdf_path": "",
            "demo_pdf_path": "",
            "final_exam_qr": "",
            "sequence_mapping": {},
            "question_bank": "default",
            "esp32_enabled": False,
            "esp32_host": "192.168.1.100",
            "esp32_port": 80
        }
    
    def load_class_config(self, class_name: str) -> Dict[str, Any]:
        """
        Carga la configuración de una clase específica
        
        Args:
            class_name (str): Nombre de la clase
            
        Returns:
            Dict[str, Any]: Configuración de la clase
        """
        try:
            class_folder = os.path.join(self.classes_dir, class_name)
            config_file = os.path.join(class_folder, "class_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Fusionar con configuración por defecto
                merged_config = self.default_config.copy()
                merged_config.update(config)
                
                # Asegurar que los paths sean absolutos
                merged_config = self._resolve_paths(merged_config, class_folder)
                
                print(f"✅ Configuración cargada para: {class_name}")
                return merged_config
            else:
                print(f"⚠️ No se encontró config.json para {class_name}, usando configuración por defecto")
                config = self.default_config.copy()
                config["folder_name"] = class_name
                config["title"] = class_name.replace("_", " ").title()
                return config
                
        except Exception as e:
            print(f"❌ Error cargando configuración para {class_name}: {e}")
            config = self.default_config.copy()
            config["folder_name"] = class_name
            config["title"] = class_name.replace("_", " ").title()
            return config
    
    def save_class_config(self, class_name: str, config: Dict[str, Any]) -> bool:
        """
        Guarda la configuración de una clase
        
        Args:
            class_name (str): Nombre de la clase
            config (Dict[str, Any]): Configuración a guardar
            
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            class_folder = os.path.join(self.classes_dir, class_name)
            os.makedirs(class_folder, exist_ok=True)
            
            config_file = os.path.join(class_folder, "class_config.json")
            
            # Convertir paths absolutos a relativos para el JSON
            save_config = self._make_paths_relative(config, class_folder)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración guardada para: {class_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando configuración para {class_name}: {e}")
            return False
    
    def list_classes(self) -> list:
        """
        Lista todas las clases disponibles
        
        Returns:
            list: Lista de nombres de clases
        """
        try:
            if not os.path.exists(self.classes_dir):
                return []
            
            classes = []
            for item in os.listdir(self.classes_dir):
                item_path = os.path.join(self.classes_dir, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    classes.append(item)
            
            return sorted(classes)
            
        except Exception as e:
            print(f"❌ Error listando clases: {e}")
            return []
    
    def get_class_info(self, class_name: str) -> Dict[str, Any]:
        """
        Obtiene información básica de una clase
        
        Args:
            class_name (str): Nombre de la clase
            
        Returns:
            Dict[str, Any]: Información de la clase
        """
        config = self.load_class_config(class_name)
        class_folder = os.path.join(self.classes_dir, class_name)
        
        info = {
            "name": class_name,
            "folder": class_folder,
            "exists": os.path.exists(class_folder),
            "has_config": os.path.exists(os.path.join(class_folder, "class_config.json")),
            "has_main_file": False,
            "main_file_path": None
        }
        
        # Buscar archivo principal
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
                info["has_main_file"] = True
                info["main_file_path"] = file_path
                break
        
        # Agregar información de configuración
        info.update({
            "title": config.get("title", class_name),
            "subject": config.get("subject", "Robótica"),
            "description": config.get("description", ""),
            "duration": config.get("duration", "45 minutos"),
            "use_diagnostic": config.get("use_diagnostic", True),
            "use_pdf": config.get("use_pdf", True),
            "use_demo": config.get("use_demo", False),
            "use_final_exam": config.get("use_final_exam", True)
        })
        
        return info
    
    def _resolve_paths(self, config: Dict[str, Any], class_folder: str) -> Dict[str, Any]:
        """
        Resuelve paths relativos a absolutos
        
        Args:
            config (Dict[str, Any]): Configuración
            class_folder (str): Directorio de la clase
            
        Returns:
            Dict[str, Any]: Configuración con paths absolutos
        """
        path_fields = ["diagnostic_qr", "pdf_path", "demo_pdf_path", "final_exam_qr"]
        
        for field in path_fields:
            if field in config and config[field]:
                path = config[field]
                if not os.path.isabs(path):
                    # Si es relativo, asumir que está en el directorio de la clase
                    config[field] = os.path.join(class_folder, path)
                # Si ya es absoluto, mantenerlo
        
        return config
    
    def _make_paths_relative(self, config: Dict[str, Any], class_folder: str) -> Dict[str, Any]:
        """
        Convierte paths absolutos a relativos para guardar en JSON
        
        Args:
            config (Dict[str, Any]): Configuración
            class_folder (str): Directorio de la clase
            
        Returns:
            Dict[str, Any]: Configuración con paths relativos
        """
        path_fields = ["diagnostic_qr", "pdf_path", "demo_pdf_path", "final_exam_qr"]
        
        for field in path_fields:
            if field in config and config[field]:
                path = config[field]
                if os.path.isabs(path):
                    try:
                        # Intentar hacer el path relativo al directorio de la clase
                        rel_path = os.path.relpath(path, class_folder)
                        config[field] = rel_path
                    except ValueError:
                        # Si no se puede hacer relativo, mantener absoluto
                        pass
        
        return config

# Instancia global del gestor de configuración
config_manager = ClassConfigManager()

def get_class_config(class_name: str) -> Dict[str, Any]:
    """
    Función de conveniencia para obtener configuración de clase
    
    Args:
        class_name (str): Nombre de la clase
        
    Returns:
        Dict[str, Any]: Configuración de la clase
    """
    return config_manager.load_class_config(class_name)

def save_class_config(class_name: str, config: Dict[str, Any]) -> bool:
    """
    Función de conveniencia para guardar configuración de clase
    
    Args:
        class_name (str): Nombre de la clase
        config (Dict[str, Any]): Configuración a guardar
        
    Returns:
        bool: True si se guardó exitosamente
    """
    return config_manager.save_class_config(class_name, config)

def list_available_classes() -> list:
    """
    Función de conveniencia para listar clases disponibles
    
    Returns:
        list: Lista de nombres de clases
    """
    return config_manager.list_classes()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Manager - Gestión de clases con carpetas individuales
"""

import os
import json
import datetime
import subprocess
import sys
import threading
import time
from typing import List, Dict, Optional, Callable
from paths import get_data_dir

# Import progress manager
try:
    from class_progress_manager import get_progress_manager, ClassPhase
    PROGRESS_MANAGER_AVAILABLE = True
except ImportError:
    PROGRESS_MANAGER_AVAILABLE = False
    print("⚠️ Progress Manager no disponible")

class ClassManager:
    """Gestor de clases con carpetas individuales para cada clase"""
    
    def __init__(self, classes_dir: str = None):
        if classes_dir is None:
            classes_dir = os.path.join(get_data_dir(), "clases")
        self.classes_dir = classes_dir
        self.metadata_file = os.path.join(classes_dir, "classes_metadata.json")
        
        # Variables de control de ejecución con threading
        self.current_process = None
        self.execution_thread = None
        self.stop_execution_flag = False
        self.class_execution_active = False
        self.current_class_info = None
        self.execution_lock = threading.Lock()  # Para sincronización
        
        # Callbacks para notificar cambios de estado
        self.on_class_started: Optional[Callable] = None
        self.on_class_executed: Optional[Callable] = None
        self.on_class_error: Optional[Callable] = None
        self.on_class_stopped: Optional[Callable] = None
        self.on_class_progress: Optional[Callable] = None
        
        # Progress manager
        self.progress_manager = None
        if PROGRESS_MANAGER_AVAILABLE:
            self.progress_manager = get_progress_manager()
        
        # Asegurar que el directorio existe
        if not os.path.exists(classes_dir):
            os.makedirs(classes_dir)
            print(f"✅ Directorio de clases creado: {classes_dir}")
        
        # Crear metadata inicial si no existe
        if not os.path.exists(self.metadata_file):
            self._create_initial_metadata()
    
    def _create_initial_metadata(self):
        """Crear metadata inicial"""
        initial_metadata = {
            "classes": [],
            "last_scan": datetime.datetime.now().isoformat()
        }
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(initial_metadata, f, indent=2, ensure_ascii=False)
    
    def scan_classes(self) -> List[Dict]:
        """
        Escanear clases en el directorio
        Ahora cada clase tiene su propia carpeta
        """
        classes = []
        
        try:
            if not os.path.exists(self.classes_dir):
                return classes
            
            # Buscar carpetas de clases
            for item in os.listdir(self.classes_dir):
                class_folder = os.path.join(self.classes_dir, item)
                
                # Solo procesar carpetas
                if not os.path.isdir(class_folder):
                    continue
                
                # Buscar archivo principal de la clase
                main_file = None
                for file in os.listdir(class_folder):
                    if file.endswith('.py') and not file.startswith('__'):
                        main_file = file
                        break
                
                if not main_file:
                    continue
                
                # Obtener información de la clase
                class_info = self._get_class_info(class_folder, main_file, item)
                if class_info:
                    classes.append(class_info)
            
            # Actualizar metadata
            self._update_metadata(classes)
            
            print(f"✅ Escaneadas {len(classes)} clases")
            return classes
            
        except Exception as e:
            print(f"❌ Error escaneando clases: {e}")
            return []
    
    def _get_class_info(self, class_folder: str, main_file: str, folder_name: str) -> Optional[Dict]:
        """Obtener información de una clase desde su carpeta"""
        try:
            main_file_path = os.path.join(class_folder, main_file)
            
            # Obtener estadísticas del archivo
            stat = os.stat(main_file_path)
            
            # Buscar archivo de configuración de la clase
            config_file = os.path.join(class_folder, "class_config.json")
            class_config = {}
            
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        class_config = json.load(f)
                except Exception as e:
                    print(f"⚠️ Error leyendo config de {folder_name}: {e}")
            
            # Listar recursos de la clase
            resources = self._scan_class_resources(class_folder)
            
            # Crear información de la clase
            class_info = {
                "name": main_file,
                "folder": folder_name,
                "file_path": main_file_path,
                "folder_path": class_folder,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
                "title": class_config.get("title", folder_name.replace("_", " ").title()),
                "subject": class_config.get("subject", "Robótica"),
                "description": class_config.get("description", f"Clase: {folder_name}"),
                "duration": class_config.get("duration", "45 minutos"),
                "created_at": class_config.get("created_at", datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()),
                "resources": resources,
                "config": class_config
            }
            
            return class_info
            
        except Exception as e:
            print(f"❌ Error obteniendo info de {folder_name}: {e}")
            return None
    
    def _scan_class_resources(self, class_folder: str) -> Dict:
        """Escanear recursos de una clase"""
        resources = {
            "files": [],
            "images": [],
            "pdfs": [],
            "qrs": [],
            "demo": [],
            "other": []
        }
        
        try:
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
                    elif file.lower().endswith('.json') and 'demo' in file.lower():
                        resources["demo"].append(file_info)
                    else:
                        resources["other"].append(file_info)
            
        except Exception as e:
            print(f"⚠️ Error escaneando recursos: {e}")
        
        return resources
    
    def _update_metadata(self, classes: List[Dict]):
        """Actualizar archivo de metadata"""
        try:
            metadata = {
                "classes": classes,
                "last_scan": datetime.datetime.now().isoformat()
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error actualizando metadata: {e}")
    
    def get_available_classes(self) -> List[Dict]:
        """Obtener lista de clases disponibles"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    return metadata.get("classes", [])
            else:
                return self.scan_classes()
        except Exception as e:
            print(f"❌ Error obteniendo clases: {e}")
            return []
    
    def refresh_classes(self) -> List[Dict]:
        """Actualizar y refrescar la lista de clases disponibles"""
        try:
            print("🔄 Refrescando lista de clases...")
            
            # Escanear clases nuevamente
            classes = self.scan_classes()
            
            # Actualizar metadata
            self._update_metadata(classes)
            
            print(f"✅ Lista de clases actualizada: {len(classes)} clases encontradas")
            
            # Notificar a callbacks si están configurados
            if hasattr(self, 'on_classes_refreshed') and self.on_classes_refreshed:
                try:
                    self.on_classes_refreshed(classes)
                except Exception as e:
                    print(f"⚠️ Error en callback de refresh: {e}")
            
            return classes
            
        except Exception as e:
            print(f"❌ Error refrescando clases: {e}")
            return []
    
    def get_class_by_name(self, class_name: str) -> Optional[Dict]:
        """Obtener información de una clase específica"""
        classes = self.get_available_classes()
        
        # Buscar por nombre exacto del archivo
        for class_info in classes:
            if class_info['name'] == class_name:
                return class_info
        
        # Si no se encuentra, buscar por nombre sin extensión
        class_name_no_ext = class_name.replace('.py', '')
        for class_info in classes:
            if class_info['name'].replace('.py', '') == class_name_no_ext:
                return class_info
        
        # Si no se encuentra, buscar por nombre de carpeta
        for class_info in classes:
            if class_info['folder'] == class_name_no_ext:
                return class_info
        
        # Debug: mostrar clases disponibles
        print(f"🔍 Buscando clase: '{class_name}'")
        print(f"📚 Clases disponibles:")
        for class_info in classes:
            print(f"   - {class_info['name']} (carpeta: {class_info['folder']})")
        
        return None
    
    def create_class_folder(self, class_name: str, title: str, subject: str = "Robótica", 
                          description: str = "", duration: str = "45 minutos") -> str:
        """
        Crear carpeta para una nueva clase
        
        Args:
            class_name: Nombre del archivo principal
            title: Título de la clase
            subject: Materia
            description: Descripción
            duration: Duración
            
        Returns:
            str: Ruta de la carpeta creada
        """
        try:
            # Crear nombre de carpeta
            folder_name = class_name.replace('.py', '').replace(' ', '_').lower()
            class_folder = os.path.join(self.classes_dir, folder_name)
            
            # Crear carpeta si no existe
            if not os.path.exists(class_folder):
                os.makedirs(class_folder)
                print(f"✅ Carpeta de clase creada: {class_folder}")
            
            # Crear archivo de configuración
            config = {
                "title": title,
                "subject": subject,
                "description": description,
                "duration": duration,
                "created_at": datetime.datetime.now().isoformat(),
                "main_file": class_name,
                "folder_name": folder_name
            }
            
            config_file = os.path.join(class_folder, "class_config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Crear subcarpetas para recursos
            subfolders = ["images", "pdfs", "qrs", "resources", "demo"]
            for subfolder in subfolders:
                subfolder_path = os.path.join(class_folder, subfolder)
                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)
            
            print(f"✅ Estructura de clase creada: {class_folder}")
            return class_folder
            
        except Exception as e:
            print(f"❌ Error creando carpeta de clase: {e}")
            return ""
    
    def save_class_file(self, class_name: str, content: str, title: str, 
                       subject: str = "Robótica", description: str = "", 
                       duration: str = "45 minutos") -> bool:
        """
        Guardar archivo de clase en su carpeta correspondiente
        
        Args:
            class_name: Nombre del archivo
            content: Contenido del archivo
            title: Título de la clase
            subject: Materia
            description: Descripción
            duration: Duración
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Crear carpeta de la clase
            class_folder = self.create_class_folder(class_name, title, subject, description, duration)
            
            if not class_folder:
                return False
            
            # Guardar archivo principal
            file_path = os.path.join(class_folder, class_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Clase guardada: {file_path}")
            
            # Actualizar metadata
            self.scan_classes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error guardando clase: {e}")
            return False
    
    def add_resource_to_class(self, class_name: str, resource_path: str, 
                            resource_type: str = "other") -> bool:
        """
        Agregar recurso a una clase
        
        Args:
            class_name: Nombre de la clase
            resource_path: Ruta del recurso
            resource_type: Tipo de recurso (images, pdfs, qrs, other)
            
        Returns:
            bool: True si se agregó correctamente
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                return False
            
            class_folder = class_info['folder_path']
            
            # Determinar carpeta de destino
            if resource_type in ["images", "pdfs", "qrs"]:
                dest_folder = os.path.join(class_folder, resource_type)
            else:
                dest_folder = os.path.join(class_folder, "resources")
            
            # Copiar archivo
            import shutil
            filename = os.path.basename(resource_path)
            dest_path = os.path.join(dest_folder, filename)
            
            shutil.copy2(resource_path, dest_path)
            
            print(f"✅ Recurso agregado: {dest_path}")
            
            # Actualizar metadata
            self.scan_classes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error agregando recurso: {e}")
            return False
    
    def get_class_resources(self, class_name: str) -> Dict:
        """Obtener recursos de una clase específica"""
        class_info = self.get_class_by_name(class_name)
        if class_info:
            return class_info.get('resources', {})
        return {}
    
    def get_class_demo_sequence(self, class_name: str) -> Optional[Dict]:
        """
        Obtener la secuencia de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            
        Returns:
            Dict con información de la secuencia de demo o None si no existe
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                return None
            
            demo_folder = os.path.join(class_info['folder_path'], 'demo')
            if not os.path.exists(demo_folder):
                return None
            
            # Buscar archivo de secuencia en la carpeta demo
            sequence_files = [f for f in os.listdir(demo_folder) if f.endswith('.json')]
            
            if not sequence_files:
                return None
            
            # Tomar el primer archivo de secuencia encontrado
            sequence_file = sequence_files[0]
            sequence_path = os.path.join(demo_folder, sequence_file)
            
            # Leer la secuencia
            with open(sequence_path, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)
            
            return {
                'name': sequence_data.get('name', sequence_file),
                'file': sequence_file,
                'path': sequence_path,
                'data': sequence_data,
                'size': os.path.getsize(sequence_path),
                'modified': datetime.datetime.fromtimestamp(os.path.getmtime(sequence_path)).isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error obteniendo secuencia de demo: {e}")
            return None
    
    def set_class_demo_sequence(self, class_name: str, sequence_data: Dict, sequence_name: str = None) -> bool:
        """
        Establecer la secuencia de demo para una clase
        
        Args:
            class_name: Nombre de la clase
            sequence_data: Datos de la secuencia
            sequence_name: Nombre de la secuencia (opcional)
            
        Returns:
            bool: True si se estableció correctamente
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                return False
            
            demo_folder = os.path.join(class_info['folder_path'], 'demo')
            if not os.path.exists(demo_folder):
                os.makedirs(demo_folder)
            
            # Generar nombre de archivo
            if not sequence_name:
                sequence_name = f"demo_sequence_{int(time.time())}"
            
            sequence_file = f"{sequence_name}.json"
            sequence_path = os.path.join(demo_folder, sequence_file)
            
            # Guardar la secuencia
            with open(sequence_path, 'w', encoding='utf-8') as f:
                json.dump(sequence_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Secuencia de demo guardada: {sequence_path}")
            
            # Actualizar metadata
            self.scan_classes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error estableciendo secuencia de demo: {e}")
            return False
    
    def copy_sequence_to_class_demo(self, class_name: str, sequence_path: str, sequence_name: str = None) -> bool:
        """
        Copiar una secuencia existente a la carpeta de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            sequence_path: Ruta de la secuencia a copiar
            sequence_name: Nombre para la secuencia (opcional)
            
        Returns:
            bool: True si se copió correctamente
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                return False
            
            if not os.path.exists(sequence_path):
                print(f"❌ Secuencia no encontrada: {sequence_path}")
                return False
            
            demo_folder = os.path.join(class_info['folder_path'], 'demo')
            if not os.path.exists(demo_folder):
                os.makedirs(demo_folder)
            
            # Generar nombre de archivo
            if not sequence_name:
                base_name = os.path.splitext(os.path.basename(sequence_path))[0]
                sequence_name = f"{base_name}_demo"
            
            sequence_file = f"{sequence_name}.json"
            dest_path = os.path.join(demo_folder, sequence_file)
            
            # Copiar archivo
            import shutil
            shutil.copy2(sequence_path, dest_path)
            
            print(f"✅ Secuencia copiada a demo: {dest_path}")
            
            # Actualizar metadata
            self.scan_classes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error copiando secuencia a demo: {e}")
            return False
    
    def remove_class_demo_sequence(self, class_name: str) -> bool:
        """
        Eliminar la secuencia de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                return False
            
            demo_folder = os.path.join(class_info['folder_path'], 'demo')
            if not os.path.exists(demo_folder):
                return True  # No hay demo para eliminar
            
            # Eliminar todos los archivos de secuencia en la carpeta demo
            sequence_files = [f for f in os.listdir(demo_folder) if f.endswith('.json')]
            
            for sequence_file in sequence_files:
                sequence_path = os.path.join(demo_folder, sequence_file)
                os.remove(sequence_path)
                print(f"✅ Secuencia eliminada: {sequence_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando secuencia de demo: {e}")
            return False
    
    def execute_class(self, class_name: str, callback: Callable = None) -> bool:
        """
        Ejecutar una clase específica en un hilo separado
        
        Args:
            class_name: Nombre del archivo de la clase
            callback: Función callback para notificar progreso
            
        Returns:
            bool: True si se inició la ejecución correctamente
        """
        try:
            # Check if already executing - if so, stop it first
            process_to_stop = None
            with self.execution_lock:
                if self.class_execution_active:
                    print("⚠️ Ya hay una clase ejecutándose - deteniendo...")
                    # Store current process to stop
                    process_to_stop = self.current_process
                    self.stop_execution_flag = True
                    
            # Stop previous execution outside the lock
            if process_to_stop:
                try:
                    process_to_stop.terminate()
                    process_to_stop.wait(timeout=2)
                except:
                    try:
                        process_to_stop.kill()
                    except:
                        pass
                
                # Wait for cleanup
                import time
                time.sleep(0.5)
            
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                if self.on_class_error:
                    self.on_class_error(f"Clase no encontrada: {class_name}")
                return False
            
            file_path = class_info['file_path']
            class_folder = class_info['folder_path']
            
            if not os.path.exists(file_path):
                print(f"❌ Archivo no encontrado: {file_path}")
                if self.on_class_error:
                    self.on_class_error(f"Archivo no encontrado: {class_name}")
                return False
            
            print(f"🚀 Ejecutando clase: {class_info['title']}")
            
            # Iniciar progreso de la clase
            if self.progress_manager:
                # Determinar tipo de clase basado en la configuración
                class_type = "default"
                if class_info.get('config', {}).get('type') == 'experimental':
                    class_type = "experimental"
                elif class_info.get('config', {}).get('type') == 'theoretical':
                    class_type = "theoretical"
                
                # Obtener duración estimada
                duration_str = class_info.get('duration', '60 minutos')
                duration = 60  # default
                if 'minutos' in duration_str:
                    try:
                        duration = int(duration_str.split()[0])
                    except:
                        duration = 60
                
                self.progress_manager.start_class(class_name, class_type, duration)
                self.progress_manager.set_phase(ClassPhase.DIAGNOSTIC_TEST, "Iniciando clase")
            
            # Set execution state
            self.class_execution_active = True
            self.stop_execution_flag = False
            self.current_class_info = class_info
            
            # Notificar que la clase ha iniciado
            if self.on_class_started:
                self.on_class_started(class_info)
            
            # Ejecutar en hilo separado para no bloquear la UI
            def run_class():
                try:
                    # Cambiar al directorio de la clase
                    original_dir = os.getcwd()
                    os.chdir(class_folder)
                    
                    # Verificar si la clase usa estructura modular
                    is_modular = self._check_if_modular_class(file_path)
                    
                    if is_modular:
                        # Para clases modulares, ejecutar desde el directorio padre para acceder a modules/
                        # class_folder está en ia-clases/clases/[nombre_clase]
                        # Necesitamos ir a ia-clases/ para acceder a modules/
                        parent_dir = os.path.dirname(os.path.dirname(class_folder))
                        os.chdir(parent_dir)
                        print(f"📁 Ejecutando clase modular desde: {parent_dir}")
                        
                        # Usar ruta relativa desde el directorio padre
                        relative_path = os.path.relpath(file_path, parent_dir)
                        file_name = relative_path.replace("\\", "/")
                    else:
                        # Para clases no modulares, usar solo el nombre del archivo
                        file_name = os.path.basename(file_path)
                    
                    # Ejecutar la clase sin capturar output para permitir ventanas de OpenCV
                    self.current_process = subprocess.Popen([sys.executable, file_name], 
                                                          stdout=None,
                                                          stderr=None,
                                                          text=True)
                    
                    # Wait for process to complete or be stopped
                    try:
                        result = self.current_process.wait(timeout=300)  # 5 minutes timeout
                        
                        if self.stop_execution_flag:
                            # Process was stopped by user
                            print(f"⏹️ Ejecución detenida: {class_name}")
                            if self.progress_manager:
                                self.progress_manager.stop_class()
                            if self.on_class_stopped:
                                self.on_class_stopped(class_info, "Ejecución detenida por el usuario")
                        else:
                            # Process completed normally
                            if result == 0:
                                print(f"✅ Clase ejecutada exitosamente: {class_name}")
                                if self.progress_manager:
                                    self.progress_manager.complete_class()
                                if self.on_class_executed:
                                    self.on_class_executed(class_info, "Clase ejecutada correctamente")
                            else:
                                error_msg = f"Error ejecutando clase: código de salida {result}"
                                print(f"❌ {error_msg}")
                                if self.progress_manager:
                                    self.progress_manager.error_in_class(error_msg)
                                if self.on_class_error:
                                    self.on_class_error(error_msg)
                        
                    except subprocess.TimeoutExpired:
                        # Process timed out
                        # self.stop_current_execution()
                        # TODO: Verificar si esto es necesario
                        error_msg = f"Timeout ejecutando clase: {class_name}"
                        print(f"⏰ {error_msg}")
                        if self.on_class_error:
                            self.on_class_error(error_msg)
                    
                    # Restaurar directorio
                    os.chdir(original_dir)
                    
                except Exception as e:
                    error_msg = f"Error ejecutando clase {class_name}: {e}"
                    print(f"❌ {error_msg}")
                    if self.on_class_error:
                        self.on_class_error(error_msg)
                finally:
                    # Clean up
                    with self.execution_lock:
                        self.class_execution_active = False
                        self.current_process = None
                        self.execution_thread = None
                        self.current_class_info = None
            
            # Iniciar ejecución en hilo separado
            self.execution_thread = threading.Thread(target=run_class, daemon=True)
            self.execution_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando ejecución: {e}")
            if self.on_class_error:
                self.on_class_error(f"Error iniciando ejecución: {e}")
            return False
    
    def stop_current_execution(self):
        """Stop the currently executing class"""
        try:
            with self.execution_lock:
                if not self.class_execution_active or not self.current_process:
                    return False
                
                print("⏹️ Deteniendo ejecución actual...")
                self.stop_execution_flag = True
                
                # Actualizar progreso
                if self.progress_manager:
                    self.progress_manager.stop_class()
                
                # Notificar que se está deteniendo
                if self.on_class_stopped and self.current_class_info:
                    self.on_class_stopped(self.current_class_info, "Deteniendo ejecución...")
            
            # Try graceful termination first
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                print("🔨 Forzando terminación...")
                self.current_process.kill()
            
            return True
            
        except Exception as e:
            print(f"❌ Error deteniendo ejecución: {e}")
            return False
    
    def stop_class_execution(self) -> bool:
        """Stop class execution (alias for stop_current_execution)"""
        return self.stop_current_execution()
    
    def force_cleanup(self):
        """Force cleanup of all execution resources"""
        try:
            with self.execution_lock:
                print("🧹 Forzando limpieza de recursos...")
                
                # Marcar para detener
                self.stop_execution_flag = True
                
                # Terminar proceso si existe
                if self.current_process:
                    try:
                        self.current_process.terminate()
                        self.current_process.wait(timeout=2)
                    except:
                        try:
                            self.current_process.kill()
                        except:
                            pass
                
                # Resetear estado
                self.class_execution_active = False
                self.current_process = None
                self.execution_thread = None
                self.current_class_info = None
                
                # Actualizar progreso
                if self.progress_manager:
                    self.progress_manager.stop_class()
                
                print("✅ Limpieza completada")
                
        except Exception as e:
            print(f"❌ Error en limpieza: {e}")
    
    def wait_for_completion(self, timeout: float = None) -> bool:
        """Wait for current class execution to complete"""
        try:
            if not self.execution_thread:
                return True
            
            self.execution_thread.join(timeout=timeout)
            return not self.execution_thread.is_alive()
            
        except Exception as e:
            print(f"❌ Error esperando completación: {e}")
            return False
    
    def is_class_running(self) -> bool:
        """Check if a class is currently running"""
        with self.execution_lock:
            return self.class_execution_active
    
    def get_current_class_info(self) -> Optional[Dict]:
        """Get information about the currently running class"""
        with self.execution_lock:
            return self.current_class_info.copy() if self.current_class_info else None
    
    def get_execution_status(self) -> Dict:
        """Get detailed execution status"""
        with self.execution_lock:
            status = {
                "is_running": self.class_execution_active,
                "current_class": self.current_class_info,
                "process_active": self.current_process is not None,
                "thread_active": self.execution_thread is not None and self.execution_thread.is_alive(),
                "stop_requested": self.stop_execution_flag
            }
            
            if self.current_process:
                status["process_id"] = self.current_process.pid
                status["process_returncode"] = self.current_process.returncode
            
            return status
    
    def update_class_progress(self, phase: str, sub_phase: str = "", details: str = ""):
        """Actualizar progreso de la clase actual"""
        if not self.progress_manager or not self.class_execution_active:
            return
        
        try:
            # Mapear fases de string a ClassPhase
            phase_mapping = {
                "diagnostic_test": ClassPhase.DIAGNOSTIC_TEST,
                "class_intro": ClassPhase.CLASS_INTRO,
                "theory_presentation": ClassPhase.THEORY_PRESENTATION,
                "practical_demo": ClassPhase.PRACTICAL_DEMO,
                "interactive_session": ClassPhase.INTERACTIVE_SESSION,
                "final_exam": ClassPhase.FINAL_EXAM,
                "completed": ClassPhase.COMPLETED,
                "paused": ClassPhase.PAUSED,
                "error": ClassPhase.ERROR
            }
            
            class_phase = phase_mapping.get(phase, ClassPhase.CLASS_INTRO)
            self.progress_manager.set_phase(class_phase, sub_phase, details)
            
        except Exception as e:
            print(f"Error actualizando progreso: {e}")
    
    def get_class_progress(self) -> Dict:
        """Obtener información del progreso actual de la clase"""
        if not self.progress_manager:
            return {"error": "Progress manager no disponible"}
        
        return self.progress_manager.get_progress_summary()
    
    def delete_class(self, class_name: str) -> bool:
        """
        Eliminar una clase y su carpeta
        
        Args:
            class_name: Nombre del archivo de la clase
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            class_info = self.get_class_by_name(class_name)
            if not class_info:
                print(f"❌ Clase no encontrada: {class_name}")
                return False
            
            class_folder = class_info['folder_path']
            
            # Verificar que la clase no esté ejecutándose
            if self.class_execution_active and self.current_class_info:
                if self.current_class_info['name'] == class_name:
                    print(f"❌ No se puede eliminar la clase mientras está ejecutándose: {class_name}")
                    return False
            
            # Eliminar carpeta completa
            import shutil
            shutil.rmtree(class_folder)
            
            print(f"✅ Clase eliminada: {class_folder}")
            
            # Actualizar metadata
            self.scan_classes()
            
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando clase: {e}")
            return False
    
    def _check_if_modular_class(self, file_path: str) -> bool:
        """
        Verificar si una clase usa la estructura modular
        
        Args:
            file_path: Ruta al archivo de la clase
            
        Returns:
            bool: True si la clase usa estructura modular
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar si importa de modules/
            modular_indicators = [
                'from modules.config import',
                'from modules.speech import',
                'from modules.camera import',
                'from modules.qr import',
                'from modules.slides import',
                'from modules.questions import',
                'from modules.esp32 import',
                'from modules.utils import'
            ]
            
            for indicator in modular_indicators:
                if indicator in content:
                    return True
                    
            return False
            
        except Exception as e:
            print(f"⚠️ Error verificando estructura modular: {e}")
            return False

# Singleton instance
_class_manager_instance = None

def get_class_manager() -> ClassManager:
    """Get the singleton class manager instance"""
    global _class_manager_instance
    if _class_manager_instance is None:
        _class_manager_instance = ClassManager()
    return _class_manager_instance

if __name__ == "__main__":
    # Test del gestor
    manager = ClassManager()
    classes = manager.scan_classes()
    print(f"Clases encontradas: {len(classes)}")
    for cls in classes:
        print(f"  - {cls['title']} ({cls['name']})")

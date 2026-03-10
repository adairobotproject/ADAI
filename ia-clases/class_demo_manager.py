#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Demo Manager - Gestión de secuencias de demo para clases
============================================================

Esta herramienta permite gestionar fácilmente las secuencias de demo
asociadas a cada clase del sistema ADAI.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Any

# Agregar el directorio actual al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from class_manager import get_class_manager
    CLASS_MANAGER_AVAILABLE = True
except ImportError:
    CLASS_MANAGER_AVAILABLE = False
    print("⚠️ Class Manager no disponible")

try:
    from sequence_esp32_logger import create_esp32_logger
    from sequence_executor_with_logging import execute_sequence_with_logging
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    print("⚠️ ESP32 Logger no disponible")

class ClassDemoManager:
    """Gestor de secuencias de demo para clases"""
    
    def __init__(self):
        """Inicializar el gestor de demo"""
        if not CLASS_MANAGER_AVAILABLE:
            raise ImportError("Class Manager no disponible")
        
        self.class_manager = get_class_manager()
        self.sequences_dir = "sequences"
        
        print("🎬 Class Demo Manager inicializado")
    
    def list_available_sequences(self) -> List[Dict]:
        """
        Listar todas las secuencias disponibles en el directorio de secuencias
        
        Returns:
            Lista de secuencias disponibles
        """
        sequences = []
        
        try:
            if not os.path.exists(self.sequences_dir):
                print(f"⚠️ Directorio de secuencias no encontrado: {self.sequences_dir}")
                return sequences
            
            for file in os.listdir(self.sequences_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.sequences_dir, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            sequence_data = json.load(f)
                        
                        sequence_info = {
                            'name': sequence_data.get('name', file),
                            'file': file,
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                            'description': sequence_data.get('description', 'Sin descripción'),
                            'steps': len(sequence_data.get('steps', []))
                        }
                        
                        sequences.append(sequence_info)
                        
                    except Exception as e:
                        print(f"⚠️ Error leyendo secuencia {file}: {e}")
            
            print(f"📋 Encontradas {len(sequences)} secuencias disponibles")
            return sequences
            
        except Exception as e:
            print(f"❌ Error listando secuencias: {e}")
            return []
    
    def list_classes_with_demo(self) -> List[Dict]:
        """
        Listar clases que tienen secuencias de demo
        
        Returns:
            Lista de clases con demo
        """
        classes_with_demo = []
        
        try:
            classes = self.class_manager.get_available_classes()
            
            for class_info in classes:
                demo_sequence = self.class_manager.get_class_demo_sequence(class_info['name'])
                
                if demo_sequence:
                    class_with_demo = {
                        'class_name': class_info['name'],
                        'class_title': class_info.get('title', 'Sin título'),
                        'demo_sequence': demo_sequence
                    }
                    classes_with_demo.append(class_with_demo)
            
            print(f"🎬 Encontradas {len(classes_with_demo)} clases con demo")
            return classes_with_demo
            
        except Exception as e:
            print(f"❌ Error listando clases con demo: {e}")
            return []
    
    def assign_sequence_to_class(self, class_name: str, sequence_path: str, sequence_name: str = None) -> bool:
        """
        Asignar una secuencia a la carpeta de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            sequence_path: Ruta de la secuencia
            sequence_name: Nombre para la secuencia (opcional)
            
        Returns:
            bool: True si se asignó correctamente
        """
        try:
            print(f"🎬 Asignando secuencia a clase: {class_name}")
            
            success = self.class_manager.copy_sequence_to_class_demo(
                class_name, sequence_path, sequence_name
            )
            
            if success:
                print(f"✅ Secuencia asignada exitosamente a {class_name}")
            else:
                print(f"❌ Error asignando secuencia a {class_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error asignando secuencia: {e}")
            return False
    
    def create_demo_sequence_for_class(self, class_name: str, sequence_name: str, steps: List[Dict]) -> bool:
        """
        Crear una secuencia de demo personalizada para una clase
        
        Args:
            class_name: Nombre de la clase
            sequence_name: Nombre de la secuencia
            steps: Lista de pasos de la secuencia
            
        Returns:
            bool: True si se creó correctamente
        """
        try:
            print(f"🎬 Creando secuencia de demo para: {class_name}")
            
            sequence_data = {
                'name': sequence_name,
                'description': f"Secuencia de demo para {class_name}",
                'created_at': datetime.now().isoformat(),
                'class_name': class_name,
                'steps': steps
            }
            
            success = self.class_manager.set_class_demo_sequence(
                class_name, sequence_data, sequence_name
            )
            
            if success:
                print(f"✅ Secuencia de demo creada exitosamente para {class_name}")
            else:
                print(f"❌ Error creando secuencia de demo para {class_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error creando secuencia de demo: {e}")
            return False
    
    def remove_demo_from_class(self, class_name: str) -> bool:
        """
        Eliminar la secuencia de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            
        Returns:
            bool: True si se eliminó correctamente
        """
        try:
            print(f"🎬 Eliminando demo de clase: {class_name}")
            
            success = self.class_manager.remove_class_demo_sequence(class_name)
            
            if success:
                print(f"✅ Demo eliminado exitosamente de {class_name}")
            else:
                print(f"❌ Error eliminando demo de {class_name}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error eliminando demo: {e}")
            return False
    
    def get_class_demo_info(self, class_name: str) -> Optional[Dict]:
        """
        Obtener información de la secuencia de demo de una clase
        
        Args:
            class_name: Nombre de la clase
            
        Returns:
            Dict con información de la demo o None si no existe
        """
        try:
            demo_sequence = self.class_manager.get_class_demo_sequence(class_name)
            
            if demo_sequence:
                print(f"🎬 Demo encontrado para {class_name}: {demo_sequence['name']}")
                return demo_sequence
            else:
                print(f"⚠️ No hay demo para la clase: {class_name}")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo info de demo: {e}")
            return None
    
    def create_simple_demo_sequence(self, class_name: str, title: str) -> bool:
        """
        Crear una secuencia de demo simple para una clase
        
        Args:
            class_name: Nombre de la clase
            title: Título de la clase
            
        Returns:
            bool: True si se creó correctamente
        """
        try:
            print(f"🎬 Creando demo simple para: {class_name}")
            
            # Secuencia de demo básica
            demo_steps = [
                {
                    "step": 1,
                    "action": "saludo",
                    "description": f"Saludo inicial para la clase de {title}",
                    "duration": 3,
                    "parameters": {
                        "message": f"¡Hola! Bienvenidos a la clase de {title}"
                    }
                },
                {
                    "step": 2,
                    "action": "presentacion",
                    "description": "Presentación del tema",
                    "duration": 5,
                    "parameters": {
                        "message": f"En esta clase aprenderemos sobre {title}"
                    }
                },
                {
                    "step": 3,
                    "action": "despedida",
                    "description": "Despedida final",
                    "duration": 3,
                    "parameters": {
                        "message": "¡Gracias por su atención!"
                    }
                }
            ]
            
            success = self.create_demo_sequence_for_class(
                class_name, f"Demo_{class_name}", demo_steps
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Error creando demo simple: {e}")
            return False
    
    def batch_assign_sequences(self, assignments: List[Dict]) -> Dict[str, bool]:
        """
        Asignar secuencias a múltiples clases en lote
        
        Args:
            assignments: Lista de asignaciones [{"class_name": "...", "sequence_path": "..."}]
            
        Returns:
            Dict con resultados de cada asignación
        """
        results = {}
        
        print(f"🎬 Iniciando asignación en lote de {len(assignments)} secuencias")
        
        for assignment in assignments:
            class_name = assignment.get('class_name')
            sequence_path = assignment.get('sequence_path')
            sequence_name = assignment.get('sequence_name')
            
            if not class_name or not sequence_path:
                print(f"⚠️ Asignación incompleta: {assignment}")
                results[class_name] = False
                continue
            
            success = self.assign_sequence_to_class(class_name, sequence_path, sequence_name)
            results[class_name] = success
        
        print(f"✅ Asignación en lote completada")
        return results
    
    def execute_class_demo_sequence(self, class_name: str, robot_controller: Optional[Any] = None, 
                                   enable_logging: bool = True) -> Optional[Any]:
        """
        Ejecutar la secuencia de demo de una clase con logging de señales ESP32
        
        Args:
            class_name: Nombre de la clase
            robot_controller: Controlador del robot (opcional)
            enable_logging: Habilitar logging de señales ESP32
            
        Returns:
            Ejecutor de secuencia o None si no se encuentra la demo
        """
        try:
            print(f"🎬 Ejecutando demo de clase: {class_name}")
            
            # Obtener la secuencia de demo
            demo_sequence = self.class_manager.get_class_demo_sequence(class_name)
            
            if not demo_sequence:
                print(f"❌ No se encontró secuencia de demo para: {class_name}")
                return None
            
            sequence_data = demo_sequence.get('data', {})
            sequence_name = demo_sequence.get('name', class_name)
            
            print(f"✅ Demo encontrado: {sequence_name}")
            print(f"   📊 Pasos: {len(sequence_data.get('steps', []))}")
            print(f"   📝 Descripción: {sequence_data.get('description', 'Sin descripción')}")
            
            # Ejecutar la secuencia con logging
            if LOGGER_AVAILABLE and enable_logging:
                executor = execute_sequence_with_logging(sequence_data, robot_controller, enable_logging)
                return executor
            else:
                print("⚠️ Logging no disponible, ejecutando sin logging")
                # Aquí podrías implementar ejecución sin logging
                return None
                
        except Exception as e:
            print(f"❌ Error ejecutando demo: {e}")
            return None
    
    def preview_demo_signals(self, class_name: str) -> bool:
        """
        Previsualizar las señales ESP32 que se enviarían durante la demo
        
        Args:
            class_name: Nombre de la clase
            
        Returns:
            bool: True si se pudo previsualizar correctamente
        """
        try:
            print(f"🎬 Previsualizando señales ESP32 para demo de: {class_name}")
            
            # Obtener la secuencia de demo
            demo_sequence = self.class_manager.get_class_demo_sequence(class_name)
            
            if not demo_sequence:
                print(f"❌ No se encontró secuencia de demo para: {class_name}")
                return False
            
            sequence_data = demo_sequence.get('data', {})
            sequence_name = demo_sequence.get('name', class_name)
            
            # Crear logger solo para previsualización
            if LOGGER_AVAILABLE:
                logger = create_esp32_logger(f"Preview_{sequence_name}", enable_console=True, enable_file=False)
                
                # Log de inicio
                logger.log_sequence_start(sequence_data)
                
                # Simular señales basadas en los pasos
                steps = sequence_data.get('steps', [])
                for i, step in enumerate(steps):
                    step_type = step.get('type', 'unknown')
                    step_name = step.get('name', f'Paso {i+1}')
                    parameters = step.get('parameters', {})
                    
                    step_info = {
                        'name': step_name,
                        'description': step.get('description', ''),
                        'type': step_type,
                        'parameters': parameters
                    }
                    
                    # Simular señal según el tipo
                    if step_type == 'movement':
                        coordinates = {
                            'x': parameters.get('x', 0),
                            'y': parameters.get('y', 0),
                            'z': parameters.get('z', 0)
                        }
                        logger.log_movement_signal(
                            parameters.get('movement_type', 'unknown'),
                            coordinates,
                            parameters.get('duration', 1.0),
                            step_info
                        )
                    elif step_type == 'gesture':
                        logger.log_gesture_signal(
                            parameters.get('gesture_type', 'unknown'),
                            parameters,
                            parameters.get('duration', 2.0),
                            step_info
                        )
                    elif step_type == 'speech':
                        logger.log_speech_signal(
                            parameters.get('message', ''),
                            parameters.get('voice_params', {}),
                            step_info
                        )
                    else:
                        logger.log_signal('unknown', parameters, step_info)
                    
                    # Pausa entre señales para mejor visualización
                    time.sleep(0.5)
                
                # Log de fin
                logger.log_sequence_end()
                logger.close()
                
                print(f"✅ Previsualización completada para: {sequence_name}")
                return True
            else:
                print("⚠️ Logger no disponible para previsualización")
                return False
                
        except Exception as e:
            print(f"❌ Error en previsualización: {e}")
            return False

# Función de conveniencia para crear el gestor
def get_demo_manager() -> ClassDemoManager:
    """Obtener instancia del gestor de demo"""
    return ClassDemoManager()

# Ejemplo de uso
def example_usage():
    """Ejemplo de uso del Class Demo Manager"""
    
    try:
        # Crear gestor
        demo_manager = get_demo_manager()
        
        # Listar secuencias disponibles
        print("\n📋 Secuencias disponibles:")
        sequences = demo_manager.list_available_sequences()
        for seq in sequences[:3]:  # Mostrar solo las primeras 3
            print(f"  - {seq['name']} ({seq['file']})")
        
        # Listar clases con demo
        print("\n🎬 Clases con demo:")
        classes_with_demo = demo_manager.list_classes_with_demo()
        for cls in classes_with_demo:
            print(f"  - {cls['class_title']} ({cls['demo_sequence']['name']})")
        
        # Crear demo simple para una clase
        print("\n🎬 Creando demo simple...")
        success = demo_manager.create_simple_demo_sequence("test_nueva_clase", "Test Nueva Clase")
        print(f"Demo creado: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ Error en ejemplo: {e}")

if __name__ == "__main__":
    example_usage()

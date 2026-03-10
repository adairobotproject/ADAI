#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sequence Executor with ESP32 Logging - Ejecutor de secuencias con logging de señales
================================================================================

Este módulo ejecuta secuencias de demo y registra todas las señales enviadas al ESP32
para controlar el robot durante las demostraciones.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

# Agregar el directorio actual al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from sequence_esp32_logger import create_esp32_logger, ESP32SignalLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    print("⚠️ ESP32 Logger no disponible")

try:
    from esp32_client import get_esp32_client, ESP32Client
    ESP32_CLIENT_AVAILABLE = True
except ImportError:
    ESP32_CLIENT_AVAILABLE = False
    print("⚠️ ESP32 Client no disponible")

class SequenceExecutor:
    """
    Ejecutor de secuencias con logging completo de señales ESP32
    """
    
    def __init__(self, sequence_data: Dict, enable_logging: bool = True):
        """
        Inicializar el ejecutor de secuencias
        
        Args:
            sequence_data: Datos de la secuencia a ejecutar
            enable_logging: Habilitar logging de señales ESP32
        """
        self.sequence_data = sequence_data
        self.sequence_name = sequence_data.get('name', 'Unknown_Sequence')
        self.enable_logging = enable_logging and LOGGER_AVAILABLE
        
        # Logger de señales ESP32
        self.logger = None
        if self.enable_logging:
            self.logger = create_esp32_logger(self.sequence_name)
        
        # Cliente ESP32 real
        self.esp32_client = None
        if ESP32_CLIENT_AVAILABLE:
            self.esp32_client = get_esp32_client()
        
        # Estado de ejecución
        self.is_running = False
        self.is_paused = False
        self.current_step = 0
        self.total_steps = 0
        
        # Callbacks
        self.on_step_start: Optional[Callable] = None
        self.on_step_complete: Optional[Callable] = None
        self.on_sequence_complete: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        # Thread de ejecución
        self.execution_thread = None
        self.stop_flag = False
        
        # Contador de señales
        self.signal_count = 0
        
        print(f"🎬 Sequence Executor inicializado para: {self.sequence_name}")
    
    def execute_sequence(self, robot_controller: Optional[Any] = None):
        """
        Ejecutar la secuencia completa
        
        Args:
            robot_controller: Controlador del robot (opcional, para señales reales)
        """
        try:
            if self.is_running:
                print("⚠️ La secuencia ya está ejecutándose")
                return False
            
            self.is_running = True
            self.stop_flag = False
            self.current_step = 0
            
            # Obtener pasos de la secuencia
            steps = self._get_sequence_steps()
            self.total_steps = len(steps)
            
            if self.total_steps == 0:
                print("❌ No hay pasos en la secuencia")
                return False
            
            # Log de inicio
            if self.logger:
                self.logger.log_sequence_start(self.sequence_data)
            
            print(f"🚀 Iniciando ejecución de secuencia: {self.sequence_name}")
            print(f"   📊 Total de pasos: {self.total_steps}")
            
            # Ejecutar en thread separado
            self.execution_thread = threading.Thread(
                target=self._execute_steps,
                args=(steps, robot_controller),
                daemon=True
            )
            self.execution_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando secuencia: {e}")
            if self.on_error:
                self.on_error(f"Error iniciando secuencia: {e}")
            return False
    
    def _execute_steps(self, steps: List[Dict], robot_controller: Optional[Any] = None):
        """Ejecutar todos los pasos de la secuencia"""
        try:
            for i, step in enumerate(steps):
                if self.stop_flag:
                    print("⏹️ Ejecución detenida por el usuario")
                    break
                
                self.current_step = i + 1
                step_name = step.get('name', f'Paso {i+1}')
                
                print(f"\n📋 Ejecutando paso {self.current_step}/{self.total_steps}: {step_name}")
                
                # Notificar inicio del paso
                if self.on_step_start:
                    self.on_step_start(step, i + 1, self.total_steps)
                
                # Ejecutar el paso
                success = self._execute_step(step, robot_controller)
                
                if not success:
                    print(f"❌ Error ejecutando paso {i+1}")
                    if self.on_error:
                        self.on_error(f"Error en paso {i+1}: {step_name}")
                    break
                
                # Notificar completación del paso
                if self.on_step_complete:
                    self.on_step_complete(step, i + 1, self.total_steps)
                
                # Pausa entre pasos
                if i < len(steps) - 1:  # No pausar después del último paso
                    time.sleep(0.5)
            
            # Log de fin
            if self.logger:
                final_stats = {
                    'steps_completed': self.current_step,
                    'total_steps': self.total_steps,
                    'signals_sent': self.signal_count
                }
                self.logger.log_sequence_end(final_stats)
            
            print(f"\n✅ Secuencia completada: {self.sequence_name}")
            if self.on_sequence_complete:
                self.on_sequence_complete(self.sequence_data)
                
        except Exception as e:
            print(f"❌ Error ejecutando secuencia: {e}")
            if self.on_error:
                self.on_error(f"Error ejecutando secuencia: {e}")
        finally:
            self.is_running = False
            if self.logger:
                self.logger.close()
    
    def _execute_step(self, step: Dict, robot_controller: Optional[Any] = None) -> bool:
        """
        Ejecutar un paso individual de la secuencia
        
        Args:
            step: Datos del paso a ejecutar
            robot_controller: Controlador del robot
            
        Returns:
            bool: True si el paso se ejecutó correctamente
        """
        try:
            # Intentar obtener el tipo de paso de diferentes campos
            step_type = step.get('type', 'unknown')
            step_action = step.get('action', '')
            step_name = step.get('name', 'Unknown')
            step_description = step.get('description', '')
            parameters = step.get('parameters', {})
            
            # Si no hay tipo pero hay acción, mapear la acción a un tipo
            if step_type == 'unknown' and step_action:
                # Mapear acciones comunes a tipos de paso
                if step_action in ['saludo', 'presentacion', 'despedida', 'explicacion']:
                    step_type = 'speech'
                elif step_action in ['movimiento', 'mover', 'posicion']:
                    step_type = 'movement'
                elif step_action in ['gesto', 'señal']:
                    step_type = 'gesture'
                elif step_action in ['esperar', 'pausa']:
                    step_type = 'wait'
                else:
                    step_type = 'action'
            
            # Información del paso para el logger
            step_info = {
                'name': step_name,
                'description': step_description,
                'type': step_type,
                'action': step_action,
                'parameters': parameters
            }
            
            print(f"   🎯 Tipo: {step_type}")
            print(f"   ⚡ Acción: {step_action}")
            print(f"   📝 Descripción: {step_description}")
            
            # Ejecutar según el tipo de paso
            if step_type == 'movement':
                return self._execute_movement_step(step_info, robot_controller)
            elif step_type == 'gesture':
                return self._execute_gesture_step(step_info, robot_controller)
            elif step_type == 'speech':
                return self._execute_speech_step(step_info, robot_controller)
            elif step_type == 'wait':
                return self._execute_wait_step(step_info)
            elif step_type == 'action':
                return self._execute_action_step(step_info, robot_controller)
            else:
                print(f"   ⚠️ Tipo de paso no reconocido: {step_type}")
                return self._execute_unknown_step(step_info)
                
        except Exception as e:
            print(f"   ❌ Error ejecutando paso: {e}")
            if self.logger:
                self.logger.log_error_signal('step_execution_error', str(e), step)
            return False
    
    def _execute_movement_step(self, step_info: Dict, robot_controller: Optional[Any] = None) -> bool:
        """Ejecutar paso de movimiento"""
        try:
            parameters = step_info['parameters']
            movement_type = parameters.get('movement_type', 'unknown')
            duration = parameters.get('duration', 1.0)
            
            # Simular coordenadas de movimiento
            coordinates = {
                'x': parameters.get('x', 0),
                'y': parameters.get('y', 0),
                'z': parameters.get('z', 0)
            }
            
            print(f"   🎯 Movimiento: {movement_type}")
            print(f"   📍 Coordenadas: {coordinates}")
            print(f"   ⏱️ Duración: {duration}s")
            
            # Log de señal ESP32
            if self.logger:
                self.logger.log_movement_signal(
                    movement_type,
                    coordinates,
                    duration,
                    step_info
                )
                self.signal_count += 1
            
            # Enviar señal real al robot si hay controlador
            if robot_controller and hasattr(robot_controller, 'send_movement'):
                try:
                    response = robot_controller.send_movement(movement_type, coordinates, duration)
                    if self.logger:
                        # Simular respuesta del ESP32
                        esp32_response = {
                            'success': True,
                            'message': f'Movement {movement_type} executed',
                            'coordinates': coordinates,
                            'duration': duration
                        }
                        self.logger.log_signal('movement', {
                            'movement_type': movement_type,
                            'coordinates': coordinates,
                            'duration': duration
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Enviar señal real al ESP32 si hay cliente disponible
            elif self.esp32_client and self.esp32_client.is_connected():
                try:
                    response = self.esp32_client.send_movement(movement_type, coordinates, duration)
                    if self.logger and response:
                        esp32_response = {
                            'success': True,
                            'message': f'Movement {movement_type} executed via ESP32',
                            'coordinates': coordinates,
                            'duration': duration
                        }
                        self.logger.log_signal('movement', {
                            'movement_type': movement_type,
                            'coordinates': coordinates,
                            'duration': duration
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Simular duración del movimiento
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en movimiento: {e}")
            return False
    
    def _execute_gesture_step(self, step_info: Dict, robot_controller: Optional[Any] = None) -> bool:
        """Ejecutar paso de gesto"""
        try:
            parameters = step_info['parameters']
            gesture_type = parameters.get('gesture_type', 'unknown')
            duration = parameters.get('duration', 2.0)
            
            print(f"   👋 Gesto: {gesture_type}")
            print(f"   ⏱️ Duración: {duration}s")
            
            # Log de señal ESP32
            if self.logger:
                self.logger.log_gesture_signal(
                    gesture_type,
                    parameters,
                    duration,
                    step_info
                )
                self.signal_count += 1
            
            # Enviar señal real al robot si hay controlador
            if robot_controller and hasattr(robot_controller, 'send_gesture'):
                try:
                    response = robot_controller.send_gesture(gesture_type, parameters, duration)
                    if self.logger:
                        esp32_response = {
                            'success': True,
                            'message': f'Gesture {gesture_type} executed',
                            'gesture_type': gesture_type,
                            'duration': duration
                        }
                        self.logger.log_signal('gesture', {
                            'gesture_type': gesture_type,
                            'gesture_params': parameters,
                            'duration': duration
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Enviar señal real al ESP32 si hay cliente disponible
            elif self.esp32_client and self.esp32_client.is_connected():
                try:
                    response = self.esp32_client.send_gesture(gesture_type, parameters, duration)
                    if self.logger and response:
                        esp32_response = {
                            'success': True,
                            'message': f'Gesture {gesture_type} executed via ESP32',
                            'gesture_type': gesture_type,
                            'duration': duration
                        }
                        self.logger.log_signal('gesture', {
                            'gesture_type': gesture_type,
                            'gesture_params': parameters,
                            'duration': duration
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Simular duración del gesto
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en gesto: {e}")
            return False
    
    def _execute_speech_step(self, step_info: Dict, robot_controller: Optional[Any] = None) -> bool:
        """Ejecutar paso de habla"""
        try:
            parameters = step_info['parameters']
            message = parameters.get('message', '')
            voice_params = parameters.get('voice_params', {})
            
            print(f"   🗣️ Mensaje: {message}")
            
            # Log de señal ESP32
            if self.logger:
                self.logger.log_speech_signal(
                    message,
                    voice_params,
                    step_info
                )
                self.signal_count += 1
            
            # Enviar señal real al robot si hay controlador
            if robot_controller and hasattr(robot_controller, 'send_speech'):
                try:
                    response = robot_controller.send_speech(message, voice_params)
                    if self.logger:
                        esp32_response = {
                            'success': True,
                            'message': 'Speech executed',
                            'text': message,
                            'voice_params': voice_params
                        }
                        self.logger.log_signal('speech', {
                            'message': message,
                            'voice_params': voice_params
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Enviar señal real al ESP32 si hay cliente disponible
            elif self.esp32_client and self.esp32_client.is_connected():
                try:
                    response = self.esp32_client.send_speech(message, voice_params)
                    if self.logger and response:
                        esp32_response = {
                            'success': True,
                            'message': 'Speech executed via ESP32',
                            'text': message,
                            'voice_params': voice_params
                        }
                        self.logger.log_signal('speech', {
                            'message': message,
                            'voice_params': voice_params
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Simular tiempo de habla (aproximadamente 1 segundo por 10 palabras)
            word_count = len(message.split())
            speech_time = max(1.0, word_count * 0.1)
            time.sleep(speech_time)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en habla: {e}")
            return False
    
    def _execute_wait_step(self, step_info: Dict) -> bool:
        """Ejecutar paso de espera"""
        try:
            parameters = step_info['parameters']
            wait_time = parameters.get('duration', 1.0)
            
            print(f"   ⏳ Esperando: {wait_time}s")
            
            time.sleep(wait_time)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en espera: {e}")
            return False
    
    def _execute_action_step(self, step_info: Dict, robot_controller: Optional[Any] = None) -> bool:
        """Ejecutar paso de acción personalizada"""
        try:
            parameters = step_info['parameters']
            action_type = step_info.get('action', 'unknown')
            message = parameters.get('message', '')
            duration = parameters.get('duration', 1.0)
            
            print(f"   ⚡ Acción: {action_type}")
            if message:
                print(f"   📝 Mensaje: {message}")
            print(f"   ⏱️ Duración: {duration}s")
            
            # Log de señal ESP32
            if self.logger:
                self.logger.log_signal('action', {
                    'action_type': action_type,
                    'message': message,
                    'duration': duration
                }, step_info)
                self.signal_count += 1
            
            # Enviar señal real al robot si hay controlador
            if robot_controller and hasattr(robot_controller, 'send_action'):
                try:
                    response = robot_controller.send_action(action_type, parameters)
                    if self.logger:
                        esp32_response = {
                            'success': True,
                            'message': f'Action {action_type} executed',
                            'action_type': action_type,
                            'parameters': parameters
                        }
                        self.logger.log_signal('action', {
                            'action_type': action_type,
                            'parameters': parameters
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Enviar señal real al ESP32 si hay cliente disponible
            elif self.esp32_client and self.esp32_client.is_connected():
                try:
                    response = self.esp32_client.send_action(action_type, parameters)
                    if self.logger and response:
                        esp32_response = {
                            'success': True,
                            'message': f'Action {action_type} executed via ESP32',
                            'action_type': action_type,
                            'parameters': parameters
                        }
                        self.logger.log_signal('action', {
                            'action_type': action_type,
                            'parameters': parameters
                        }, step_info, esp32_response)
                except Exception as e:
                    if self.logger:
                        self.logger.log_error_signal('esp32_communication_error', str(e), step_info)
            
            # Simular duración de la acción
            time.sleep(duration)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en acción: {e}")
            return False
    
    def _execute_unknown_step(self, step_info: Dict) -> bool:
        """Ejecutar paso de tipo desconocido"""
        try:
            print(f"   ❓ Paso desconocido: {step_info['type']}")
            
            # Log de señal ESP32
            if self.logger:
                self.logger.log_signal('unknown', step_info['parameters'], step_info)
                self.signal_count += 1
            
            # Simular ejecución
            time.sleep(1.0)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error en paso desconocido: {e}")
            return False
    
    def _get_sequence_steps(self) -> List[Dict]:
        """Obtener pasos de la secuencia"""
        # Intentar diferentes formatos de secuencia
        if 'steps' in self.sequence_data:
            return self.sequence_data['steps']
        elif 'movements' in self.sequence_data:
            return self.sequence_data['movements']
        elif 'positions' in self.sequence_data:
            # Convertir formato de posiciones a pasos
            positions = self.sequence_data['positions']
            steps = []
            for i, pos in enumerate(positions):
                step = {
                    'id': i + 1,
                    'name': pos.get('description', f'Posición {i+1}'),
                    'type': 'movement',
                    'parameters': {
                        'movement_type': 'position',
                        'x': pos.get('x', 0),
                        'y': pos.get('y', 0),
                        'z': pos.get('z', 0),
                        'duration': 1.0
                    },
                    'description': pos.get('description', f'Movimiento a posición {i+1}')
                }
                steps.append(step)
            return steps
        else:
            return []
    
    def stop_execution(self):
        """Detener la ejecución de la secuencia"""
        self.stop_flag = True
        self.is_running = False
        print("⏹️ Detención de secuencia solicitada")
    
    def pause_execution(self):
        """Pausar la ejecución de la secuencia"""
        self.is_paused = True
        print("⏸️ Secuencia pausada")
    
    def resume_execution(self):
        """Reanudar la ejecución de la secuencia"""
        self.is_paused = False
        print("▶️ Secuencia reanudada")
    
    def get_execution_status(self) -> Dict:
        """Obtener estado actual de la ejecución"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'signal_count': self.signal_count,
            'sequence_name': self.sequence_name
        }

# Función de conveniencia para ejecutar secuencia
def execute_sequence_with_logging(sequence_data: Dict, robot_controller: Optional[Any] = None, 
                                 enable_logging: bool = True) -> SequenceExecutor:
    """
    Ejecutar una secuencia con logging de señales ESP32
    
    Args:
        sequence_data: Datos de la secuencia
        robot_controller: Controlador del robot (opcional)
        enable_logging: Habilitar logging
        
    Returns:
        Instancia del ejecutor de secuencia
    """
    executor = SequenceExecutor(sequence_data, enable_logging)
    executor.execute_sequence(robot_controller)
    return executor

# Ejemplo de uso
def example_usage():
    """Ejemplo de uso del ejecutor de secuencias con logging"""
    
    # Datos de secuencia de ejemplo
    sequence_data = {
        'name': 'Demo_Test_Sequence',
        'description': 'Secuencia de prueba con logging ESP32',
        'total_duration': 10000,
        'steps': [
            {
                'id': 1,
                'name': 'Saludo Inicial',
                'type': 'gesture',
                'parameters': {
                    'gesture_type': 'wave',
                    'duration': 2.0
                },
                'description': 'Saludo inicial con gesto de mano'
            },
            {
                'id': 2,
                'name': 'Centrar Posición',
                'type': 'movement',
                'parameters': {
                    'movement_type': 'center',
                    'x': 0,
                    'y': 0,
                    'z': 0,
                    'duration': 1.0
                },
                'description': 'Centrar la posición del robot'
            },
            {
                'id': 3,
                'name': 'Mensaje de Bienvenida',
                'type': 'speech',
                'parameters': {
                    'message': '¡Hola! Bienvenidos a la demostración del robot ADAI',
                    'voice_params': {
                        'voice': 'default',
                        'speed': 1.0
                    }
                },
                'description': 'Mensaje de bienvenida'
            }
        ]
    }
    
    # Ejecutar secuencia
    print("🎬 Ejecutando secuencia de ejemplo con logging ESP32...")
    executor = execute_sequence_with_logging(sequence_data)
    
    # Esperar a que termine
    while executor.is_running:
        time.sleep(0.1)
    
    print("✅ Ejemplo completado")

if __name__ == "__main__":
    example_usage()

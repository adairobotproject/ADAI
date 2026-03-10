#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sequence ESP32 Logger - Sistema de logging de señales ESP32 para secuencias
=======================================================================

Este módulo proporciona funcionalidades para registrar y mostrar las señales
que se envían al ESP32 durante la ejecución de secuencias de demo.
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading

# Agregar el directorio actual al path para importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

class ESP32SignalLogger:
    """
    Logger especializado para señales ESP32 durante ejecución de secuencias
    """
    
    def __init__(self, sequence_name: str = "unknown", enable_console: bool = True, enable_file: bool = True):
        """
        Inicializar el logger de señales ESP32
        
        Args:
            sequence_name: Nombre de la secuencia que se está ejecutando
            enable_console: Habilitar logging en consola
            enable_file: Habilitar logging en archivo
        """
        self.sequence_name = sequence_name
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.start_time = time.time()
        self.signal_count = 0
        
        # Crear directorio de logs si no existe
        self.logs_dir = "logs/esp32_signals"
        if self.enable_file and not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)
        
        # Archivo de log
        self.log_file = None
        if self.enable_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"esp32_signals_{sequence_name}_{timestamp}.log"
            self.log_file_path = os.path.join(self.logs_dir, filename)
            self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
        
        # Estadísticas
        self.stats = {
            'total_signals': 0,
            'movement_signals': 0,
            'gesture_signals': 0,
            'speech_signals': 0,
            'error_signals': 0,
            'total_duration': 0
        }
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        print(f"🎯 ESP32 Signal Logger iniciado para secuencia: {sequence_name}")
        if self.enable_file:
            print(f"📁 Log file: {self.log_file_path}")
    
    def log_signal(self, signal_type: str, parameters: Dict[str, Any], 
                   step_info: Optional[Dict] = None, response: Optional[Dict] = None):
        """
        Registrar una señal enviada al ESP32
        
        Args:
            signal_type: Tipo de señal (movement, gesture, speech, etc.)
            parameters: Parámetros de la señal
            step_info: Información del paso de la secuencia
            response: Respuesta del ESP32 (opcional)
        """
        with self.lock:
            self.signal_count += 1
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            
            # Crear entrada de log
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'elapsed_time': f"{elapsed_time:.3f}s",
                'signal_id': self.signal_count,
                'signal_type': signal_type,
                'parameters': parameters,
                'step_info': step_info or {},
                'response': response,
                'sequence_name': self.sequence_name
            }
            
            # Actualizar estadísticas
            self.stats['total_signals'] += 1
            if signal_type == 'movement':
                self.stats['movement_signals'] += 1
            elif signal_type == 'gesture':
                self.stats['gesture_signals'] += 1
            elif signal_type == 'speech':
                self.stats['speech_signals'] += 1
            elif signal_type == 'error':
                self.stats['error_signals'] += 1
            
            # Log en consola
            if self.enable_console:
                self._print_signal(log_entry)
            
            # Log en archivo
            if self.enable_file and self.log_file:
                self._write_signal_to_file(log_entry)
    
    def _print_signal(self, log_entry: Dict):
        """Imprimir señal en consola con formato colorido"""
        signal_id = log_entry['signal_id']
        signal_type = log_entry['signal_type']
        elapsed_time = log_entry['elapsed_time']
        parameters = log_entry['parameters']
        step_info = log_entry.get('step_info', {})
        
        # Colores para diferentes tipos de señal
        colors = {
            'movement': '\033[94m',  # Azul
            'gesture': '\033[92m',   # Verde
            'speech': '\033[93m',    # Amarillo
            'error': '\033[91m',     # Rojo
            'default': '\033[0m'     # Reset
        }
        
        color = colors.get(signal_type, colors['default'])
        reset = colors['default']
        
        # Imprimir encabezado de señal
        print(f"\n{color}🎯 SEÑAL ESP32 #{signal_id} [{signal_type.upper()}] - {elapsed_time}{reset}")
        
        # Información del paso si está disponible
        if step_info:
            step_name = step_info.get('name', 'Unknown')
            step_description = step_info.get('description', '')
            print(f"   📋 Paso: {step_name}")
            if step_description:
                print(f"   📝 Descripción: {step_description}")
        
        # Parámetros de la señal
        print(f"   ⚙️ Parámetros:")
        for key, value in parameters.items():
            if isinstance(value, dict):
                print(f"      {key}:")
                for sub_key, sub_value in value.items():
                    print(f"        {sub_key}: {sub_value}")
            else:
                print(f"      {key}: {value}")
        
        # Respuesta del ESP32 si está disponible
        if log_entry.get('response'):
            response = log_entry['response']
            if response.get('success'):
                print(f"   ✅ ESP32 Response: {response.get('message', 'Success')}")
            else:
                print(f"   ❌ ESP32 Error: {response.get('error', 'Unknown error')}")
    
    def _write_signal_to_file(self, log_entry: Dict):
        """Escribir señal en archivo de log"""
        try:
            json_line = json.dumps(log_entry, ensure_ascii=False, indent=2)
            self.log_file.write(json_line + "\n")
            self.log_file.flush()  # Asegurar que se escriba inmediatamente
        except Exception as e:
            print(f"❌ Error escribiendo al archivo de log: {e}")
    
    def log_movement_signal(self, movement_type: str, coordinates: Dict[str, float], 
                           duration: float = 1.0, step_info: Optional[Dict] = None):
        """
        Registrar señal de movimiento específica
        
        Args:
            movement_type: Tipo de movimiento (head, arm, torso, etc.)
            coordinates: Coordenadas del movimiento
            duration: Duración del movimiento
            step_info: Información del paso
        """
        parameters = {
            'movement_type': movement_type,
            'coordinates': coordinates,
            'duration': duration,
            'timestamp': time.time()
        }
        
        self.log_signal('movement', parameters, step_info)
    
    def log_gesture_signal(self, gesture_type: str, gesture_params: Dict[str, Any], 
                          duration: float = 2.0, step_info: Optional[Dict] = None):
        """
        Registrar señal de gesto específica
        
        Args:
            gesture_type: Tipo de gesto (wave, point, etc.)
            gesture_params: Parámetros del gesto
            duration: Duración del gesto
            step_info: Información del paso
        """
        parameters = {
            'gesture_type': gesture_type,
            'gesture_params': gesture_params,
            'duration': duration,
            'timestamp': time.time()
        }
        
        self.log_signal('gesture', parameters, step_info)
    
    def log_speech_signal(self, message: str, voice_params: Dict[str, Any] = None, 
                         step_info: Optional[Dict] = None):
        """
        Registrar señal de habla específica
        
        Args:
            message: Mensaje a pronunciar
            voice_params: Parámetros de voz
            step_info: Información del paso
        """
        parameters = {
            'message': message,
            'voice_params': voice_params or {},
            'timestamp': time.time()
        }
        
        self.log_signal('speech', parameters, step_info)
    
    def log_error_signal(self, error_type: str, error_message: str, 
                        original_signal: Optional[Dict] = None):
        """
        Registrar error en señal ESP32
        
        Args:
            error_type: Tipo de error
            error_message: Mensaje de error
            original_signal: Señal original que causó el error
        """
        parameters = {
            'error_type': error_type,
            'error_message': error_message,
            'original_signal': original_signal,
            'timestamp': time.time()
        }
        
        self.log_signal('error', parameters)
    
    def log_sequence_start(self, sequence_data: Dict):
        """Registrar inicio de secuencia"""
        print(f"\n🎬 INICIANDO SECUENCIA: {self.sequence_name}")
        print(f"   📊 Total de pasos: {len(sequence_data.get('steps', []))}")
        print(f"   ⏱️ Duración estimada: {sequence_data.get('total_duration', 'Unknown')}ms")
        print(f"   📝 Descripción: {sequence_data.get('description', 'No description')}")
        print("=" * 60)
        
        if self.enable_file and self.log_file:
            header = {
                'type': 'sequence_start',
                'timestamp': datetime.now().isoformat(),
                'sequence_name': self.sequence_name,
                'sequence_data': sequence_data
            }
            self.log_file.write(json.dumps(header, ensure_ascii=False, indent=2) + "\n")
    
    def log_sequence_end(self, final_stats: Optional[Dict] = None):
        """Registrar fin de secuencia"""
        total_time = time.time() - self.start_time
        self.stats['total_duration'] = total_time
        
        print(f"\n🎬 FINALIZANDO SECUENCIA: {self.sequence_name}")
        print(f"   ⏱️ Tiempo total: {total_time:.3f}s")
        print(f"   📊 Señales enviadas: {self.stats['total_signals']}")
        print(f"   🎯 Movimientos: {self.stats['movement_signals']}")
        print(f"   👋 Gestos: {self.stats['gesture_signals']}")
        print(f"   🗣️ Habla: {self.stats['speech_signals']}")
        print(f"   ❌ Errores: {self.stats['error_signals']}")
        print("=" * 60)
        
        if self.enable_file and self.log_file:
            footer = {
                'type': 'sequence_end',
                'timestamp': datetime.now().isoformat(),
                'sequence_name': self.sequence_name,
                'final_stats': self.stats,
                'additional_stats': final_stats or {}
            }
            self.log_file.write(json.dumps(footer, ensure_ascii=False, indent=2) + "\n")
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas actuales"""
        return self.stats.copy()
    
    def close(self):
        """Cerrar el logger y archivos"""
        if self.log_file:
            self.log_file.close()
            print(f"📁 Log file cerrado: {self.log_file_path}")

# Función de conveniencia para crear logger
def create_esp32_logger(sequence_name: str, enable_console: bool = True, enable_file: bool = True) -> ESP32SignalLogger:
    """
    Crear una instancia del logger de señales ESP32
    
    Args:
        sequence_name: Nombre de la secuencia
        enable_console: Habilitar logging en consola
        enable_file: Habilitar logging en archivo
        
    Returns:
        Instancia del logger
    """
    return ESP32SignalLogger(sequence_name, enable_console, enable_file)

# Ejemplo de uso
def example_usage():
    """Ejemplo de uso del ESP32 Signal Logger"""
    
    # Crear logger
    logger = create_esp32_logger("Demo_Test_Sequence")
    
    # Simular datos de secuencia
    sequence_data = {
        'name': 'Demo_Test_Sequence',
        'description': 'Secuencia de prueba para logging',
        'total_duration': 10000,
        'steps': [
            {'name': 'Saludo', 'description': 'Saludo inicial'},
            {'name': 'Movimiento', 'description': 'Movimiento del brazo'},
            {'name': 'Habla', 'description': 'Pronunciar mensaje'}
        ]
    }
    
    # Log de inicio
    logger.log_sequence_start(sequence_data)
    
    # Simular señales
    logger.log_movement_signal(
        'head',
        {'x': 0, 'y': 0, 'z': 0},
        1.0,
        {'name': 'Saludo', 'description': 'Saludo inicial'}
    )
    
    logger.log_gesture_signal(
        'wave',
        {'intensity': 0.8, 'speed': 1.0},
        2.0,
        {'name': 'Movimiento', 'description': 'Movimiento del brazo'}
    )
    
    logger.log_speech_signal(
        "¡Hola! Bienvenidos a la clase de prueba",
        {'voice': 'default', 'speed': 1.0},
        {'name': 'Habla', 'description': 'Pronunciar mensaje'}
    )
    
    # Log de fin
    logger.log_sequence_end()
    
    # Cerrar logger
    logger.close()

if __name__ == "__main__":
    example_usage()

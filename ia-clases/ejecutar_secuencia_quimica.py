#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Secuencia de Química
================================

Script para ejecutar la secuencia JSON de neutralización de ácido
y controlar el robot ADAI de manera segura.
"""

import json
import time
import requests
import sys
import os
from typing import Dict, List, Optional
import threading

class SecuenciaQuimicaExecutor:
    """Ejecutor de secuencias de química para el robot ADAI"""
    
    def __init__(self, esp32_ip: str = "192.168.1.100", esp32_port: int = 80):
        """
        Inicializar ejecutor de secuencias
        
        Args:
            esp32_ip: IP del ESP32
            esp32_port: Puerto del ESP32
        """
        self.esp32_ip = esp32_ip
        self.esp32_port = esp32_port
        self.base_url = f"http://{esp32_ip}:{esp32_port}"
        self.connected = False
        self.session = requests.Session()
        self.session.timeout = 5.0
        
        # Estado de ejecución
        self.sequence_data = None
        self.current_movement = 0
        self.total_movements = 0
        self.execution_running = False
        self.pause_execution = False
        self.stop_execution = False
        
        print("🧪 Inicializando Ejecutor de Secuencia de Química")
        print(f"🤖 Conectando a ESP32 en {self.base_url}")
        
        # Intentar conexión
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Probar conexión con el ESP32"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=3)
            if response.status_code == 200:
                self.connected = True
                print("✅ Conectado al ESP32")
                return True
            else:
                print(f"❌ Error de conexión: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando al ESP32: {e}")
            print("⚠️ Continuando en modo simulación...")
            return False
    
    def load_sequence(self, sequence_file: str) -> bool:
        """
        Cargar secuencia desde archivo JSON
        
        Args:
            sequence_file: Ruta al archivo JSON de secuencia
            
        Returns:
            True si se cargó correctamente
        """
        try:
            if not os.path.exists(sequence_file):
                print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
                return False
            
            with open(sequence_file, 'r', encoding='utf-8') as f:
                self.sequence_data = json.load(f)
            
            self.total_movements = len(self.sequence_data.get('movements', []))
            print(f"✅ Secuencia cargada: {self.sequence_data.get('title', 'Sin título')}")
            print(f"📊 Total de movimientos: {self.total_movements}")
            print(f"⏱️ Duración estimada: {self.sequence_data.get('duration_minutes', 0)} minutos")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando secuencia: {e}")
            return False
    
    def send_command(self, command: str, parameters: Dict = None) -> Optional[Dict]:
        """
        Enviar comando al ESP32
        
        Args:
            command: Comando a enviar
            parameters: Parámetros del comando
            
        Returns:
            Respuesta del ESP32 o None si hay error
        """
        try:
            if not self.connected:
                print(f"⚠️ Simulando comando: {command}")
                return {"status": "simulated", "command": command}
            
            url = f"{self.base_url}/api/command"
            data = {
                'command': command,
                'timestamp': time.time()
            }
            
            if parameters:
                data['parameters'] = parameters
            
            print(f"📤 Enviando: {command}")
            if parameters:
                print(f"   📝 Parámetros: {parameters}")
            
            response = self.session.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Comando ejecutado: {command}")
                return result
            else:
                print(f"❌ Error ejecutando comando: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error enviando comando: {e}")
            return None
    
    def execute_action(self, action: Dict) -> bool:
        """
        Ejecutar una acción individual
        
        Args:
            action: Diccionario con la acción a ejecutar
            
        Returns:
            True si la acción fue exitosa
        """
        try:
            command = action.get('command', '')
            parameters = action.get('parameters', {})
            duration = action.get('duration', 1000) / 1000.0  # Convertir a segundos
            description = action.get('description', 'Sin descripción')
            
            print(f"🎯 Ejecutando: {description}")
            
            # Enviar comando
            result = self.send_command(command, parameters)
            
            # Esperar la duración especificada
            if duration > 0:
                time.sleep(duration)
            
            return result is not None
            
        except Exception as e:
            print(f"❌ Error ejecutando acción: {e}")
            return False
    
    def execute_movement(self, movement: Dict) -> bool:
        """
        Ejecutar un movimiento completo
        
        Args:
            movement: Diccionario con el movimiento a ejecutar
            
        Returns:
            True si el movimiento fue exitoso
        """
        try:
            movement_id = movement.get('id', 0)
            movement_name = movement.get('name', 'Sin nombre')
            movement_type = movement.get('type', 'unknown')
            description = movement.get('description', 'Sin descripción')
            actions = movement.get('actions', [])
            
            print(f"\n🎬 Movimiento {movement_id}/{self.total_movements}: {movement_name}")
            print(f"📝 Tipo: {movement_type}")
            print(f"📋 Descripción: {description}")
            print(f"⚙️ Acciones: {len(actions)}")
            print("-" * 50)
            
            # Verificar si debe pausar
            if self.pause_execution:
                print("⏸️ Ejecución pausada. Presiona Enter para continuar...")
                input()
                self.pause_execution = False
            
            # Verificar si debe detener
            if self.stop_execution:
                print("⏹️ Ejecución detenida por el usuario")
                return False
            
            # Ejecutar cada acción del movimiento
            for i, action in enumerate(actions):
                if self.stop_execution:
                    print("⏹️ Ejecución detenida")
                    return False
                
                print(f"  🔧 Acción {i+1}/{len(actions)}")
                success = self.execute_action(action)
                
                if not success:
                    print(f"❌ Error en acción {i+1}, continuando...")
            
            print(f"✅ Movimiento {movement_id} completado")
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando movimiento: {e}")
            return False
    
    def execute_sequence(self, auto_pause: bool = False) -> bool:
        """
        Ejecutar la secuencia completa
        
        Args:
            auto_pause: Pausar automáticamente entre movimientos
            
        Returns:
            True si la secuencia fue exitosa
        """
        if not self.sequence_data:
            print("❌ No hay secuencia cargada")
            return False
        
        print(f"\n🚀 Iniciando ejecución de secuencia: {self.sequence_data.get('title', 'Sin título')}")
        print("=" * 60)
        
        self.execution_running = True
        self.current_movement = 0
        
        try:
            movements = self.sequence_data.get('movements', [])
            
            for i, movement in enumerate(movements):
                self.current_movement = i + 1
                
                # Pausa automática si está habilitada
                if auto_pause and i > 0:
                    print("\n⏸️ Pausa automática entre movimientos...")
                    input("Presiona Enter para continuar...")
                
                # Ejecutar movimiento
                success = self.execute_movement(movement)
                
                if not success:
                    print(f"❌ Error en movimiento {i+1}, continuando...")
                
                # Pequeña pausa entre movimientos
                time.sleep(0.5)
            
            print("\n" + "=" * 60)
            print("🎉 Secuencia completada exitosamente!")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Ejecución interrumpida por el usuario")
            return False
        except Exception as e:
            print(f"\n❌ Error en la ejecución: {e}")
            return False
        finally:
            self.execution_running = False
    
    def execute_interactive(self) -> bool:
        """Ejecutar secuencia en modo interactivo"""
        if not self.sequence_data:
            print("❌ No hay secuencia cargada")
            return False
        
        print(f"\n🎭 Modo Interactivo: {self.sequence_data.get('title', 'Sin título')}")
        print("=" * 60)
        
        movements = self.sequence_data.get('movements', [])
        
        for i, movement in enumerate(movements):
            movement_name = movement.get('name', 'Sin nombre')
            description = movement.get('description', 'Sin descripción')
            
            print(f"\n🎬 Movimiento {i+1}/{len(movements)}: {movement_name}")
            print(f"📝 {description}")
            
            # Preguntar si ejecutar este movimiento
            response = input("¿Ejecutar este movimiento? (s/n/p para pausar): ").strip().lower()
            
            if response == 'n':
                print("⏭️ Movimiento omitido")
                continue
            elif response == 'p':
                print("⏸️ Ejecución pausada. Presiona Enter para continuar...")
                input()
            
            # Ejecutar movimiento
            success = self.execute_movement(movement)
            
            if not success:
                print(f"❌ Error en movimiento {i+1}")
                continue_response = input("¿Continuar con el siguiente? (s/n): ").strip().lower()
                if continue_response != 's':
                    break
        
        print("\n🎉 Ejecución interactiva completada!")
        return True
    
    def get_progress(self) -> Dict:
        """Obtener progreso actual de la ejecución"""
        if not self.sequence_data:
            return {"error": "No hay secuencia cargada"}
        
        total_movements = len(self.sequence_data.get('movements', []))
        progress_percentage = (self.current_movement / total_movements * 100) if total_movements > 0 else 0
        
        return {
            "current_movement": self.current_movement,
            "total_movements": total_movements,
            "progress_percentage": progress_percentage,
            "execution_running": self.execution_running,
            "sequence_title": self.sequence_data.get('title', 'Sin título')
        }
    
    def pause(self):
        """Pausar la ejecución"""
        self.pause_execution = True
        print("⏸️ Ejecución pausada")
    
    def resume(self):
        """Reanudar la ejecución"""
        self.pause_execution = False
        print("▶️ Ejecución reanudada")
    
    def stop(self):
        """Detener la ejecución"""
        self.stop_execution = True
        self.execution_running = False
        print("⏹️ Ejecución detenida")

def main():
    """Función principal"""
    print("🧪 Ejecutor de Secuencia de Química - Neutralización de Ácido")
    print("🤖 Controlador del Robot ADAI")
    print("=" * 60)
    
    # Configuración del ESP32
    esp32_ip = input("📡 IP del ESP32 (default: 192.168.1.100): ").strip()
    if not esp32_ip:
        esp32_ip = "192.168.1.100"
    
    # Crear ejecutor
    executor = SecuenciaQuimicaExecutor(esp32_ip)
    
    # Cargar secuencia
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    if not executor.load_sequence(sequence_file):
        print(f"❌ No se pudo cargar la secuencia: {sequence_file}")
        return
    
    # Mostrar información de la secuencia
    sequence_data = executor.sequence_data
    print(f"\n📋 INFORMACIÓN DE LA SECUENCIA:")
    print(f"   Título: {sequence_data.get('title', 'Sin título')}")
    print(f"   Descripción: {sequence_data.get('description', 'Sin descripción')}")
    print(f"   Duración: {sequence_data.get('duration_minutes', 0)} minutos")
    print(f"   Movimientos: {len(sequence_data.get('movements', []))}")
    print(f"   Modo seguro: {sequence_data.get('safety_mode', False)}")
    
    # Mostrar objetivos educativos
    objectives = sequence_data.get('educational_objectives', [])
    if objectives:
        print(f"\n🎯 OBJETIVOS EDUCATIVOS:")
        for i, objective in enumerate(objectives, 1):
            print(f"   {i}. {objective}")
    
    # Mostrar materiales necesarios
    materials = sequence_data.get('materials_needed', [])
    if materials:
        print(f"\n🧪 MATERIALES NECESARIOS:")
        for material in materials:
            print(f"   • {material}")
    
    # Menú de opciones
    while True:
        print("\n" + "=" * 40)
        print("🎓 MENÚ DE EJECUCIÓN")
        print("=" * 40)
        print("1. 🚀 Ejecutar Secuencia Completa")
        print("2. 🎭 Ejecutar Modo Interactivo")
        print("3. 📊 Ver Progreso")
        print("4. ⏸️ Pausar Ejecución")
        print("5. ▶️ Reanudar Ejecución")
        print("6. ⏹️ Detener Ejecución")
        print("7. ❌ Salir")
        print("=" * 40)
        
        opcion = input("Selecciona una opción (1-7): ").strip()
        
        try:
            if opcion == "1":
                print("\n🚀 Iniciando ejecución completa...")
                executor.execute_sequence()
            elif opcion == "2":
                print("\n🎭 Iniciando modo interactivo...")
                executor.execute_interactive()
            elif opcion == "3":
                progress = executor.get_progress()
                print(f"\n📊 PROGRESO ACTUAL:")
                print(f"   Secuencia: {progress.get('sequence_title', 'Sin título')}")
                print(f"   Movimiento: {progress.get('current_movement', 0)}/{progress.get('total_movements', 0)}")
                print(f"   Progreso: {progress.get('progress_percentage', 0):.1f}%")
                print(f"   Ejecutando: {progress.get('execution_running', False)}")
            elif opcion == "4":
                executor.pause()
            elif opcion == "5":
                executor.resume()
            elif opcion == "6":
                executor.stop()
            elif opcion == "7":
                print("👋 ¡Hasta luego!")
                executor.stop()
                break
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            print("\n⏹️ Operación interrumpida")
            executor.stop()
        except Exception as e:
            print(f"❌ Error: {e}")
            executor.stop()

if __name__ == "__main__":
    main()

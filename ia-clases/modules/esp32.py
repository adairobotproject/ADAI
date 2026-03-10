"""
Módulo de funciones ESP32 para ADAI
==================================

Contiene todas las funciones relacionadas con:
- Control del robot ESP32
- Ejecución de secuencias
- Comunicación con el robot
"""

import os
import sys
import json
import time
from .config import ESP32_DEFAULT_CONFIG

def esp32_action_resolver(sequence_name: str) -> bool:
    """
    Ejecuta una secuencia en el ESP32 del robot
    
    Args:
        sequence_name: Nombre de la secuencia a ejecutar
        
    Returns:
        bool: True si se ejecutó correctamente, False en caso contrario
    """
    try:
        print(f"🤖 Ejecutando secuencia ESP32: {sequence_name}")
        
        # Importar servicios ESP32
        try:
            # Calcular la ruta correcta desde main.py a services/esp32_services
            current_file_dir = os.path.dirname(os.path.abspath(__file__))  # modules/
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir)))  # ia-clases/
            esp32_services_path = os.path.join(project_root, "services", "esp32_services")
            
            if esp32_services_path not in sys.path:
                sys.path.append(esp32_services_path)
                print(f"✅ Agregado al path: {esp32_services_path}")
            
            # Ahora importar desde la ruta correcta
            from esp32_config_binary import ESP32BinaryConfig
            from esp32_client import ESP32Client
            print("✅ Servicios ESP32 importados correctamente")

        except ImportError as e:
            print(f"❌ Error importando servicios ESP32: {e}")
            return False
        
        # Cargar configuración ESP32
        try:
            esp32_config = ESP32BinaryConfig()
            config_data = esp32_config.load_config()
            
            if not config_data:
                print("⚠️ No se encontró configuración ESP32, usando valores por defecto")
                host = ESP32_DEFAULT_CONFIG['host']
                port = ESP32_DEFAULT_CONFIG['port']
            else:
                host = config_data.host
                port = config_data.port
                print(f"✅ Configuración ESP32 cargada: {host}:{port}")
                
        except Exception as e:
            print(f"⚠️ Error cargando configuración ESP32: {e}")
            host = ESP32_DEFAULT_CONFIG['host']
            port = ESP32_DEFAULT_CONFIG['port']
        
        # Conectar al ESP32
        try:
            esp32_client = ESP32Client()
            esp32_client.host = host
            esp32_client.port = port
            success = esp32_client.connect()
            
            if not success:
                print(f"❌ No se pudo conectar al ESP32 en {host}:{port}")
                return False
            
            print(f"✅ Conectado al ESP32 en {host}:{port}")
            
        except Exception as e:
            print(f"❌ Error conectando al ESP32: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Buscar y cargar la secuencia
        try:
            # Buscar la secuencia en el directorio de secuencias
            sequences_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_file_dir))), "sequences")
            sequence_file = None
            
            # Buscar archivo de secuencia
            for file in os.listdir(sequences_dir):
                if file.endswith('.json') and sequence_name.lower() in file.lower():
                    sequence_file = os.path.join(sequences_dir, file)
                    break
            
            if not sequence_file:
                print(f"❌ No se encontró secuencia: {sequence_name}")
                return False
            
            print(f"📁 Cargando secuencia: {sequence_file}")
            
            # Cargar archivo JSON de la secuencia
            with open(sequence_file, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)
            
            print(f"✅ Secuencia cargada: {len(sequence_data.get('actions', []))} acciones")
            
        except Exception as e:
            print(f"❌ Error cargando secuencia: {e}")
            return False
        
        # Ejecutar la secuencia
        try:
            print("🚀 Ejecutando secuencia...")
            
            # Obtener acciones de la secuencia - CORREGIDO para manejar estructura movements/actions
            movements = sequence_data.get('movements', [])
            actions = []

            # Si no hay movements pero sí hay actions directamente (compatibilidad)
            if not movements:
                actions = sequence_data.get('actions', [])
            else:
                # Extraer todas las actions de todos los movements
                for movement in movements:
                    movement_actions = movement.get('actions', [])
                    actions.extend(movement_actions)

            print(f"📋 Total movimientos encontrados: {len(movements)}")
            print(f"📋 Total acciones extraídas: {len(actions)}")

            for i, action in enumerate(actions):
                print(f"   Acción {i+1}/{len(actions)}: {action.get('command', 'Unknown')}")
                
                # Ejecutar acción según el tipo
                command = action.get('command', '')
                parameters = action.get('parameters', {})
                duration = action.get('duration', 1000)
                
                if command == "BRAZOS":
                    # Comando de movimiento de brazos
                    # Support both old format (BI/BD/FI/FD/HI/HD/PD) and new format (M1-M8)
                    if 'M1' in parameters:
                        # New M1-M8 format
                        pd = parameters.get('M1', 0)
                        fd = parameters.get('M2', 0)
                        bd = parameters.get('M3', 0)
                        hd = parameters.get('M4', 0)
                        pi = parameters.get('M5', 90)
                        fi = parameters.get('M6', 0)
                        bi = parameters.get('M7', 0)
                        hi = parameters.get('M8', 0)
                    else:
                        # Old named format
                        bi = parameters.get('BI', 0)
                        bd = parameters.get('BD', 0)
                        fi = parameters.get('FI', 0)
                        fd = parameters.get('FD', 0)
                        hi = parameters.get('HI', 0)
                        hd = parameters.get('HD', 0)
                        pd = parameters.get('PD', 0)
                        pi = parameters.get('PI', 90)

                    print(f"      Moviendo brazos: BI={bi}, BD={bd}, FI={fi}, FD={fd}, HI={hi}, HD={hd}, PD={pd}, PI={pi}")

                    # Enviar comando al ESP32
                    response = esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd, pi)
                    
                    if response:
                        print(f"      ✅ Comando ejecutado")
                    else:
                        print(f"      ❌ Error ejecutando comando")
                    
                elif command == "GESTO":
                    # Comando de gesto
                    hand = parameters.get('hand', 'derecha')
                    gesture = parameters.get('gesture', '')
                    print(f"      Ejecutando gesto: {hand} {gesture}")

                    # Enviar comando de gesto al ESP32
                    response = esp32_client.send_gesture(hand, gesture)
                    
                    if response:
                        print(f"      ✅ Gesto ejecutado")
                    else:
                        print(f"      ❌ Error ejecutando gesto")
                    
                elif command == "HABLAR":
                    # Comando de habla
                    text = parameters.get('texto', '')
                    print(f"      Hablando: {text}")
                    
                    # Enviar comando de habla al ESP32
                    response = esp32_client.send_speech(text)
                    
                    if response:
                        print(f"      ✅ Habla ejecutada")
                    else:
                        print(f"      ❌ Error ejecutando habla")
                    
                elif command == "ESPERAR":
                    # Comando de espera
                    wait_time = duration / 1000.0  # Convertir a segundos
                    print(f"      Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                    
                else:
                    print(f"      ⚠️ Comando no reconocido: {command}")
                
                # Pequeña pausa entre acciones
                time.sleep(0.1)
            
            print("✅ Secuencia ejecutada completamente")
            
        except Exception as e:
            print(f"❌ Error ejecutando secuencia: {e}")
            return False
        
        # Desconectar del ESP32
        try:
            esp32_client.disconnect()
            print("🔌 Desconectado del ESP32")
        except Exception as e:
            print(f"⚠️ Error desconectando del ESP32: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error general en esp32_action_resolver: {e}")
        import traceback
        traceback.print_exc()
        return False

def execute_esp32_sequence(sequence_name: str) -> bool:
    """
    Ejecuta una secuencia en el ESP32 del robot (alias para compatibilidad)
    
    Args:
        sequence_name: Nombre de la secuencia a ejecutar
        
    Returns:
        bool: True si se ejecutó correctamente, False en caso contrario
    """
    return esp32_action_resolver(sequence_name)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Sequence Tester - Prueba de secuencias de robot
"""

import os
import sys
import json
import time
import traceback

# Agregar el directorio actual al path para importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar servicios ESP32
try:
    from services.esp32_services.esp32_client import ESP32Client
    from services.esp32_services.esp32_config_binary import ESP32BinaryConfig
    print("✅ Servicios ESP32 importados correctamente")
except ImportError as e:
    print(f"❌ Error importando servicios ESP32: {e}")
    sys.exit(1)

class ESP32SequenceTester:
    """Clase para probar secuencias ESP32"""

    def __init__(self):
        self.esp32_client = None
        self.esp32_config = None
        self.sequences_dir = os.path.join(current_dir, "sequences")

        # Inicializar configuración
        self.init_config()

    def init_config(self):
        """Inicializar configuración ESP32"""
        try:
            self.esp32_config = ESP32BinaryConfig()
            config_data = self.esp32_config.load_config()

            if config_data:
                print(f"✅ Configuración ESP32 cargada: {config_data.host}:{config_data.port}")
            else:
                print("⚠️ No se encontró configuración ESP32, usando valores por defecto")

        except Exception as e:
            print(f"❌ Error inicializando configuración ESP32: {e}")

    def connect_esp32(self):
        """Conectar al ESP32"""
        try:
            print("🔌 Conectando al ESP32...")

            if not self.esp32_client:
                self.esp32_client = ESP32Client()

            # Cargar configuración
            config_data = None
            if self.esp32_config:
                config_data = self.esp32_config.load_config()

            if config_data:
                host = config_data.host
                port = config_data.port
            else:
                host = '192.168.1.100'
                port = 80

            # Configurar cliente y conectar
            self.esp32_client.host = host
            self.esp32_client.port = port
            success = self.esp32_client.connect()

            if success:
                print(f"✅ Conectado exitosamente al ESP32 en {host}:{port}")
                return True
            else:
                print(f"❌ Error conectando al ESP32 en {host}:{port}")
                return False

        except Exception as e:
            print(f"❌ Error conectando al ESP32: {e}")
            traceback.print_exc()
            return False

    def disconnect_esp32(self):
        """Desconectar del ESP32"""
        try:
            if self.esp32_client:
                self.esp32_client.disconnect()
                print("🔌 Desconectado del ESP32")
        except Exception as e:
            print(f"⚠️ Error desconectando: {e}")

    def list_sequences(self):
        """Listar secuencias disponibles"""
        try:
            if not os.path.exists(self.sequences_dir):
                print(f"❌ Directorio de secuencias no encontrado: {self.sequences_dir}")
                return []

            sequences = []
            for file in os.listdir(self.sequences_dir):
                if file.endswith('.json'):
                    sequences.append(file[:-5])  # Remover extensión .json

            print(f"📋 Secuencias disponibles ({len(sequences)}):")
            for i, seq in enumerate(sequences, 1):
                print(f"  {i}. {seq}")

            return sequences

        except Exception as e:
            print(f"❌ Error listando secuencias: {e}")
            return []

    def load_sequence(self, sequence_name):
        """Cargar una secuencia desde archivo"""
        try:
            sequence_file = None

            # Buscar archivo de secuencia
            for file in os.listdir(self.sequences_dir):
                if file.endswith('.json') and sequence_name.lower() in file.lower():
                    sequence_file = os.path.join(self.sequences_dir, file)
                    break

            if not sequence_file:
                print(f"❌ Secuencia '{sequence_name}' no encontrada")
                return None

            print(f"📂 Cargando secuencia: {sequence_file}")

            # Cargar archivo JSON
            with open(sequence_file, 'r', encoding='utf-8') as f:
                sequence_data = json.load(f)

            actions = sequence_data.get('actions', [])
            print(f"✅ Secuencia cargada: {len(actions)} acciones")

            return sequence_data

        except Exception as e:
            print(f"❌ Error cargando secuencia: {e}")
            traceback.print_exc()
            return None

    def execute_sequence(self, sequence_name, simulate=False):
        """Ejecutar una secuencia"""
        try:
            print(f"🚀 Ejecutando secuencia: {sequence_name}")
            print("=" * 50)

            # Cargar secuencia
            sequence_data = self.load_sequence(sequence_name)
            if not sequence_data:
                return False

            actions = sequence_data.get('actions', [])

            if simulate:
                print("🎭 MODO SIMULACIÓN - No se enviarán comandos al ESP32")
                print("-" * 50)

            # Ejecutar cada acción
            for i, action in enumerate(actions):
                print(f"⚡ Acción {i+1}/{len(actions)}: {action.get('command', 'Unknown')}")

                command = action.get('command', '')
                parameters = action.get('parameters', {})
                duration = action.get('duration', 1000)

                if command == "BRAZOS":
                    # Comando de movimiento de brazos
                    bi = parameters.get('BI', 0)
                    bd = parameters.get('BD', 0)
                    fi = parameters.get('FI', 0)
                    fd = parameters.get('FD', 0)
                    hi = parameters.get('HI', 0)
                    hd = parameters.get('HD', 0)
                    pd = parameters.get('PD', 0)

                    print(f"   🤖 Moviendo brazos: BI={bi}, BD={bd}, FI={fi}, FD={fd}, HI={hi}, HD={hd}, PD={pd}")

                    if not simulate and self.esp32_client:
                        response = self.esp32_client.send_movement(bi, bd, fi, fd, hi, hd, pd)
                        if response:
                            print("   ✅ Comando ejecutado")
                        else:
                            print("   ❌ Error ejecutando comando")

                elif command == "GESTO":
                    # Comando de gesto
                    gesture = parameters.get('gesture', '')
                    print(f"   🤖 Ejecutando gesto: {gesture}")

                    if not simulate and self.esp32_client:
                        response = self.esp32_client.send_gesture(gesture)
                        if response:
                            print("   ✅ Gesto ejecutado")
                        else:
                            print("   ❌ Error ejecutando gesto")

                elif command == "HABLAR":
                    # Comando de habla
                    text = parameters.get('texto', '')
                    print(f"   🗣️ Hablando: {text}")

                    if not simulate and self.esp32_client:
                        response = self.esp32_client.send_speech(text)
                        if response:
                            print("   ✅ Habla ejecutada")
                        else:
                            print("   ❌ Error ejecutando habla")

                elif command == "ESPERAR":
                    # Comando de espera
                    wait_time = duration / 1000.0
                    print(f"   ⏱️ Esperando {wait_time} segundos...")
                    time.sleep(wait_time)

                else:
                    print(f"   ⚠️ Comando no reconocido: {command}")

                # Pequeña pausa entre acciones
                if not simulate:
                    time.sleep(0.5)

            print("=" * 50)
            print(f"✅ Secuencia '{sequence_name}' completada")
            return True

        except Exception as e:
            print(f"❌ Error ejecutando secuencia: {e}")
            traceback.print_exc()
            return False

    def test_connection(self):
        """Probar conexión ESP32"""
        try:
            print("🧪 Probando conexión ESP32...")

            if not self.esp32_client:
                print("❌ Cliente ESP32 no inicializado")
                return False

            # Intentar enviar un comando de prueba
            response = self.esp32_client.send_movement(0, 0, 0, 0, 0, 0, 0)

            if response:
                print("✅ Conexión ESP32 funcionando correctamente")
                return True
            else:
                print("❌ Error en conexión ESP32")
                return False

        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
            return False

def main():
    """Función principal del tester"""
    print("🤖 ESP32 Sequence Tester")
    print("=" * 30)

    tester = ESP32SequenceTester()

    while True:
        print("\n📋 Menú de opciones:")
        print("1. Listar secuencias disponibles")
        print("2. Probar conexión ESP32")
        print("3. Ejecutar secuencia (modo real)")
        print("4. Ejecutar secuencia (modo simulación)")
        print("5. Salir")

        try:
            opcion = input("\nSeleccione una opción (1-5): ").strip()

            if opcion == "1":
                # Listar secuencias
                sequences = tester.list_sequences()

            elif opcion == "2":
                # Probar conexión
                if tester.connect_esp32():
                    tester.test_connection()
                    tester.disconnect_esp32()

            elif opcion == "3":
                # Ejecutar secuencia real
                sequences = tester.list_sequences()
                if sequences:
                    sequence_name = input("Ingrese el nombre de la secuencia: ").strip()
                    if sequence_name:
                        if tester.connect_esp32():
                            success = tester.execute_sequence(sequence_name, simulate=False)
                            tester.disconnect_esp32()
                            if success:
                                print("🎉 ¡Secuencia ejecutada exitosamente!")
                            else:
                                print("❌ Error ejecutando secuencia")
                        else:
                            print("❌ No se pudo conectar al ESP32")

            elif opcion == "4":
                # Ejecutar secuencia simulación
                sequences = tester.list_sequences()
                if sequences:
                    sequence_name = input("Ingrese el nombre de la secuencia: ").strip()
                    if sequence_name:
                        success = tester.execute_sequence(sequence_name, simulate=True)
                        if success:
                            print("🎭 Simulación completada exitosamente")
                        else:
                            print("❌ Error en simulación")

            elif opcion == "5":
                # Salir
                print("👋 ¡Hasta luego!")
                break

            else:
                print("❌ Opción no válida")

        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Client for Classes
========================

Cliente ESP32 simplificado para que las clases puedan conectarse
y enviar comandos usando la configuración binaria.
"""

import socket
import json
import time
import threading
from typing import Dict, Optional, Any, Callable
from urllib.parse import urlencode
import requests

try:
    from .esp32_config_binary import get_esp32_connection_info, update_esp32_connection_status
    CONFIG_AVAILABLE = True
except ImportError:
    try:
        from esp32_config_binary import get_esp32_connection_info, update_esp32_connection_status
        CONFIG_AVAILABLE = True
    except ImportError:
        CONFIG_AVAILABLE = False
        print("⚠️ ESP32 Binary Config no disponible")

class ESP32Client:
    """Cliente ESP32 simplificado para clases"""
    
    def __init__(self, host: str = None, port: int = None, timeout: float = 5.0):
        """
        Inicializar cliente ESP32
        
        Args:
            host: Host del ESP32 (opcional, usa configuración por defecto)
            port: Puerto del ESP32 (opcional, usa configuración por defecto)
            timeout: Timeout de conexión
        """
        # Cargar configuración si está disponible
        if CONFIG_AVAILABLE and (host is None or port is None):
            config_host, config_port = get_esp32_connection_info()
            self.host = host or config_host
            self.port = port or config_port
        else:
            self.host = host or "192.168.1.100"
            self.port = port or 80
        
        self.timeout = timeout
        self.connected = False
        self.session = None
        self.lock = threading.Lock()
        
        # Callbacks
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_command_sent: Optional[Callable] = None
        self.on_error: Optional[Callable] = None
        
        print(f"🔧 [ESP32 CLIENT] Inicializado para {self.host}:{self.port}")
        print(f"   📍 Host: {self.host}")
        print(f"   🔌 Puerto: {self.port}")
        print(f"   ⏱️ Timeout: {self.timeout}s")
    
    def connect(self) -> bool:
        """
        Conectar al ESP32
        
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            with self.lock:
                if self.connected:
                    print("⚠️ [ESP32 CONNECTION] Ya conectado al ESP32")
                    return True
                
                print(f"🔌 [ESP32 CONNECTION] Conectando a ESP32 en {self.host}:{self.port}...")
                
                # Crear sesión HTTP
                print(f"🔧 [ESP32 CONNECTION] Creando sesión HTTP...")
                self.session = requests.Session()
                self.session.timeout = self.timeout
                print(f"   ⏱️ Timeout configurado: {self.timeout}s")
                
                # Probar conexión básica
                try:
                    print(f"🔍 [ESP32 CONNECTION] Probando conexión a {self.host}:{self.port}")
                    response = self.session.get(f"http://{self.host}:{self.port}/", timeout=self.timeout)
                    print(f"📥 [ESP32 CONNECTION] Response status: {response.status_code}")
                    print(f"   📄 Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        self.connected = True
                        print(f"✅ [ESP32 CONNECTION] Conectado exitosamente al ESP32")
                        print(f"   🌐 URL base: http://{self.host}:{self.port}/")
                        print(f"   📊 Estado: Conectado")
                        
                        # Actualizar estado de conexión
                        if CONFIG_AVAILABLE:
                            update_esp32_connection_status("connected")
                        
                        # Notificar conexión
                        if self.on_connect:
                            self.on_connect()
                        
                        return True
                    else:
                        print(f"❌ [ESP32 CONNECTION] Error de conexión: HTTP {response.status_code}")
                        print(f"   📄 Response content: {response.text[:200]}...")
                        return False
                        
                except requests.exceptions.RequestException as e:
                    print(f"❌ [ESP32 CONNECTION] Error de conexión: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ [ESP32 CONNECTION] Error conectando al ESP32: {e}")
            if self.on_error:
                self.on_error(f"Error de conexión: {e}")
            return False
    
    def disconnect(self):
        """Desconectar del ESP32"""
        try:
            with self.lock:
                if not self.connected:
                    return
                
                print("🔌 [ESP32 DISCONNECT] Desconectando del ESP32...")
                
                if self.session:
                    self.session.close()
                    self.session = None
                
                self.connected = False
                
                # Actualizar estado de conexión
                if CONFIG_AVAILABLE:
                    update_esp32_connection_status("disconnected")
                
                # Notificar desconexión
                if self.on_disconnect:
                    self.on_disconnect()
                
                print("✅ [ESP32 DISCONNECT] Desconectado del ESP32")
                
        except Exception as e:
            print(f"❌ [ESP32 DISCONNECT] Error desconectando del ESP32: {e}")
    
    def send_command(self, command: str, parameters: Dict = None) -> Optional[Dict]:
        """
        Enviar comando al ESP32
        
        Args:
            command: Comando a enviar
            parameters: Parámetros del comando
            
        Returns:
            Dict con respuesta o None si hay error
        """
        try:
            with self.lock:
                if not self.connected:
                    print("⚠️ [ESP32 COMMAND] No conectado al ESP32, intentando conectar...")
                    if not self.connect():
                        print("❌ [ESP32 COMMAND] No se pudo conectar al ESP32")
                        return None
                    print("✅ [ESP32 COMMAND] Conectado al ESP32, enviando comando...")
                
                # Build the command string for the firmware /cmd endpoint
                cmd_str = command
                if parameters:
                    param_parts = [f"{k}={v}" for k, v in parameters.items()]
                    cmd_str += " " + " ".join(param_parts)

                # Enviar comando HTTP POST (form-urlencoded to /cmd)
                url = f"http://{self.host}:{self.port}/cmd"
                data = {'cmd': cmd_str}

                print(f"🚀 [ESP32 REQUEST] Enviando comando genérico:")
                print(f"   📡 URL: {url}")
                print(f"   📝 cmd: {cmd_str}")
                print(f"   🔧 Comando: {command}")
                if parameters:
                    print(f"   📋 Parámetros: {parameters}")

                response = self.session.post(url, data=data, timeout=self.timeout)

                print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
                print(f"   📄 Response: {response.text}")

                if response.status_code == 200:
                    result = {'status': 'ok', 'response': response.text}
                    print(f"✅ [ESP32 COMMAND] Comando ejecutado exitosamente: {command}")
                    print(f"   📊 Resultado: {result}")

                    # Notificar comando enviado
                    if self.on_command_sent:
                        self.on_command_sent(command, parameters, result)

                    return result
                else:
                    print(f"❌ [ESP32 COMMAND] Error ejecutando comando: HTTP {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"❌ [ESP32 COMMAND] Error enviando comando: {e}")
            if self.on_error:
                self.on_error(f"Error enviando comando: {e}")
            return None
    
    def send_movement(self, bi: int, bd: int, fi: int, fd: int, hi: int, hd: int, pd: int, pi: int = 90) -> bool:
        """
        Enviar comando de movimiento de brazos

        Args:
            bi: Brazo Izquierdo (M7)
            bd: Brazo Derecho (M3)
            fi: Frente Izquierdo (M6)
            fd: Frente Derecho (M2)
            hi: High Izquierdo (M8)
            hd: High Derecho (M4)
            pd: Pollo Derecho (M1)
            pi: Pollo Izquierdo (M5, default=90)

        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando BRAZOS (firmware 8-motor M1-M8 format)
            params = f"M1={pd} M2={fd} M3={bd} M4={hd} M5={pi} M6={fi} M7={bi} M8={hi}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'BRAZOS',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando movimiento de brazos:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Movimiento de brazos enviado: {params}")
                return True
            else:
                print(f"❌ Error enviando movimiento: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando movimiento: {e}")
            return False

    def send_gesture(self, hand: str, gesture: str) -> bool:
        """
        Enviar comando de gesto
        
        Args:
            hand: Mano (izquierda, derecha, ambas)
            gesture: Tipo de gesto
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando GESTO
            params = f"mano={hand} gesto={gesture}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'GESTO',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando gesto:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Gesto enviado: {hand} {gesture}")
                return True
            else:
                print(f"❌ Error enviando gesto: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando gesto: {e}")
            return False

    def send_speech(self, text: str) -> bool:
        """
        Enviar comando de habla
        
        Args:
            text: Texto a pronunciar
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando HABLAR
            params = f"texto={text}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'HABLAR',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando habla:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Habla enviada: {text}")
                return True
            else:
                print(f"❌ Error enviando habla: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando habla: {e}")
            return False

    def send_wait(self, duration_ms: int) -> bool:
        """
        Enviar comando de espera
        
        Args:
            duration_ms: Duración en milisegundos
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando ESPERAR
            params = f"tiempo={duration_ms}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'ESPERAR',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando espera:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Espera enviada: {duration_ms}ms")
                return True
            else:
                print(f"❌ Error enviando espera: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando espera: {e}")
            return False
    
    def send_finger_control(self, hand: str, finger: str, angle: int) -> bool:
        """
        Enviar comando de control de dedo

        Args:
            hand: Mano (izquierda, derecha)
            finger: Dedo a controlar
            angle: Ángulo del dedo

        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Usar el endpoint específico para dedos
            url = f"http://{self.host}:{self.port}/manos/dedo"
            data = {
                'mano': hand,
                'dedo': finger,
                'angulo': str(angle)
            }

            print(f"🚀 [ESP32 REQUEST] Enviando control de dedo:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Mano: {hand}, Dedo: {finger}, Ángulo: {angle}")

            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Control de dedo enviado: {hand} {finger} {angle}°")
                return True
            else:
                print(f"❌ Error enviando control de dedo: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando control de dedo: {e}")
            return False
    
    def send_wrist_control(self, hand: str, angle: int) -> bool:
        """
        Enviar comando de control de muñeca
        
        Args:
            hand: Mano (izquierda, derecha)
            angle: Ángulo de la muñeca
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando MUNECA
            params = f"mano={hand} angulo={angle}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'MUNECA',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando control de muñeca:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Control de muñeca enviado: {hand} {angle}°")
                return True
            else:
                print(f"❌ Error enviando control de muñeca: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando control de muñeca: {e}")
            return False
    
    def send_neck_movement(self, l: int, i: int, s: int) -> bool:
        """
        Enviar comando de movimiento del cuello
        
        Args:
            l: Lado (izquierda/derecha)
            i: Inclinación
            s: Subida/bajada
            
        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Crear parámetros para el comando CUELLO
            params = f"L={l} I={i} S={s}"
            
            # Enviar comando usando el endpoint de secuencias
            url = f"http://{self.host}:{self.port}/sequence/command"
            data = {
                'command': 'CUELLO',
                'params': params
            }
            
            print(f"🚀 [ESP32 REQUEST] Enviando movimiento del cuello:")
            print(f"   📡 URL: {url}")
            print(f"   📝 Data: {data}")
            print(f"   🔧 Parámetros: {params}")
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            
            print(f"📥 [ESP32 RESPONSE] Status: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
            if response.status_code == 200:
                print(f"✅ Movimiento del cuello enviado: L={l} I={i} S={s}")
                return True
            else:
                print(f"❌ Error enviando movimiento del cuello: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error enviando movimiento del cuello: {e}")
            return False

    def get_status(self) -> Optional[Dict]:
        """
        Obtener estado del ESP32
        
        Returns:
            Dict con estado o None si hay error
        """
        try:
            if not self.connected:
                print("⚠️ [ESP32 STATUS] No conectado al ESP32")
                return None
            
            # Obtener estado usando el endpoint de debug
            url = f"http://{self.host}:{self.port}/debug"
            print(f"🔍 [ESP32 STATUS] Obteniendo estado desde: {url}")
            
            response = self.session.get(url, timeout=self.timeout)
            
            print(f"📥 [ESP32 STATUS] Response status: {response.status_code}")
            print(f"   📄 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                return {'status': 'connected', 'debug_info': response.text}
            else:
                return {'status': 'error', 'http_code': response.status_code}
                
        except Exception as e:
            print(f"❌ Error obteniendo estado: {e}")
            return None

    def is_connected(self) -> bool:
        """Verificar si está conectado al ESP32"""
        return self.connected
    
    def get_connection_info(self) -> Dict:
        """Obtener información de conexión"""
        return {
            'host': self.host,
            'port': self.port,
            'connected': self.connected,
            'timeout': self.timeout
        }

# Cliente global para uso en clases
_esp32_client_instance = None

def get_esp32_client() -> ESP32Client:
    """
    Obtener instancia global del cliente ESP32
    
    Returns:
        Instancia del cliente ESP32
    """
    global _esp32_client_instance
    if _esp32_client_instance is None:
        _esp32_client_instance = ESP32Client()
    return _esp32_client_instance

def connect_to_esp32() -> bool:
    """
    Conectar al ESP32 usando el cliente global
    
    Returns:
        bool: True si la conexión es exitosa
    """
    client = get_esp32_client()
    return client.connect()

def send_esp32_command(command: str, parameters: Dict = None) -> Optional[Dict]:
    """
    Enviar comando al ESP32 usando el cliente global
    
    Args:
        command: Comando a enviar
        parameters: Parámetros del comando
        
    Returns:
        Dict con respuesta o None si hay error
    """
    client = get_esp32_client()
    return client.send_command(command, parameters)

def send_esp32_movement(bi: int, bd: int, fi: int, fd: int, hi: int, hd: int, pd: int, pi: int = 90) -> bool:
    """
    Enviar movimiento de brazos al ESP32 usando el cliente global

    Args:
        bi: Brazo Izquierdo (M7)
        bd: Brazo Derecho (M3)
        fi: Frente Izquierdo (M6)
        fd: Frente Derecho (M2)
        hi: High Izquierdo (M8)
        hd: High Derecho (M4)
        pd: Pollo Derecho (M1)
        pi: Pollo Izquierdo (M5, default=90)

    Returns:
        bool: True si se envió correctamente
    """
    client = get_esp32_client()
    return client.send_movement(bi, bd, fi, fd, hi, hd, pd, pi)

def send_esp32_gesture(hand: str, gesture: str) -> bool:
    """
    Enviar gesto al ESP32 usando el cliente global
    
    Args:
        hand: Mano (izquierda, derecha, ambas)
        gesture: Tipo de gesto
        
    Returns:
        bool: True si se envió correctamente
    """
    client = get_esp32_client()
    return client.send_gesture(hand, gesture)

def send_esp32_speech(message: str) -> bool:
    """
    Enviar habla al ESP32 usando el cliente global
    
    Args:
        message: Mensaje a pronunciar
        
    Returns:
        bool: True si se envió correctamente
    """
    client = get_esp32_client()
    return client.send_speech(message)

def disconnect_from_esp32():
    """Desconectar del ESP32 usando el cliente global"""
    global _esp32_client_instance
    if _esp32_client_instance:
        _esp32_client_instance.disconnect()
        _esp32_client_instance = None

# Ejemplo de uso
def example_usage():
    """Ejemplo de uso del cliente ESP32"""
    
    print("🧪 Probando cliente ESP32...")
    
    # Crear cliente
    client = ESP32Client()
    
    # Conectar
    if client.connect():
        print("✅ Conectado al ESP32")
        
        # Enviar comando de movimiento de brazos (bi, bd, fi, fd, hi, hd, pd, pi)
        if client.send_movement(100, 30, 95, 160, 140, 165, 100, 90):
            print("✅ Movimiento de brazos enviado")
        
        # Enviar comando de gesto
        if client.send_gesture('derecha', 'paz'):
            print("✅ Gesto enviado")
        
        # Enviar comando de habla
        if client.send_speech("¡Hola! Soy el robot ADAI"):
            print("✅ Habla enviada")
        
        # Obtener estado
        status = client.get_status()
        if status:
            print(f"📊 Estado del ESP32: {status}")
        
        # Desconectar
        client.disconnect()
        print("✅ Desconectado del ESP32")
    else:
        print("❌ No se pudo conectar al ESP32")
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    example_usage()

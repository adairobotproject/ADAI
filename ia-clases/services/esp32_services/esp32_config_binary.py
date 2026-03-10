#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESP32 Binary Configuration Manager
==================================

Este módulo maneja la configuración de conexión ESP32 en formato binario
para que las clases puedan leer automáticamente la configuración y conectarse.
"""

import os
import sys
import struct
import json
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import socket

# Ensure paths module is importable (lives in ia-clases/)
_ia_clases_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ia_clases_dir not in sys.path:
    sys.path.insert(0, _ia_clases_dir)
from paths import get_data_dir

@dataclass
class ESP32Config:
    """Configuración de conexión ESP32"""
    host: str
    port: int
    timeout: float
    enable_control: bool
    auto_connect: bool
    retry_attempts: int
    retry_delay: float
    last_connection: float
    connection_status: str
    firmware_version: str
    device_name: str

class ESP32BinaryConfig:
    """Gestor de configuración ESP32 en formato binario"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Use writable data directory for the binary config file
            config_file = os.path.join(get_data_dir(), "esp32_config.bin")
        self.config_file = config_file
        self.magic_header = b'ESP32CON'
        self.version = 1
        
    def save_config(self, config: ESP32Config) -> bool:
        """
        Guardar configuración ESP32 en formato binario
        
        Args:
            config: Configuración ESP32 a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Preparar datos para escritura binaria
            host_bytes = config.host.encode('utf-8')
            host_length = len(host_bytes)
            
            firmware_version_bytes = config.firmware_version.encode('utf-8')
            firmware_version_length = len(firmware_version_bytes)
            
            device_name_bytes = config.device_name.encode('utf-8')
            device_name_length = len(device_name_bytes)
            
            connection_status_bytes = config.connection_status.encode('utf-8')
            connection_status_length = len(connection_status_bytes)
            
            # Estructura del archivo binario:
            # - Magic header (8 bytes)
            # - Version (4 bytes)
            # - Timestamp (8 bytes)
            # - Host length (4 bytes)
            # - Host (variable)
            # - Port (4 bytes)
            # - Timeout (8 bytes)
            # - Enable control (1 byte)
            # - Auto connect (1 byte)
            # - Retry attempts (4 bytes)
            # - Retry delay (8 bytes)
            # - Last connection (8 bytes)
            # - Connection status length (4 bytes)
            # - Connection status (variable)
            # - Firmware version length (4 bytes)
            # - Firmware version (variable)
            # - Device name length (4 bytes)
            # - Device name (variable)
            
            with open(self.config_file, 'wb') as f:
                # Magic header
                f.write(self.magic_header)
                
                # Version
                f.write(struct.pack('<I', self.version))
                
                # Timestamp
                f.write(struct.pack('<Q', int(time.time())))
                
                # Host
                f.write(struct.pack('<I', host_length))
                f.write(host_bytes)
                
                # Port
                f.write(struct.pack('<I', config.port))
                
                # Timeout
                f.write(struct.pack('<d', config.timeout))
                
                # Enable control
                f.write(struct.pack('<?', config.enable_control))
                
                # Auto connect
                f.write(struct.pack('<?', config.auto_connect))
                
                # Retry attempts
                f.write(struct.pack('<I', config.retry_attempts))
                
                # Retry delay
                f.write(struct.pack('<d', config.retry_delay))
                
                # Last connection
                f.write(struct.pack('<Q', int(config.last_connection)))
                
                # Connection status
                f.write(struct.pack('<I', connection_status_length))
                f.write(connection_status_bytes)
                
                # Firmware version
                f.write(struct.pack('<I', firmware_version_length))
                f.write(firmware_version_bytes)
                
                # Device name
                f.write(struct.pack('<I', device_name_length))
                f.write(device_name_bytes)
            
            print(f"✅ Configuración ESP32 guardada en: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando configuración ESP32: {e}")
            return False
    
    def load_config(self) -> Optional[ESP32Config]:
        """
        Cargar configuración ESP32 desde archivo binario
        
        Returns:
            ESP32Config o None si hay error
        """
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️ Archivo de configuración no encontrado: {self.config_file}")
                return None
            
            with open(self.config_file, 'rb') as f:
                # Leer magic header
                magic = f.read(8)
                if magic != self.magic_header:
                    print(f"❌ Header mágico inválido: {magic}")
                    return None
                
                # Leer version
                version = struct.unpack('<I', f.read(4))[0]
                if version != self.version:
                    print(f"⚠️ Versión de archivo diferente: {version} (esperado: {self.version})")
                
                # Leer timestamp
                timestamp = struct.unpack('<Q', f.read(8))[0]
                
                # Leer host
                host_length = struct.unpack('<I', f.read(4))[0]
                host = f.read(host_length).decode('utf-8')
                
                # Leer port
                port = struct.unpack('<I', f.read(4))[0]
                
                # Leer timeout
                timeout = struct.unpack('<d', f.read(8))[0]
                
                # Leer enable control
                enable_control = struct.unpack('<?', f.read(1))[0]
                
                # Leer auto connect
                auto_connect = struct.unpack('<?', f.read(1))[0]
                
                # Leer retry attempts
                retry_attempts = struct.unpack('<I', f.read(4))[0]
                
                # Leer retry delay
                retry_delay = struct.unpack('<d', f.read(8))[0]
                
                # Leer last connection
                last_connection = struct.unpack('<Q', f.read(8))[0]
                
                # Leer connection status
                connection_status_length = struct.unpack('<I', f.read(4))[0]
                connection_status = f.read(connection_status_length).decode('utf-8')
                
                # Leer firmware version
                firmware_version_length = struct.unpack('<I', f.read(4))[0]
                firmware_version = f.read(firmware_version_length).decode('utf-8')
                
                # Leer device name
                device_name_length = struct.unpack('<I', f.read(4))[0]
                device_name = f.read(device_name_length).decode('utf-8')
                
                # Crear objeto de configuración
                config = ESP32Config(
                    host=host,
                    port=port,
                    timeout=timeout,
                    enable_control=enable_control,
                    auto_connect=auto_connect,
                    retry_attempts=retry_attempts,
                    retry_delay=retry_delay,
                    last_connection=last_connection,
                    connection_status=connection_status,
                    firmware_version=firmware_version,
                    device_name=device_name
                )
                
                print(f"✅ Configuración ESP32 cargada desde: {self.config_file}")
                return config
                
        except Exception as e:
            print(f"❌ Error cargando configuración ESP32: {e}")
            return None
    
    def create_default_config(self) -> ESP32Config:
        """
        Crear configuración por defecto
        
        Returns:
            ESP32Config con valores por defecto
        """
        return ESP32Config(
            host="192.168.1.100",
            port=80,
            timeout=5.0,
            enable_control=True,
            auto_connect=True,
            retry_attempts=3,
            retry_delay=2.0,
            last_connection=time.time(),
            connection_status="disconnected",
            firmware_version="1.0.0",
            device_name="ADAI_ESP32"
        )
    
    def update_connection_status(self, status: str) -> bool:
        """
        Actualizar solo el estado de conexión
        
        Args:
            status: Nuevo estado de conexión
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            config = self.load_config()
            if not config:
                config = self.create_default_config()
            
            config.connection_status = status
            config.last_connection = time.time()
            
            return self.save_config(config)
            
        except Exception as e:
            print(f"❌ Error actualizando estado de conexión: {e}")
            return False
    
    def get_connection_info(self) -> Tuple[str, int]:
        """
        Obtener información básica de conexión
        
        Returns:
            Tuple con (host, port)
        """
        try:
            config = self.load_config()
            if config:
                return config.host, config.port
            else:
                # Valores por defecto
                return "192.168.1.100", 80
                
        except Exception as e:
            print(f"❌ Error obteniendo información de conexión: {e}")
            return "192.168.1.100", 80
    
    def validate_config(self, config: ESP32Config) -> bool:
        """
        Validar configuración ESP32
        
        Args:
            config: Configuración a validar
            
        Returns:
            bool: True si la configuración es válida
        """
        try:
            # Validar host
            if not config.host or len(config.host) == 0:
                print("❌ Host no puede estar vacío")
                return False
            
            # Validar puerto
            if config.port < 1 or config.port > 65535:
                print(f"❌ Puerto inválido: {config.port}")
                return False
            
            # Validar timeout
            if config.timeout <= 0:
                print(f"❌ Timeout inválido: {config.timeout}")
                return False
            
            # Validar retry attempts
            if config.retry_attempts < 0:
                print(f"❌ Intentos de reconexión inválidos: {config.retry_attempts}")
                return False
            
            # Validar retry delay
            if config.retry_delay < 0:
                print(f"❌ Delay de reconexión inválido: {config.retry_delay}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False
    
    def test_connection(self, host: str = None, port: int = None) -> bool:
        """
        Probar conexión al ESP32
        
        Args:
            host: Host a probar (opcional, usa configuración por defecto)
            port: Puerto a probar (opcional, usa configuración por defecto)
            
        Returns:
            bool: True si la conexión es exitosa
        """
        try:
            if host is None or port is None:
                config = self.load_config()
                if config:
                    host = config.host
                    port = config.port
                else:
                    host = "192.168.1.100"
                    port = 80
            
            print(f"🔍 Probando conexión a {host}:{port}...")
            
            # Crear socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            # Intentar conexión
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Conexión exitosa a {host}:{port}")
                self.update_connection_status("connected")
                return True
            else:
                print(f"❌ Conexión fallida a {host}:{port}")
                self.update_connection_status("disconnected")
                return False
                
        except Exception as e:
            print(f"❌ Error probando conexión: {e}")
            self.update_connection_status("error")
            return False
    
    def export_to_json(self, json_file: str = "esp32_config.json") -> bool:
        """
        Exportar configuración a JSON
        
        Args:
            json_file: Archivo JSON de destino
            
        Returns:
            bool: True si se exportó correctamente
        """
        try:
            config = self.load_config()
            if not config:
                print("❌ No hay configuración para exportar")
                return False
            
            # Convertir a diccionario
            config_dict = {
                'host': config.host,
                'port': config.port,
                'timeout': config.timeout,
                'enable_control': config.enable_control,
                'auto_connect': config.auto_connect,
                'retry_attempts': config.retry_attempts,
                'retry_delay': config.retry_delay,
                'last_connection': config.last_connection,
                'connection_status': config.connection_status,
                'firmware_version': config.firmware_version,
                'device_name': config.device_name,
                'exported_at': time.time()
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración exportada a: {json_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando configuración: {e}")
            return False
    
    def import_from_json(self, json_file: str) -> bool:
        """
        Importar configuración desde JSON
        
        Args:
            json_file: Archivo JSON de origen
            
        Returns:
            bool: True si se importó correctamente
        """
        try:
            if not os.path.exists(json_file):
                print(f"❌ Archivo JSON no encontrado: {json_file}")
                return False
            
            with open(json_file, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # Crear objeto de configuración
            config = ESP32Config(
                host=config_dict.get('host', '192.168.1.100'),
                port=config_dict.get('port', 80),
                timeout=config_dict.get('timeout', 5.0),
                enable_control=config_dict.get('enable_control', True),
                auto_connect=config_dict.get('auto_connect', True),
                retry_attempts=config_dict.get('retry_attempts', 3),
                retry_delay=config_dict.get('retry_delay', 2.0),
                last_connection=config_dict.get('last_connection', time.time()),
                connection_status=config_dict.get('connection_status', 'disconnected'),
                firmware_version=config_dict.get('firmware_version', '1.0.0'),
                device_name=config_dict.get('device_name', 'ADAI_ESP32')
            )
            
            # Validar y guardar
            if self.validate_config(config):
                return self.save_config(config)
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error importando configuración: {e}")
            return False

# Funciones de conveniencia para uso en clases
def get_esp32_connection_info() -> Tuple[str, int]:
    """
    Obtener información de conexión ESP32 para uso en clases
    
    Returns:
        Tuple con (host, port)
    """
    config_manager = ESP32BinaryConfig()
    return config_manager.get_connection_info()

def test_esp32_connection() -> bool:
    """
    Probar conexión ESP32 para uso en clases
    
    Returns:
        bool: True si la conexión es exitosa
    """
    config_manager = ESP32BinaryConfig()
    return config_manager.test_connection()

def update_esp32_connection_status(status: str) -> bool:
    """
    Actualizar estado de conexión ESP32 para uso en clases
    
    Args:
        status: Nuevo estado de conexión
        
    Returns:
        bool: True si se actualizó correctamente
    """
    config_manager = ESP32BinaryConfig()
    return config_manager.update_connection_status(status)

# Ejemplo de uso
def example_usage():
    """Ejemplo de uso del gestor de configuración ESP32"""
    
    print("🧪 Probando gestor de configuración ESP32...")
    
    # Crear gestor
    config_manager = ESP32BinaryConfig()
    
    # Crear configuración por defecto
    config = config_manager.create_default_config()
    print(f"📋 Configuración por defecto creada:")
    print(f"   Host: {config.host}")
    print(f"   Puerto: {config.port}")
    print(f"   Timeout: {config.timeout}s")
    print(f"   Control habilitado: {config.enable_control}")
    
    # Guardar configuración
    if config_manager.save_config(config):
        print("✅ Configuración guardada correctamente")
    
    # Cargar configuración
    loaded_config = config_manager.load_config()
    if loaded_config:
        print("✅ Configuración cargada correctamente")
        print(f"   Estado de conexión: {loaded_config.connection_status}")
    
    # Probar conexión
    config_manager.test_connection()
    
    # Exportar a JSON
    config_manager.export_to_json()
    
    print("✅ Prueba completada")

if __name__ == "__main__":
    example_usage()

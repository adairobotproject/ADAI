#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Sequence Builder ESP32 Connection
=====================================

Script para probar que el SequenceBuilderTab puede conectarse al ESP32
"""

import sys
import os

# Agregar el directorio de servicios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

try:
    from esp32_services.esp32_client import ESP32Client
    from esp32_services.esp32_config_binary import ESP32BinaryConfig
    print("✅ ESP32 services importados correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32 services: {e}")
    sys.exit(1)

def test_sequence_builder_esp32_connection():
    """Probar la conexión ESP32 como lo hace SequenceBuilderTab"""
    print("🧪 Probando conexión ESP32 como SequenceBuilderTab...")
    
    try:
        # Simular la inicialización del SequenceBuilderTab
        print("🔧 Inicializando ESP32 integration...")
        
        # Load ESP32 configuration
        esp32_config = ESP32BinaryConfig()
        config_data = esp32_config.load_config()
        
        if config_data:
            print(f"✅ ESP32 config loaded: {config_data.host}:{config_data.port}")
        else:
            print("⚠️ No ESP32 config found, using defaults")
        
        # Initialize ESP32 client
        esp32_client = ESP32Client()
        
        # Simular el método connect_esp32 del SequenceBuilderTab
        print("🔌 Simulando connect_esp32...")
        
        # Load config if available
        host = None
        port = None
        
        if config_data:
            # config_data is an ESP32Config object, access attributes directly
            host = config_data.host
            port = config_data.port
        else:
            host = '192.168.1.100'
            port = 80
        
        print(f"📍 Configurando para {host}:{port}")
        
        # Update ESP32 client configuration and connect
        esp32_client.host = host
        esp32_client.port = port
        success = esp32_client.connect()
        
        if success:
            print(f"✅ Connected to ESP32 at {host}:{port}")
            
            # Test sending a command
            print("🤖 Testing movement command...")
            if esp32_client.send_movement(10, 40, 80, 90, 80, 80, 45):
                print("✅ Movement command successful")
            else:
                print("❌ Movement command failed")
            
            # Disconnect
            esp32_client.disconnect()
            print("✅ Disconnected from ESP32")
            
        else:
            print(f"❌ Failed to connect to ESP32 at {host}:{port}")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🤖 Test Sequence Builder ESP32 Connection")
    print("=" * 60)
    
    success = test_sequence_builder_esp32_connection()
    
    if success:
        print("\n✅ Test completado exitosamente!")
    else:
        print("\n❌ Test falló")
    
    print("\n" + "=" * 60)
    print("🏁 Test completado")
    print("=" * 60)

if __name__ == "__main__":
    main()

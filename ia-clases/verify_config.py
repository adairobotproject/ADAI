#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify ESP32 Configuration
==========================

Script simple para verificar que la configuración ESP32 se carga correctamente
desde la nueva ubicación en services/esp32_services/.
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_config():
    """Verify ESP32 configuration loading"""
    
    print("🔍 Verificando configuración ESP32...")
    
    try:
        from services.esp32_services.esp32_config_binary import ESP32BinaryConfig, ESP32Config
        
        # Create configuration manager
        config_manager = ESP32BinaryConfig()
        print(f"📁 Ruta del archivo: {config_manager.config_file}")
        
        # Check if file exists
        if os.path.exists(config_manager.config_file):
            file_size = os.path.getsize(config_manager.config_file)
            print(f"✅ Archivo existe: {file_size} bytes")
        else:
            print("❌ Archivo no existe")
            return False
        
        # Load configuration
        config = config_manager.load_config()
        if config:
            print("✅ Configuración cargada:")
            print(f"   📡 Host: {config.host}")
            print(f"   🔌 Puerto: {config.port}")
            print(f"   ⏱️ Timeout: {config.timeout}")
            print(f"   🔧 Control habilitado: {config.enable_control}")
            print(f"   🔗 Estado: {config.connection_status}")
        else:
            print("❌ No se pudo cargar la configuración")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_esp32_client():
    """Test ESP32 client with the configuration"""
    
    print("\n🔍 Probando cliente ESP32...")
    
    try:
        from services.esp32_services.esp32_client import get_esp32_client
        
        # Get client
        client = get_esp32_client()
        info = client.get_connection_info()
        
        print("✅ Cliente ESP32:")
        print(f"   📡 Host: {info['host']}")
        print(f"   🔌 Puerto: {info['port']}")
        print(f"   🔗 Conectado: {info['connected']}")
        print(f"   ⏱️ Timeout: {info['timeout']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    
    print("🚀 Verificación de Configuración ESP32")
    print("=" * 50)
    
    # Verify configuration
    config_ok = verify_config()
    
    # Test client
    client_ok = test_esp32_client()
    
    print("\n" + "=" * 50)
    if config_ok and client_ok:
        print("✅ Configuración ESP32 funcionando correctamente")
        print("   📁 Ubicación: services/esp32_services/esp32_config.bin")
    else:
        print("❌ Problemas con la configuración ESP32")
    
    return config_ok and client_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

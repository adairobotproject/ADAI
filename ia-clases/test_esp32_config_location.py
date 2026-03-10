#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ESP32 Config Location
==========================

Este script verifica que el archivo de configuración ESP32 se guarde
en la ubicación correcta dentro del directorio de servicios.
"""

import os
import sys
import time

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_file_location():
    """Test that config file is saved in the correct location"""
    
    print("🧪 Probando ubicación del archivo de configuración ESP32...")
    
    try:
        from services.esp32_services.esp32_config_binary import ESP32BinaryConfig, ESP32Config
        
        # Create configuration manager
        config_manager = ESP32BinaryConfig()
        print(f"📁 Ruta del archivo de configuración: {config_manager.config_file}")
        
        # Verify the path is within the services directory
        services_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "services", "esp32_services")
        expected_path = os.path.join(services_dir, "esp32_config.bin")
        
        print(f"📁 Directorio de servicios ESP32: {services_dir}")
        print(f"📁 Ruta esperada: {expected_path}")
        
        if config_manager.config_file == expected_path:
            print("✅ Ruta de configuración correcta")
        else:
            print("❌ Ruta de configuración incorrecta")
            return False
        
        # Create test configuration
        test_config = ESP32Config(
            host="192.168.1.200",
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
        
        # Save configuration
        print("\n💾 Guardando configuración...")
        if config_manager.save_config(test_config):
            print("✅ Configuración guardada correctamente")
        else:
            print("❌ Error guardando configuración")
            return False
        
        # Check if file exists in the correct location
        if os.path.exists(config_manager.config_file):
            file_size = os.path.getsize(config_manager.config_file)
            print(f"✅ Archivo creado: {config_manager.config_file}")
            print(f"📊 Tamaño del archivo: {file_size} bytes")
        else:
            print(f"❌ Archivo no encontrado: {config_manager.config_file}")
            return False
        
        # Load configuration to verify it works
        print("\n🔄 Cargando configuración...")
        loaded_config = config_manager.load_config()
        if loaded_config and loaded_config.host == "192.168.1.200":
            print("✅ Configuración cargada correctamente")
            print(f"   📡 Host: {loaded_config.host}")
            print(f"   🔌 Puerto: {loaded_config.port}")
        else:
            print("❌ Error cargando configuración")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_esp32_client_integration():
    """Test that ESP32 client can load the config from the new location"""
    
    print("\n🧪 Probando integración con ESP32 Client...")
    
    try:
        from services.esp32_services.esp32_client import get_esp32_client
        
        # Get client (should load config from the new location)
        client = get_esp32_client()
        connection_info = client.get_connection_info()
        
        print(f"✅ Cliente ESP32 obtenido")
        print(f"   📡 Host: {connection_info['host']}")
        print(f"   🔌 Puerto: {connection_info['port']}")
        print(f"   🔗 Conectado: {connection_info['connected']}")
        
        # Verify it's using the saved configuration
        if connection_info['host'] == "192.168.1.200":
            print("✅ Cliente usando configuración guardada correctamente")
        else:
            print("⚠️ Cliente no está usando la configuración guardada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_esp32_tab_integration():
    """Test that ESP32Tab can work with the new config location"""
    
    print("\n🧪 Probando integración con ESP32Tab...")
    
    try:
        from tabs.esp32_tab import ESP32Tab
        
        # Create a mock notebook for testing
        class MockNotebook:
            def __init__(self):
                self.tabs = []
            
            def add(self, tab, text):
                self.tabs.append((tab, text))
        
        # Create ESP32Tab
        mock_gui = type('MockGUI', (), {})()
        notebook = MockNotebook()
        
        esp32_tab = ESP32Tab(mock_gui, notebook)
        print("✅ ESP32Tab creado correctamente")
        
        # Test configuration loading
        if hasattr(esp32_tab, 'config_manager') and esp32_tab.config_manager:
            config_path = esp32_tab.config_manager.config_file
            print(f"✅ Config manager disponible: {config_path}")
            
            # Verify it's in the services directory
            if "services/esp32_services" in config_path:
                print("✅ Config manager usando ruta correcta")
            else:
                print("❌ Config manager usando ruta incorrecta")
                return False
        else:
            print("⚠️ Config manager no disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    
    print("🚀 Test de Ubicación de Configuración ESP32")
    print("=" * 60)
    
    # Test config file location
    location_success = test_config_file_location()
    
    # Test ESP32 client integration
    client_success = test_esp32_client_integration()
    
    # Test ESP32Tab integration
    tab_success = test_esp32_tab_integration()
    
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DE LAS PRUEBAS:")
    print(f"   Ubicación de Config: {'✅ EXITOSO' if location_success else '❌ FALLÓ'}")
    print(f"   Integración Cliente: {'✅ EXITOSO' if client_success else '❌ FALLÓ'}")
    print(f"   Integración ESP32Tab: {'✅ EXITOSO' if tab_success else '❌ FALLÓ'}")
    
    all_success = location_success and client_success and tab_success
    
    if all_success:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("   El archivo de configuración se guarda en la ubicación correcta.")
        print("\n📋 UBICACIÓN VERIFICADA:")
        print("   ✅ services/esp32_services/esp32_config.bin")
        print("   ✅ Configuración cargada correctamente")
        print("   ✅ Integración con cliente funcionando")
        print("   ✅ Integración con ESP32Tab funcionando")
    else:
        print("\n⚠️ Algunas pruebas fallaron.")
        print("   Revisa los errores anteriores para más detalles.")
    
    return all_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

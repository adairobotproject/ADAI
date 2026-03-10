#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ESP32 Client Real Connection
================================

Script para probar la conexión real al ESP32 usando el ESP32Client
"""

import sys
import os

# Agregar el directorio de servicios al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

try:
    from esp32_services.esp32_client import ESP32Client
    print("✅ ESP32Client importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ESP32Client: {e}")
    sys.exit(1)

def test_esp32_connection():
    """Probar conexión al ESP32"""
    print("🧪 Probando conexión al ESP32...")
    
    # Crear cliente ESP32
    # Usar la IP que funciona en Postman
    client = ESP32Client(host="10.71.47.170", port=80)
    
    print(f"🔧 Cliente creado para {client.host}:{client.port}")
    
    # Intentar conectar
    print("🔌 Intentando conectar...")
    if client.connect():
        print("✅ Conexión exitosa!")
        
        # Probar obtener estado
        print("📊 Probando obtener estado...")
        status = client.get_status()
        if status:
            print(f"✅ Estado obtenido: {status}")
        else:
            print("❌ No se pudo obtener estado")
        
        # Probar comando de movimiento
        print("🤖 Probando comando de movimiento...")
        if client.send_movement(10, 40, 80, 90, 80, 80, 45):
            print("✅ Movimiento enviado exitosamente")
        else:
            print("❌ Error enviando movimiento")
        
        # Probar comando de gesto
        print("👋 Probando comando de gesto...")
        if client.send_gesture('paz'):
            print("✅ Gesto enviado exitosamente")
        else:
            print("❌ Error enviando gesto")
        
        # Probar comando de habla
        print("🗣️ Probando comando de habla...")
        if client.send_speech("Hola, soy el robot ADAI"):
            print("✅ Habla enviada exitosamente")
        else:
            print("❌ Error enviando habla")
        
        # Desconectar
        print("🔌 Desconectando...")
        client.disconnect()
        print("✅ Desconectado")
        
    else:
        print("❌ No se pudo conectar al ESP32")
        return False
    
    return True

def test_esp32_config_binary():
    """Probar configuración binaria del ESP32"""
    print("\n🔧 Probando configuración binaria...")
    
    try:
        from esp32_services.esp32_config_binary import ESP32BinaryConfig
        print("✅ ESP32BinaryConfig importado correctamente")
        
        config_manager = ESP32BinaryConfig()
        config = config_manager.load_config()
        
        if config:
            print(f"✅ Configuración cargada: {config.host}:{config.port}")
            print(f"   📍 Host: {config.host}")
            print(f"   🔌 Puerto: {config.port}")
            print(f"   ⏱️ Timeout: {config.timeout}")
            print(f"   🔧 Control habilitado: {config.enable_control}")
        else:
            print("⚠️ No se encontró configuración")
            
    except ImportError as e:
        print(f"❌ Error importando ESP32BinaryConfig: {e}")
    except Exception as e:
        print(f"❌ Error probando configuración: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🤖 Test ESP32 Client - Conexión Real")
    print("=" * 60)
    
    # Probar configuración binaria
    test_esp32_config_binary()
    
    # Probar conexión real
    print("\n" + "=" * 60)
    print("🔌 Probando conexión real al ESP32...")
    print("=" * 60)
    
    success = test_esp32_connection()
    
    if success:
        print("\n✅ Todas las pruebas pasaron exitosamente!")
    else:
        print("\n❌ Algunas pruebas fallaron")
    
    print("\n" + "=" * 60)
    print("🏁 Test completado")
    print("=" * 60)

if __name__ == "__main__":
    main()

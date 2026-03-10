#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug ESP32 Binary Configuration
===============================

Este script debuggea el sistema de configuración binaria ESP32
para identificar el problema con el magic header.
"""

import os
import sys
import time
import struct

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_magic_header():
    """Debug the magic header issue"""
    
    print("🔍 Debugging magic header issue...")
    
    # Test magic header
    magic_header = b'ESP32CONF'
    print(f"Magic header: {repr(magic_header)}")
    print(f"Length: {len(magic_header)}")
    print(f"Expected: b'ESP32CONF'")
    
    # Test writing and reading
    test_file = "test_magic.bin"
    
    try:
        # Write magic header
        with open(test_file, 'wb') as f:
            f.write(magic_header)
        
        print(f"✅ Magic header written to {test_file}")
        
        # Read magic header
        with open(test_file, 'rb') as f:
            read_magic = f.read(8)
        
        print(f"Read magic header: {repr(read_magic)}")
        print(f"Match: {read_magic == magic_header}")
        
        # Clean up
        os.remove(test_file)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def debug_esp32_config():
    """Debug the ESP32 configuration system"""
    
    print("\n🔍 Debugging ESP32 configuration system...")
    
    try:
        from services.esp32_services.esp32_config_binary import ESP32BinaryConfig, ESP32Config
        
        # Create configuration manager
        config_manager = ESP32BinaryConfig()
        print(f"Config file path: {config_manager.config_file}")
        print(f"Magic header: {repr(config_manager.magic_header)}")
        
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
        print("\n💾 Saving configuration...")
        if config_manager.save_config(test_config):
            print("✅ Configuration saved")
        else:
            print("❌ Failed to save configuration")
            return
        
        # Check file size
        if os.path.exists(config_manager.config_file):
            file_size = os.path.getsize(config_manager.config_file)
            print(f"File size: {file_size} bytes")
        
        # Read magic header directly
        print("\n📖 Reading magic header directly...")
        with open(config_manager.config_file, 'rb') as f:
            magic = f.read(8)
            print(f"Magic header from file: {repr(magic)}")
            print(f"Expected: {repr(config_manager.magic_header)}")
            print(f"Match: {magic == config_manager.magic_header}")
        
        # Try to load configuration
        print("\n🔄 Loading configuration...")
        loaded_config = config_manager.load_config()
        if loaded_config:
            print(f"✅ Configuration loaded: {loaded_config.host}:{loaded_config.port}")
        else:
            print("❌ Failed to load configuration")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    
    print("🚀 ESP32 Binary Configuration Debug")
    print("=" * 50)
    
    # Debug magic header
    debug_magic_header()
    
    # Debug ESP32 configuration
    debug_esp32_config()
    
    print("\n" + "=" * 50)
    print("✅ Debug completed")

if __name__ == "__main__":
    main()

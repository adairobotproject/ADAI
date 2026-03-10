#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to diagnose import issues
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_import(module_name, description):
    """Test importing a module"""
    try:
        print(f"🔍 Testing import: {description}")
        __import__(module_name)
        print(f"✅ {description}: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {description}: FAILED - {e}")
        return False

def main():
    print("🚀 Starting import diagnostics...\n")

    # Test basic tkinter
    test_import("tkinter", "Basic tkinter")

    # Test tabs module
    test_import("tabs", "Tabs package")

    # Test base tab
    test_import("tabs.base_tab", "Base tab module")

    # Test ESP32 tab
    test_import("tabs.esp32_tab", "ESP32 tab module")

    # Test ESP32 services
    test_import("services.esp32_services.esp32_client", "ESP32 client")
    test_import("services.esp32_services.esp32_config_binary", "ESP32 config binary")

    print("\n🎯 Import diagnostics completed!")

if __name__ == "__main__":
    main()
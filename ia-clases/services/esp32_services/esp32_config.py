#!/usr/bin/env python3
"""
ESP32 Configuration Manager
==========================

Manages ESP32 connection configuration and settings.
"""

import json
import os
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

# Ensure paths module is importable (lives in ia-clases/)
_ia_clases_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ia_clases_dir not in sys.path:
    sys.path.insert(0, _ia_clases_dir)
from paths import get_data_dir

@dataclass
class ESP32Settings:
    """ESP32 connection settings"""
    host: str = "192.168.1.100"
    port: int = 80
    timeout: float = 2.0
    retry_attempts: int = 3
    auto_connect: bool = False
    enable_control: bool = False

class ESP32ConfigManager:
    """Manages ESP32 configuration persistence"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = os.path.join(get_data_dir(), "esp32_config.json")
        self.config_file = config_file
        self.settings = ESP32Settings()
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    # Update settings with loaded data
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
                return True
        except Exception as e:
            print(f"Error loading ESP32 config: {e}")
        return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.settings), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving ESP32 config: {e}")
        return False
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific setting"""
        if hasattr(self.settings, key):
            setattr(self.settings, key, value)
            return self.save_config()
        return False
    
    def get_setting(self, key: str) -> Any:
        """Get a specific setting"""
        return getattr(self.settings, key, None)
    
    def reset_to_defaults(self) -> bool:
        """Reset settings to defaults"""
        self.settings = ESP32Settings()
        return self.save_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return asdict(self.settings)

# Global config manager instance
config_manager = ESP32ConfigManager()

def get_esp32_config() -> ESP32Settings:
    """Get ESP32 configuration"""
    return config_manager.settings

def update_esp32_config(key: str, value: Any) -> bool:
    """Update ESP32 configuration"""
    return config_manager.update_setting(key, value)

def reset_esp32_config() -> bool:
    """Reset ESP32 configuration to defaults"""
    return config_manager.reset_to_defaults()

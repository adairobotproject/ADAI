#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prueba simple de importación de módulos
"""

import os
import sys

# Configurar rutas
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(current_dir, "modules")

print(f"📁 Directorio actual: {current_dir}")
print(f"📁 Directorio de módulos: {modules_dir}")
print(f"📁 ¿Existe módulos? {os.path.exists(modules_dir)}")

if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)
    print(f"✅ Agregado al path: {modules_dir}")

# Probar importación simple
try:
    print("🔄 Probando importación de config...")
    from modules.config import client
    print("✅ Config importado correctamente")
except Exception as e:
    print(f"❌ Error importando config: {e}")

try:
    print("🔄 Probando importación de speech...")
    from modules.speech import initialize_tts
    print("✅ Speech importado correctamente")
except Exception as e:
    print(f"❌ Error importando speech: {e}")

print("🎯 Prueba completada")

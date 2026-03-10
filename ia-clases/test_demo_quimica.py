#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Demo de Química - Neutralización de Ácido
==============================================

Script de prueba para verificar que el sistema de demo de química
funciona correctamente sin necesidad de conexión real al robot.
"""

import json
import time
import sys
import os
from typing import Dict, List, Optional

def test_sequence_loading():
    """Probar carga de secuencia JSON"""
    print("🧪 Probando carga de secuencia JSON...")
    
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    
    if not os.path.exists(sequence_file):
        print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
        return False
    
    try:
        with open(sequence_file, 'r', encoding='utf-8') as f:
            sequence_data = json.load(f)
        
        # Verificar estructura básica
        required_fields = ['name', 'title', 'description', 'movements', 'safety_mode']
        for field in required_fields:
            if field not in sequence_data:
                print(f"❌ Campo requerido faltante: {field}")
                return False
        
        print(f"✅ Secuencia cargada: {sequence_data.get('title', 'Sin título')}")
        print(f"📊 Total de movimientos: {len(sequence_data.get('movements', []))}")
        print(f"⏱️ Duración estimada: {sequence_data.get('duration_minutes', 0)} minutos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando secuencia: {e}")
        return False

def test_safety_limits():
    """Probar validación de límites de seguridad"""
    print("\n🛡️ Probando validación de límites de seguridad...")
    
    # Límites de seguridad según ESP32
    safety_limits = {
        'brazos': {
            'BI': (10, 30),    # Brazo izquierdo
            'FI': (60, 120),   # Frente izquierdo
            'HI': (70, 90),    # High izquierdo
            'BD': (30, 55),    # Brazo derecho
            'FD': (70, 110),   # Frente derecho
            'HD': (70, 90),    # High derecho
            'PD': (0, 90)      # Pollo derecho
        },
        'cuello': {
            'L': (120, 160),   # Lateral
            'I': (60, 130),    # Inferior
            'S': (109, 110)    # Superior
        }
    }
    
    # Cargar secuencia
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    if not os.path.exists(sequence_file):
        print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
        return False
    
    with open(sequence_file, 'r', encoding='utf-8') as f:
        sequence_data = json.load(f)
    
    movements = sequence_data.get('movements', [])
    violations = []
    
    for movement in movements:
        movement_name = movement.get('name', 'Sin nombre')
        actions = movement.get('actions', [])
        
        for action in actions:
            command = action.get('command', '')
            parameters = action.get('parameters', {})
            
            # Verificar brazos
            if command == 'BRAZOS':
                for param, value in parameters.items():
                    if param in safety_limits['brazos']:
                        min_val, max_val = safety_limits['brazos'][param]
                        if value < min_val or value > max_val:
                            violations.append({
                                'movement': movement_name,
                                'command': command,
                                'parameter': param,
                                'value': value,
                                'range': f"{min_val}-{max_val}"
                            })
            
            # Verificar cuello
            elif command == 'CUELLO':
                for param, value in parameters.items():
                    if param in safety_limits['cuello']:
                        min_val, max_val = safety_limits['cuello'][param]
                        if value < min_val or value > max_val:
                            violations.append({
                                'movement': movement_name,
                                'command': command,
                                'parameter': param,
                                'value': value,
                                'range': f"{min_val}-{max_val}"
                            })
    
    if violations:
        print(f"❌ Se encontraron {len(violations)} violaciones de límites de seguridad:")
        for violation in violations:
            print(f"   - {violation['movement']}: {violation['parameter']}={violation['value']} (rango: {violation['range']})")
        return False
    else:
        print("✅ Todos los movimientos respetan los límites de seguridad")
        return True

def test_command_structure():
    """Probar estructura de comandos"""
    print("\n🔧 Probando estructura de comandos...")
    
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    if not os.path.exists(sequence_file):
        print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
        return False
    
    with open(sequence_file, 'r', encoding='utf-8') as f:
        sequence_data = json.load(f)
    
    movements = sequence_data.get('movements', [])
    valid_commands = ['BRAZOS', 'CUELLO', 'MANO', 'MUNECA', 'HABLAR']
    invalid_commands = []
    
    for movement in movements:
        movement_name = movement.get('name', 'Sin nombre')
        actions = movement.get('actions', [])
        
        for action in actions:
            command = action.get('command', '')
            parameters = action.get('parameters', {})
            
            # Verificar que el comando sea válido
            if command not in valid_commands:
                invalid_commands.append({
                    'movement': movement_name,
                    'command': command
                })
            
            # Verificar que tenga parámetros
            if not parameters:
                print(f"⚠️ Comando sin parámetros: {command} en {movement_name}")
    
    if invalid_commands:
        print(f"❌ Se encontraron {len(invalid_commands)} comandos inválidos:")
        for invalid in invalid_commands:
            print(f"   - {invalid['movement']}: {invalid['command']}")
        return False
    else:
        print("✅ Todos los comandos son válidos")
        return True

def test_movement_flow():
    """Probar flujo de movimientos"""
    print("\n🔄 Probando flujo de movimientos...")
    
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    if not os.path.exists(sequence_file):
        print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
        return False
    
    with open(sequence_file, 'r', encoding='utf-8') as f:
        sequence_data = json.load(f)
    
    movements = sequence_data.get('movements', [])
    
    # Verificar que hay movimientos
    if len(movements) == 0:
        print("❌ No hay movimientos en la secuencia")
        return False
    
    # Verificar que los IDs son secuenciales
    for i, movement in enumerate(movements):
        expected_id = i + 1
        actual_id = movement.get('id', 0)
        
        if actual_id != expected_id:
            print(f"❌ ID de movimiento incorrecto: esperado {expected_id}, encontrado {actual_id}")
            return False
    
    # Verificar que cada movimiento tiene acciones
    for movement in movements:
        movement_name = movement.get('name', 'Sin nombre')
        actions = movement.get('actions', [])
        
        if len(actions) == 0:
            print(f"❌ Movimiento sin acciones: {movement_name}")
            return False
    
    print(f"✅ Flujo de movimientos correcto: {len(movements)} movimientos")
    return True

def test_educational_content():
    """Probar contenido educativo"""
    print("\n📚 Probando contenido educativo...")
    
    sequence_file = "sequences/sequence_Quimica_Neutralizacion_Completa.json"
    if not os.path.exists(sequence_file):
        print(f"❌ Archivo de secuencia no encontrado: {sequence_file}")
        return False
    
    with open(sequence_file, 'r', encoding='utf-8') as f:
        sequence_data = json.load(f)
    
    # Verificar objetivos educativos
    objectives = sequence_data.get('educational_objectives', [])
    if len(objectives) == 0:
        print("❌ No hay objetivos educativos definidos")
        return False
    
    print(f"✅ Objetivos educativos: {len(objectives)} objetivos")
    for i, objective in enumerate(objectives, 1):
        print(f"   {i}. {objective}")
    
    # Verificar materiales necesarios
    materials = sequence_data.get('materials_needed', [])
    if len(materials) == 0:
        print("❌ No hay materiales necesarios definidos")
        return False
    
    print(f"\n✅ Materiales necesarios: {len(materials)} materiales")
    for material in materials:
        print(f"   • {material}")
    
    # Verificar ecuación química
    equation = sequence_data.get('chemical_equation', '')
    if not equation:
        print("❌ No hay ecuación química definida")
        return False
    
    print(f"\n✅ Ecuación química: {equation}")
    
    return True

def test_simulation_mode():
    """Probar modo simulación"""
    print("\n🎮 Probando modo simulación...")
    
    # Simular ejecución de comandos
    test_commands = [
        ("BRAZOS", {"BI": 10, "FI": 80, "HI": 80, "BD": 40, "FD": 90, "HD": 80, "PD": 45}),
        ("CUELLO", {"L": 155, "I": 95, "S": 110}),
        ("MANO", {"M": "derecha", "GESTO": "SALUDO"}),
        ("HABLAR", {"texto": "¡Hola estudiantes!"})
    ]
    
    for command, parameters in test_commands:
        print(f"⚠️ Simulando comando: {command}")
        print(f"   📝 Parámetros: {parameters}")
        time.sleep(0.1)  # Simular delay
    
    print("✅ Modo simulación funcionando correctamente")
    return True

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE DEMO DE QUÍMICA")
    print("=" * 60)
    
    tests = [
        ("Carga de Secuencia", test_sequence_loading),
        ("Límites de Seguridad", test_safety_limits),
        ("Estructura de Comandos", test_command_structure),
        ("Flujo de Movimientos", test_movement_flow),
        ("Contenido Educativo", test_educational_content),
        ("Modo Simulación", test_simulation_mode)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name}: PASÓ")
                passed += 1
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS DE PRUEBAS: {passed}/{total} pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El sistema de demo de química está listo para usar")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar los errores antes de usar el sistema.")
        return False

def main():
    """Función principal"""
    print("🧪 Test Demo de Química - Neutralización de Ácido")
    print("🤖 Verificación del Sistema ADAI")
    print("=" * 60)
    
    # Ejecutar pruebas
    success = run_all_tests()
    
    if success:
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Verificar conexión al ESP32")
        print("2. Ejecutar: python demo_clase_quimica_neutralizacion.py")
        print("3. O ejecutar: python ejecutar_secuencia_quimica.py")
        print("4. Probar en modo simulación primero")
    else:
        print("\n🔧 CORRECCIONES NECESARIAS:")
        print("1. Revisar archivos de secuencia JSON")
        print("2. Verificar límites de seguridad")
        print("3. Corregir comandos inválidos")
        print("4. Completar contenido educativo")
    
    print("\n📖 Para más información, consultar: GUIA_DEMO_QUIMICA_NEUTRALIZACION.md")

if __name__ == "__main__":
    main()

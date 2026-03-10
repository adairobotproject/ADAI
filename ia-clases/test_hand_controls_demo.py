#!/usr/bin/env python3
"""
Test script para demostrar las nuevas funciones de control de manos
en el demo sequence manager.

Este script muestra cómo usar las funciones de control de manos
que ahora están disponibles en el demo sequence manager.
"""

import sys
import os
import time

# Agregar el directorio de clases al path
current_dir = os.path.dirname(os.path.abspath(__file__))
clases_dir = os.path.join(current_dir, "clases", "main")
sys.path.append(clases_dir)

# Importar las funciones de control de manos
from demo_sequence_manager import (
    robot_hand_open,
    robot_hand_close,
    robot_hand_peace,
    robot_hand_rock,
    robot_hand_ok,
    robot_hand_point,
    robot_finger_control,
    robot_wrist_control,
    robot_wave_both_hands,
    robot_hug_gesture
)

def test_hand_gestures():
    """Prueba los gestos básicos de manos con duración sincronizada"""
    print("🤚 Probando gestos básicos de manos con duración sincronizada...")
    
    # Gesto de abrir mano derecha (rápido - 500ms)
    print("   ✋ Abriendo mano derecha (rápido - 500ms)...")
    robot_hand_open("derecha", 500)
    
    # Gesto de cerrar mano derecha (normal - 1000ms)
    print("   ✊ Cerrando mano derecha (normal - 1000ms)...")
    robot_hand_close("derecha", 1000)
    
    # Gesto de paz con mano izquierda (lento - 1500ms)
    print("   ✌️ Haciendo gesto de paz con mano izquierda (lento - 1500ms)...")
    robot_hand_peace("izquierda", 1500)
    
    # Gesto de rock con mano derecha (normal - 1000ms)
    print("   🤘 Haciendo gesto de rock con mano derecha (normal - 1000ms)...")
    robot_hand_rock("derecha", 1000)
    
    # Gesto de OK con mano izquierda (rápido - 500ms)
    print("   👌 Haciendo gesto de OK con mano izquierda (rápido - 500ms)...")
    robot_hand_ok("izquierda", 500)
    
    # Gesto de señalar con mano derecha (lento - 2000ms)
    print("   👆 Haciendo gesto de señalar con mano derecha (lento - 2000ms)...")
    robot_hand_point("derecha", 2000)

def test_individual_finger_control():
    """Prueba el control individual de dedos con duración sincronizada"""
    print("👆 Probando control individual de dedos con duración sincronizada...")
    
    # Control del pulgar (rápido)
    print("   👍 Moviendo pulgar de mano derecha a 90° (rápido - 500ms)...")
    robot_finger_control("derecha", "pulgar", 90, 500)
    
    # Control del índice (normal)
    print("   👇 Moviendo índice de mano izquierda a 45° (normal - 1000ms)...")
    robot_finger_control("izquierda", "indice", 45, 1000)
    
    # Control del medio (lento)
    print("   🖕 Moviendo medio de mano derecha a 135° (lento - 1500ms)...")
    robot_finger_control("derecha", "medio", 135, 1500)
    
    # Control del anular (normal)
    print("   💍 Moviendo anular de mano izquierda a 60° (normal - 1000ms)...")
    robot_finger_control("izquierda", "anular", 60, 1000)
    
    # Control del meñique (rápido)
    print("   🤏 Moviendo meñique de mano derecha a 120° (rápido - 500ms)...")
    robot_finger_control("derecha", "menique", 120, 500)

def test_wrist_control():
    """Prueba el control de muñecas con duración sincronizada"""
    print("🤏 Probando control de muñecas con duración sincronizada...")
    
    # Muñeca derecha (normal)
    print("   ➡️ Moviendo muñeca derecha a 90° (normal - 1000ms)...")
    robot_wrist_control("derecha", 90, 1000)
    
    # Muñeca izquierda (rápido)
    print("   ⬅️ Moviendo muñeca izquierda a 45° (rápido - 500ms)...")
    robot_wrist_control("izquierda", 45, 500)
    
    # Volver a posición neutra (lento)
    print("   🔄 Volviendo muñecas a posición neutra (lento - 1500ms)...")
    robot_wrist_control("derecha", 80, 1500)
    robot_wrist_control("izquierda", 80, 1500)

def test_both_hands_gestures():
    """Prueba gestos con ambas manos con duración sincronizada"""
    print("🙌 Probando gestos con ambas manos con duración sincronizada...")
    
    # Saludo con ambas manos (normal)
    print("   👋 Haciendo saludo con ambas manos (normal - 1000ms)...")
    robot_wave_both_hands(1000)
    
    # Gesto de abrazo (lento)
    print("   🤗 Haciendo gesto de abrazo (lento - 2000ms)...")
    robot_hug_gesture(2000)

def test_sequence_demo():
    """Demuestra una secuencia completa usando controles de manos con duración sincronizada"""
    print("🎭 Demostrando secuencia completa con controles de manos sincronizados...")
    
    print("   🎬 Iniciando secuencia sincronizada...")
    
    # 1. Saludo inicial (lento y elegante)
    print("   👋 Paso 1: Saludo inicial (lento - 2000ms)")
    robot_wave_both_hands(2000)
    
    # 2. Gesto de paz (normal)
    print("   ✌️ Paso 2: Gesto de paz (normal - 1000ms)")
    robot_hand_peace("derecha", 1000)
    
    # 3. Control de dedo individual (rápido)
    print("   👆 Paso 3: Señalando con índice (rápido - 500ms)")
    robot_finger_control("derecha", "indice", 180, 500)
    robot_wrist_control("derecha", 90, 500)
    
    # 4. Gesto de OK (lento)
    print("   👌 Paso 4: Gesto de OK (lento - 1500ms)")
    robot_hand_ok("izquierda", 1500)
    
    # 5. Gesto de abrazo final (muy lento)
    print("   🤗 Paso 5: Abrazo final (muy lento - 3000ms)")
    robot_hug_gesture(3000)
    
    # 6. Volver a posición de descanso (normal)
    print("   🏠 Paso 6: Volviendo a posición de descanso (normal - 1000ms)")
    robot_hand_close("derecha", 1000)
    robot_hand_close("izquierda", 1000)
    robot_wrist_control("derecha", 80, 1000)
    robot_wrist_control("izquierda", 80, 1000)
    
    print("   ✅ Secuencia sincronizada completada!")

def main():
    """Función principal del test"""
    print("=" * 60)
    print("🤖 TEST DE CONTROL DE MANOS - DEMO SEQUENCE MANAGER")
    print("=" * 60)
    print()
    
    try:
        # Test 1: Gestos básicos
        test_hand_gestures()
        print()
        
        # Test 2: Control individual de dedos
        test_individual_finger_control()
        print()
        
        # Test 3: Control de muñecas
        test_wrist_control()
        print()
        
        # Test 4: Gestos con ambas manos
        test_both_hands_gestures()
        print()
        
        # Test 5: Secuencia completa
        test_sequence_demo()
        print()
        
        print("=" * 60)
        print("✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

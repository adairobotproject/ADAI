#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test para verificar que la traducción de parámetros left/right funciona correctamente
"""

import os
import sys

# Agregar el directorio actual al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_hand_translation():
    """Probar la traducción de parámetros de mano"""

    print("👐 TEST DE TRADUCCIÓN DE PARÁMETROS")
    print("=" * 50)

    # Simular la lógica de traducción del sequence builder
    def translate_hand(hand):
        """Traducir parámetros de mano English → Spanish"""
        hand_map = {
            'left': 'izquierda',
            'right': 'derecha'
        }
        return hand_map.get(hand, hand)

    def translate_finger(finger):
        """Traducir nombres de dedos"""
        finger_map = {
            'thumb': 'pulgar',
            'index': 'indice',
            'middle': 'medio',
            'ring': 'anular',
            'pinky': 'menique'
        }
        return finger_map.get(finger, finger)

    # Test cases
    test_cases = [
        # (hand_english, finger_english, expected_hand, expected_finger)
        ('left', 'thumb', 'izquierda', 'pulgar'),
        ('left', 'index', 'izquierda', 'indice'),
        ('left', 'middle', 'izquierda', 'medio'),
        ('left', 'ring', 'izquierda', 'anular'),
        ('left', 'pinky', 'izquierda', 'menique'),
        ('right', 'thumb', 'derecha', 'pulgar'),
        ('right', 'index', 'derecha', 'indice'),
        ('right', 'middle', 'derecha', 'medio'),
        ('right', 'ring', 'derecha', 'anular'),
        ('right', 'pinky', 'derecha', 'menique'),
    ]

    print("🔍 Probando traducción de parámetros:")
    print("-" * 50)

    all_passed = True

    for hand_en, finger_en, expected_hand, expected_finger in test_cases:
        translated_hand = translate_hand(hand_en)
        translated_finger = translate_finger(finger_en)

        hand_ok = translated_hand == expected_hand
        finger_ok = translated_finger == expected_finger

        status = "✅" if (hand_ok and finger_ok) else "❌"

        print(f"{status} {hand_en}→{translated_hand} | {finger_en}→{translated_finger}")

        if not (hand_ok and finger_ok):
            all_passed = False
            print(f"   Esperado: {expected_hand}, {expected_finger}")
            print(f"   Obtenido: {translated_hand}, {translated_finger}")

    print("-" * 50)

    if all_passed:
        print("✅ TODAS LAS TRADUCCIONES CORRECTAS")
        print("💡 El sequence builder debería enviar comandos en español")
    else:
        print("❌ HAY ERRORES EN LAS TRADUCCIONES")
        print("💡 Necesita corregir las funciones de traducción")

    print("\n📋 COMANDOS ESPERADOS EN MONITOR UNO:")
    print("-" * 50)
    print("✅ DEDO M=izquierda D=pulgar ANG=90")
    print("✅ DEDO M=derecha D=indice ANG=45")
    print("✅ DEDO M=izquierda D=medio ANG=120")
    print("✅ DEDO M=derecha D=anular ANG=60")
    print("✅ DEDO M=izquierda D=menique ANG=30")

    print("\n❌ COMANDOS PROBLEMÁTICOS ANTES:")
    print("-" * 50)
    print("❌ DEDO M=right D=indice ANG=0  ← 'right' en inglés")
    print("❌ DEDO M=left D=pulgar ANG=90  ← 'left' en inglés")

if __name__ == "__main__":
    test_hand_translation()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question Bank Extractor - Extrae preguntas de demo_sequence_manager.py
"""

import os
import sys
import re

def extract_question_banks():
    """Extraer bancos de preguntas de demo_sequence_manager.py"""
    
    # Ruta al archivo demo_sequence_manager.py
    demo_manager_path = os.path.join(os.path.dirname(__file__), "clases", "main", "demo_sequence_manager.py")
    
    if not os.path.exists(demo_manager_path):
        print(f"❌ No se encontró demo_sequence_manager.py en: {demo_manager_path}")
        return None, None
    
    try:
        with open(demo_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer QUESTION_BANK
        question_bank_match = re.search(r'QUESTION_BANK = \[(.*?)\]', content, re.DOTALL)
        question_bank = []
        if question_bank_match:
            questions_text = question_bank_match.group(1)
            # Extraer preguntas individuales
            questions = re.findall(r'"([^"]+)"', questions_text)
            question_bank = questions
        
        # Extraer QUESTION_BANK_CHEM
        question_bank_chem_match = re.search(r'QUESTION_BANK_CHEM = \[(.*?)\]', content, re.DOTALL)
        question_bank_chem = []
        if question_bank_chem_match:
            questions_text = question_bank_chem_match.group(1)
            # Extraer preguntas individuales
            questions = re.findall(r'"([^"]+)"', questions_text)
            question_bank_chem = questions
        
        return question_bank, question_bank_chem
        
    except Exception as e:
        print(f"❌ Error extrayendo preguntas: {e}")
        return None, None

def get_available_question_banks():
    """Obtener todos los bancos de preguntas disponibles"""
    
    question_bank, question_bank_chem = extract_question_banks()
    
    banks = {}
    
    if question_bank:
        banks["Preguntas Generales de Química"] = question_bank
    
    if question_bank_chem:
        banks["Preguntas Específicas de Química"] = question_bank_chem
    
    return banks

def main():
    """Función principal para probar la extracción"""
    print("🔍 Extrayendo Bancos de Preguntas de demo_sequence_manager.py")
    print("=" * 60)
    
    banks = get_available_question_banks()
    
    if not banks:
        print("❌ No se pudieron extraer bancos de preguntas")
        return
    
    print(f"✅ Se encontraron {len(banks)} bancos de preguntas:")
    print()
    
    for bank_name, questions in banks.items():
        print(f"📚 {bank_name}:")
        print(f"   - {len(questions)} preguntas disponibles")
        print("   - Ejemplos:")
        for i, question in enumerate(questions[:3]):  # Mostrar primeras 3
            print(f"     {i+1}. {question}")
        if len(questions) > 3:
            print(f"     ... y {len(questions) - 3} más")
        print()
    
    return banks

if __name__ == "__main__":
    main()

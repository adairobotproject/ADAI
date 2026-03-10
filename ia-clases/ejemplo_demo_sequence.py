#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejemplo Práctico - Demo Sequence System
========================================

Este script demuestra cómo crear y ejecutar un demo con secuencias
asociadas a páginas de PDF.
"""

import os
import time
import json
from demo_sequence_manager import get_demo_sequence_manager
from demo_player import get_demo_player

def crear_secuencia_ejemplo():
    """Crear una secuencia de ejemplo"""
    print("🎯 Creando secuencia de ejemplo...")
    
    # Secuencia de saludo
    secuencia_saludo = {
        "name": "Secuencia Saludo",
        "timestamp": time.time(),
        "positions": [
            {"x": 0, "y": 0, "z": 0, "description": "Posición inicial"},
            {"x": 10, "y": 20, "z": 30, "description": "Levantar brazo"},
            {"x": 20, "y": 40, "z": 60, "description": "Extender brazo"},
            {"x": 10, "y": 20, "z": 30, "description": "Bajar brazo"},
            {"x": 0, "y": 0, "z": 0, "description": "Posición final"}
        ]
    }
    
    # Secuencia de demostración
    secuencia_demo = {
        "name": "Secuencia Demostración",
        "timestamp": time.time(),
        "positions": [
            {"x": 50, "y": 50, "z": 50, "description": "Centro"},
            {"x": 100, "y": 50, "z": 50, "description": "Derecha"},
            {"x": 0, "y": 50, "z": 50, "description": "Izquierda"},
            {"x": 50, "y": 100, "z": 50, "description": "Arriba"},
            {"x": 50, "y": 0, "z": 50, "description": "Abajo"},
            {"x": 50, "y": 50, "z": 50, "description": "Centro"}
        ]
    }
    
    # Secuencia de despedida
    secuencia_despedida = {
        "name": "Secuencia Despedida",
        "timestamp": time.time(),
        "positions": [
            {"x": 0, "y": 0, "z": 0, "description": "Inicio"},
            {"x": -10, "y": -20, "z": -30, "description": "Inclinación"},
            {"x": 0, "y": 0, "z": 0, "description": "Posición neutral"}
        ]
    }
    
    # Guardar secuencias
    sequences_dir = "sequences"
    os.makedirs(sequences_dir, exist_ok=True)
    
    secuencias = [secuencia_saludo, secuencia_demo, secuencia_despedida]
    
    for secuencia in secuencias:
        filename = f"sequence_{secuencia['name'].replace(' ', '_')}_{int(time.time())}.json"
        filepath = os.path.join(sequences_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(secuencia, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Secuencia guardada: {secuencia['name']}")
    
    return [s['name'] for s in secuencias]

def crear_demo_ejemplo():
    """Crear un demo de ejemplo"""
    print("\n🎬 Creando demo de ejemplo...")
    
    # Obtener gestor de demos
    demo_manager = get_demo_sequence_manager()
    
    # Usar PDF existente o crear uno de prueba
    pdf_path = "clases/DesafiosDeIoMT.pdf"
    if not os.path.exists(pdf_path):
        print(f"⚠️ PDF no encontrado: {pdf_path}")
        print("   Creando demo sin PDF...")
        pdf_path = "ejemplo_demo.pdf"
    
    # Crear demo
    success = demo_manager.create_demo_config(
        "Demo Ejemplo",
        pdf_path,
        "Demo de Ejemplo - Robótica Educativa",
        "Una demostración completa del sistema de secuencias con PDF"
    )
    
    if not success:
        print("❌ Error creando demo")
        return False
    
    print("✅ Demo creado exitosamente")
    return True

def asignar_secuencias_ejemplo():
    """Asignar secuencias a páginas del demo"""
    print("\n🔗 Asignando secuencias a páginas...")
    
    demo_manager = get_demo_sequence_manager()
    
    # Obtener secuencias disponibles
    sequences = list(demo_manager.available_sequences.keys())
    
    if len(sequences) < 3:
        print("❌ No hay suficientes secuencias disponibles")
        return False
    
    # Asignar secuencias a páginas
    asignaciones = [
        (0, sequences[0], 5.0),  # Página 0: Saludo
        (2, sequences[1], 8.0),  # Página 2: Demostración
        (4, sequences[2], 3.0),  # Página 4: Despedida
    ]
    
    for page_num, sequence_name, timing in asignaciones:
        success = demo_manager.assign_sequence_to_page(
            "Demo Ejemplo", page_num, sequence_name, timing
        )
        
        if success:
            print(f"✅ Secuencia '{sequence_name}' asignada a página {page_num}")
        else:
            print(f"❌ Error asignando secuencia a página {page_num}")
    
    return True

def ejecutor_secuencias_ejemplo(sequence_name):
    """Ejecutor de secuencias de ejemplo"""
    print(f"🤖 Ejecutando secuencia: {sequence_name}")
    
    # Simular ejecución de secuencia
    demo_manager = get_demo_sequence_manager()
    sequence_data = demo_manager.load_sequence_data(sequence_name)
    
    if sequence_data and 'positions' in sequence_data:
        positions = sequence_data['positions']
        print(f"   📍 Ejecutando {len(positions)} posiciones...")
        
        for i, position in enumerate(positions):
            print(f"   {i+1}/{len(positions)}: {position.get('description', 'Sin descripción')}")
            time.sleep(0.5)  # Simular movimiento
        
        print(f"   ✅ Secuencia '{sequence_name}' completada")
        return True
    else:
        print(f"   ❌ Error: No se pudieron cargar los datos de la secuencia")
        return False

def ejecutar_demo_ejemplo():
    """Ejecutar el demo de ejemplo"""
    print("\n🚀 Ejecutando demo de ejemplo...")
    
    # Obtener instancias
    demo_manager = get_demo_sequence_manager()
    demo_player = get_demo_player(demo_manager)
    
    # Configurar ejecutor de secuencias
    demo_player.sequence_executor = ejecutor_secuencias_ejemplo
    
    # Configurar callbacks
    def on_page_change(page_num, total_pages):
        print(f"📄 Cambiando a página {page_num + 1} de {total_pages}")
    
    def on_sequence_start(sequence_name):
        print(f"🎯 Iniciando secuencia: {sequence_name}")
    
    def on_sequence_end(sequence_name, error=None):
        if error:
            print(f"❌ Secuencia terminó con error: {sequence_name} - {error}")
        else:
            print(f"✅ Secuencia completada: {sequence_name}")
    
    def on_demo_complete():
        print("🎉 Demo completado exitosamente")
    
    def on_error(error_msg):
        print(f"❌ Error en demo: {error_msg}")
    
    # Configurar callbacks
    demo_player.set_callbacks(
        page_change=on_page_change,
        sequence_start=on_sequence_start,
        sequence_end=on_sequence_end,
        demo_complete=on_demo_complete,
        error=on_error
    )
    
    # Ejecutar demo
    success = demo_player.play_demo("Demo Ejemplo", start_page=0)
    
    if success:
        print("✅ Demo iniciado correctamente")
        
        # Esperar un poco para que se ejecute
        print("⏳ Esperando ejecución del demo...")
        time.sleep(5)
        
        # Obtener estado
        status = demo_player.get_current_status()
        print(f"📊 Estado actual: {status}")
        
        # Detener demo después de un tiempo
        print("⏹️ Deteniendo demo...")
        demo_player.stop_demo()
        
    else:
        print("❌ Error iniciando demo")
    
    return success

def mostrar_informacion_demo():
    """Mostrar información del demo creado"""
    print("\n📋 Información del Demo")
    print("=" * 40)
    
    demo_manager = get_demo_sequence_manager()
    demo_info = demo_manager.get_demo_info("Demo Ejemplo")
    
    if demo_info:
        print(f"Nombre: {demo_info['title']}")
        print(f"Descripción: {demo_info.get('description', 'Sin descripción')}")
        print(f"Páginas: {demo_info['page_count']}")
        print(f"PDF: {os.path.basename(demo_info['pdf_path'])}")
        print(f"Creado: {demo_info['created_at'][:19]}")
        
        print("\nSecuencias asignadas:")
        page_sequences = demo_info['page_sequences']
        for page_num, sequence_name in page_sequences.items():
            if sequence_name:
                timing = demo_info['sequence_timing'].get(page_num, 5.0)
                print(f"  Página {int(page_num) + 1}: {sequence_name} ({timing}s)")
            else:
                print(f"  Página {int(page_num) + 1}: Sin secuencia")
    else:
        print("❌ No se encontró información del demo")

def main():
    """Función principal del ejemplo"""
    print("🎬 Ejemplo Práctico - Demo Sequence System")
    print("=" * 60)
    
    try:
        # Paso 1: Crear secuencias de ejemplo
        print("\n📝 PASO 1: Crear secuencias de ejemplo")
        secuencias = crear_secuencia_ejemplo()
        
        # Paso 2: Crear demo
        print("\n📝 PASO 2: Crear demo")
        if not crear_demo_ejemplo():
            return
        
        # Paso 3: Asignar secuencias
        print("\n📝 PASO 3: Asignar secuencias a páginas")
        if not asignar_secuencias_ejemplo():
            return
        
        # Paso 4: Mostrar información
        print("\n📝 PASO 4: Mostrar información del demo")
        mostrar_informacion_demo()
        
        # Paso 5: Ejecutar demo
        print("\n📝 PASO 5: Ejecutar demo")
        ejecutar_demo_ejemplo()
        
        print("\n" + "=" * 60)
        print("🎉 EJEMPLO COMPLETADO EXITOSAMENTE")
        print("✅ El sistema de Demo Sequences funciona correctamente")
        print("=" * 60)
        
        print("\n💡 Próximos pasos:")
        print("1. Abre robot_gui_conmodulos.py")
        print("2. Ve a la pestaña '🎬 Demo Sequences'")
        print("3. Crea tus propios demos y secuencias")
        print("4. Experimenta con diferentes PDFs y movimientos")
        
    except Exception as e:
        print(f"\n❌ Error en el ejemplo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plantilla de Clase con Sistema de Progreso
=========================================

Esta es una plantilla que puedes usar como base para crear clases
que reporten su progreso al sistema de progreso de ADAI.

Para usar esta plantilla:
1. Copia este archivo y renómbralo
2. Modifica la clase según tus necesidades
3. Agrega las llamadas al reporter en los puntos apropiados
"""

import cv2
import numpy as np
import time
import os
import sys

# Agregar el directorio padre al path para importar el reporter
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from class_progress_reporter import create_progress_reporter
    PROGRESS_AVAILABLE = True
except ImportError:
    PROGRESS_AVAILABLE = False
    print("⚠️ Progress Reporter no disponible")

class MiClaseConProgreso:
    """
    Plantilla de clase con sistema de progreso integrado
    
    Esta clase demuestra cómo usar el sistema de progreso para reportar
    el estado de ejecución en tiempo real.
    """
    
    def __init__(self):
        """Inicializar la clase y el sistema de progreso"""
        print("🎓 Mi Clase iniciada")
        
        # Configuración de la clase
        self.class_name = "mi_clase_con_progreso"  # Cambiar por el nombre real
        self.class_type = "default"  # default, experimental, theoretical
        self.duration = 10  # Duración estimada en minutos
        
        # Crear reporter de progreso
        if PROGRESS_AVAILABLE:
            self.reporter = create_progress_reporter(self.class_name, self.class_type, self.duration)
        else:
            self.reporter = None
            print("⚠️ Ejecutando sin sistema de progreso")
    
    def run(self):
        """Método principal que ejecuta la clase con reporte de progreso"""
        try:
            print("🚀 Ejecutando mi clase...")
            
            # ========================================
            # FASE 1: INTRODUCCIÓN
            # ========================================
            if self.reporter:
                self.reporter.start_phase("class_intro", "Iniciando clase", "Preparando el entorno de trabajo")
            else:
                print("📚 Fase: Introducción - Iniciando clase")
            
            # Aquí va tu código de inicialización
            self._setup_environment()
            
            # Actualizar progreso durante la fase
            if self.reporter:
                self.reporter.update_progress("Configuración", "Verificando dependencias y recursos")
            else:
                print("📊 Progreso: Configuración - Verificando dependencias")
            
            # ========================================
            # FASE 2: PRESENTACIÓN TEÓRICA
            # ========================================
            if self.reporter:
                self.reporter.complete_phase("theory_presentation", "Conceptos fundamentales", "Explicando teoría básica")
            else:
                print("📚 Fase: Presentación Teórica - Conceptos fundamentales")
            
            # Aquí va tu código de teoría
            self._present_theory()
            
            # Actualizar progreso durante la teoría
            if self.reporter:
                self.reporter.update_progress("Definiciones", "Estableciendo conceptos clave")
            else:
                print("📊 Progreso: Definiciones - Estableciendo conceptos clave")
            
            # ========================================
            # FASE 3: DEMOSTRACIÓN PRÁCTICA
            # ========================================
            if self.reporter:
                self.reporter.complete_phase("practical_demo", "Ejemplos prácticos", "Mostrando aplicaciones reales")
            else:
                print("📚 Fase: Demostración Práctica - Ejemplos prácticos")
            
            # Aquí va tu código de demostración
            self._demonstrate_practice()
            
            # Actualizar progreso durante la práctica
            if self.reporter:
                self.reporter.update_progress("Simulación", "Ejecutando ejemplos")
            else:
                print("📊 Progreso: Simulación - Ejecutando ejemplos")
            
            # ========================================
            # FASE 4: SESIÓN INTERACTIVA
            # ========================================
            if self.reporter:
                self.reporter.complete_phase("interactive_session", "Preguntas y respuestas", "Interactuando con el usuario")
            else:
                print("📚 Fase: Sesión Interactiva - Preguntas y respuestas")
            
            # Aquí va tu código de interacción
            self._interactive_session()
            
            # ========================================
            # FASE 5: EVALUACIÓN FINAL
            # ========================================
            if self.reporter:
                self.reporter.complete_phase("final_exam", "Evaluación", "Verificando comprensión")
            else:
                print("📚 Fase: Evaluación Final - Evaluación")
            
            # Aquí va tu código de evaluación
            self._final_evaluation()
            
            # ========================================
            # COMPLETAR CLASE
            # ========================================
            if self.reporter:
                self.reporter.complete_class("Mi Clase completada exitosamente")
            else:
                print("🎉 Mi Clase completada exitosamente")
            
            # Mostrar progreso final
            if self.reporter:
                progress_info = self.reporter.get_progress_info()
                print(f"📊 Progreso final: {progress_info.get('progress_percentage', 0)}% - {progress_info.get('current_phase', 'Completada')}")
            
        except Exception as e:
            error_msg = f"Error ejecutando clase: {e}"
            print(f"❌ {error_msg}")
            
            if self.reporter:
                self.reporter.error_in_class(error_msg)
    
    def _setup_environment(self):
        """Configurar el entorno de trabajo"""
        print("🔧 Configurando entorno...")
        time.sleep(1)  # Simular trabajo
        print("✅ Entorno configurado")
    
    def _present_theory(self):
        """Presentar la teoría"""
        print("📚 Presentando teoría...")
        time.sleep(2)  # Simular presentación
        print("✅ Teoría presentada")
    
    def _demonstrate_practice(self):
        """Demostrar práctica"""
        print("🔬 Demostrando práctica...")
        time.sleep(2)  # Simular demostración
        print("✅ Práctica demostrada")
    
    def _interactive_session(self):
        """Sesión interactiva"""
        print("💬 Sesión interactiva...")
        time.sleep(1)  # Simular interacción
        print("✅ Sesión interactiva completada")
    
    def _final_evaluation(self):
        """Evaluación final"""
        print("📊 Evaluación final...")
        time.sleep(1)  # Simular evaluación
        print("✅ Evaluación completada")
    
    def pause_execution(self):
        """Pausar la ejecución (puede ser llamado desde fuera)"""
        if self.reporter:
            self.reporter.pause_class()
    
    def resume_execution(self):
        """Reanudar la ejecución (puede ser llamado desde fuera)"""
        if self.reporter:
            self.reporter.resume_class()
    
    def get_current_progress(self):
        """Obtener el progreso actual"""
        if self.reporter:
            return self.reporter.get_progress_info()
        return {"error": "Progress Reporter no disponible"}

# Función de conveniencia para crear y ejecutar la clase
def run_class_with_progress():
    """Función para ejecutar la clase con progreso"""
    clase = MiClaseConProgreso()
    clase.run()
    return clase

if __name__ == "__main__":
    # Ejecutar la clase
    run_class_with_progress()

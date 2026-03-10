#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Class Progress Manager - Sistema de progreso de clases
====================================================

Gestiona el progreso de las clases para mostrar en qué parte se encuentra el usuario
tanto en robot_gui como en la app móvil.
"""

import os
import json
import datetime
import threading
import time
from typing import Dict, List, Optional, Callable
from enum import Enum

class ClassPhase(Enum):
    """Fases estándar de una clase ADAI"""
    NOT_STARTED = "not_started"
    DIAGNOSTIC_TEST = "diagnostic_test"
    CLASS_INTRO = "class_intro"
    THEORY_PRESENTATION = "theory_presentation"
    PRACTICAL_DEMO = "practical_demo"
    INTERACTIVE_SESSION = "interactive_session"
    FINAL_EXAM = "final_exam"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"

class ClassProgressManager:
    """Gestor de progreso de clases"""
    
    def __init__(self):
        self.current_class = None
        self.current_phase = ClassPhase.NOT_STARTED
        self.progress_percentage = 0
        self.start_time = None
        self.estimated_duration = 0
        self.elapsed_time = 0
        self.remaining_time = 0
        
        # Información detallada de la fase actual
        self.current_phase_info = {
            "name": "",
            "description": "",
            "step": 0,
            "total_steps": 0,
            "sub_phase": "",
            "details": ""
        }
        
        # Callbacks para notificar cambios
        self.on_progress_update: Optional[Callable] = None
        self.on_phase_change: Optional[Callable] = None
        self.on_class_complete: Optional[Callable] = None
        
        # Thread para actualizar tiempo
        self.update_thread = None
        self.running = False
        
        # Historial de fases
        self.phase_history = []
        
        # Configuración de fases por tipo de clase
        self.class_phase_configs = {
            "default": [
                {"phase": ClassPhase.DIAGNOSTIC_TEST, "name": "Prueba Diagnóstica", "duration": 5, "description": "Evaluación inicial del conocimiento"},
                {"phase": ClassPhase.CLASS_INTRO, "name": "Introducción", "duration": 3, "description": "Presentación del tema y objetivos"},
                {"phase": ClassPhase.THEORY_PRESENTATION, "name": "Presentación Teórica", "duration": 20, "description": "Explicación de conceptos fundamentales"},
                {"phase": ClassPhase.PRACTICAL_DEMO, "name": "Demostración Práctica", "duration": 15, "description": "Ejemplos y aplicaciones prácticas"},
                {"phase": ClassPhase.INTERACTIVE_SESSION, "name": "Sesión Interactiva", "duration": 10, "description": "Participación y preguntas"},
                {"phase": ClassPhase.FINAL_EXAM, "name": "Examen Final", "duration": 7, "description": "Evaluación final del aprendizaje"}
            ],
            "experimental": [
                {"phase": ClassPhase.DIAGNOSTIC_TEST, "name": "Prueba Diagnóstica", "duration": 5, "description": "Evaluación inicial"},
                {"phase": ClassPhase.CLASS_INTRO, "name": "Introducción al Experimento", "duration": 5, "description": "Objetivos y materiales"},
                {"phase": ClassPhase.THEORY_PRESENTATION, "name": "Teoría y Seguridad", "duration": 10, "description": "Conceptos y medidas de seguridad"},
                {"phase": ClassPhase.PRACTICAL_DEMO, "name": "Fases del Experimento", "duration": 25, "description": "Ejecución paso a paso"},
                {"phase": ClassPhase.INTERACTIVE_SESSION, "name": "Observación y Registro", "duration": 10, "description": "Análisis de resultados"},
                {"phase": ClassPhase.FINAL_EXAM, "name": "Evaluación Final", "duration": 5, "description": "Comprensión del experimento"}
            ],
            "theoretical": [
                {"phase": ClassPhase.DIAGNOSTIC_TEST, "name": "Prueba Diagnóstica", "duration": 5, "description": "Evaluación inicial"},
                {"phase": ClassPhase.CLASS_INTRO, "name": "Introducción", "duration": 5, "description": "Presentación del tema"},
                {"phase": ClassPhase.THEORY_PRESENTATION, "name": "Desarrollo Teórico", "duration": 25, "description": "Explicación de conceptos"},
                {"phase": ClassPhase.PRACTICAL_DEMO, "name": "Ejemplos Prácticos", "duration": 10, "description": "Aplicaciones y casos"},
                {"phase": ClassPhase.INTERACTIVE_SESSION, "name": "Discusión", "duration": 10, "description": "Preguntas y respuestas"},
                {"phase": ClassPhase.FINAL_EXAM, "name": "Evaluación", "duration": 5, "description": "Comprensión del tema"}
            ]
        }
    
    def start_class(self, class_name: str, class_type: str = "default", duration: int = 60):
        """Iniciar una nueva clase"""
        self.current_class = class_name
        self.current_phase = ClassPhase.NOT_STARTED
        self.progress_percentage = 0
        self.start_time = datetime.datetime.now()
        self.estimated_duration = duration
        self.elapsed_time = 0
        self.remaining_time = duration
        self.phase_history = []
        
        # Configurar fases según el tipo de clase
        self.class_phases = self.class_phase_configs.get(class_type, self.class_phase_configs["default"])
        
        # Iniciar thread de actualización
        self.running = True
        self.update_thread = threading.Thread(target=self._update_time_thread, daemon=True)
        self.update_thread.start()
        
        print(f"🎓 Iniciando clase: {class_name}")
        self._notify_progress_update()
    
    def set_phase(self, phase: ClassPhase, sub_phase: str = "", details: str = ""):
        """Establecer la fase actual de la clase"""
        if self.current_class is None:
            return
        
        # Registrar cambio de fase
        if self.current_phase != ClassPhase.NOT_STARTED:
            self.phase_history.append({
                "phase": self.current_phase.value,
                "duration": self.elapsed_time,
                "timestamp": datetime.datetime.now().isoformat()
            })
        
        self.current_phase = phase
        
        # Actualizar información de la fase
        phase_config = next((p for p in self.class_phases if p["phase"] == phase), None)
        if phase_config:
            self.current_phase_info = {
                "name": phase_config["name"],
                "description": phase_config["description"],
                "step": self._get_phase_step(phase),
                "total_steps": len(self.class_phases),
                "sub_phase": sub_phase,
                "details": details
            }
        
        # Calcular progreso
        self._calculate_progress()
        
        print(f"📚 Fase actual: {self.current_phase_info['name']} - {sub_phase}")
        self._notify_phase_change()
        self._notify_progress_update()
    
    def update_sub_phase(self, sub_phase: str, details: str = ""):
        """Actualizar sub-fase actual"""
        self.current_phase_info["sub_phase"] = sub_phase
        self.current_phase_info["details"] = details
        self._notify_progress_update()
    
    def pause_class(self):
        """Pausar la clase"""
        self.current_phase = ClassPhase.PAUSED
        self._notify_progress_update()
        print("⏸️ Clase pausada")
    
    def resume_class(self):
        """Reanudar la clase"""
        if self.current_phase == ClassPhase.PAUSED:
            # Restaurar la última fase activa
            if self.phase_history:
                last_phase = self.phase_history[-1]["phase"]
                self.current_phase = ClassPhase(last_phase)
            else:
                self.current_phase = ClassPhase.CLASS_INTRO
            self._notify_progress_update()
            print("▶️ Clase reanudada")
    
    def complete_class(self):
        """Completar la clase"""
        self.current_phase = ClassPhase.COMPLETED
        self.progress_percentage = 100
        self.running = False
        self._notify_progress_update()
        self._notify_class_complete()
        print("✅ Clase completada")
    
    def error_in_class(self, error_message: str):
        """Marcar error en la clase"""
        self.current_phase = ClassPhase.ERROR
        self.current_phase_info["details"] = f"Error: {error_message}"
        self.running = False
        self._notify_progress_update()
        print(f"❌ Error en clase: {error_message}")
    
    def stop_class(self):
        """Detener la clase"""
        self.running = False
        self.current_class = None
        self.current_phase = ClassPhase.NOT_STARTED
        self.progress_percentage = 0
        print("🛑 Clase detenida")
    
    def get_progress_info(self) -> Dict:
        """Obtener información completa del progreso"""
        if self.current_class is None:
            return {
                "class_name": None,
                "phase": "not_started",
                "progress_percentage": 0,
                "elapsed_time": 0,
                "remaining_time": 0,
                "phase_info": {},
                "is_active": False
            }
        
        return {
            "class_name": self.current_class,
            "phase": self.current_phase.value,
            "progress_percentage": self.progress_percentage,
            "elapsed_time": self.elapsed_time,
            "remaining_time": self.remaining_time,
            "phase_info": self.current_phase_info,
            "is_active": self.running and self.current_phase not in [ClassPhase.COMPLETED, ClassPhase.ERROR],
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "estimated_duration": self.estimated_duration,
            "phase_history": self.phase_history
        }
    
    def get_progress_summary(self) -> Dict:
        """Obtener resumen del progreso para UI"""
        progress_info = self.get_progress_info()
        
        # Crear resumen visual
        phase_emoji = {
            "not_started": "⏳",
            "diagnostic_test": "📝",
            "class_intro": "🎯",
            "theory_presentation": "📚",
            "practical_demo": "🔬",
            "interactive_session": "💬",
            "final_exam": "📊",
            "completed": "✅",
            "paused": "⏸️",
            "error": "❌"
        }
        
        return {
            "class_name": progress_info["class_name"],
            "current_phase": progress_info["phase_info"].get("name", "No iniciada"),
            "phase_emoji": phase_emoji.get(progress_info["phase"], "❓"),
            "progress_percentage": progress_info["progress_percentage"],
            "elapsed_time": self._format_time(progress_info["elapsed_time"]),
            "remaining_time": self._format_time(progress_info["remaining_time"]),
            "sub_phase": progress_info["phase_info"].get("sub_phase", ""),
            "details": progress_info["phase_info"].get("details", ""),
            "step": progress_info["phase_info"].get("step", 0),
            "total_steps": progress_info["phase_info"].get("total_steps", 0),
            "is_active": progress_info["is_active"],
            "status": self._get_status_text(progress_info["phase"])
        }
    
    def _calculate_progress(self):
        """Calcular porcentaje de progreso"""
        if not self.class_phases:
            self.progress_percentage = 0
            return
        
        current_step = self._get_phase_step(self.current_phase)
        total_steps = len(self.class_phases)
        
        if current_step <= 0:
            self.progress_percentage = 0
        elif current_step >= total_steps:
            self.progress_percentage = 100
        else:
            # Calcular progreso basado en fases completadas
            completed_phases = current_step - 1
            self.progress_percentage = int((completed_phases / total_steps) * 100)
    
    def _get_phase_step(self, phase: ClassPhase) -> int:
        """Obtener el número de paso de una fase"""
        for i, phase_config in enumerate(self.class_phases):
            if phase_config["phase"] == phase:
                return i + 1
        return 0
    
    def _update_time_thread(self):
        """Thread para actualizar tiempo transcurrido"""
        while self.running:
            if self.start_time and self.current_phase not in [ClassPhase.PAUSED, ClassPhase.COMPLETED, ClassPhase.ERROR]:
                self.elapsed_time = int((datetime.datetime.now() - self.start_time).total_seconds())
                self.remaining_time = max(0, self.estimated_duration - self.elapsed_time)
                self._notify_progress_update()
            time.sleep(1)
    
    def _format_time(self, seconds: int) -> str:
        """Formatear tiempo en formato legible"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _get_status_text(self, phase: str) -> str:
        """Obtener texto de estado para la UI"""
        status_texts = {
            "not_started": "Listo para comenzar",
            "diagnostic_test": "Realizando prueba diagnóstica",
            "class_intro": "Introducción a la clase",
            "theory_presentation": "Presentación teórica",
            "practical_demo": "Demostración práctica",
            "interactive_session": "Sesión interactiva",
            "final_exam": "Evaluación final",
            "completed": "Clase completada",
            "paused": "Clase pausada",
            "error": "Error en la clase"
        }
        return status_texts.get(phase, "Estado desconocido")
    
    def _notify_progress_update(self):
        """Notificar actualización de progreso"""
        if self.on_progress_update:
            try:
                self.on_progress_update(self.get_progress_info())
            except Exception as e:
                print(f"Error en callback de progreso: {e}")
    
    def _notify_phase_change(self):
        """Notificar cambio de fase"""
        if self.on_phase_change:
            try:
                self.on_phase_change(self.current_phase, self.current_phase_info)
            except Exception as e:
                print(f"Error en callback de cambio de fase: {e}")
    
    def _notify_class_complete(self):
        """Notificar completación de clase"""
        if self.on_class_complete:
            try:
                self.on_class_complete(self.current_class, self.get_progress_info())
            except Exception as e:
                print(f"Error en callback de completación: {e}")

# Instancia global del gestor de progreso
_progress_manager = None

def get_progress_manager() -> ClassProgressManager:
    """Obtener instancia global del gestor de progreso"""
    global _progress_manager
    if _progress_manager is None:
        _progress_manager = ClassProgressManager()
    return _progress_manager

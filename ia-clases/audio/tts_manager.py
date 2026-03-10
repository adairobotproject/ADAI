"""
Módulo para manejar texto a voz (TTS)
"""
import pyttsx3
import threading
import time
from typing import Optional

class TTSManager:
    def __init__(self):
        """
        Inicializa el gestor de texto a voz.
        """
        self.engine = None
        self.initialize_tts()
    
    def initialize_tts(self):
        """Inicializa el motor de texto a voz."""
        try:
            self.engine = pyttsx3.init()
            
            # Configurar propiedades del motor
            voices = self.engine.getProperty('voices')
            if voices:
                # Usar la primera voz disponible
                self.engine.setProperty('voice', voices[0].id)
            
            # Configurar velocidad y volumen
            self.engine.setProperty('rate', 150)  # Palabras por minuto
            self.engine.setProperty('volume', 0.9)  # Volumen (0.0 a 1.0)
            
            print("✅ Motor TTS inicializado correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar TTS: {e}")
            self.engine = None
    
    def speak(self, text: str, block: bool = True):
        """
        Convierte texto a voz.
        
        Args:
            text: Texto a convertir a voz
            block: Si debe bloquear hasta terminar de hablar
        """
        if not self.engine:
            print("❌ Motor TTS no inicializado")
            return
        
        try:
            if block:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Ejecutar en un hilo separado para no bloquear
                thread = threading.Thread(target=self._speak_thread, args=(text,))
                thread.daemon = True
                thread.start()
        except Exception as e:
            print(f"❌ Error al hablar: {e}")
    
    def _speak_thread(self, text: str):
        """Hilo para hablar sin bloquear."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Error en hilo de TTS: {e}")
    
    def stop_speaking(self):
        """Detiene el habla actual."""
        if self.engine:
            try:
                self.engine.stop()
            except Exception as e:
                print(f"❌ Error al detener TTS: {e}")
    
    def set_rate(self, rate: int):
        """
        Establece la velocidad de habla.
        
        Args:
            rate: Palabras por minuto
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """
        Establece el volumen.
        
        Args:
            volume: Volumen (0.0 a 1.0)
        """
        if self.engine:
            self.engine.setProperty('volume', volume)
    
    def get_available_voices(self) -> list:
        """
        Obtiene las voces disponibles.
        
        Returns:
            list: Lista de voces disponibles
        """
        if self.engine:
            return self.engine.getProperty('voices')
        return []
    
    def set_voice(self, voice_id: str):
        """
        Establece la voz a usar.
        
        Args:
            voice_id: ID de la voz
        """
        if self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def cleanup(self):
        """Limpia los recursos del TTS."""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass

def speak_with_animation(tts_manager: TTSManager, text: str):
    """
    Habla con animación visual.
    
    Args:
        tts_manager: Gestor de TTS
        text: Texto a hablar
    """
    # Aquí se podría agregar animación visual mientras habla
    tts_manager.speak(text, block=False)
    
    # Simular tiempo de habla basado en la longitud del texto
    estimated_time = len(text.split()) * 0.5  # ~0.5 segundos por palabra
    time.sleep(min(estimated_time, 10))  # Máximo 10 segundos 
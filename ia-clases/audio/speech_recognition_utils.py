"""
Utilidades para reconocimiento de voz
"""
import speech_recognition as sr
import time
from typing import Optional, Tuple

class SpeechRecognitionManager:
    def __init__(self):
        """
        Inicializa el gestor de reconocimiento de voz.
        """
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.setup_microphone()
    
    def setup_microphone(self):
        """Configura el micrófono."""
        try:
            self.microphone = sr.Microphone()
            # Ajustar para el ruido ambiental
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Micrófono configurado correctamente")
        except Exception as e:
            print(f"❌ Error al configurar micrófono: {e}")
    
    def listen(self, timeout: int = 5, phrase_time_limit: Optional[int] = None) -> Tuple[Optional[str], bool]:
        """
        Escucha y reconoce voz.
        
        Args:
            timeout: Tiempo máximo de espera en segundos
            phrase_time_limit: Tiempo máximo de frase en segundos
            
        Returns:
            Tuple[Optional[str], bool]: (texto reconocido, si se reconoció correctamente)
        """
        if not self.microphone:
            print("❌ Micrófono no configurado")
            return None, False
        
        try:
            with self.microphone as source:
                print("🎤 Escuchando...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
            
            print("🔄 Procesando audio...")
            text = self.recognizer.recognize_google(audio, language='es-ES')
            print(f"✅ Reconocido: {text}")
            return text, True
            
        except sr.WaitTimeoutError:
            print("⏰ Tiempo de espera agotado")
            return None, False
        except sr.UnknownValueError:
            print("❓ No se pudo entender el audio")
            return None, False
        except sr.RequestError as e:
            print(f"❌ Error en el servicio de reconocimiento: {e}")
            return None, False
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return None, False
    
    def listen_for_keywords(self, keywords: list, timeout: int = 10) -> Tuple[Optional[str], bool]:
        """
        Escucha palabras clave específicas.
        
        Args:
            keywords: Lista de palabras clave a buscar
            timeout: Tiempo máximo de espera
            
        Returns:
            Tuple[Optional[str], bool]: (palabra clave encontrada, si se encontró)
        """
        text, success = self.listen(timeout=timeout)
        
        if success and text:
            text_lower = text.lower()
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return keyword, True
        
        return None, False
    
    def listen_for_yes_no(self, timeout: int = 5) -> Optional[bool]:
        """
        Escucha una respuesta de sí o no.
        
        Args:
            timeout: Tiempo máximo de espera
            
        Returns:
            Optional[bool]: True para sí, False para no, None si no se entendió
        """
        text, success = self.listen(timeout=timeout)
        
        if success and text:
            text_lower = text.lower()
            if any(word in text_lower for word in ['sí', 'si', 'yes', 'correcto', 'verdadero']):
                return True
            elif any(word in text_lower for word in ['no', 'false', 'incorrecto', 'falso']):
                return False
        
        return None
    
    def get_available_microphones(self) -> list:
        """
        Obtiene los micrófonos disponibles.
        
        Returns:
            list: Lista de micrófonos disponibles
        """
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            print(f"❌ Error al obtener micrófonos: {e}")
            return []
    
    def set_microphone(self, device_index: int):
        """
        Establece el micrófono a usar.
        
        Args:
            device_index: Índice del dispositivo de micrófono
        """
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print(f"✅ Micrófono cambiado al dispositivo {device_index}")
        except Exception as e:
            print(f"❌ Error al cambiar micrófono: {e}")

def listen_for_command(timeout: int = 5) -> Optional[str]:
    """
    Función de conveniencia para escuchar comandos.
    
    Args:
        timeout: Tiempo máximo de espera
        
    Returns:
        Optional[str]: Comando reconocido o None
    """
    recognizer = SpeechRecognitionManager()
    text, success = recognizer.listen(timeout=timeout)
    return text if success else None 
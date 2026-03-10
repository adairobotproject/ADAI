"""
Módulo de sistema de preguntas y evaluación para ADAI
===================================================

Contiene todas las funciones relacionadas con:
- Gestión de preguntas aleatorias
- Evaluación de respuestas de estudiantes
- Sistema de preguntas y respuestas
"""

import random
import openai
from .config import OPENAI_API_KEY, QUESTION_BANK, QUESTION_BANK_CHEM

# Configurar cliente OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def process_question(engine, current_users, known_faces, pdf_text, hand_raised_counter, current_hand_raiser):
    """
    Procesamiento de preguntas basado en la identificación de estudiantes
    """
    print("🤔 Procesando preguntas de usuarios...")
    
    try:
        # Determinar quién hizo la pregunta
        student_id = current_hand_raiser.value
        
        # Si no tenemos un ID concreto, preguntamos quién hizo la pregunta
        if student_id < 0 or student_id >= len(current_users):
            if len(current_users) > 1:
                from .speech import speak_with_animation, listen
                speak_with_animation(engine, "Alguien ha levantado la mano. ¿Quién desea preguntar?")
                name = listen()
                if name and name not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""] and name.lower() in [user.lower() for user in current_users]:
                    current_user = next(user for user in current_users if user.lower() == name.lower())
                else:
                    # Si no entendemos el nombre o no coincide, usamos el primer usuario
                    current_user = list(current_users)[0]
            else:
                current_user = list(current_users)[0]
        else:
            # Convertir el ID numérico al nombre del estudiante 
            if student_id < len(current_users):
                current_user = list(current_users)[student_id]
            else:
                # Si el ID está fuera de rango, usar el primer estudiante
                current_user = list(current_users)[0]
        
        from .speech import speak_with_animation, listen
        speak_with_animation(engine, f"Sí, {current_user}, ¿cuál es tu pregunta?")
        
        # Escuchar la pregunta con mejor manejo de errores
        question = listen(timeout=10)  # Aumentamos el timeout para preguntas
        hand_raised_counter.value = 0
        
        if not question or question in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
            if question and question.startswith("error"):
                speak_with_animation(engine, "Hubo un problema con el reconocimiento de voz. Continuemos con la clase.")
            else:
                speak_with_animation(engine, "No pude entender tu pregunta. Continuemos con la clase.")
            return True
        
        try:
            from .utils import ask_openai
            answer = ask_openai(question, pdf_text)
            speak_with_animation(engine, answer)
        except Exception as e:
            print(f"❌ Error al procesar la respuesta con OpenAI: {e}")
            speak_with_animation(engine, "Lo siento, tuve un problema al generar una respuesta. Continuemos con la clase.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en process_question: {e}")
        return False

def evaluate_student_answer(question, answer, context, student_name):
    """
    Función específica para evaluar respuestas de estudiantes
    Separada de ask_openai para evitar conflictos
    
    Args:
        question (str): Pregunta realizada
        answer (str): Respuesta del estudiante
        context (str): Contexto del material de clase
        student_name (str): Nombre del estudiante
        
    Returns:
        str: Evaluación de la respuesta
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Eres ADAI, un profesor robot amigable que evalúa respuestas de estudiantes sobre robótica médica. 
                
INSTRUCCIONES IMPORTANTES:
- NO uses asteriscos, guiones, viñetas, ni formato especial
- NO uses emojis ni símbolos especiales  
- Habla de manera natural como un profesor amigable
- Máximo 3 oraciones
- Si el estudiante dice "no sé", sé comprensivo y educativo
- NO digas palabras como "retroalimentación", "corrección", "evaluación"
- Responde como si estuvieras hablando directamente al estudiante"""},
                
                {"role": "user", "content": f"""Un estudiante llamado {student_name} respondió a la pregunta: "{question}"
                
Su respuesta fue: "{answer}"

Contexto del material de clase: {context[:1000]}...

Da una respuesta natural y educativa como profesor. Si la respuesta es incorrecta o es "no sé", corrige de manera amable pero sin usar palabras técnicas como "retroalimentación"."""}
            ]
        )
        
        # Limpiar respuesta de cualquier formato
        evaluation = response.choices[0].message.content
        evaluation = evaluation.replace("*", "").replace("**", "").replace("***", "")
        evaluation = evaluation.replace("- ", "").replace("• ", "")
        evaluation = evaluation.strip()
        
        return evaluation
        
    except Exception as e:
        print(f"❌ Error evaluando respuesta de {student_name}: {e}")
        # Respuesta de emergencia natural
        if "no sé" in answer.lower() or "no se" in answer.lower():
            return f"No hay problema, {student_name}. Estas son preguntas complejas sobre robótica médica. Continuemos con la clase."
        else:
            return f"Gracias por tu respuesta, {student_name}. Continuemos con la clase."

class RandomQuestionManager:
    """
    Gestor de preguntas aleatorias para el sistema de clase
    """
    
    def __init__(self, students, question_bank=None):
        """
        Inicializa el gestor de preguntas aleatorias
        
        Args:
            students (list): Lista de estudiantes registrados
            question_bank (list): Banco de preguntas (opcional)
        """
        self.students = students.copy()
        self.question_bank = question_bank or QUESTION_BANK.copy()
        self.original_question_bank = QUESTION_BANK.copy()
        
        # Tracking de estudiantes y preguntas
        self.available_students = students.copy()
        self.used_questions = []
        self.student_question_history = {student: [] for student in students}
        
        # Estadísticas
        self.total_questions_asked = 0
        self.questions_per_student = {student: 0 for student in students}
        
        print(f"🎯 Gestor de preguntas inicializado:")
        print(f"   - {len(self.students)} estudiantes registrados")
        print(f"   - {len(self.question_bank)} preguntas disponibles")
    
    def reset_cycle_if_needed(self):
        """
        Reinicia el ciclo si todos los estudiantes ya fueron preguntados
        
        Returns:
            bool: True si se reinició el ciclo
        """
        if not self.available_students:
            print("🔄 Todos los estudiantes han sido preguntados. Reiniciando ciclo...")
            self.available_students = self.students.copy()
            return True
        return False
    
    def reset_questions_if_needed(self):
        """
        Reinicia el banco de preguntas si se agotaron
        
        Returns:
            bool: True si se reinició el banco
        """
        if not self.question_bank:
            print("🔄 Banco de preguntas agotado. Reiniciando...")
            self.question_bank = self.original_question_bank.copy()
            # Remover preguntas ya usadas en esta sesión para evitar repetición inmediata
            for used_q in self.used_questions[-10:]:  # Solo evitar las últimas 10
                if used_q in self.question_bank:
                    self.question_bank.remove(used_q)
            return True
        return False
    
    def select_random_student(self):
        """
        Selecciona un estudiante aleatorio que no haya sido preguntado en esta ronda
        
        Returns:
            tuple: (student_name, student_index) o (None, None) si no hay estudiantes
        """
        self.reset_cycle_if_needed()
        
        if not self.available_students:
            print("⚠️ No hay estudiantes disponibles para preguntas")
            return None, None
        
        # Seleccionar estudiante aleatorio
        selected_student = random.choice(self.available_students)
        student_index = self.students.index(selected_student)
        
        # Remover de disponibles
        self.available_students.remove(selected_student)
        
        print(f"🎯 Estudiante seleccionado: {selected_student} (posición {student_index + 1})")
        return selected_student, student_index
    
    def select_random_question(self):
        """
        Selecciona una pregunta aleatoria del banco
        
        Returns:
            str: Pregunta seleccionada o None si no hay preguntas
        """
        self.reset_questions_if_needed()
        
        if not self.question_bank:
            print("⚠️ No hay preguntas disponibles")
            return None
        
        # Seleccionar pregunta aleatoria
        selected_question = random.choice(self.question_bank)
        
        # Remover de banco para evitar repetición
        self.question_bank.remove(selected_question)
        self.used_questions.append(selected_question)
        
        print(f"❓ Pregunta seleccionada: {selected_question[:50]}...")
        return selected_question
    
    def conduct_random_question(self, engine, pdf_text):
        """
        Conduce una pregunta aleatoria completa - VERSIÓN TRADICIONAL
        
        Args:
            engine: Motor de TTS
            pdf_text (str): Texto del PDF para contexto
            
        Returns:
            bool: True si se completó exitosamente, False si hubo error
        """
        try:
            # Importar funciones necesarias
            from .speech import speak_with_animation, listen
            
            # Seleccionar estudiante y pregunta
            student_name, student_index = self.select_random_student()
            question = self.select_random_question()
            
            if not student_name or not question:
                print("⚠️ No se pudo realizar pregunta aleatoria")
                return False
            
            # Anunciar pregunta aleatoria
            announcement = f"Momento de verificación de aprendizaje. {student_name}, tienes una pregunta especial."
            speak_with_animation(engine, announcement)
            
            # Hacer la pregunta
            speak_with_animation(engine, question)
            
            # Escuchar respuesta
            print(f"🎤 Esperando respuesta de {student_name}...")
            answer = listen(timeout=15)  # Más tiempo para respuesta reflexiva
            
            # Procesar respuesta
            if answer and answer not in ["error_capture", "error_google", "error_unknown", "error_general", "timeout", ""]:
                print(f"💬 Respuesta de {student_name}: {answer}")
                
                # Registrar en historial
                self.student_question_history[student_name].append({
                    'question': question,
                    'answer': answer,
                    'slide_number': None  # Se puede agregar después
                })
                self.questions_per_student[student_name] += 1
                self.total_questions_asked += 1
                
                # Evaluar respuesta con OpenAI
                try:
                    evaluation = evaluate_student_answer(question, answer, pdf_text, student_name)
                    
                    # Dar retroalimentación
                    speak_with_animation(engine, evaluation)
                    
                    # Mensaje de continuación basado en la evaluación
                    if "excelente" in evaluation.lower() or "correcta" in evaluation.lower():
                        speak_with_animation(engine, f"¡Muy bien, {student_name}! Continuemos con la clase.")
                    else:
                        speak_with_animation(engine, f"Gracias por tu respuesta, {student_name}. Continuemos.")
                    
                except Exception as e:
                    print(f"❌ Error evaluando respuesta: {e}")
                    speak_with_animation(engine, f"Gracias por tu respuesta, {student_name}. Continuemos con la clase.")
                
            else:
                # No se obtuvo respuesta válida
                print(f"⚠️ No se obtuvo respuesta válida de {student_name}")
                speak_with_animation(engine, f"No hay problema, {student_name}. Continuemos con la clase.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en pregunta aleatoria: {e}")
            speak_with_animation(engine, "Continuemos con la clase.")
            return False
    
    def get_statistics(self):
        """
        Retorna estadísticas del sistema de preguntas
        
        Returns:
            dict: Estadísticas del sistema
        """
        return {
            'total_questions': self.total_questions_asked,
            'questions_per_student': self.questions_per_student,
            'available_students': len(self.available_students),
            'available_questions': len(self.question_bank),
            'student_history': self.student_question_history
        }

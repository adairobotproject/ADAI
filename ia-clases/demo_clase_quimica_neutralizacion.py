#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Clase de Química - Neutralización de Ácido
===============================================

Script para controlar el robot ADAI durante una demostración de neutralización
de ácido con bicarbonato de sodio. Respeta los límites de seguridad del robot.

Comandos ESP32 utilizados:
- BRAZOS: Control de brazos (BI, FI, HI, BD, FD, HD, PD)
- CUELLO: Control de cuello (L, I, S)
- MANO: Control de manos y dedos
- MUNECA: Control de muñecas
- GESTO: Gestos predefinidos
- HABLAR: Texto a voz

Límites de seguridad según ESP32:
- Brazos: BI(10-30), FI(60-120), HI(70-90), BD(30-55), FD(70-110), HD(70-90), PD(0-90)
- Cuello: L(120-160), I(60-130), S(109-110)
- Dedos: 0-180 grados
- Muñecas: 0-160 grados
"""

import requests
import json
import time
import threading
from typing import Dict, Optional, List
import sys
import os

class RobotQuimicaDemo:
    """Controlador del robot para demo de química"""
    
    def __init__(self, esp32_ip: str = "192.168.1.100", esp32_port: int = 80):
        """
        Inicializar controlador del robot
        
        Args:
            esp32_ip: IP del ESP32
            esp32_port: Puerto del ESP32
        """
        self.esp32_ip = esp32_ip
        self.esp32_port = esp32_port
        self.base_url = f"http://{esp32_ip}:{esp32_port}"
        self.connected = False
        self.session = requests.Session()
        self.session.timeout = 5.0
        
        # Posiciones de descanso seguras
        self.pos_descanso = {
            'brazos': {'BI': 10, 'FI': 80, 'HI': 80, 'BD': 40, 'FD': 90, 'HD': 80, 'PD': 45},
            'cuello': {'L': 155, 'I': 95, 'S': 110},
            'manos': {'derecha': 'DESCANSO', 'izquierda': 'DESCANSO'},
            'muñecas': {'derecha': 80, 'izquierda': 80}
        }
        
        # Límites de seguridad
        self.limites_seguridad = {
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
        
        print("🧪 Inicializando Demo de Química - Neutralización de Ácido")
        print(f"🤖 Conectando a ESP32 en {self.base_url}")
        
        # Intentar conexión
        self.test_connection()
    
    def test_connection(self) -> bool:
        """Probar conexión con el ESP32"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=3)
            if response.status_code == 200:
                self.connected = True
                print("✅ Conectado al ESP32")
                return True
            else:
                print(f"❌ Error de conexión: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error conectando al ESP32: {e}")
            print("⚠️ Continuando en modo simulación...")
            return False
    
    def send_command(self, command: str, parameters: Dict = None) -> Optional[Dict]:
        """
        Enviar comando al ESP32
        
        Args:
            command: Comando a enviar
            parameters: Parámetros del comando
            
        Returns:
            Respuesta del ESP32 o None si hay error
        """
        try:
            if not self.connected:
                print(f"⚠️ Simulando comando: {command}")
                return {"status": "simulated", "command": command}
            
            url = f"{self.base_url}/api/command"
            data = {
                'command': command,
                'timestamp': time.time()
            }
            
            if parameters:
                data['parameters'] = parameters
            
            print(f"📤 Enviando: {command}")
            if parameters:
                print(f"   📝 Parámetros: {parameters}")
            
            response = self.session.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Comando ejecutado: {command}")
                return result
            else:
                print(f"❌ Error ejecutando comando: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error enviando comando: {e}")
            return None
    
    def validar_limites(self, tipo: str, valores: Dict) -> bool:
        """
        Validar que los valores estén dentro de los límites de seguridad
        
        Args:
            tipo: Tipo de control ('brazos', 'cuello')
            valores: Diccionario con valores a validar
            
        Returns:
            True si todos los valores son seguros
        """
        if tipo not in self.limites_seguridad:
            return True
        
        limites = self.limites_seguridad[tipo]
        
        for clave, valor in valores.items():
            if clave in limites:
                min_val, max_val = limites[clave]
                if valor < min_val or valor > max_val:
                    print(f"❌ Valor fuera de límites seguros: {clave}={valor} (rango: {min_val}-{max_val})")
                    return False
        
        return True
    
    def mover_brazos(self, **kwargs) -> bool:
        """
        Mover brazos del robot
        
        Args:
            **kwargs: Parámetros de brazos (BI, FI, HI, BD, FD, HD, PD)
            
        Returns:
            True si el movimiento fue exitoso
        """
        if not self.validar_limites('brazos', kwargs):
            return False
        
        comando = "BRAZOS"
        for clave, valor in kwargs.items():
            comando += f" {clave}={valor}"
        
        return self.send_command(comando) is not None
    
    def mover_cuello(self, L: int = None, I: int = None, S: int = None) -> bool:
        """
        Mover cuello del robot
        
        Args:
            L: Lateral (120-160)
            I: Inferior (60-130)
            S: Superior (109-110)
            
        Returns:
            True si el movimiento fue exitoso
        """
        valores = {}
        if L is not None: valores['L'] = L
        if I is not None: valores['I'] = I
        if S is not None: valores['S'] = S
        
        if not self.validar_limites('cuello', valores):
            return False
        
        comando = "CUELLO"
        for clave, valor in valores.items():
            comando += f" {clave}={valor}"
        
        return self.send_command(comando) is not None
    
    def controlar_mano(self, mano: str, gesto: str) -> bool:
        """
        Controlar mano del robot
        
        Args:
            mano: 'derecha', 'izquierda', 'ambas'
            gesto: Tipo de gesto
            
        Returns:
            True si el gesto fue exitoso
        """
        comando = f"MANO M={mano} GESTO={gesto}"
        return self.send_command(comando) is not None
    
    def controlar_muñeca(self, mano: str, angulo: int) -> bool:
        """
        Controlar muñeca del robot
        
        Args:
            mano: 'derecha' o 'izquierda'
            angulo: Ángulo (0-160)
            
        Returns:
            True si el movimiento fue exitoso
        """
        if angulo < 0 or angulo > 160:
            print(f"❌ Ángulo de muñeca fuera de límites: {angulo}")
            return False
        
        comando = f"MUNECA M={mano} ANG={angulo}"
        return self.send_command(comando) is not None
    
    def hablar(self, texto: str) -> bool:
        """
        Hacer que el robot hable
        
        Args:
            texto: Texto a pronunciar
            
        Returns:
            True si el comando fue exitoso
        """
        print(f"🗣️ ADAI dice: {texto}")
        comando = "HABLAR"
        return self.send_command(comando, {"texto": texto}) is not None
    
    def posicion_descanso(self) -> bool:
        """Mover robot a posición de descanso"""
        print("🏠 Moviendo a posición de descanso...")
        
        # Brazos en descanso
        self.mover_brazos(**self.pos_descanso['brazos'])
        time.sleep(0.5)
        
        # Cuello en descanso
        self.mover_cuello(**self.pos_descanso['cuello'])
        time.sleep(0.5)
        
        # Manos en descanso
        self.controlar_mano('derecha', 'DESCANSO')
        self.controlar_mano('izquierda', 'DESCANSO')
        time.sleep(0.5)
        
        # Muñecas en descanso
        self.controlar_muñeca('derecha', self.pos_descanso['muñecas']['derecha'])
        self.controlar_muñeca('izquierda', self.pos_descanso['muñecas']['izquierda'])
        
        print("✅ Posición de descanso alcanzada")
        return True
    
    def saludo_inicial(self) -> bool:
        """Saludo inicial de la clase"""
        print("👋 Iniciando saludo...")
        
        # Hablar saludo
        self.hablar("¡Hola estudiantes! Bienvenidos a la clase de química")
        time.sleep(2)
        
        # Gesto de saludo con brazo derecho
        self.mover_brazos(BD=25, FD=110, HD=85, PD=60)
        time.sleep(1)
        
        # Movimiento de saludo
        for i in range(3):
            self.mover_brazos(FD=90)
            time.sleep(0.3)
            self.mover_brazos(FD=110)
            time.sleep(0.3)
        
        # Volver a descanso
        self.posicion_descanso()
        
        print("✅ Saludo completado")
        return True
    
    def introduccion_tema(self) -> bool:
        """Introducción al tema de neutralización"""
        print("📚 Introduciendo tema...")
        
        # Hablar introducción
        self.hablar("Hoy aprenderemos sobre neutralización de ácidos")
        time.sleep(1)
        
        # Gesto de explicación
        self.controlar_mano('derecha', 'EXPLICAR')
        time.sleep(2)
        
        self.hablar("La neutralización es una reacción química entre un ácido y una base")
        time.sleep(1)
        
        # Mirar hacia los reactivos (izquierda)
        self.mover_cuello(L=130)
        time.sleep(1)
        
        # Mirar hacia los equipos (derecha)
        self.mover_cuello(L=150)
        time.sleep(1)
        
        # Volver al centro
        self.mover_cuello(L=155)
        time.sleep(0.5)
        
        print("✅ Introducción completada")
        return True
    
    def demostrar_reactivos(self) -> bool:
        """Demostrar los reactivos"""
        print("🧪 Demostrando reactivos...")
        
        # Hablar sobre reactivos
        self.hablar("Para esta demostración necesitamos ácido clorhídrico y bicarbonato de sodio")
        time.sleep(1)
        
        # Señalar reactivos con brazo derecho
        self.mover_brazos(BD=30, FD=100, HD=80)
        self.controlar_mano('derecha', 'SENALAR')
        time.sleep(2)
        
        self.hablar("El ácido clorhídrico es muy corrosivo, por eso usamos equipo de protección")
        time.sleep(1)
        
        # Gesto de precaución
        self.controlar_mano('ambas', 'PRECAUCION')
        time.sleep(2)
        
        # Volver a posición normal
        self.posicion_descanso()
        
        print("✅ Demostración de reactivos completada")
        return True
    
    def preparar_experimento(self) -> bool:
        """Preparar el experimento"""
        print("🔬 Preparando experimento...")
        
        # Hablar sobre preparación
        self.hablar("Ahora vamos a preparar nuestro experimento de neutralización")
        time.sleep(1)
        
        # Gesto de preparación
        self.controlar_mano('derecha', 'PREPARAR')
        time.sleep(2)
        
        # Mirar hacia la mesa de trabajo
        self.mover_cuello(I=110)
        time.sleep(1)
        
        self.hablar("Primero, colocamos el bicarbonato de sodio en el matraz")
        time.sleep(1)
        
        # Simular colocación con gesto
        self.mover_brazos(BD=35, FD=95, HD=75)
        self.controlar_mano('derecha', 'COLOCAR')
        time.sleep(2)
        
        # Volver a posición normal
        self.posicion_descanso()
        
        print("✅ Preparación completada")
        return True
    
    def realizar_neutralizacion(self) -> bool:
        """Realizar la neutralización"""
        print("⚗️ Realizando neutralización...")
        
        # Hablar sobre el proceso
        self.hablar("Ahora agregamos lentamente el ácido clorhídrico al bicarbonato")
        time.sleep(1)
        
        # Gesto de agregar gota a gota
        self.mover_brazos(BD=30, FD=105, HD=80)
        self.controlar_mano('derecha', 'GOTEAR')
        time.sleep(3)
        
        self.hablar("Observen la reacción: se produce dióxido de carbono y agua")
        time.sleep(1)
        
        # Gesto de observación
        self.mover_cuello(I=120)
        self.controlar_mano('derecha', 'OBSERVAR')
        time.sleep(2)
        
        # Gesto de éxito
        self.controlar_mano('derecha', 'EXITO')
        time.sleep(1)
        
        self.hablar("¡La neutralización ha sido exitosa! El pH se ha neutralizado")
        time.sleep(1)
        
        # Volver a posición normal
        self.posicion_descanso()
        
        print("✅ Neutralización completada")
        return True
    
    def explicar_resultados(self) -> bool:
        """Explicar los resultados"""
        print("📊 Explicando resultados...")
        
        # Hablar sobre resultados
        self.hablar("En esta reacción, el ácido clorhídrico reacciona con el bicarbonato")
        time.sleep(1)
        
        # Gesto de explicación
        self.controlar_mano('derecha', 'EXPLICAR')
        time.sleep(2)
        
        self.hablar("La ecuación química es: HCl + NaHCO3 → NaCl + H2O + CO2")
        time.sleep(1)
        
        # Mirar hacia la pizarra (izquierda)
        self.mover_cuello(L=130)
        time.sleep(1)
        
        # Gesto de escribir en pizarra
        self.controlar_mano('derecha', 'ESCRIBIR')
        time.sleep(2)
        
        # Volver al centro
        self.mover_cuello(L=155)
        time.sleep(0.5)
        
        self.hablar("Esta es una reacción de neutralización típica")
        time.sleep(1)
        
        print("✅ Explicación completada")
        return True
    
    def conclusion(self) -> bool:
        """Conclusión de la clase"""
        print("🎓 Conclusión de la clase...")
        
        # Hablar conclusión
        self.hablar("Hemos aprendido que la neutralización es fundamental en química")
        time.sleep(1)
        
        # Gesto de aprobación
        self.controlar_mano('derecha', 'APROBAR')
        time.sleep(2)
        
        self.hablar("Recuerden siempre usar equipo de protección en el laboratorio")
        time.sleep(1)
        
        # Gesto de despedida
        self.controlar_mano('ambas', 'DESPEDIDA')
        time.sleep(1)
        
        self.hablar("¡Gracias por su atención! ¿Tienen alguna pregunta?")
        time.sleep(1)
        
        # Saludo final
        self.saludo_inicial()
        
        print("✅ Conclusión completada")
        return True
    
    def ejecutar_demo_completa(self) -> bool:
        """Ejecutar la demo completa de neutralización"""
        print("🚀 Iniciando Demo Completa de Neutralización")
        print("=" * 60)
        
        try:
            # 1. Posición inicial
            self.posicion_descanso()
            time.sleep(1)
            
            # 2. Saludo inicial
            self.saludo_inicial()
            time.sleep(2)
            
            # 3. Introducción al tema
            self.introduccion_tema()
            time.sleep(2)
            
            # 4. Demostrar reactivos
            self.demostrar_reactivos()
            time.sleep(2)
            
            # 5. Preparar experimento
            self.preparar_experimento()
            time.sleep(2)
            
            # 6. Realizar neutralización
            self.realizar_neutralizacion()
            time.sleep(2)
            
            # 7. Explicar resultados
            self.explicar_resultados()
            time.sleep(2)
            
            # 8. Conclusión
            self.conclusion()
            time.sleep(2)
            
            # 9. Posición final de descanso
            self.posicion_descanso()
            
            print("=" * 60)
            print("🎉 Demo de neutralización completada exitosamente!")
            return True
            
        except Exception as e:
            print(f"❌ Error en la demo: {e}")
            # Intentar volver a posición de descanso
            self.posicion_descanso()
            return False
    
    def demo_interactiva(self) -> bool:
        """Demo interactiva con pausas para preguntas"""
        print("🎭 Iniciando Demo Interactiva")
        print("=" * 60)
        
        try:
            # 1. Saludo
            self.saludo_inicial()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para continuar con la introducción...")
            
            # 2. Introducción
            self.introduccion_tema()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para mostrar los reactivos...")
            
            # 3. Reactivos
            self.demostrar_reactivos()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para preparar el experimento...")
            
            # 4. Preparación
            self.preparar_experimento()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para realizar la neutralización...")
            
            # 5. Neutralización
            self.realizar_neutralizacion()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para explicar los resultados...")
            
            # 6. Resultados
            self.explicar_resultados()
            
            # Pausa para preguntas
            input("\n⏸️ Presiona Enter para la conclusión...")
            
            # 7. Conclusión
            self.conclusion()
            
            print("=" * 60)
            print("🎉 Demo interactiva completada!")
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrumpida por el usuario")
            self.posicion_descanso()
            return False
        except Exception as e:
            print(f"❌ Error en la demo interactiva: {e}")
            self.posicion_descanso()
            return False

def main():
    """Función principal"""
    print("🧪 Demo de Clase de Química - Neutralización de Ácido")
    print("🤖 Controlador del Robot ADAI")
    print("=" * 60)
    
    # Configuración del ESP32
    esp32_ip = input("📡 IP del ESP32 (default: 192.168.1.100): ").strip()
    if not esp32_ip:
        esp32_ip = "192.168.1.100"
    
    # Crear controlador
    robot = RobotQuimicaDemo(esp32_ip)
    
    # Menú de opciones
    while True:
        print("\n" + "=" * 40)
        print("🎓 MENÚ DE DEMO DE QUÍMICA")
        print("=" * 40)
        print("1. 🚀 Demo Completa Automática")
        print("2. 🎭 Demo Interactiva (con pausas)")
        print("3. 👋 Solo Saludo")
        print("4. 🧪 Solo Demostración de Reactivos")
        print("5. ⚗️ Solo Neutralización")
        print("6. 🏠 Posición de Descanso")
        print("7. ❌ Salir")
        print("=" * 40)
        
        opcion = input("Selecciona una opción (1-7): ").strip()
        
        try:
            if opcion == "1":
                robot.ejecutar_demo_completa()
            elif opcion == "2":
                robot.demo_interactiva()
            elif opcion == "3":
                robot.saludo_inicial()
            elif opcion == "4":
                robot.demostrar_reactivos()
            elif opcion == "5":
                robot.realizar_neutralizacion()
            elif opcion == "6":
                robot.posicion_descanso()
            elif opcion == "7":
                print("👋 ¡Hasta luego!")
                robot.posicion_descanso()
                break
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            print("\n⏹️ Operación interrumpida")
            robot.posicion_descanso()
        except Exception as e:
            print(f"❌ Error: {e}")
            robot.posicion_descanso()

if __name__ == "__main__":
    main()

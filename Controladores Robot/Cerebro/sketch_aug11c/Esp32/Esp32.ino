#include <WiFi.h>
#include <WebServer.h>
#include <HardwareSerial.h>
#include <ArduinoJson.h>

// UART1 en ESP32
HardwareSerial UART1(2);
const int RX2_PIN = 16;   // ESP32 RX2 <- Mega TX2
const int TX2_PIN = 17;   // ESP32 TX2 -> Mega RX2
const long MEGA_BAUD = 115200;

// WiFi
const char* ssid = "Senpai";
const char* password = "01234567";

WebServer server(80);

#ifndef LED_BUILTIN
#define LED_BUILTIN 2
#endif

// Variables del sistema
String megaLine;
String ultimoEstadoMega = "";
String ultimoEstadoUno = "";
unsigned long lastPingMs = 0;
unsigned long lastConnectionCheck = 0;
bool modoSeguridad = true;
bool modoLento = true;
bool megaConectado = false;
bool unoConectado = false;

// Posiciones actuales de los brazos (BI, FI, HI, BD, FD, HD, PD)
int posActualBrazos[7] = {10, 80, 80, 40, 90, 80, 45};
String nombresBrazos[7] = {"Brazo Izq", "Frente Izq", "High Izq", "Brazo Der", "Frente Der", "High Der", "Pollo Der"};
// Rangos seguros según MEGA: BI(10-30), FI(60-120), HI(70-90), BD(30-55), FD(70-110), HD(70-90), PD(0-90)
int limitesBrazos[7][2] = {{10, 30}, {60, 120}, {70, 90}, {0, 30}, {70, 110}, {70, 90}, {0, 90}};

// Posiciones actuales de las manos
int posActualManos[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0}; // 5 dedos mano derecha + 5 dedos mano izquierda
String nombresDedos[10] = {"D-Pulgar", "D-Índice", "D-Medio", "D-Anular", "D-Meñique", 
                           "I-Pulgar", "I-Índice", "I-Medio", "I-Anular", "I-Meñique"};
int limitesDedos[10][2] = {{0, 120}, {0, 120}, {0, 120}, {0, 120}, {0, 120},
                           {0, 120}, {0, 120}, {0, 120}, {0, 120}, {0, 120}};

// Posiciones actuales de las muñecas
int posActualMuñecas[2] = {80, 80}; // Derecha, Izquierda
String nombresMuñecas[2] = {"Muñeca Der", "Muñeca Izq"};
int limitesMuñecas[2][2] = {{70, 180}, {70, 180}};

// Sistema de posicionamiento relativo para muñeca derecha
int posicionRelativaMuñecaDerecha = 80; // Posición actual guardada
const int MIN_MOVIMIENTOS = 0; // No puede bajar de 80°
const int MAX_MOVIMIENTOS = 5;  // 5 movimientos hacia arriba (80+5*20=180°)
const int INCREMENTO_ANGULO = 20; // Cada movimiento representa 20°

// Posiciones actuales del cuello (Lateral, Inferior, Superior)
int posActualCuello[3] = {155, 95, 110}; 
String nombresCuello[3] = {"Lateral", "Inferior", "Superior"};
// Rangos seguros según MEGA: L(120-160), I(60-130), S(109-110)
int limitesCuello[3][2] = {{120, 160}, {60, 130}, {109, 110}};

// Posiciones de descanso (según MEGA)         //
const int POS_DESCANSO_BRAZOS[7] = {10, 80, 80, 0, 70, 80, 45}; // BI, FI, HI, BD, FD, HD, PD
const int POS_DESCANSO_CUELLO[3] = {155, 95, 110}; // L, I, S

// Configuración de seguridad
const int VELOCIDAD_LENTA = 50;  // ms entre movimientos
const int VELOCIDAD_NORMAL = 20; // ms entre movimientos

// Declaraciones de funciones
void controlarMuñecaDerechaRelativa(int anguloObjetivo);
void moverMuñecaDerechaRelativa(int direccion);

// Utilidades
void sendToMega(const String &msg) {
  UART1.print(msg);
  if (!msg.endsWith("\n")) UART1.print("\n");
  Serial.print("[TX MEGA] ");
  Serial.println(msg);
}

String jsonEscape(const String &s) {
  String out;
  for (size_t i = 0; i < s.length(); i++) {
    char c = s[i];
    if (c == '\\' || c == '"') { out += '\\'; out += c; }
    else if (c == '\n') { out += "\\n"; }
    else if (c == '\r') { /* skip */ }
    else { out += c; }
  }
  return out;
}

// Comprobador de conexiones
void checkConnections() {
  if (millis() - lastConnectionCheck > 3000) {
    lastConnectionCheck = millis();
    
    // Ping al MEGA
    sendToMega("PING");
    
    // El UNO se comunica a través del MEGA
    sendToMega("UNO:PING");
  }
}

// Función para sincronizar estado de seguridad con el MEGA
void sincronizarSeguridad() {
  String comandoSeguridad = modoSeguridad ? "SEGURIDAD ON" : "SEGURIDAD OFF";
  sendToMega(comandoSeguridad);
  Serial.println("Sincronizando seguridad con MEGA: " + String(modoSeguridad ? "ACTIVADA" : "DESACTIVADA"));
}

// Función de seguridad para validar movimientos
bool validarMovimiento(const String& tipo, int valor, int min, int max) {
  if (!modoSeguridad) return true;
  
  if (valor < min || valor > max) {
    Serial.print("MOVIMIENTO BLOQUEADO: ");
    Serial.print(tipo);
    Serial.print(" = ");
    Serial.print(valor);
    Serial.print(" (rango: ");
    Serial.print(min);
    Serial.print("-");
    Serial.print(max);
    Serial.println(")");
    return false;
  }
  return true;
}

// Función para enviar comandos con modo lento
void enviarComandoLento(const String& comando) {
  if (modoLento) {
    sendToMega(comando + " VEL=" + String(VELOCIDAD_LENTA));
  } else {
    sendToMega(comando + " VEL=" + String(VELOCIDAD_NORMAL));
  }
}

// ===== FUNCIONES DE CONTROL =====

// Función de posición de descanso
void posicionDescanso() {
  Serial.println("🔄 Moviendo robot a posición de descanso...");
  
  // Mover brazos a posición de descanso
  controlarBrazos(POS_DESCANSO_BRAZOS[0], POS_DESCANSO_BRAZOS[1], POS_DESCANSO_BRAZOS[2],
                  POS_DESCANSO_BRAZOS[3], POS_DESCANSO_BRAZOS[4], POS_DESCANSO_BRAZOS[5], POS_DESCANSO_BRAZOS[6]);
  
  // Mover cuello a posición de descanso
  controlarCuello(POS_DESCANSO_CUELLO[0], POS_DESCANSO_CUELLO[1], POS_DESCANSO_CUELLO[2]);
  
  // Abrir ambas manos
  // controlarMano("ambas", "abrir");
  
  // Mover muñeca derecha a posición de descanso (80°)
  controlarMuñecaDerechaRelativa(80);
  
  // Actualizar posiciones actuales
  for (int i = 0; i < 7; i++) {
    posActualBrazos[i] = POS_DESCANSO_BRAZOS[i];
  }
  for (int i = 0; i < 3; i++) {
    posActualCuello[i] = POS_DESCANSO_CUELLO[i];
  }
  for (int i = 0; i < 10; i++) {
    posActualManos[i] = (i < 5) ? 0 : 90; // Derecha abierta, izquierda cerrada
  }
  
  // Actualizar posición relativa de muñeca derecha
  posicionRelativaMuñecaDerecha = 80;
  
  Serial.println("✅ Robot en posición de descanso");
}

// Control de Manos
void controlarMano(const String& mano, const String& accion, int angulo = -1) {
  String comando = "MANO M=" + mano + " A=" + accion;
  if (angulo >= 0) comando += " ANG=" + String(angulo);
  enviarComandoLento(comando);
  
  // Actualizar posiciones de manos según el gesto
  if (accion == "abrir") {
    if (mano == "derecha" || mano == "ambas") {
      for (int i = 0; i < 5; i++) posActualManos[i] = 0;
    }
    if (mano == "izquierda" || mano == "ambas") {
      for (int i = 5; i < 10; i++) posActualManos[i] = 120;
    }
  }
  else if (accion == "cerrar") {
    if (mano == "derecha" || mano == "ambas") {
      for (int i = 0; i < 5; i++) posActualManos[i] = 120;
    }
    if (mano == "izquierda" || mano == "ambas") {
      for (int i = 5; i < 10; i++) posActualManos[i] = 0;
    }
  }
}

// Control de Dedos
void controlarDedo(const String& mano, const String& dedo, int angulo) {
  if (!validarMovimiento("dedo", angulo, 0, 180)) return;
  
  // Actualizar posición actual del dedo
  int indice = obtenerIndiceDedo(mano, dedo);
  if (indice >= 0) {
    posActualManos[indice] = angulo;
  }
  
  String comando = "DEDO M=" + mano + " D=" + dedo + " ANG=" + String(angulo);
  enviarComandoLento(comando);
}

// Función auxiliar para obtener el índice del dedo en el array
int obtenerIndiceDedo(const String& mano, const String& dedo) {
  int base = (mano == "derecha") ? 0 : 5;
  if (dedo == "pulgar") return base + 0;
  if (dedo == "indice") return base + 1;
  if (dedo == "medio") return base + 2;
  if (dedo == "anular") return base + 3;
  if (dedo == "menique") return base + 4;
  return -1;
}

// Control de Cuello
void controlarCuello(int lateral, int inferior, int superior) {
  if (!validarMovimiento("lateral", lateral, 120, 190) ||
      !validarMovimiento("inferior", inferior, 60, 130) ||
      !validarMovimiento("superior", superior, 90, 120)) return;
  
  // Actualizar posiciones actuales
  posActualCuello[0] = lateral;
  posActualCuello[1] = inferior;
  posActualCuello[2] = superior;
  
  String comando = "CUELLO L=" + String(lateral) + " I=" + String(inferior) + " S=" + String(superior);
  enviarComandoLento(comando);
}

// Control de Muñecas


void controlarMuñeca(const String& mano, int angulo) {
  if (mano == "derecha") {
    // Sistema de posicionamiento relativo para muñeca derecha
    controlarMuñecaDerechaRelativa(angulo);
  } else {
    // Sistema normal para muñeca izquierda
    int indice = 1; // Izquierda
    posActualMuñecas[indice] = angulo;
    
    String comando = "MUNECA M=" + mano + " ANG=" + String(angulo);
    enviarComandoLento(comando);
  }
}

// Función para controlar muñeca derecha con sistema relativo
void controlarMuñecaDerechaRelativa(int anguloObjetivo) {
  // Validar límites absolutos
  if (anguloObjetivo < 80) {
    Serial.println("⚠️ Muñeca derecha: no puede bajar de 80°");
    return;
  }
  if (anguloObjetivo > 180) {
    Serial.println("⚠️ Muñeca derecha: no puede subir de 180°");
    return;
  }
  
  // Calcular cuántos movimientos necesitamos
  int diferencia = anguloObjetivo - posicionRelativaMuñecaDerecha;
  int movimientosNecesarios = diferencia / INCREMENTO_ANGULO;
  
  Serial.print("🎯 Muñeca derecha: Objetivo=");
  Serial.print(anguloObjetivo);
  Serial.print("°, Actual=");
  Serial.print(posicionRelativaMuñecaDerecha);
  Serial.print("°, Movimientos=");
  Serial.println(movimientosNecesarios);
  
  // Si no hay movimiento necesario, no hacer nada
  if (movimientosNecesarios == 0) {
    Serial.println("✅ Muñeca derecha ya está en la posición objetivo");
    return;
  }
  
  // Ejecutar los movimientos
  for (int i = 0; i < abs(movimientosNecesarios); i++) {
    int direccion = (movimientosNecesarios > 0) ? 1 : -1;
    
    // Enviar comando de movimiento relativo
    String comando = "MUNECA M=derecha ANG=" + String(direccion);
    enviarComandoLento(comando);
  
    
    // Actualizar posición relativa
    posicionRelativaMuñecaDerecha += (direccion * INCREMENTO_ANGULO);
    
    // Pequeña pausa entre movimientos
    delay(200);
  }
  
  // Actualizar posición en el array general
  posActualMuñecas[0] = posicionRelativaMuñecaDerecha;
  
  Serial.print("✅ Muñeca derecha movida a ");
  Serial.print(posicionRelativaMuñecaDerecha);
  Serial.println("°");
}

void moverMuñecaConFlecha(int indice, int direccion) {
  if (indice < 0 || indice >= 2) return;
  
  if (indice == 0) {
    // Muñeca derecha - usar sistema relativo
    moverMuñecaDerechaRelativa(direccion);
  } else {
    // Muñeca izquierda - sistema normal
    String mano = "izquierda";
    
    if (direccion == -1) {
      controlarMuñeca(mano, -1);
    } else if (direccion == 1) {
      controlarMuñeca(mano, 1);
    }
  }
}

// Función para mover muñeca derecha con sistema relativo usando flechas
void moverMuñecaDerechaRelativa(int direccion) {
  // Calcular nueva posición objetivo
  int nuevaPosicion = posicionRelativaMuñecaDerecha + (direccion * INCREMENTO_ANGULO);
  
  // Validar límites - no puede bajar de 80° ni subir de 180°
  if (nuevaPosicion < 80) {
    Serial.println("⚠️ Muñeca derecha: no puede bajar de 80°");
    return;
  }
  if (nuevaPosicion > 180) {
    Serial.println("⚠️ Muñeca derecha: no puede subir de 180°");
    return;
  }
  
  // Enviar comando de movimiento relativo
  String comando = "MUNECA M=derecha ANG=" + String(direccion);
  enviarComandoLento(comando);
  
  // Actualizar posición relativa
  posicionRelativaMuñecaDerecha = nuevaPosicion;
  posActualMuñecas[0] = posicionRelativaMuñecaDerecha;
  
  Serial.print("🎯 Muñeca derecha movida a ");
  Serial.print(posicionRelativaMuñecaDerecha);
  Serial.println("°");
}

// Control de Brazos
void controlarBrazos(int bi, int fi, int hi, int bd, int fd, int hd, int pd) {
  if (!validarMovimiento("brazo_izq", bi, 10, 30) ||
      !validarMovimiento("frente_izq", fi, 60, 120) ||
      !validarMovimiento("high_izq", hi, 70, 90) ||
      !validarMovimiento("brazo_der", bd, 0, 30) ||
      !validarMovimiento("frente_der", fd, 70, 110) ||
      !validarMovimiento("high_der", hd, 70, 90) ||
      !validarMovimiento("pollo_der", pd, 0, 90)) return;
  
  // Actualizar posiciones actuales
  posActualBrazos[0] = bi;
  posActualBrazos[1] = fi;
  posActualBrazos[2] = hi;
  posActualBrazos[3] = bd;
  posActualBrazos[4] = fd;
  posActualBrazos[5] = hd;
  posActualBrazos[6] = pd;
  
  String comando = "BRAZOS BI=" + String(bi) + " FI=" + String(fi) + " HI=" + String(hi) + 
                   " BD=" + String(bd) + " FD=" + String(fd) + " HD=" + String(hd) + " PD=" + String(pd);
  enviarComandoLento(comando);
}

// Gestos predefinidos
void gestoPaz(const String& mano) {
  controlarMano(mano, "PAZ");
  
  // Actualizar posiciones para gesto de paz
  if (mano == "derecha" || mano == "ambas") {
    posActualManos[0] = 0;  // Pulgar
    posActualManos[1] = 0;  // Índice
    posActualManos[2] = 180; // Medio
    posActualManos[3] = 180; // Anular
    posActualManos[4] = 180; // Meñique
  }
  if (mano == "izquierda" || mano == "ambas") {
    posActualManos[5] = 180; // Pulgar
    posActualManos[6] = 180; // Índice
    posActualManos[7] = 0;   // Medio
    posActualManos[8] = 0;   // Anular
    posActualManos[9] = 0;   // Meñique
  }
}

void gestoRock(const String& mano) {
  controlarMano(mano, "ROCK");
}

void gestoOK(const String& mano) {
  controlarMano(mano, "OK");
}

void gestoSeñalar(const String& mano) {
  controlarMano(mano, "SENALAR");
}

// ===== FUNCIONES DE CONTROL CON FLECHAS =====

// Control de brazos con flechas
void moverBrazoConFlecha(int indice, int direccion) {
  if (indice < 0 || indice >= 7) return;
  
  int nuevaPos = posActualBrazos[indice] + (direccion * 5); // Incremento de 5 grados
  int min = limitesBrazos[indice][0];
  int max = limitesBrazos[indice][1];
  
  if (nuevaPos >= min && nuevaPos <= max) {
    posActualBrazos[indice] = nuevaPos;
    controlarBrazos(posActualBrazos[0], posActualBrazos[1], posActualBrazos[2], 
                    posActualBrazos[3], posActualBrazos[4], posActualBrazos[5], posActualBrazos[6]);
  }
}

// Control de dedos con flechas
void moverDedoConFlecha(int indice, int direccion) {
  if (indice < 0 || indice >= 10) return;
  
  int nuevaPos = posActualManos[indice] + (direccion * 10); // Incremento de 10 grados
  int min = limitesDedos[indice][0];
  int max = limitesDedos[indice][1];
  
  if (nuevaPos >= min && nuevaPos <= max) {
    posActualManos[indice] = nuevaPos;
    
    // Determinar mano y dedo
    String mano = (indice < 5) ? "derecha" : "izquierda";
    String dedo;
    int dedoIndice = indice % 5;
    switch(dedoIndice) {
      case 0: dedo = "pulgar"; break;
      case 1: dedo = "indice"; break;
      case 2: dedo = "medio"; break;
      case 3: dedo = "anular"; break;
      case 4: dedo = "menique"; break;
    }
    
    controlarDedo(mano, dedo, nuevaPos);
  }
}

// Control de cuello con flechas
void moverCuelloConFlecha(int indice, int direccion) {
  if (indice < 0 || indice >= 3) return;
  
  int nuevaPos = posActualCuello[indice] + (direccion * 5); // Incremento de 5 grados
  int min = limitesCuello[indice][0];
  int max = limitesCuello[indice][1];
  
  if (nuevaPos >= min && nuevaPos <= max) {
    posActualCuello[indice] = nuevaPos;
    controlarCuello(posActualCuello[0], posActualCuello[1], posActualCuello[2]);
  }
}



// Función para actualizar posiciones desde respuestas del MEGA
void actualizarPosicionesDesdeRespuesta(const String& respuesta) {
  // Actualizar brazos
  if (respuesta.indexOf("BI=") >= 0) {
    int bi = extraerValor(respuesta, "BI=");
    int fi = extraerValor(respuesta, "FI=");
    int hi = extraerValor(respuesta, "HI=");
    int bd = extraerValor(respuesta, "BD=");
    int fd = extraerValor(respuesta, "FD=");
    int hd = extraerValor(respuesta, "HD=");
    int pd = extraerValor(respuesta, "PD=");
    
    if (bi >= 0) posActualBrazos[0] = bi;
    if (fi >= 0) posActualBrazos[1] = fi;
    if (hi >= 0) posActualBrazos[2] = hi;
    if (bd >= 0) posActualBrazos[3] = bd;
    if (fd >= 0) posActualBrazos[4] = fd;
    if (hd >= 0) posActualBrazos[5] = hd;
    if (pd >= 0) posActualBrazos[6] = pd;
  }
  
  // Actualizar cuello
  if (respuesta.indexOf("L=") >= 0) {
    int l = extraerValor(respuesta, "L=");
    int i = extraerValor(respuesta, "I=");
    int s = extraerValor(respuesta, "S=");
    
    if (l >= 0) posActualCuello[0] = l;
    if (i >= 0) posActualCuello[1] = i;
    if (s >= 0) posActualCuello[2] = s;
  }
}

// Función auxiliar para extraer valores de las respuestas
int extraerValor(const String& texto, const String& parametro) {
  int index = texto.indexOf(parametro);
  if (index == -1) return -1;
  
  int start = index + parametro.length();
  int end = texto.indexOf(" ", start);
  if (end == -1) end = texto.length();
  
  return texto.substring(start, end).toInt();
}

// Función para actualizar posiciones de manos desde respuestas del UNO
void actualizarPosicionesManosDesdeRespuesta(const String& respuesta) {
  // Extraer información del dedo movido
  String mano = "";
  String dedo = "";
  int angulo = -1;
  
  // Buscar mano
  if (respuesta.indexOf("mano derecha") >= 0) mano = "derecha";
  else if (respuesta.indexOf("mano izquierda") >= 0) mano = "izquierda";
  
  // Buscar dedo
  if (respuesta.indexOf("pulgar") >= 0) dedo = "pulgar";
  else if (respuesta.indexOf("indice") >= 0) dedo = "indice";
  else if (respuesta.indexOf("medio") >= 0) dedo = "medio";
  else if (respuesta.indexOf("anular") >= 0) dedo = "anular";
  else if (respuesta.indexOf("menique") >= 0) dedo = "menique";
  
  // Buscar ángulo
  int angIndex = respuesta.indexOf("a ");
  if (angIndex >= 0) {
    int endIndex = respuesta.indexOf("°", angIndex);
    if (endIndex >= 0) {
      angulo = respuesta.substring(angIndex + 2, endIndex).toInt();
    }
  }
  
  // Actualizar posición si tenemos toda la información
  if (mano.length() > 0 && dedo.length() > 0 && angulo >= 0) {
    int indice = obtenerIndiceDedo(mano, dedo);
    if (indice >= 0) {
      posActualManos[indice] = angulo;
    }
  }
}

// ===== INTERFAZ WEB =====

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<title>Robot Control - ESP32</title>";
  html += "<style>";
  html += "body{font-family:Arial;margin:16px;background:#f5f5f5}";
  html += ".container{max-width:1200px;margin:0 auto;background:white;padding:20px;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}";
  html += ".header{text-align:center;border-bottom:2px solid #007bff;padding-bottom:10px;margin-bottom:20px}";
  html += ".status{display:flex;justify-content:space-around;margin:20px 0;padding:15px;background:#f8f9fa;border-radius:8px}";
  html += ".status-item{text-align:center}";
  html += ".status-online{color:green;font-weight:bold}";
  html += ".status-offline{color:red;font-weight:bold}";
  html += ".section{background:#f8f9fa;padding:15px;margin:10px 0;border-radius:8px;border-left:4px solid #007bff}";
  html += "button{margin:4px;padding:8px 12px;border:none;border-radius:4px;cursor:pointer;background:#007bff;color:white}";
  html += "button:hover{background:#0056b3}";
  html += "button.danger{background:#dc3545}";
  html += "button.danger:hover{background:#c82333}";
  html += "button.success{background:#28a745}";
  html += "button.success:hover{background:#218838}";
  html += "input,select{margin:4px;padding:6px;border:1px solid #ddd;border-radius:4px}";
  html += ".control-group{margin:10px 0}";
  html += ".debug{background:#000;color:#0f0;padding:10px;border-radius:4px;font-family:monospace;max-height:300px;overflow-y:auto}";
  html += ".brazo-control,.cuello-control,.dedo-control{background:#f8f9fa;padding:10px;border-radius:8px;text-align:center;border:1px solid #dee2e6}";
  html += ".posicion-display{background:#007bff;color:white;padding:5px;border-radius:4px;margin:5px 0;font-weight:bold;transition:background-color 0.3s ease}";
  html += ".flechas{display:flex;justify-content:center;gap:5px;margin-top:5px}";
  html += ".flechas button{width:40px;height:40px;font-size:16px}";
  html += "h4,h5{margin:5px 0;color:#495057}";
  html += ".feedback{position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;color:white;font-weight:bold;z-index:1000;box-shadow:0 4px 12px rgba(0,0,0,0.3);animation:slideIn 0.3s ease}";
  html += ".feedback-info{background:#17a2b8}";
  html += ".feedback-success{background:#28a745}";
  html += ".feedback-warning{background:#ffc107;color:#212529}";
  html += ".feedback-error{background:#dc3545}";
  html += "@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}";
  html += ".loading{opacity:0.6;pointer-events:none}";
  html += ".button-pressed{transform:scale(0.95);background:#0056b3 !important}";
  html += "</style></head><body>";
  
  html += "<div class='container'>";
  html += "<div class='header'>";
  html += "<h1>🤖 Robot Control System</h1>";
  html += "<p>IP: <b>" + WiFi.localIP().toString() + "</b> | WiFi: <b>" + (WiFi.status()==WL_CONNECTED?"Conectado":"Desconectado") + "</b></p>";
  html += "</div>";

  // Estado de conexiones
  html += "<div class='status'>";
  html += "<div class='status-item'>";
  html += "<h3>MEGA</h3>";
  html += "<span class='" + String(megaConectado ? "status-online" : "status-offline") + "'>";
  html += megaConectado ? "🟢 Conectado" : "🔴 Desconectado";
  html += "</span>";
  html += "</div>";
  html += "<div class='status-item'>";
  html += "<h3>UNO</h3>";
  html += "<span class='" + String(unoConectado ? "status-online" : "status-offline") + "'>";
  html += unoConectado ? "🟢 Conectado" : "🔴 Desconectado";
  html += "</span>";
  html += "</div>";
  html += "<div class='status-item'>";
  html += "<h3>Modo Seguridad</h3>";
  html += "<span class='" + String(modoSeguridad ? "status-online" : "status-offline") + "'>";
  html += modoSeguridad ? "🛡️ ACTIVO" : "⚠️ DESACTIVADO";
  html += "</span>";
  html += "</div>";
  html += "<div class='status-item'>";
  html += "<h3>Velocidad</h3>";
  html += "<span class='" + String(modoLento ? "status-online" : "status-offline") + "'>";
  html += modoLento ? "🐌 LENTA" : "⚡ NORMAL";
  html += "</span>";
  html += "</div>";
  html += "</div>";

  // Controles de sistema
  html += "<div class='section'>";
  html += "<h2>⚙️ Configuración del Sistema</h2>";
  html += "<div class='control-group'>";
  html += "<button onclick='cambiarSeguridad()' class='" + String(modoSeguridad ? "danger" : "success") + "'>";
  html += modoSeguridad ? "Desactivar Seguridad" : "Activar Seguridad";
  html += "</button>";
  html += "<button onclick='cambiarVelocidad()' class='" + String(modoLento ? "success" : "danger") + "'>";
  html += modoLento ? "Velocidad Normal" : "Velocidad Lenta";
  html += "</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick='verificarConexiones()' class='success'>🔍 Verificar Conexiones</button>";
  html += "<button onclick='sincronizarSeguridad()' class='success'>🔄 Sincronizar Seguridad</button>";
  html += "<button onclick='enviarPingMega()' class='success'>📡 Ping MEGA</button>";
  html += "<button onclick='enviarPingUno()' class='success'>📡 Ping UNO</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick='posicionDescanso()' class='success'>🛌 Posición Descanso</button>";
  html += "<button onclick='resetRobot()' class='danger'>🔄 Reset Robot</button>";
  html += "<button onclick='reiniciarESP32()' class='danger'>🔄 Reiniciar ESP32</button>";
  html += "</div>";
  html += "</div>";

  // Información detallada de conexiones
  html += "<div class='section'>";
  html += "<h2>📡 Estado de Conexiones</h2>";
  html += "<div id='conexion-info' style='background:#f8f9fa;padding:15px;border-radius:8px;font-family:monospace;'>";
  html += "<h3>Estado General:</h3>";
  html += "<div id='estado-general'>Cargando...</div>";
  html += "<h3>Última Comunicación:</h3>";
  html += "<div id='ultima-comunicacion'>MEGA: " + jsonEscape(ultimoEstadoMega) + "</div>";
  html += "<div id='ultima-comunicacion-uno'>UNO: " + jsonEscape(ultimoEstadoUno) + "</div>";
  html += "<h3>Configuración UART:</h3>";
  html += "<div>ESP32 ↔ MEGA: 115200 baud (TX2:17, RX2:16)</div>";
  html += "<div>ESP32 ↔ UNO: A través del MEGA</div>";
  html += "<h3>Configuración WiFi:</h3>";
  html += "<div>SSID: Senpai | Password: 01234567</div>";
  html += "<div>IP Local: " + WiFi.localIP().toString() + "</div>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick='actualizarEstadoConexiones()' class='success'>🔄 Actualizar Estado</button>";
  html += "<button onclick='testConexiones()' class='success'>🧪 Test Completo</button>";
  html += "</div>";
  html += "</div>";

  // Control de Muñecas con Flechas y Sliders
  html += "<div class='section'>";
  html += "<h2>🦴 Control de Muñecas con Flechas y Sliders</h2>";
  html += "<div id='muñecas-container' class='control-group'>";
  html += "<div style='display:grid;grid-template-columns:repeat(2,1fr);gap:10px;'>";
  html += "<div class='brazo-control'>";
  html += "<h4>Muñeca Derecha</h4>";
  html += "<div class='posicion-display' id='muneca-0'>Posición: 80°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverMuñecaFlecha(0, -1)'>⬅️</button>";
  html += "<button onclick='moverMuñecaFlecha(0, 1)'>➡️</button>";
  html += "</div>";
  html += "<input type='range' id='slider-muneca-0' min='80' max='180' value='80' step='20' onchange='moverMuñecaSlider(0, this.value)' style='width:100%;margin-top:10px;'>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>Muñeca Izquierda</h4>";
  html += "<div class='posicion-display' id='muneca-1'>Posición: 80°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverMuñecaFlecha(1, -1)'>⬅️</button>";
  html += "<button onclick='moverMuñecaFlecha(1, 1)'>➡️</button>";
  html += "</div>";
  html += "<input type='range' id='slider-muneca-1' min='0' max='160' value='80' onchange='moverMuñecaSlider(1, this.value)' style='width:100%;margin-top:10px;'>";
  html += "</div>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=fetch('/munecas/centrar')>Centrar Muñecas</button>";
  html += "<button onclick=fetch('/munecas/aleatorio')>Aleatorio</button>";
  html += "</div>";
  html += "</div>";
  
  // Control manual de muñecas
  html += "<div class='section'>";
  html += "<h2>🦴 Control Manual de Muñecas</h2>";
  html += "<div class='control-group'>";
  html += "<label>Mano:</label><select id=mano_muneca><option value=derecha>Derecha</option><option value=izquierda>Izquierda</option><option value=ambas>Ambas</option></select>";
  html += "<label>Ángulo:</label><input id=angulo_muneca type=number value=80 min=80 max=180 step=20>";
  html += "<button onclick=moverMuñeca()>Mover Muñeca</button>";
  html += "</div>";
  html += "</div>";

  // Control de Manos con Flechas
  html += "<div class='section'>";
  html += "<h2>🤚 Control de Manos con Flechas</h2>";
  html += "<div class='control-group'>";
  html += "<select id=mano><option value=derecha>Derecha</option><option value=izquierda>Izquierda</option><option value=ambas>Ambas</option></select>";
  html += "<button onclick=gesto('paz')>✌️ Paz</button>";
  html += "<button onclick=gesto('rock')>🤘 Rock</button>";
  html += "<button onclick=gesto('ok')>👌 OK</button>";
  html += "<button onclick=gesto('senalar')>👆 Señalar</button>";
  html += "<button onclick=gesto('abrir')>🖐️ Abrir</button>";
  html += "<button onclick=gesto('cerrar')>✊ Cerrar</button>";
  html += "</div>";
  
  // Control de dedos con flechas
  html += "<div id='manos-container' class='control-group'>";
  html += "<h3>Mano Derecha</h3>";
  html += "<div style='display:grid;grid-template-columns:repeat(5,1fr);gap:5px;'>";
  html += "<div class='dedo-control'><h5>Pulgar</h5><div class='posicion-display' id='dedo-0'>0°</div><button onclick='moverDedoFlecha(0, -1)'>⬆️</button><button onclick='moverDedoFlecha(0, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Índice</h5><div class='posicion-display' id='dedo-1'>0°</div><button onclick='moverDedoFlecha(1, -1)'>⬆️</button><button onclick='moverDedoFlecha(1, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Medio</h5><div class='posicion-display' id='dedo-2'>0°</div><button onclick='moverDedoFlecha(2, -1)'>⬆️</button><button onclick='moverDedoFlecha(2, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Anular</h5><div class='posicion-display' id='dedo-3'>0°</div><button onclick='moverDedoFlecha(3, -1)'>⬆️</button><button onclick='moverDedoFlecha(3, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Meñique</h5><div class='posicion-display' id='dedo-4'>0°</div><button onclick='moverDedoFlecha(4, -1)'>⬆️</button><button onclick='moverDedoFlecha(4, 1)'>⬇️</button></div>";
  html += "</div>";
  html += "<h3>Mano Izquierda</h3>";
  html += "<div style='display:grid;grid-template-columns:repeat(5,1fr);gap:5px;'>";
  html += "<div class='dedo-control'><h5>Pulgar</h5><div class='posicion-display' id='dedo-5'>0°</div><button onclick='moverDedoFlecha(5, -1)'>⬆️</button><button onclick='moverDedoFlecha(5, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Índice</h5><div class='posicion-display' id='dedo-6'>0°</div><button onclick='moverDedoFlecha(6, -1)'>⬆️</button><button onclick='moverDedoFlecha(6, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Medio</h5><div class='posicion-display' id='dedo-7'>0°</div><button onclick='moverDedoFlecha(7, -1)'>⬆️</button><button onclick='moverDedoFlecha(7, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Anular</h5><div class='posicion-display' id='dedo-8'>0°</div><button onclick='moverDedoFlecha(8, -1)'>⬆️</button><button onclick='moverDedoFlecha(8, 1)'>⬇️</button></div>";
  html += "<div class='dedo-control'><h5>Meñique</h5><div class='posicion-display' id='dedo-9'>0°</div><button onclick='moverDedoFlecha(9, -1)'>⬆️</button><button onclick='moverDedoFlecha(9, 1)'>⬇️</button></div>";
  html += "</div>";
  html += "</div>";
  
  // Control manual de dedos
  html += "<div class='control-group'>";
  html += "<label>Dedo:</label><select id=dedo><option value=pulgar>Pulgar</option><option value=indice>Índice</option><option value=medio>Medio</option><option value=anular>Anular</option><option value=menique>Meñique</option></select>";
  html += "<label>Ángulo:</label><input id=angulo_dedo type=number value=90 min=0 max=180>";
  html += "<button onclick=moverDedo()>Mover Dedo</button>";
  html += "</div>";
  html += "</div>";

  // Control de Cuello con Flechas
  html += "<div class='section'>";
  html += "<h2>🦴 Control de Cuello con Flechas</h2>";
  html += "<div id='cuello-container' class='control-group'>";
  html += "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;'>";
  html += "<div class='cuello-control'>";
  html += "<h4>Lateral</h4>";
  html += "<div class='posicion-display' id='cuello-0'>Posición: 155°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverCuelloFlecha(0, -1)'>⬅️</button>";
  html += "<button onclick='moverCuelloFlecha(0, 1)'>➡️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='cuello-control'>";
  html += "<h4>Inferior</h4>";
  html += "<div class='posicion-display' id='cuello-1'>Posición: 95°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverCuelloFlecha(1, -1)'>⬆️</button>";
  html += "<button onclick='moverCuelloFlecha(1, 1)'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='cuello-control'>";
  html += "<h4>Superior</h4>";
  html += "<div class='posicion-display' id='cuello-2'>Posición: 105°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverCuelloFlecha(2, -1)'>↩️</button>";
  html += "<button onclick='moverCuelloFlecha(2, 1)'>↪️</button>";
  html += "</div>";
  html += "</div>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=fetch('/cuello/centrar')>Centrar</button>";
  html += "<button onclick=fetch('/cuello/aleatorio')>Aleatorio</button>";
  html += "<button onclick=fetch('/cuello/si')>Sí</button>";
  html += "<button onclick=fetch('/cuello/no')>No</button>";
  html += "</div>";
  html += "</div>";
  
  // Control manual de cuello
  html += "<div class='section'>";
  html += "<h2>🦴 Control Manual de Cuello</h2>";
  html += "<div class='control-group'>";
  html += "<label>Lateral:</label><input id=lateral type=number value=155 min=120 max=190>";
  html += "<label>Inferior:</label><input id=inferior type=number value=95 min=60 max=130>";
  html += "<label>Superior:</label><input id=superior type=number value=105 min=90 max=120>";
  html += "<button onclick=moverCuello()>Mover Cuello</button>";
  html += "</div>";
  html += "</div>";
  
  // Control manual de brazos
  html += "<div class='section'>";
  html += "<h2>💪 Control Manual de Brazos</h2>";
  html += "<div class='control-group'>";
  html += "<label>Brazo Izq:</label><input id=bi type=number value=10 min=10 max=30>";
  html += "<label>Frente Izq:</label><input id=fi type=number value=80 min=60 max=120>";
  html += "<label>High Izq:</label><input id=hi type=number value=80 min=70 max=90>";
  html += "<label>Brazo Der:</label><input id=bd type=number value=40 min=30 max=55>";
  html += "<label>Frente Der:</label><input id=fd type=number value=90 min=70 max=110>";
  html += "<label>High Der:</label><input id=hd type=number value=80 min=70 max=90>";
  html += "<label>Pollo Der:</label><input id=pd type=number value=45 min=0 max=90>";
  html += "<button onclick=moverBrazos()>Mover Brazos</button>";
  html += "</div>";
  html += "</div>";

  // Control de Brazos con Flechas
  html += "<div class='section'>";
  html += "<h2>💪 Control de Brazos con Flechas</h2>";
  html += "<div id='brazos-container' class='control-group'>";
  html += "<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:10px;'>";
  html += "<div class='brazo-control'>";
  html += "<h4>Brazo Izquierdo</h4>";
  html += "<div class='posicion-display' id='brazo-0'>Posición: 10°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(0, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(0, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>Frente Izquierdo</h4>";
  html += "<div class='posicion-display' id='brazo-1'>Posición: 80°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(1, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(1, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>High Izquierdo</h4>";
  html += "<div class='posicion-display' id='brazo-2'>Posición: 80°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(2, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(2, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>Brazo Derecho</h4>";
  html += "<div class='posicion-display' id='brazo-3'>Posición: 40°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(3, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(3, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>Frente Derecho</h4>";
  html += "<div class='posicion-display' id='brazo-4'>Posición: 90°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(4, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(4, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>High Derecho</h4>";
  html += "<div class='posicion-display' id='brazo-5'>Posición: 80°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(5, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(5, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "<div class='brazo-control'>";
  html += "<h4>Pollo Derecho</h4>";
  html += "<div class='posicion-display' id='brazo-6'>Posición: 45°</div>";
  html += "<div class='flechas'>";
  html += "<button onclick='moverBrazoFlecha(6, -1)' style='grid-area:1/2/2/3;'>⬆️</button>";
  html += "<button onclick='moverBrazoFlecha(6, 1)' style='grid-area:3/2/4/3;'>⬇️</button>";
  html += "</div>";
  html += "</div>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=fetch('/brazos/descanso')>Posición Descanso</button>";
  html += "<button onclick=fetch('/brazos/saludo')>Saludo</button>";
  html += "<button onclick=fetch('/brazos/abrazar')>Abrazar</button>";
  html += "</div>";
  html += "</div>";

  // Control Directo de Servos
  html += "<div class='section'>";
  html += "<h2>🔧 Control Directo de Servos</h2>";
  html += "<div class='control-group'>";
  html += "<label>Canal:</label><input id=ch type=number value=0 min=0 max=15>";
  html += "<label>Ángulo:</label><input id=ang type=number value=90 min=0 max=180>";
  html += "<button onclick=moverServo()>Mover Servo</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<label>Comando:</label><input id=cmd type=text value='PING' placeholder='Comando personalizado'>";
  html += "<button onclick=enviarCmd()>Enviar</button>";
  html += "</div>";
  html += "</div>";

  // Control Web Directo de Dedos
  html += "<div class='section'>";
  html += "<h2>👐 Control Web Directo de Dedos</h2>";
  html += "<div class='control-group'>";
  html += "<label>Mano:</label><select id=web_mano><option value=derecha>Derecha</option><option value=izquierda>Izquierda</option></select>";
  html += "<label>Dedo:</label><select id=web_dedo><option value=pulgar>Pulgar</option><option value=indice>Índice</option><option value=medio>Medio</option><option value=anular>Anular</option><option value=menique>Meñique</option></select>";
  html += "<label>Ángulo:</label><input id=web_angulo_dedo type=number value=90 min=0 max=180>";
  html += "<button onclick=moverDedoWeb()>Mover Dedo Web</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=moverDedoWebPos('derecha','pulgar',0)>Pulgar Der Abierto</button>";
  html += "<button onclick=moverDedoWebPos('derecha','pulgar',120)>Pulgar Der Cerrado</button>";
  html += "<button onclick=moverDedoWebPos('izquierda','pulgar',120)>Pulgar Izq Abierto</button>";
  html += "<button onclick=moverDedoWebPos('izquierda','pulgar',0)>Pulgar Izq Cerrado</button>";
  html += "</div>";
  html += "</div>";

  // Control Web de Muñecas
  html += "<div class='section'>";
  html += "<h2>🦴 Control Web de Muñecas</h2>";
  html += "<div class='control-group'>";
  html += "<label>Mano:</label><select id=web_mano_muneca><option value=derecha>Derecha</option><option value=izquierda>Izquierda</option></select>";
  html += "<label>Ángulo:</label><input id=web_angulo_muneca type=number value=80 min=80 max=180 step=20>";
  html += "<button onclick=moverMunecaWeb()>Mover Muñeca Web</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=moverMunecaWebPos('derecha',80)>Muñeca Der Mínimo</button>";
  html += "<button onclick=moverMunecaWebPos('derecha',80)>Muñeca Der Centro</button>";
  html += "<button onclick=moverMunecaWebPos('derecha',180)>Muñeca Der Derecha</button>";
  html += "</div>";
  html += "</div>";

  // Control Web de Brazos
  html += "<div class='section'>";
  html += "<h2>💪 Control Web de Brazos</h2>";
  html += "<div class='control-group'>";
  html += "<h4>Brazo Izquierdo</h4>";
  html += "<label>Brazo:</label><input id=web_bi type=number value=10 min=10 max=30>";
  html += "<label>Frente:</label><input id=web_fi type=number value=80 min=60 max=120>";
  html += "<label>High:</label><input id=web_hi type=number value=80 min=70 max=90>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<h4>Brazo Derecho</h4>";
  html += "<label>Brazo:</label><input id=web_bd type=number value=40 min=0 max=30>";
  html += "<label>Frente:</label><input id=web_fd type=number value=90 min=70 max=110>";
  html += "<label>High:</label><input id=web_hd type=number value=80 min=70 max=90>";
  html += "<label>Pollo:</label><input id=web_pd type=number value=45 min=0 max=90>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=moverBrazosWeb()>Mover Brazos Web</button>";
  html += "<button onclick=moverBrazosWebPos(10,80,80,40,90,80,45)>Posición Descanso</button>";
  html += "</div>";
  html += "</div>";

  // Control Web de Cuello
  html += "<div class='section'>";
  html += "<h2>🦴 Control Web de Cuello</h2>";
  html += "<div class='control-group'>";
  html += "<label>Lateral:</label><input id=web_lateral type=number value=155 min=120 max=190>";
  html += "<label>Inferior:</label><input id=web_inferior type=number value=95 min=60 max=130>";
  html += "<label>Superior:</label><input id=web_superior type=number value=105 min=90 max=120>";
  html += "<button onclick=moverCuelloWeb()>Mover Cuello Web</button>";
  html += "</div>";
  html += "<div class='control-group'>";
  html += "<button onclick=moverCuelloWebPos(155,95,105)>Centro</button>";
  html += "<button onclick=moverCuelloWebPos(120,95,105)>Izquierda</button>";
  html += "<button onclick=moverCuelloWebPos(190,95,105)>Derecha</button>";
  html += "</div>";
  html += "</div>";

  // Debug y Logs
  // Información de posiciones actuales
  html += "<div class='section'>";
  html += "<h2>📊 Posiciones Actuales</h2>";
  html += "<div id='posiciones-info' style='background:#f8f9fa;padding:15px;border-radius:8px;font-family:monospace;'>";
  html += "<h3>Brazos:</h3>";
  html += "<div id='info-brazos'>Cargando...</div>";
  html += "<h3>Manos:</h3>";
  html += "<div id='info-manos'>Cargando...</div>";
  html += "<h3>Muñecas:</h3>";
  html += "<div id='info-munecas'>Cargando...</div>";
  html += "<h3>Cuello:</h3>";
  html += "<div id='info-cuello'>Cargando...</div>";
  html += "</div>";
  html += "<button onclick=actualizarPosiciones()>Actualizar Posiciones</button>";
  html += "</div>";
  
  html += "<div class='section'>";
  html += "<h2>📊 Debug y Logs</h2>";
  html += "<div class='debug' id=log>Esperando datos...</div>";
  html += "<button onclick=limpiarLog()>Limpiar Log</button>";
  html += "<button onclick=exportarLog()>Exportar Log</button>";
  html += "<button onclick=actualizarPosiciones()>Actualizar Posiciones</button>";
  html += "</div>";

  html += "</div>"; // container

  // JavaScript mejorado con feedback visual y manejo de errores
  html += "<script>";
  html += "// Variables globales para control\n";
  html += "let isMoving = false;\n";
  html += "let lastCommand = '';\n";
  html += "let commandQueue = [];\n";
  html += "let isProcessing = false;\n\n";
  
  html += "// Función para mostrar feedback visual\n";
  html += "function showFeedback(message, type = 'info') {\n";
  html += "  const feedback = document.getElementById('feedback') || createFeedbackElement();\n";
  html += "  feedback.textContent = message;\n";
  html += "  feedback.className = `feedback feedback-${type}`;\n";
  html += "  feedback.style.display = 'block';\n";
  html += "  setTimeout(() => { feedback.style.display = 'none'; }, 2000);\n";
  html += "}\n\n";
  
  html += "function createFeedbackElement() {\n";
  html += "  const div = document.createElement('div');\n";
  html += "  div.id = 'feedback';\n";
  html += "  div.style.cssText = 'position:fixed;top:20px;right:20px;padding:10px;border-radius:5px;z-index:1000;display:none;';\n";
  html += "  document.body.appendChild(div);\n";
  html += "  return div;\n";
  html += "}\n\n";
  
  html += "// Función mejorada para enviar comandos con feedback\n";
  html += "async function sendCommand(url, data, successMsg = 'Comando enviado') {\n";
  html += "  if (isMoving) {\n";
  html += "    showFeedback('Robot en movimiento, esperando...', 'warning');\n";
  html += "    return;\n";
  html += "  }\n";
  html += "  \n";
  html += "  isMoving = true;\n";
  html += "  showFeedback('Enviando comando...', 'info');\n";
  html += "  \n";
  html += "  try {\n";
  html += "    const response = await fetch(url, {\n";
  html += "      method: 'POST',\n";
  html += "      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },\n";
  html += "      body: data\n";
  html += "    });\n";
  html += "    \n";
  html += "    if (response.ok) {\n";
  html += "      const result = await response.text();\n";
  html += "      showFeedback(successMsg + ': ' + result, 'success');\n";
  html += "      actualizarPosiciones();\n";
  html += "    } else {\n";
  html += "      showFeedback('Error: ' + response.status, 'error');\n";
  html += "    }\n";
  html += "  } catch (error) {\n";
  html += "    showFeedback('Error de conexión: ' + error.message, 'error');\n";
  html += "  } finally {\n";
  html += "    isMoving = false;\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "// Funciones de control mejoradas\n";
  html += "function gesto(g) {\n";
  html += "  const m = document.getElementById('mano').value;\n";
  html += "  sendCommand('/manos/gesto', `mano=${m}&gesto=${g}`, 'Gesto ejecutado');\n";
  html += "}\n\n";
  
  html += "function moverDedo() {\n";
  html += "  const m = document.getElementById('mano').value;\n";
  html += "  const d = document.getElementById('dedo').value;\n";
  html += "  const a = document.getElementById('angulo_dedo').value;\n";
  html += "  sendCommand('/manos/dedo', `mano=${m}&dedo=${d}&angulo=${a}`, 'Dedo movido');\n";
  html += "}\n\n";
  
  html += "function moverCuello() {\n";
  html += "  const l = document.getElementById('lateral').value;\n";
  html += "  const i = document.getElementById('inferior').value;\n";
  html += "  const s = document.getElementById('superior').value;\n";
  html += "  sendCommand('/cuello/mover', `lateral=${l}&inferior=${i}&superior=${s}`, 'Cuello movido');\n";
  html += "}\n\n";
  
  html += "function moverMuñeca() {\n";
  html += "  const m = document.getElementById('mano_muneca').value;\n";
  html += "  const a = document.getElementById('angulo_muneca').value;\n";
  html += "  sendCommand('/munecas/mover', `mano=${m}&angulo=${a}`, 'Muñeca movida');\n";
  html += "}\n\n";
  
  html += "function moverBrazos() {\n";
  html += "  const bi = document.getElementById('bi').value;\n";
  html += "  const fi = document.getElementById('fi').value;\n";
  html += "  const hi = document.getElementById('hi').value;\n";
  html += "  const bd = document.getElementById('bd').value;\n";
  html += "  const fd = document.getElementById('fd').value;\n";
  html += "  const hd = document.getElementById('hd').value;\n";
  html += "  const pd = document.getElementById('pd').value;\n";
  html += "  sendCommand('/brazos/mover', `bi=${bi}&fi=${fi}&hi=${hi}&bd=${bd}&fd=${fd}&hd=${hd}&pd=${pd}`, 'Brazos movidos');\n";
  html += "}\n\n";
  
  html += "function moverServo() {\n";
  html += "  const c = document.getElementById('ch').value;\n";
  html += "  const a = document.getElementById('ang').value;\n";
  html += "  sendCommand('/servo', `ch=${c}&ang=${a}`, 'Servo movido');\n";
  html += "}\n\n";
  
  html += "function enviarCmd() {\n";
  html += "  const c = document.getElementById('cmd').value;\n";
  html += "  sendCommand('/cmd', `cmd=${encodeURIComponent(c)}`, 'Comando enviado');\n";
  html += "}\n\n";
  
  html += "function limpiarLog() {\n";
  html += "  document.getElementById('log').innerHTML = 'Log limpiado';\n";
  html += "  showFeedback('Log limpiado', 'info');\n";
  html += "}\n\n";
  
  html += "function exportarLog() {\n";
  html += "  const log = document.getElementById('log').innerText;\n";
  html += "  const blob = new Blob([log], { type: 'text/plain' });\n";
  html += "  const url = URL.createObjectURL(blob);\n";
  html += "  const a = document.createElement('a');\n";
  html += "  a.href = url;\n";
  html += "  a.download = 'robot_log.txt';\n";
  html += "  a.click();\n";
  html += "  showFeedback('Log exportado', 'success');\n";
  html += "}\n\n";
  
  html += "async function cambiarSeguridad() {\n";
  html += "  try {\n";
  html += "    const isCurrentlyDanger = document.querySelector('button[onclick=\"cambiarSeguridad()\"]').classList.contains('danger');\n";
  html += "    const r = await fetch('/system/security?on=' + (!isCurrentlyDanger ? 'true' : 'false'));\n";
  html += "    const t = await r.text();\n";
  html += "    showFeedback(t, 'success');\n";
  html += "    setTimeout(() => location.reload(), 1000);\n";
  html += "  } catch (e) {\n";
  html += "    showFeedback('Error al cambiar seguridad: ' + e.message, 'error');\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "async function cambiarVelocidad() {\n";
  html += "  try {\n";
  html += "    const isCurrentlySuccess = document.querySelector('button[onclick=\"cambiarVelocidad()\"]').classList.contains('success');\n";
  html += "    const r = await fetch('/system/speed?slow=' + (!isCurrentlySuccess ? 'true' : 'false'));\n";
  html += "    const t = await r.text();\n";
  html += "    showFeedback(t, 'success');\n";
  html += "    setTimeout(() => location.reload(), 1000);\n";
  html += "  } catch (e) {\n";
  html += "    showFeedback('Error al cambiar velocidad: ' + e.message, 'error');\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "async function poll() {\n";
  html += "  try {\n";
  html += "    const r = await fetch('/debug');\n";
  html += "    const t = await r.text();\n";
  html += "    document.getElementById('log').innerHTML = t.replace(/\\n/g, '<br>');\n";
  html += "  } catch (e) {\n";
  html += "    console.error('Error en poll:', e);\n";
  html += "  }\n";
  html += "  setTimeout(poll, 1000);\n";
  html += "}\n";
  html += "poll();\n";
  
  // Funciones mejoradas para control con flechas
  html += "async function moverBrazoFlecha(indice, direccion) {\n";
  html += "  const nombres = ['Brazo Izq', 'Frente Izq', 'High Izq', 'Brazo Der', 'Frente Der', 'High Der', 'Pollo Der'];\n";
  html += "  const nombre = nombres[indice] || 'Brazo';\n";
  html += "  const dir = direccion > 0 ? 'incrementar' : 'decrementar';\n";
  html += "  await sendCommand('/brazos/flecha', `indice=${indice}&direccion=${direccion}`, `${nombre} ${dir}`);\n";
  html += "}\n\n";
  
  html += "async function moverDedoFlecha(indice, direccion) {\n";
  html += "  const nombres = ['D-Pulgar', 'D-Índice', 'D-Medio', 'D-Anular', 'D-Meñique', 'I-Pulgar', 'I-Índice', 'I-Medio', 'I-Anular', 'I-Meñique'];\n";
  html += "  const nombre = nombres[indice] || 'Dedo';\n";
  html += "  const dir = direccion > 0 ? 'incrementar' : 'decrementar';\n";
  html += "  await sendCommand('/manos/flecha', `indice=${indice}&direccion=${direccion}`, `${nombre} ${dir}`);\n";
  html += "}\n\n";
  
  html += "async function moverMuñecaFlecha(indice, direccion) {\n";
  html += "  const nombres = ['Muñeca Der', 'Muñeca Izq'];\n";
  html += "  const nombre = nombres[indice] || 'Muñeca';\n";
  html += "  const dir = direccion > 0 ? 'incrementar' : 'decrementar';\n";
  html += "  await sendCommand('/munecas/flecha', `indice=${indice}&direccion=${direccion}`, `${nombre} ${dir}`);\n";
  html += "}\n\n";
  
  html += "async function moverCuelloFlecha(indice, direccion) {\n";
  html += "  const nombres = ['Lateral', 'Inferior', 'Superior'];\n";
  html += "  const nombre = nombres[indice] || 'Cuello';\n";
  html += "  const dir = direccion > 0 ? 'incrementar' : 'decrementar';\n";
  html += "  await sendCommand('/cuello/flecha', `indice=${indice}&direccion=${direccion}`, `Cuello ${nombre} ${dir}`);\n";
  html += "}\n\n";
  
  html += "// Función para control con sliders\n";
  html += "async function moverMuñecaSlider(indice, valor) {\n";
  html += "  const nombres = ['Muñeca Der', 'Muñeca Izq'];\n";
  html += "  const nombre = nombres[indice] || 'Muñeca';\n";
  html += "  const mano = indice === 0 ? 'derecha' : 'izquierda';\n";
  html += "  \n";
  html += "  // Para muñeca derecha, asegurar que el valor sea múltiplo de 20 y no baje de 80\n";
  html += "  if (indice === 0) {\n";
  html += "    valor = Math.round(valor / 20) * 20;\n";
  html += "    if (valor < 80) valor = 80; // No permitir valores menores a 80\n";
  html += "    // Actualizar el slider para mostrar el valor correcto\n";
  html += "    document.getElementById(`slider-muneca-${indice}`).value = valor;\n";
  html += "  }\n";
  html += "  \n";
  html += "  await sendCommand('/munecas/mover', `mano=${mano}&angulo=${valor}`, `${nombre} movida a ${valor}°`);\n";
  html += "}\n\n";
  html += "// Función mejorada para actualizar posiciones\n";
  html += "async function actualizarPosiciones() {\n";
  html += "  try {\n";
  html += "    const r = await fetch('/posiciones');\n";
  html += "    if (!r.ok) throw new Error('Error al obtener posiciones');\n";
  html += "    const data = await r.json();\n";
  html += "    actualizarDisplayBrazos(data.brazos);\n";
  html += "    actualizarDisplayManos(data.manos);\n";
  html += "    actualizarDisplayMunecas(data.munecas);\n";
  html += "    actualizarDisplayCuello(data.cuello);\n";
  html += "    actualizarInfoPosiciones(data);\n";
  html += "  } catch (e) {\n";
  html += "    console.error('Error actualizando posiciones:', e);\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "function actualizarDisplayBrazos(brazos) {\n";
  html += "  brazos.forEach((brazo, i) => {\n";
  html += "    const el = document.getElementById(`brazo-${i}`);\n";
  html += "    if (el) {\n";
  html += "      el.textContent = `Posición: ${brazo.posicion}°`;\n";
  html += "      el.style.backgroundColor = getColorByPosition(brazo.posicion, brazo.min, brazo.max);\n";
  html += "    }\n";
  html += "  });\n";
  html += "}\n\n";
  
  html += "function actualizarDisplayManos(manos) {\n";
  html += "  manos.forEach((mano, i) => {\n";
  html += "    const el = document.getElementById(`dedo-${i}`);\n";
  html += "    if (el) {\n";
  html += "      el.textContent = `${mano.posicion}°`;\n";
  html += "      el.style.backgroundColor = getColorByPosition(mano.posicion, mano.min, mano.max);\n";
  html += "    }\n";
  html += "  });\n";
  html += "}\n\n";
  
  html += "function actualizarDisplayMunecas(munecas) {\n";
  html += "  munecas.forEach((m, i) => {\n";
  html += "    const el = document.getElementById(`muneca-${i}`);\n";
  html += "    const slider = document.getElementById(`slider-muneca-${i}`);\n";
  html += "    if (el) {\n";
  html += "      el.textContent = `Posición: ${m.posicion}°`;\n";
  html += "      el.style.backgroundColor = getColorByPosition(m.posicion, m.min, m.max);\n";
  html += "    }\n";
  html += "    if (slider) {\n";
  html += "      // Para muñeca derecha (i=0), asegurar que el valor sea múltiplo de 20 y no baje de 80\n";
  html += "      let valor = m.posicion;\n";
  html += "      if (i === 0) {\n";
  html += "        valor = Math.round(m.posicion / 20) * 20;\n";
  html += "        if (valor < 80) valor = 80; // No permitir valores menores a 80\n";
  html += "      }\n";
  html += "      slider.value = valor;\n";
  html += "    }\n";
  html += "  });\n";
  html += "}\n\n";
  
  html += "function actualizarDisplayCuello(cuello) {\n";
  html += "  cuello.forEach((c, i) => {\n";
  html += "    const el = document.getElementById(`cuello-${i}`);\n";
  html += "    if (el) {\n";
  html += "      el.textContent = `Posición: ${c.posicion}°`;\n";
  html += "      el.style.backgroundColor = getColorByPosition(c.posicion, c.min, c.max);\n";
  html += "    }\n";
  html += "  });\n";
  html += "}\n\n";
  
  html += "function actualizarInfoPosiciones(data) {\n";
  html += "  const infoBrazos = document.getElementById('info-brazos');\n";
  html += "  const infoManos = document.getElementById('info-manos');\n";
  html += "  const infoMunecas = document.getElementById('info-munecas');\n";
  html += "  const infoCuello = document.getElementById('info-cuello');\n";
  html += "  \n";
  html += "  if (infoBrazos) infoBrazos.innerHTML = data.brazos.map(b => `${b.nombre}: ${b.posicion}° (${b.min}-${b.max}°)`).join('<br>');\n";
  html += "  if (infoManos) infoManos.innerHTML = data.manos.map(m => `${m.nombre}: ${m.posicion}° (${m.min}-${m.max}°)`).join('<br>');\n";
  html += "  if (infoMunecas) infoMunecas.innerHTML = data.munecas.map(m => `${m.nombre}: ${m.posicion}° (${m.min}-${m.max}°)`).join('<br>');\n";
  html += "  if (infoCuello) infoCuello.innerHTML = data.cuello.map(c => `${c.nombre}: ${c.posicion}° (${c.min}-${c.max}°)`).join('<br>');\n";
  html += "}\n\n";
  
  html += "// Función para obtener color según posición (verde=normal, amarillo=medio, rojo=extremo)\n";
  html += "function getColorByPosition(pos, min, max) {\n";
  html += "  const range = max - min;\n";
  html += "  const normalized = (pos - min) / range;\n";
  html += "  if (normalized < 0.2 || normalized > 0.8) return '#ff6b6b';\n";
  html += "  if (normalized < 0.3 || normalized > 0.7) return '#ffd93d';\n";
  html += "  return '#6bcf7f';\n";
  html += "}\n\n";

  // Funciones de conexión y sistema mejoradas
  html += "async function verificarConexiones() {\n";
  html += "  await sendCommand('/system/check', '', 'Verificación enviada');\n";
  html += "}\n\n";
  
  html += "async function sincronizarSeguridad() {\n";
  html += "  await sendCommand('/system/sync-security', '', 'Seguridad sincronizada');\n";
  html += "}\n\n";
  
  html += "async function enviarPingMega() {\n";
  html += "  await sendCommand('/cmd', 'cmd=PING', 'Ping enviado al MEGA');\n";
  html += "}\n\n";
  
  html += "async function enviarPingUno() {\n";
  html += "  await sendCommand('/cmd', 'cmd=UNO:PING', 'Ping enviado al UNO');\n";
  html += "}\n\n";
  
  html += "async function posicionDescanso() {\n";
  html += "  await sendCommand('/system/descanso', '', 'Robot movido a posición de descanso');\n";
  html += "}\n\n";
  
  html += "async function resetRobot() {\n";
  html += "  if (confirm('¿Está seguro de resetear el robot?')) {\n";
  html += "    await sendCommand('/system/reset', '', 'Robot reseteado');\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "async function reiniciarESP32() {\n";
  html += "  if (confirm('¿Está seguro de reiniciar la ESP32?')) {\n";
  html += "    showFeedback('Reiniciando ESP32...', 'info');\n";
  html += "    try {\n";
  html += "      await fetch('/system/restart');\n";
  html += "      setTimeout(() => { location.reload(); }, 3000);\n";
  html += "    } catch (e) {\n";
  html += "      showFeedback('Error al reiniciar ESP32: ' + e.message, 'error');\n";
  html += "    }\n";
  html += "  }\n";
  html += "}\n\n";
  html += "async function actualizarEstadoConexiones() {\n";
  html += "  try {\n";
  html += "    const r = await fetch('/system/status');\n";
  html += "    const data = await r.json();\n";
  html += "    const estadoGeneral = document.getElementById('estado-general');\n";
  html += "    if (estadoGeneral) {\n";
  html += "      estadoGeneral.innerHTML = `WiFi: ${data.wifi ? '🟢 Conectado' : '🔴 Desconectado'}<br>MEGA: ${data.mega ? '🟢 Conectado' : '🔴 Desconectado'}<br>UNO: ${data.uno ? '🟢 Conectado' : '🔴 Desconectado'}<br>Seguridad: ${data.seguridad ? '🛡️ ACTIVA' : '⚠️ DESACTIVADA'}<br>Velocidad: ${data.velocidad ? '🐌 LENTA' : '⚡ NORMAL'}<br>Uptime: ${data.uptime}s`;\n";
  html += "    }\n";
  html += "  } catch (e) {\n";
  html += "    console.error('Error:', e);\n";
  html += "    showFeedback('Error al actualizar estado de conexiones', 'error');\n";
  html += "  }\n";
  html += "}\n\n";
  
  html += "async function testConexiones() {\n";
  html += "  showFeedback('Iniciando test completo de conexiones...', 'info');\n";
  html += "  try {\n";
  html += "    await verificarConexiones();\n";
  html += "    await new Promise(r => setTimeout(r, 1000));\n";
  html += "    await enviarPingMega();\n";
  html += "    await new Promise(r => setTimeout(r, 1000));\n";
  html += "    await enviarPingUno();\n";
  html += "    await new Promise(r => setTimeout(r, 1000));\n";
  html += "    await sincronizarSeguridad();\n";
  html += "    await new Promise(r => setTimeout(r, 1000));\n";
  html += "    await actualizarEstadoConexiones();\n";
  html += "    showFeedback('Test completo finalizado', 'success');\n";
  html += "  } catch (e) {\n";
  html += "    console.error('Error:', e);\n";
  html += "    showFeedback('Error durante el test de conexiones', 'error');\n";
  html += "  }\n";
  html += "}\n\n";

  html += "async function actualizarComunicacion() {\n";
  html += "  try {\n";
  html += "    const r = await fetch('/debug');\n";
  html += "    const log = await r.text();\n";
  html += "    const lineas = log.split('\\n');\n";
  html += "    let ultimaMega = '';\n";
  html += "    let ultimaUno = '';\n";
  html += "    for (let i = lineas.length - 1; i >= 0; i--) {\n";
  html += "      const linea = lineas[i];\n";
  html += "      if (linea.includes('[MEGA]') && !ultimaMega) {\n";
  html += "        ultimaMega = linea.replace('[MEGA] ', '');\n";
  html += "      }\n";
  html += "      if (linea.includes('UNO:') && !ultimaUno) {\n";
  html += "        ultimaUno = linea.replace('UNO:', '');\n";
  html += "      }\n";
  html += "    }\n";
  html += "    const elMega = document.getElementById('ultima-comunicacion');\n";
  html += "    const elUno = document.getElementById('ultima-comunicacion-uno');\n";
  html += "    if (elMega) elMega.textContent = 'MEGA: ' + ultimaMega;\n";
  html += "    if (elUno) elUno.textContent = 'UNO: ' + ultimaUno;\n";
  html += "  } catch (e) {\n";
  html += "    console.error('Error:', e);\n";
  html += "  }\n";
  html += "}\n\n";

  // ===== FUNCIONES PARA CONTROL WEB DIRECTO MEJORADAS =====
  html += "async function moverDedoWeb() {\n";
  html += "  const m = document.getElementById('web_mano').value;\n";
  html += "  const d = document.getElementById('web_dedo').value;\n";
  html += "  const a = document.getElementById('web_angulo_dedo').value;\n";
  html += "  await sendCommand('/web/dedo', `mano=${m}&dedo=${d}&angulo=${a}`, 'Dedo movido desde web');\n";
  html += "}\n\n";
  
  html += "async function moverDedoWebPos(mano, dedo, angulo) {\n";
  html += "  await sendCommand('/web/dedo', `mano=${mano}&dedo=${dedo}&angulo=${angulo}`, `${mano} ${dedo} movido a ${angulo}°`);\n";
  html += "}\n\n";
  
  html += "async function moverMunecaWeb() {\n";
  html += "  const m = document.getElementById('web_mano_muneca').value;\n";
  html += "  const a = document.getElementById('web_angulo_muneca').value;\n";
  html += "  await sendCommand('/web/muneca', `mano=${m}&angulo=${a}`, 'Muñeca movida desde web');\n";
  html += "}\n\n";
  
  html += "async function moverMunecaWebPos(mano, angulo) {\n";
  html += "  await sendCommand('/web/muneca', `mano=${mano}&angulo=${angulo}`, `Muñeca ${mano} movida a ${angulo}°`);\n";
  html += "}\n\n";
  
  html += "async function moverBrazosWeb() {\n";
  html += "  const bi = document.getElementById('web_bi').value;\n";
  html += "  const fi = document.getElementById('web_fi').value;\n";
  html += "  const hi = document.getElementById('web_hi').value;\n";
  html += "  const bd = document.getElementById('web_bd').value;\n";
  html += "  const fd = document.getElementById('web_fd').value;\n";
  html += "  const hd = document.getElementById('web_hd').value;\n";
  html += "  const pd = document.getElementById('web_pd').value;\n";
  html += "  await sendCommand('/web/brazos', `bi=${bi}&fi=${fi}&hi=${hi}&bd=${bd}&fd=${fd}&hd=${hd}&pd=${pd}`, 'Brazos movidos desde web');\n";
  html += "}\n\n";
  
  html += "async function moverBrazosWebPos(bi, fi, hi, bd, fd, hd, pd) {\n";
  html += "  await sendCommand('/web/brazos', `bi=${bi}&fi=${fi}&hi=${hi}&bd=${bd}&fd=${fd}&hd=${hd}&pd=${pd}`, 'Brazos movidos a posición específica');\n";
  html += "}\n\n";
  
  html += "async function moverCuelloWeb() {\n";
  html += "  const l = document.getElementById('web_lateral').value;\n";
  html += "  const i = document.getElementById('web_inferior').value;\n";
  html += "  const s = document.getElementById('web_superior').value;\n";
  html += "  await sendCommand('/web/cuello', `lateral=${l}&inferior=${i}&superior=${s}`, 'Cuello movido desde web');\n";
  html += "}\n\n";
  
  html += "async function moverCuelloWebPos(lateral, inferior, superior) {\n";
  html += "  await sendCommand('/web/cuello', `lateral=${lateral}&inferior=${inferior}&superior=${superior}`, 'Cuello movido a posición específica');\n";
  html += "}\n\n";

  // Configuración de intervalos mejorada
  html += "setInterval(actualizarPosiciones, 1000); // Actualizar posiciones cada segundo\n";
  html += "setInterval(actualizarEstadoConexiones, 5000);\n";
  html += "setInterval(actualizarComunicacion, 3000);\n";
  html += "\n";
  html += "// Función para añadir efectos visuales a los botones\n";
  html += "function addButtonEffects() {\n";
  html += "  document.querySelectorAll('button').forEach(btn => {\n";
  html += "    btn.addEventListener('mousedown', function() {\n";
  html += "      this.classList.add('button-pressed');\n";
  html += "    });\n";
  html += "    btn.addEventListener('mouseup', function() {\n";
  html += "      this.classList.remove('button-pressed');\n";
  html += "    });\n";
  html += "    btn.addEventListener('mouseleave', function() {\n";
  html += "      this.classList.remove('button-pressed');\n";
  html += "    });\n";
  html += "  });\n";
  html += "}\n\n";
  html += "\n";
  html += "// Inicialización cuando se carga la página\n";
  html += "window.onload = function() {\n";
  html += "  actualizarPosiciones();\n";
  html += "  actualizarEstadoConexiones();\n";
  html += "  actualizarComunicacion();\n";
  html += "  addButtonEffects();\n";
  html += "  showFeedback('Sistema de control del robot cargado', 'success');\n";
  html += "};\n";
  html += "</script></body></html>";

  server.send(200, "text/html", html);
}

// ===== HANDLERS DE ENDPOINTS =====

// Sistema
void handleSystemSecurity() {
  String onValue = server.arg("on");
  modoSeguridad = (onValue == "1" || onValue == "true");
  
  // Sincronizar con el MEGA
  String comandoSeguridad = modoSeguridad ? "SEGURIDAD ON" : "SEGURIDAD OFF";
  sendToMega(comandoSeguridad);
  
  server.send(200, "text/plain", modoSeguridad ? "Seguridad ACTIVADA" : "Seguridad DESACTIVADA");
}

void handleSystemSpeed() {
  String slowValue = server.arg("slow");
  modoLento = (slowValue == "1" || slowValue == "true");
  server.send(200, "text/plain", modoLento ? "Velocidad LENTA" : "Velocidad NORMAL");
}

void handleSystemCheck() {
  checkConnections();
  server.send(200, "text/plain", "Verificación enviada");
}

void handleSystemSyncSecurity() {
  sincronizarSeguridad();
  server.send(200, "text/plain", "Seguridad sincronizada con MEGA");
}

void handleSystemReset() {
  sendToMega("RESET");
  server.send(200, "text/plain", "Reset enviado");
}

void handleSystemRestart() {
  server.send(200, "text/plain", "Reiniciando ESP32...");
  delay(1000);
  ESP.restart();
}

void handleSystemStatus() {
  String json = "{";
  json += "\"wifi\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
  json += "\"mega\":" + String(megaConectado ? "true" : "false") + ",";
  json += "\"uno\":" + String(unoConectado ? "true" : "false") + ",";
  json += "\"seguridad\":" + String(modoSeguridad ? "true" : "false") + ",";
  json += "\"velocidad\":" + String(modoLento ? "true" : "false") + ",";
  json += "\"uptime\":" + String(millis() / 1000) + ",";
  json += "\"ip\":\"" + WiFi.localIP().toString() + "\",";
  json += "\"ssid\":\"" + WiFi.SSID() + "\"";
  json += "}";

  server.send(200, "application/json", json);
}

void handleSystemDescanso() {
  posicionDescanso();
  server.send(200, "text/plain", "Robot movido a posición de descanso");
}

// ===== ENDPOINTS PARA SECUENCIAS =====

// Endpoint para comandos de secuencia
void handleSequenceCommand() {
  String command = server.arg("command");
  String params = server.arg("params");
  
  if (command.length() == 0) {
    server.send(400, "text/plain", "Comando vacío");
    return;
  }
  
  Serial.print("📋 Comando de secuencia recibido: ");
  Serial.print(command);
  if (params.length() > 0) {
    Serial.print(" con parámetros: ");
    Serial.print(params);
  }
  Serial.println();
  
  // Procesar comandos de secuencia
  if (command == "BRAZOS") {
    // Extraer parámetros BI, FI, HI, BD, FD, HD, PD
    int bi = extraerValor(params, "BI=");
    int fi = extraerValor(params, "FI=");
    int hi = extraerValor(params, "HI=");
    int bd = extraerValor(params, "BD=");
    int fd = extraerValor(params, "FD=");
    int hd = extraerValor(params, "HD=");
    int pd = extraerValor(params, "PD=");
    
    if (bi >= 0 && fi >= 0 && hi >= 0 && bd >= 0 && fd >= 0 && hd >= 0 && pd >= 0) {
      controlarBrazos(bi, fi, hi, bd, fd, hd, pd);
      server.send(200, "text/plain", "Brazos movidos por secuencia");
    } else {
      server.send(400, "text/plain", "Parámetros de brazos inválidos");
    }
  }
  else if (command == "GESTO") {
    // Extraer parámetros de gesto
    String mano = "";
    String gesto = "";
    
    if (params.indexOf("mano=") >= 0) {
      int start = params.indexOf("mano=") + 5;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      mano = params.substring(start, end);
    }
    
    if (params.indexOf("gesto=") >= 0) {
      int start = params.indexOf("gesto=") + 6;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      gesto = params.substring(start, end);
    }
    
    if (mano.length() > 0 && gesto.length() > 0) {
      if (gesto == "paz") gestoPaz(mano);
      else if (gesto == "rock") gestoRock(mano);
      else if (gesto == "ok") gestoOK(mano);
      else if (gesto == "senalar") gestoSeñalar(mano);
      else if (gesto == "ABRIR") {
        controlarMano(mano, "abrir");
      }
      else if (gesto == "CERRAR") {
        controlarMano(mano, "cerrar");
      }
      else controlarMano(mano, gesto);
      
      server.send(200, "text/plain", "Gesto ejecutado por secuencia");
    } else {
      server.send(400, "text/plain", "Parámetros de gesto inválidos");
    }
  }
  else if (command == "HABLAR") {
    // Extraer texto a hablar
    String texto = "";
    if (params.indexOf("texto=") >= 0) {
      int start = params.indexOf("texto=") + 6;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      texto = params.substring(start, end);
    }
    
    if (texto.length() > 0) {
      // Enviar comando de habla al MEGA
      String comandoHabla = "HABLAR TEXTO=" + texto;
      sendToMega(comandoHabla);
      server.send(200, "text/plain", "Comando de habla enviado: " + texto);
    } else {
      server.send(400, "text/plain", "Texto de habla vacío");
    }
  }
  else if (command == "ESPERAR") {
    // Extraer tiempo de espera
    int tiempo = 1000; // Default 1 segundo
    if (params.indexOf("tiempo=") >= 0) {
      int start = params.indexOf("tiempo=") + 7;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      tiempo = params.substring(start, end).toInt();
    }
    
    if (tiempo > 0) {
      // Enviar comando de espera al MEGA
      String comandoEspera = "ESPERAR TIEMPO=" + String(tiempo);
      sendToMega(comandoEspera);
      server.send(200, "text/plain", "Comando de espera enviado: " + String(tiempo) + "ms");
    } else {
      server.send(400, "text/plain", "Tiempo de espera inválido");
    }
  }
  else if (command == "CUELLO") {
    // Extraer parámetros L, I, S
    int l = extraerValor(params, "L=");
    int i = extraerValor(params, "I=");
    int s = extraerValor(params, "S=");
    
    if (l >= 0 && i >= 0 && s >= 0) {
      controlarCuello(l, i, s);
      server.send(200, "text/plain", "Cuello movido por secuencia");
    } else {
      server.send(400, "text/plain", "Parámetros de cuello inválidos");
    }
  }
  else if (command == "MANO") {
    // Extraer parámetros de mano
    String mano = "";
    String accion = "";
    int angulo = -1;
    
    if (params.indexOf("M=") >= 0) {
      int start = params.indexOf("M=") + 2;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      mano = params.substring(start, end);
    }
    
    if (params.indexOf("A=") >= 0) {
      int start = params.indexOf("A=") + 2;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      accion = params.substring(start, end);
    }
    
    if (params.indexOf("ANG=") >= 0) {
      int start = params.indexOf("ANG=") + 4;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      angulo = params.substring(start, end).toInt();
    }
    
    if (mano.length() > 0 && accion.length() > 0) {
      controlarMano(mano, accion, angulo);
      server.send(200, "text/plain", "Mano controlada por secuencia");
    } else {
      server.send(400, "text/plain", "Parámetros de mano inválidos");
    }
  }
  else if (command == "MUNECA") {
    // Extraer parámetros de muñeca (formato: mano=X angulo=Y)
    String mano = "";
    int angulo = -1;

    if (params.indexOf("mano=") >= 0) {
      int start = params.indexOf("mano=") + 5;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      mano = params.substring(start, end);
    }

    if (params.indexOf("angulo=") >= 0) {
      int start = params.indexOf("angulo=") + 7;
      int end = params.indexOf(" ", start);
      if (end == -1) end = params.length();
      angulo = params.substring(start, end).toInt();
    }

    if (mano.length() > 0 && angulo >= 0) {
      controlarMuñeca(mano, angulo);
      server.send(200, "text/plain", "Muñeca movida por secuencia");
    } else {
      Serial.print("DEBUG: mano='"); Serial.print(mano);
      Serial.print("' angulo="); Serial.println(angulo);
      server.send(400, "text/plain", "Parámetros de muñeca inválidos");
    }
  }
  else {
    // Comando no reconocido, enviarlo directamente al MEGA
    sendToMega(command + " " + params);
    server.send(200, "text/plain", "Comando enviado al MEGA: " + command + " " + params);
  }
}

// Endpoint para ejecutar secuencia completa
void handleExecuteSequence() {
  String sequenceName = server.arg("sequence");
  
  if (sequenceName.length() == 0) {
    server.send(400, "text/plain", "Nombre de secuencia vacío");
    return;
  }
  
  Serial.print("🎬 Ejecutando secuencia: ");
  Serial.println(sequenceName);
  
  // Por ahora solo confirmamos que se recibió la secuencia
  // En el futuro se podría cargar y ejecutar desde aquí
  server.send(200, "text/plain", "Secuencia recibida: " + sequenceName);
}

// Manos
void handleManoGesto() {
  String mano = server.arg("mano");
  String gesto = server.arg("gesto");
  
  if (gesto == "paz") gestoPaz(mano);
  else if (gesto == "rock") gestoRock(mano);
  else if (gesto == "ok") gestoOK(mano);
  else if (gesto == "senalar") gestoSeñalar(mano);
  else if (gesto == "abrir") controlarMano(mano, "abrir");
  else if (gesto == "cerrar") controlarMano(mano, "cerrar");
  else if (gesto == "ABRIR") controlarMano(mano, "abrir");
  else if (gesto == "CERRAR") controlarMano(mano, "cerrar");
  else controlarMano(mano, gesto);
  
  server.send(200, "text/plain", "Gesto enviado");
}

void handleManoDedo() {
  String mano = server.arg("mano");
  String dedo = server.arg("dedo");
  int angulo = server.arg("angulo").toInt();
  
  controlarDedo(mano, dedo, angulo);
  server.send(200, "text/plain", "Dedo movido");
}

void handleManoFlecha() {
  int indice = server.arg("indice").toInt();
  int direccion = server.arg("direccion").toInt();
  
  moverDedoConFlecha(indice, direccion);
  server.send(200, "text/plain", "Dedo movido con flecha");
}

// Muñecas
void handleMuñecaMover() {
  String mano = server.arg("mano");
  int angulo = server.arg("angulo").toInt();
  
  controlarMuñeca(mano, angulo);
  server.send(200, "text/plain", "Muñeca movida");
}

void handleMuñecaFlecha() {
  int indice = server.arg("indice").toInt();
  int direccion = server.arg("direccion").toInt();
  
  moverMuñecaConFlecha(indice, direccion);
  server.send(200, "text/plain", "Muñeca movida con flecha");
}

void handleMuñecaCentrar() { 
  // Muñeca derecha - usar sistema relativo para ir a 80°
  controlarMuñecaDerechaRelativa(80);
  
  // Muñeca izquierda - sistema normal
  controlarMuñeca("izquierda", 80);
  
  // Actualizar posiciones de centrado
  posicionRelativaMuñecaDerecha = 80; // Derecha
  posActualMuñecas[0] = 80; // Derecha
  posActualMuñecas[1] = 80; // Izquierda
  
  server.send(200, "text/plain", "Muñecas centradas en 80°"); 
}

void handleMuñecaAleatorio() { 
  // Para muñeca derecha, generar ángulo en múltiplos de 20 entre 80 y 180
  int anguloDerecha = random(4, 10) * 20; // 80, 100, 120, 140, 160, 180
  int anguloIzquierda = random(0, 161);
  
  // Muñeca derecha - usar sistema relativo
  controlarMuñecaDerechaRelativa(anguloDerecha);
  
  // Muñeca izquierda - sistema normal
  controlarMuñeca("izquierda", anguloIzquierda);
  
  server.send(200, "text/plain", "Muñecas en posición aleatoria"); 
}

// Cuello
void handleCuelloMover() {
  int lateral = server.arg("lateral").toInt();
  int inferior = server.arg("inferior").toInt();
  int superior = server.arg("superior").toInt();
  
  controlarCuello(lateral, inferior, superior);
  server.send(200, "text/plain", "Cuello movido");
}

void handleCuelloFlecha() {
  int indice = server.arg("indice").toInt();
  int direccion = server.arg("direccion").toInt();
  
  moverCuelloConFlecha(indice, direccion);
  server.send(200, "text/plain", "Cuello movido con flecha");
}

void handleCuelloCentrar() { 
  controlarCuello(155, 95, 105); 
  
  // Actualizar posiciones de centrado
  posActualCuello[0] = 155; // Lateral
  posActualCuello[1] = 95;  // Inferior
  posActualCuello[2] = 105; // Superior
  
  server.send(200, "text/plain", "Cuello centrado"); 
}

void handleCuelloAleatorio() { 
  sendToMega("CUELLO ALEATORIO"); 
  server.send(200, "text/plain", "Cuello aleatorio"); 
}

void handleCuelloSi() { 
  sendToMega("CUELLO SI"); 
  server.send(200, "text/plain", "Cuello: Sí"); 
}

void handleCuelloNo() { 
  sendToMega("CUELLO NO"); 
  server.send(200, "text/plain", "Cuello: No"); 
}

// Brazos
void handleBrazosMover() {
  int bi = server.arg("bi").toInt();
  int fi = server.arg("fi").toInt();
  int hi = server.arg("hi").toInt();
  int bd = server.arg("bd").toInt();
  int fd = server.arg("fd").toInt();
  int hd = server.arg("hd").toInt();
  int pd = server.arg("pd").toInt();
  
  controlarBrazos(bi, fi, hi, bd, fd, hd, pd);
  server.send(200, "text/plain", "Brazos movidos");
}

void handleBrazosFlecha() {
  int indice = server.arg("indice").toInt();
  int direccion = server.arg("direccion").toInt();
  
  moverBrazoConFlecha(indice, direccion);
  server.send(200, "text/plain", "Brazo movido con flecha");
}

void handleBrazosDescanso() { 
  sendToMega("BRAZOS DESCANSO"); 
  
  // Actualizar posiciones de descanso
  posActualBrazos[0] = 10;  // BI
  posActualBrazos[1] = 80;  // FI
  posActualBrazos[2] = 80;  // HI
  posActualBrazos[3] = 40;  // BD
  posActualBrazos[4] = 90;  // FD
  posActualBrazos[5] = 80;  // HD
  posActualBrazos[6] = 45;  // PD
  
  server.send(200, "text/plain", "Brazos en descanso"); 
}

void handleBrazosSaludo() { 
  sendToMega("BRAZOS SALUDO"); 
  server.send(200, "text/plain", "Saludo enviado"); 
}

void handleBrazosAbrazar() { 
  sendToMega("BRAZOS ABRAZAR"); 
  server.send(200, "text/plain", "Abrazo enviado"); 
}

// Servo directo
void handleServoDirecto() {
  int ch = server.arg("ch").toInt();
  int ang = server.arg("ang").toInt();
  
  if (!validarMovimiento("servo", ang, 0, 180)) {
    server.send(400, "text/plain", "Ángulo fuera de rango");
    return;
  }
  
  String cmd = "SERVO CH=" + String(ch) + " ANG=" + String(ang);
  enviarComandoLento(cmd);
  server.send(200, "text/plain", "Servo movido");
}

// Comando personalizado
void handleCmd() {
  String cmd = server.arg("cmd");
  if (cmd.length() == 0) {
    server.send(400, "text/plain", "Comando vacío");
    return;
  }
  sendToMega(cmd);
  server.send(200, "text/plain", "Comando enviado");
}

// ===== NUEVOS ENDPOINTS PARA CONTROL DIRECTO DE SERVOS =====

// Control directo de servos desde web
void handleServoDirectoWeb() {
  int canal = server.arg("canal").toInt();
  int angulo = server.arg("angulo").toInt();

  if (!validarMovimiento("servo_web", angulo, 0, 180)) {
    server.send(400, "text/plain", "Ángulo fuera de rango (0-180°)");
    return;
  }

  if (canal < 0 || canal > 15) {
    server.send(400, "text/plain", "Canal fuera de rango (0-15)");
    return;
  }

  String comando = "SERVO CH=" + String(canal) + " ANG=" + String(angulo);
  sendToMega(comando);

  server.send(200, "text/plain", "Servo CH=" + String(canal) + " movido a " + String(angulo) + "°");
}

// Control de dedos individual desde web
void handleDedoDirectoWeb() {
  String mano = server.arg("mano");
  String dedo = server.arg("dedo");
  int angulo = server.arg("angulo").toInt();

  if (!validarMovimiento("dedo_web", angulo, 0, 180)) {
    server.send(400, "text/plain", "Ángulo fuera de rango (0-180°)");
    return;
  }

  controlarDedo(mano, dedo, angulo);

  server.send(200, "text/plain", "Dedo " + dedo + " de mano " + mano + " movido a " + String(angulo) + "°");
}

// Control de muñecas desde web
void handleMunecaDirectoWeb() {
  String mano = server.arg("mano");
  int angulo = server.arg("angulo").toInt();

  if (!validarMovimiento("muñeca_web", angulo, 0, 160)) {
    server.send(400, "text/plain", "Ángulo fuera de rango (0-160°)");
    return;
  }

  controlarMuñeca(mano, angulo);

  server.send(200, "text/plain", "Muñeca " + mano + " movida a " + String(angulo) + "°");
}

// Control de brazos desde web
void handleBrazosDirectoWeb() {
  int bi = server.arg("bi").toInt();
  int fi = server.arg("fi").toInt();
  int hi = server.arg("hi").toInt();
  int bd = server.arg("bd").toInt();
  int fd = server.arg("fd").toInt();
  int hd = server.arg("hd").toInt();
  int pd = server.arg("pd").toInt();

  controlarBrazos(bi, fi, hi, bd, fd, hd, pd);

  server.send(200, "text/plain", "Brazos movidos desde web");
}

// Control de cuello desde web
void handleCuelloDirectoWeb() {
  int lateral = server.arg("lateral").toInt();
  int inferior = server.arg("inferior").toInt();
  int superior = server.arg("superior").toInt();

  controlarCuello(lateral, inferior, superior);

  server.send(200, "text/plain", "Cuello movido desde web");
}

// Debug
void handleDebug() {
  String debug = "=== DEBUG ROBOT ===\n";
  debug += "WiFi: " + String(WiFi.status()==WL_CONNECTED ? "Conectado" : "Desconectado") + "\n";
  debug += "IP: " + WiFi.localIP().toString() + "\n";
  debug += "MEGA: " + String(megaConectado ? "Conectado" : "Desconectado") + "\n";
  debug += "UNO: " + String(unoConectado ? "Conectado" : "Desconectado") + "\n";
  debug += "Seguridad: " + String(modoSeguridad ? "ACTIVA" : "INACTIVA") + "\n";
  debug += "Velocidad: " + String(modoLento ? "LENTA" : "NORMAL") + "\n";
  debug += "Uptime: " + String(millis()/1000) + "s\n\n";
  debug += "=== ÚLTIMO ESTADO MEGA ===\n";
  debug += ultimoEstadoMega + "\n\n";
  debug += "=== ÚLTIMO ESTADO UNO ===\n";
  debug += ultimoEstadoUno + "\n";
  
  server.send(200, "text/plain", debug);
}

// Obtener posiciones actuales
void handlePosiciones() {
  String json = "{";
  json += "\"brazos\":[";
  for (int i = 0; i < 7; i++) {
    if (i > 0) json += ",";
    json += "{\"nombre\":\"" + nombresBrazos[i] + "\",\"posicion\":" + String(posActualBrazos[i]) + ",\"min\":" + String(limitesBrazos[i][0]) + ",\"max\":" + String(limitesBrazos[i][1]) + "}";
  }
  json += "],";
  json += "\"manos\":[";
  for (int i = 0; i < 10; i++) {
    if (i > 0) json += ",";
    json += "{\"nombre\":\"" + nombresDedos[i] + "\",\"posicion\":" + String(posActualManos[i]) + ",\"min\":" + String(limitesDedos[i][0]) + ",\"max\":" + String(limitesDedos[i][1]) + "}";
  }
  json += "],";
  json += "\"munecas\":[";
  for (int i = 0; i < 2; i++) {
    if (i > 0) json += ",";
    int posicion = (i == 0) ? posicionRelativaMuñecaDerecha : posActualMuñecas[i];
    int min = (i == 0) ? 80 : limitesMuñecas[i][0];
    int max = (i == 0) ? 180 : limitesMuñecas[i][1];
    json += "{\"nombre\":\"" + nombresMuñecas[i] + "\",\"posicion\":" + String(posicion) + ",\"min\":" + String(min) + ",\"max\":" + String(max) + "}";
  }
  json += "],";
  json += "\"cuello\":[";
  for (int i = 0; i < 3; i++) {
    if (i > 0) json += ",";
    json += "{\"nombre\":\"" + nombresCuello[i] + "\",\"posicion\":" + String(posActualCuello[i]) + ",\"min\":" + String(limitesCuello[i][0]) + ",\"max\":" + String(limitesCuello[i][1]) + "}";
  }
  json += "]";
  json += "}";
  
  server.send(200, "application/json", json);
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);

  Serial.begin(115200);
  UART1.begin(MEGA_BAUD, SERIAL_8N1, RX2_PIN, TX2_PIN);
  Serial.println("🤖 Robot Control System - ESP32");
  Serial.println("UART1=115200 RX2=16 TX2=17");

  // Conectar WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(400);
    Serial.print('.');
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println();
  Serial.print("IP: "); Serial.println(WiFi.localIP());

  // Configurar rutas del servidor
  server.on("/", handleRoot);
  
  // Sistema
  server.on("/system/security", handleSystemSecurity);
  server.on("/system/speed", handleSystemSpeed);
  server.on("/system/check", handleSystemCheck);
  server.on("/system/sync-security", handleSystemSyncSecurity);
  server.on("/system/descanso", handleSystemDescanso);
  server.on("/system/reset", handleSystemReset);
  server.on("/system/restart", handleSystemRestart);
  server.on("/system/status", handleSystemStatus);
  
  // Secuencias
  server.on("/sequence/command", HTTP_POST, handleSequenceCommand);
  server.on("/sequence/execute", HTTP_POST, handleExecuteSequence);
  
  // Manos
  server.on("/manos/gesto", HTTP_POST, handleManoGesto);
  server.on("/manos/dedo", HTTP_POST, handleManoDedo);
  server.on("/manos/flecha", HTTP_POST, handleManoFlecha);
  
  // Muñecas
  server.on("/munecas/mover", HTTP_POST, handleMuñecaMover);
  server.on("/munecas/flecha", HTTP_POST, handleMuñecaFlecha);
  server.on("/munecas/centrar", handleMuñecaCentrar);
  server.on("/munecas/aleatorio", handleMuñecaAleatorio);
  
  // Cuello
  server.on("/cuello/mover", HTTP_POST, handleCuelloMover);
  server.on("/cuello/flecha", HTTP_POST, handleCuelloFlecha);
  server.on("/cuello/centrar", handleCuelloCentrar);
  server.on("/cuello/aleatorio", handleCuelloAleatorio);
  server.on("/cuello/si", handleCuelloSi);
  server.on("/cuello/no", handleCuelloNo);
  
  // Brazos
  server.on("/brazos/mover", HTTP_POST, handleBrazosMover);
  server.on("/brazos/flecha", HTTP_POST, handleBrazosFlecha);
  server.on("/brazos/descanso", handleBrazosDescanso);
  server.on("/brazos/saludo", handleBrazosSaludo);
  server.on("/brazos/abrazar", handleBrazosAbrazar);
  
  // Control directo
  server.on("/servo", HTTP_POST, handleServoDirecto);
  server.on("/cmd", HTTP_POST, handleCmd);
  
  // Debug
  server.on("/debug", handleDebug);
  server.on("/posiciones", handlePosiciones);

  // ===== NUEVOS ENDPOINTS PARA CONTROL WEB =====
  server.on("/web/servo", HTTP_POST, handleServoDirectoWeb);
  server.on("/web/dedo", HTTP_POST, handleDedoDirectoWeb);
  server.on("/web/muneca", HTTP_POST, handleMunecaDirectoWeb);
  server.on("/web/brazos", HTTP_POST, handleBrazosDirectoWeb);
  server.on("/web/cuello", HTTP_POST, handleCuelloDirectoWeb);

  server.begin();
  Serial.println("🌐 Servidor HTTP iniciado");
  Serial.println("📱 Abre http://" + WiFi.localIP().toString() + " en tu navegador");
  
  // Mover robot a posición de descanso al inicio
  delay(2000); // Esperar a que todo se inicialice
  posicionDescanso();
  
  // Sincronizar estado de seguridad con el MEGA
  delay(1000);
  sincronizarSeguridad();
}

void loop() {
  server.handleClient();
  checkConnections();

  // Leer datos del MEGA
  while (UART1.available()) {
    char c = (char)UART1.read();
    if (c == '\r') continue;
    if (c == '\n') {
      if (megaLine.length()) {
        ultimoEstadoMega = megaLine;
        Serial.print("[MEGA] "); Serial.println(megaLine);
        
        // Detectar respuestas de ping
        if (megaLine.indexOf("MEGA:PONG") >= 0) {
          megaConectado = true;
        }
        if (megaLine.indexOf("UNO:PONG") >= 0) {
          unoConectado = true;
        }
        
        // Detectar respuestas de seguridad
        if (megaLine.indexOf("MEGA:Seguridad") >= 0) {
          Serial.println("Estado de seguridad del MEGA actualizado");
        }
        
        // Actualizar posiciones desde respuestas del MEGA
        if (megaLine.indexOf("MEGA:Brazos movidos") >= 0) {
          actualizarPosicionesDesdeRespuesta(megaLine);
        }
        if (megaLine.indexOf("MEGA:Cuello movido") >= 0) {
          actualizarPosicionesDesdeRespuesta(megaLine);
        }
        
        // Actualizar posiciones de manos desde respuestas del UNO
        if (megaLine.indexOf("UNO:Dedo") >= 0) {
          actualizarPosicionesManosDesdeRespuesta(megaLine);
        }
        
        megaLine = "";
      }
    } else {
      megaLine += c;
    }
  }

  // Ping periódico
  if (millis() - lastPingMs > 5000) {
    lastPingMs = millis();
    sendToMega("PING");
  }
}

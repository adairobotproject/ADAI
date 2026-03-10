#include <avr/io.h>

// === ARDUINO NANO – CUATRO MOTORES (DRV8833 / L298N) ===
// Nuevos mapeos solicitados:
// - M1/M2 en pines D10..D13.
// - M3/M4 en A0..A3 como digitales.
// - Encoders (A/B) distribuidos en D2..D9.
// - Botones MOVE / DIR en A4 / A5 (INPUT_PULLUP).
// - Motor 5 se elimina.
//
// Serial 9600: Comandos simples como ComprobadorComunicacion.ino
//              F=adelante, B=atras, S=stop, Vxxx=velocidad (0-255)
//              Reporte de RPM cada segundo para los 4 motores

// ---------- MAPEO DE PINES (TAL CUAL EN TU MENSAJE) ----------
// Motor 1 (antes L298N) -> AHORA DRV8833
const int IN1_1 = 10;   // PWM hardware
const int IN2_1 = 11;   // PWM hardware
// Motor 2 (antes L298N) -> AHORA DRV8833
const int IN1_2 = 12;   // digital (sin PWM)
const int IN2_2 = 13;   // digital (LED integrado)
// DRV8833 - Motor 3 (canal 1)
const int IN1_3 = A0;   // digital (D14)
const int IN2_3 = A1;   // digital (D15)

// DRV8833 - Motor 4 (canal 2)
const int IN1_4 = A2;   // digital (D16)
const int IN2_4 = A3;   // digital (D17)

// Encoders (M1..M4)
const int encoderA1 = 2;    // INT0
const int encoderB1 = 3;
const int encoderA2 = 4;    // PCINT20
const int encoderB2 = 5;
const int encoderA3 = 6;    // PCINT22
const int encoderB3 = 7;
const int encoderA4 = 8;    // PCINT0
const int encoderB4 = 9;

// Botones globales
const int BTN_MOVE = A4;    // mantener para mover (INPUT_PULLUP, a GND)
const int BTN_DIR  = A5;    // pulsar para invertir sentido global (INPUT_PULLUP, a GND)

// ---------- ESTADOS ----------
volatile long contadorPulsos1 = 0;
volatile long contadorPulsos2 = 0;
volatile long contadorPulsos3 = 0;
volatile long contadorPulsos4 = 0;

// Contadores de interrupciones para diagnóstico
volatile unsigned long isrCount1 = 0;
volatile unsigned long isrCount2 = 0;
volatile unsigned long isrCount3 = 0;
volatile unsigned long isrCount4 = 0;

int pwmCmd1 = 0, pwmCmd2 = 0, pwmCmd3 = 0, pwmCmd4 = 0;
int pwmTarget1 = 0, pwmTarget2 = 0, pwmTarget3 = 0, pwmTarget4 = 0;

int velocidad = 150;              // Velocidad PWM inicial (0-255) - como ComprobadorComunicacion
int pwmMax = 200;                // velocidad tope (0..255) - mantenido para compatibilidad
const int pwmMin = 100;          // mínimo de arranque
const int rampStep = 4;          // pasos de rampa
const unsigned long rampDt = 12; // ms entre pasos de rampa
unsigned long tRamp = 0;

bool direccionAdelante = true;   // sentido global 1..4
bool invert1 = false, invert2 = false, invert3 = false, invert4 = false;
volatile uint8_t lastPortDState = 0;
volatile uint8_t lastPortBState = 0;

// Modo de control: 0 = toda la mano, 1-4 = dedo individual (M1-M4)
int modoControl = 0;  // 0 = toda la mano, 1 = dedo 1, 2 = dedo 2, 3 = dedo 3, 4 = dedo 4

// Reporte de RPM cada segundo (como ComprobadorComunicacion.ino)
unsigned long lastTime = 0;
long lastCount1 = 0, lastCount2 = 0, lastCount3 = 0, lastCount4 = 0;

// Debounce para BTN_DIR (1..4) - opcional, puede deshabilitarse
const unsigned long debounceMs = 35;
int  dir_lastStable = HIGH;
int  dir_lastRead   = HIGH;
unsigned long dir_lastChangeMs = 0;

// ---------- MEDICIÓN / STREAM CSV ----------
const float TICKS_REV_1 = 12.0f; // AJUSTA a tu CPR real (modo A-Rising 1x)
const float TICKS_REV_2 = 12.0f;
const float TICKS_REV_3 = 12.0f;
const float TICKS_REV_4 = 12.0f;
// Nota: ComprobadorComunicacion usa 11 pulsos por vuelta, ajusta según tu encoder

unsigned long samplePeriodMs = 20; // 50 Hz por defecto
unsigned long lastSampleMs = 0;
bool streamOn = false;
long lastCnt1=0, lastCnt2=0, lastCnt3=0, lastCnt4=0;

inline long readAtomic(volatile long &ctr){ noInterrupts(); long v=ctr; interrupts(); return v; }

void enablePcInt(uint8_t pin){
  volatile uint8_t *pcmsk = digitalPinToPCMSK(pin);
  if (!pcmsk) return;
  *pcmsk |= _BV(digitalPinToPCMSKbit(pin));
  PCICR  |= _BV(digitalPinToPCICRbit(pin));
}

void printCSVHeader(){
  Serial.println(F("# time_ms,pwm1,pwm2,pwm3,pwm4,dirGlobal,c1,c2,c3,c4,rpm1,rpm2,rpm3,rpm4"));
}

void sampleAndPrint(){
  unsigned long now = millis();
  unsigned long dt = now - lastSampleMs;
  if (dt < samplePeriodMs) return;
  lastSampleMs = now;

  long c1 = readAtomic(contadorPulsos1);
  long c2 = readAtomic(contadorPulsos2);
  long c3 = readAtomic(contadorPulsos3);
  long c4 = readAtomic(contadorPulsos4);
  long d1 = c1 - lastCnt1; lastCnt1 = c1;
  long d2 = c2 - lastCnt2; lastCnt2 = c2;
  long d3 = c3 - lastCnt3; lastCnt3 = c3;
  long d4 = c4 - lastCnt4; lastCnt4 = c4;

  float s = dt / 1000.0f;
  float rpm1 = (TICKS_REV_1>0) ? (d1 / TICKS_REV_1) * (60.0f / s) : 0;
  float rpm2 = (TICKS_REV_2>0) ? (d2 / TICKS_REV_2) * (60.0f / s) : 0;
  float rpm3 = (TICKS_REV_3>0) ? (d3 / TICKS_REV_3) * (60.0f / s) : 0;
  float rpm4 = (TICKS_REV_4>0) ? (d4 / TICKS_REV_4) * (60.0f / s) : 0;
  Serial.print(now); Serial.print(',');
  Serial.print(pwmCmd1); Serial.print(',');
  Serial.print(pwmCmd2); Serial.print(',');
  Serial.print(pwmCmd3); Serial.print(',');
  Serial.print(pwmCmd4); Serial.print(',');
  Serial.print(direccionAdelante ? 1 : 0); Serial.print(',');
  Serial.print(c1); Serial.print(',');
  Serial.print(c2); Serial.print(',');
  Serial.print(c3); Serial.print(',');
  Serial.print(c4); Serial.print(',');
  Serial.print(rpm1,3); Serial.print(',');
  Serial.print(rpm2,3); Serial.print(',');
  Serial.print(rpm3,3); Serial.print(',');
  Serial.println(rpm4,3);
}

// ---------- HELP ----------
void printHelp() {
  Serial.println(F("\n=== Controles Serial (como ComprobadorComunicacion) ==="));
  Serial.println(F("--- Control de TODA LA MANO ---"));
  Serial.println(F("F : adelante (todos los motores)"));
  Serial.println(F("B : atras (todos los motores)"));
  Serial.println(F("S : stop (detener todos los motores)"));
  Serial.println(F("Vxxx : velocidad (0-255), ej: V150"));
  Serial.println(F("A : abrir dedos (adelante)"));
  Serial.println(F("C : cerrar dedos (atras)"));
  Serial.println(F("--- Seleccion de Modo ---"));
  Serial.println(F("M0 : modo toda la mano"));
  Serial.println(F("M1 : modo dedo 1"));
  Serial.println(F("M2 : modo dedo 2"));
  Serial.println(F("M3 : modo dedo 3"));
  Serial.println(F("M4 : modo dedo 4"));
  Serial.println(F("--- Comandos adicionales ---"));
  Serial.println(F("p : imprimir contadores de pulsos"));
  Serial.println(F("d : diagnostico de encoders y motores"));
  Serial.println(F("e : prueba de encoders (girar manualmente)"));
  Serial.println(F("i : prueba de interrupciones (verificar ISRs)"));
  Serial.println(F("t : ON/OFF stream CSV; v : encabezado; 2/5 : 50/100 Hz"));
  Serial.println(F("h : ayuda"));
  Serial.print (F("Velocidad actual=")); Serial.print(velocidad);
  Serial.print (F(" | sentido=")); Serial.println(direccionAdelante ? F("Adelante") : F("Atras"));
  Serial.print (F("Modo actual="));
  if (modoControl == 0) {
    Serial.println(F("TODA LA MANO"));
  } else {
    Serial.print(F("DEDO M")); Serial.println(modoControl);
  }
  Serial.println(F("Reporte de RPM cada segundo para M1-M4"));
  Serial.println(F("=================\n"));
}

void printPulsos(){
  Serial.print(F("P1=")); Serial.print(contadorPulsos1);
  Serial.print(F(" P2=")); Serial.print(contadorPulsos2);
  Serial.print(F(" P3=")); Serial.print(contadorPulsos3);
  Serial.print(F(" P4=")); Serial.println(contadorPulsos4);
}

// ---------- DIAGNÓSTICO DE ENCODERS ----------
void diagnosticarEncoders() {
  Serial.println(F("\n=== DIAGNÓSTICO DE ENCODERS ==="));
  Serial.println(F("Conexiones esperadas:"));
  Serial.println(F("M1: D2=C1, D3=C2"));
  Serial.println(F("M2: D4=C1, D5=C2"));
  Serial.println(F("M3: D6=C1, D7=C2"));
  Serial.println(F("M4: D8=C1, D9=C2"));
  Serial.println();
  
  // Leer estados actuales de los pines (múltiples lecturas para detectar cambios)
  Serial.println(F("Estados de pines (5 lecturas):"));
  for (int i = 0; i < 5; i++) {
    Serial.print(F("  Lectura ")); Serial.print(i+1); Serial.print(F(": "));
    Serial.print(F("M1(D2=")); Serial.print(digitalRead(encoderA1));
    Serial.print(F(",D3=")); Serial.print(digitalRead(encoderB1));
    Serial.print(F(") M2(D4=")); Serial.print(digitalRead(encoderA2));
    Serial.print(F(",D5=")); Serial.print(digitalRead(encoderB2));
    Serial.print(F(") M3(D6=")); Serial.print(digitalRead(encoderA3));
    Serial.print(F(",D7=")); Serial.print(digitalRead(encoderB3));
    Serial.print(F(") M4(D8=")); Serial.print(digitalRead(encoderA4));
    Serial.print(F(",D9=")); Serial.print(digitalRead(encoderB4));
    Serial.println(F(")"));
    delay(100);
  }
  Serial.println();
  
  // Contadores actuales
  Serial.print(F("Contadores: M1=")); Serial.print(contadorPulsos1);
  Serial.print(F(" M2=")); Serial.print(contadorPulsos2);
  Serial.print(F(" M3=")); Serial.print(contadorPulsos3);
  Serial.print(F(" M4=")); Serial.println(contadorPulsos4);
  
  // Contadores de interrupciones (para diagnóstico)
  noInterrupts();
  unsigned long ic1 = isrCount1, ic2 = isrCount2, ic3 = isrCount3, ic4 = isrCount4;
  interrupts();
  Serial.print(F("ISR Counts: M1=")); Serial.print(ic1);
  Serial.print(F(" M2=")); Serial.print(ic2);
  Serial.print(F(" M3=")); Serial.print(ic3);
  Serial.print(F(" M4=")); Serial.println(ic4);
  
  // Estados de PWM
  Serial.print(F("PWM Targets: M1=")); Serial.print(pwmTarget1);
  Serial.print(F(" M2=")); Serial.print(pwmTarget2);
  Serial.print(F(" M3=")); Serial.print(pwmTarget3);
  Serial.print(F(" M4=")); Serial.println(pwmTarget4);
  
  Serial.print(F("PWM Actual: M1=")); Serial.print(pwmCmd1);
  Serial.print(F(" M2=")); Serial.print(pwmCmd2);
  Serial.print(F(" M3=")); Serial.print(pwmCmd3);
  Serial.print(F(" M4=")); Serial.println(pwmCmd4);
  
  // Verificar estados de salida de los motores
  Serial.print(F("Salidas Digitales: "));
  Serial.print(F("M1(IN1=")); Serial.print(digitalRead(IN1_1));
  Serial.print(F(",IN2=")); Serial.print(digitalRead(IN2_1));
  Serial.print(F(") M2(IN1=")); Serial.print(digitalRead(IN1_2));
  Serial.print(F(",IN2=")); Serial.print(digitalRead(IN2_2));
  Serial.print(F(") M3(IN1=")); Serial.print(digitalRead(IN1_3));
  Serial.print(F(",IN2=")); Serial.print(digitalRead(IN2_3));
  Serial.print(F(") M4(IN1=")); Serial.print(digitalRead(IN1_4));
  Serial.print(F(",IN2=")); Serial.print(digitalRead(IN2_4));
  Serial.println(F(")"));
  
  Serial.print(F("Direccion: ")); Serial.println(direccionAdelante ? F("Adelante") : F("Atras"));
  
  // Verificar estados de salida de los motores
  Serial.print(F("Salidas Digitales: "));
  Serial.print(F("M1(D10=")); Serial.print(digitalRead(IN1_1));
  Serial.print(F(",D11=")); Serial.print(digitalRead(IN2_1));
  Serial.print(F(") M2(D12=")); Serial.print(digitalRead(IN1_2));
  Serial.print(F(",D13=")); Serial.print(digitalRead(IN2_2));
  Serial.print(F(") M3(A0=")); Serial.print(digitalRead(IN1_3));
  Serial.print(F(",A1=")); Serial.print(digitalRead(IN2_3));
  Serial.print(F(") M4(A2=")); Serial.print(digitalRead(IN1_4));
  Serial.print(F(",A3=")); Serial.print(digitalRead(IN2_4));
  Serial.println(F(")"));
  
  Serial.println(F("===============================\n"));
}

// ---------- PRUEBA DE ENCODERS (girar manualmente) ----------
void pruebaEncoders() {
  Serial.println(F("PRUEBA DE ENCODERS - Gira los motores manualmente"));
  Serial.println(F("Presiona cualquier tecla para detener..."));
  
  // Resetear contadores de ISR para esta prueba
  noInterrupts();
  isrCount1 = isrCount2 = isrCount3 = isrCount4 = 0;
  interrupts();
  
  long contadoresIniciales[4] = {contadorPulsos1, contadorPulsos2, contadorPulsos3, contadorPulsos4};
  unsigned long inicio = millis();
  unsigned long ultimoReporte = millis();
  
  while (!Serial.available()) {
    unsigned long ahora = millis();
    
    // Reporte cada segundo
    if (ahora - ultimoReporte >= 1000) {
      ultimoReporte = ahora;
      
      noInterrupts();
      long c1 = contadorPulsos1, c2 = contadorPulsos2, c3 = contadorPulsos3, c4 = contadorPulsos4;
      unsigned long ic1 = isrCount1, ic2 = isrCount2, ic3 = isrCount3, ic4 = isrCount4;
      interrupts();
      
      long delta1 = c1 - contadoresIniciales[0];
      long delta2 = c2 - contadoresIniciales[1];
      long delta3 = c3 - contadoresIniciales[2];
      long delta4 = c4 - contadoresIniciales[3];
      
      Serial.print(F("T=")); Serial.print((ahora - inicio) / 1000); Serial.print(F("s: "));
      Serial.print(F("Pulsos: M1=")); Serial.print(delta1);
      Serial.print(F(" M2=")); Serial.print(delta2);
      Serial.print(F(" M3=")); Serial.print(delta3);
      Serial.print(F(" M4=")); Serial.print(delta4);
      Serial.print(F(" | ISRs: M1=")); Serial.print(ic1);
      Serial.print(F(" M2=")); Serial.print(ic2);
      Serial.print(F(" M3=")); Serial.print(ic3);
      Serial.print(F(" M4=")); Serial.println(ic4);
      
      contadoresIniciales[0] = c1;
      contadoresIniciales[1] = c2;
      contadoresIniciales[2] = c3;
      contadoresIniciales[3] = c4;
    }
    delay(10);
  }
  
  // Limpiar buffer
  while (Serial.available()) Serial.read();
  Serial.println(F("Prueba finalizada"));
}

// ---------- PRUEBA DE INTERRUPCIONES DIRECTA ----------
void pruebaInterrupciones() {
  Serial.println(F("\n=== PRUEBA DE INTERRUPCIONES ==="));
  Serial.println(F("Esta prueba verifica que las interrupciones respondan a cambios"));
  Serial.println(F("Conecta/desconecta rápidamente los pines de encoder a GND"));
  Serial.println(F("o gira los motores manualmente"));
  Serial.println(F("Presiona cualquier tecla para detener...\n"));
  
  // Resetear contadores
  noInterrupts();
  isrCount1 = isrCount2 = isrCount3 = isrCount4 = 0;
  contadorPulsos1 = contadorPulsos2 = contadorPulsos3 = contadorPulsos4 = 0;
  interrupts();
  
  unsigned long inicio = millis();
  unsigned long ultimoReporte = millis();
  
  while (!Serial.available()) {
    unsigned long ahora = millis();
    
    // Reporte cada 500ms
    if (ahora - ultimoReporte >= 500) {
      ultimoReporte = ahora;
      
      noInterrupts();
      unsigned long ic1 = isrCount1, ic2 = isrCount2, ic3 = isrCount3, ic4 = isrCount4;
      long c1 = contadorPulsos1, c2 = contadorPulsos2, c3 = contadorPulsos3, c4 = contadorPulsos4;
      interrupts();
      
      Serial.print(F("T=")); Serial.print((ahora - inicio) / 1000.0, 1); Serial.print(F("s: "));
      Serial.print(F("ISR: M1=")); Serial.print(ic1);
      Serial.print(F(" M2=")); Serial.print(ic2);
      Serial.print(F(" M3=")); Serial.print(ic3);
      Serial.print(F(" M4=")); Serial.print(ic4);
      Serial.print(F(" | Pulsos: M1=")); Serial.print(c1);
      Serial.print(F(" M2=")); Serial.print(c2);
      Serial.print(F(" M3=")); Serial.print(c3);
      Serial.print(F(" M4=")); Serial.println(c4);
      
      // Si alguna ISR se disparó, mostrar éxito
      if (ic1 > 0 || ic2 > 0 || ic3 > 0 || ic4 > 0) {
        Serial.println(F("✓ INTERRUPCIONES FUNCIONANDO!"));
      }
    }
    delay(10);
  }
  
  // Limpiar buffer
  while (Serial.available()) Serial.read();
  Serial.println(F("Prueba finalizada"));
}

// ---------- DECLARACIÓN FORWARD ----------
void setDireccion(bool adelante);
void aplicarPWM();

// ---------- FUNCIONES DE CONTROL (como ComprobadorComunicacion.ino) ----------
void adelante() {
  direccionAdelante = true;
  setDireccion(direccionAdelante);
  
  // Activar todos los motores a velocidad configurada (aplicar directamente como ComprobadorComunicacion)
  pwmTarget1 = velocidad;
  pwmTarget2 = velocidad;
  pwmTarget3 = velocidad;
  pwmTarget4 = velocidad;
  
  // Aplicar inmediatamente (sin esperar rampa) para comportamiento como ComprobadorComunicacion
  pwmCmd1 = velocidad;
  pwmCmd2 = velocidad;
  pwmCmd3 = velocidad;
  pwmCmd4 = velocidad;
  
  // Aplicar PWM directamente
  aplicarPWM();
  
  Serial.println(F("Motor adelante"));
}

void atras() {
  direccionAdelante = false;
  setDireccion(direccionAdelante);
  
  // Activar todos los motores a velocidad configurada
  pwmTarget1 = velocidad;
  pwmTarget2 = velocidad;
  pwmTarget3 = velocidad;
  pwmTarget4 = velocidad;
  
  // Aplicar inmediatamente
  pwmCmd1 = velocidad;
  pwmCmd2 = velocidad;
  pwmCmd3 = velocidad;
  pwmCmd4 = velocidad;
  
  // Aplicar PWM directamente
  aplicarPWM();
  
  Serial.println(F("Motor atras"));
}

void stopMotor() {
  // Detener todos los motores
  pwmTarget1 = 0;
  pwmTarget2 = 0;
  pwmTarget3 = 0;
  pwmTarget4 = 0;
  
  // Aplicar inmediatamente
  pwmCmd1 = 0;
  pwmCmd2 = 0;
  pwmCmd3 = 0;
  pwmCmd4 = 0;
  
  // Aplicar PWM directamente
  aplicarPWM();
  
  Serial.println(F("Motor detenido"));
}

// ---------- FUNCIÓN PARA APLICAR PWM DIRECTAMENTE ----------
void aplicarPWM() {
  // M1 con DRV8833 usando IN1/IN2 (D10, D11 - tienen PWM hardware)
  bool fwd1 = direccionAdelante ^ invert1;
  if (pwmCmd1 == 0) { 
    digitalWrite(IN1_1, LOW); 
    digitalWrite(IN2_1, LOW); 
  } else { 
    if (fwd1) { 
      analogWrite(IN1_1, pwmCmd1); 
      digitalWrite(IN2_1, LOW); 
    } else { 
      analogWrite(IN2_1, pwmCmd1); 
      digitalWrite(IN1_1, LOW); 
    } 
  }

  // M2 con DRV8833 usando IN1/IN2 (D12, D13 - NO tienen PWM hardware, usar digital)
  bool fwd2 = direccionAdelante ^ invert2;
  if (pwmCmd2 == 0) { 
    digitalWrite(IN1_2, LOW); 
    digitalWrite(IN2_2, LOW); 
  } else { 
    // D12 y D13 no tienen PWM, usar digitalWrite con velocidad simulada
    if (fwd2) { 
      digitalWrite(IN1_2, HIGH);  // Activar directamente
      digitalWrite(IN2_2, LOW); 
    } else { 
      digitalWrite(IN2_2, HIGH);  // Activar directamente
      digitalWrite(IN1_2, LOW); 
    } 
  }

  // M3 (A0/D14, A1/D15 - NO tienen PWM hardware, usar digital)
  bool fwd3 = direccionAdelante ^ invert3;
  if (pwmCmd3 == 0) {
    digitalWrite(IN1_3, LOW); 
    digitalWrite(IN2_3, LOW);
  } else {
    // A0 y A1 no tienen PWM, usar digitalWrite con velocidad simulada
    if (fwd3) { 
      digitalWrite(IN1_3, HIGH);  // Activar directamente
      digitalWrite(IN2_3, LOW); 
    } else { 
      digitalWrite(IN2_3, HIGH);  // Activar directamente
      digitalWrite(IN1_3, LOW); 
    }
  }

  // M4 (A2/D16, A3/D17 - NO tienen PWM hardware, usar digital)
  bool fwd4 = direccionAdelante ^ invert4;
  if (pwmCmd4 == 0) {
    digitalWrite(IN1_4, LOW); 
    digitalWrite(IN2_4, LOW);
  } else {
    // A2 y A3 no tienen PWM, usar digitalWrite con velocidad simulada
    if (fwd4) { 
      digitalWrite(IN1_4, HIGH);  // Activar directamente
      digitalWrite(IN2_4, LOW); 
    } else { 
      digitalWrite(IN2_4, HIGH);  // Activar directamente
      digitalWrite(IN1_4, LOW); 
    }
  }
}

// ---------- DIRECCION CON DEAD-TIME (1..4) ----------
void setDireccion(bool /*adelante*/) {
  // "Coast" breve en M1..M4 para evitar cross-conduction
  digitalWrite(IN1_1, LOW); digitalWrite(IN2_1, LOW);
  digitalWrite(IN1_2, LOW); digitalWrite(IN2_2, LOW);
  digitalWrite(IN1_3, LOW); digitalWrite(IN2_3, LOW);
  digitalWrite(IN1_4, LOW); digitalWrite(IN2_4, LOW);

  delay(2); // dead-time ~2 ms
}

// ---------- ISRs DE ENCODER ----------
void contarPulsos1(){ 
  isrCount1++;
  if (digitalRead(encoderB1)==HIGH) contadorPulsos1++; 
  else contadorPulsos1--; 
}
void contarPulsos2(){ 
  isrCount2++;
  if (digitalRead(encoderB2)==HIGH) contadorPulsos2++; 
  else contadorPulsos2--; 
}
void contarPulsos3(){ 
  isrCount3++;
  if (digitalRead(encoderB3)==HIGH) contadorPulsos3++; 
  else contadorPulsos3--; 
}
void contarPulsos4(){ 
  isrCount4++;
  if (digitalRead(encoderB4)==HIGH) contadorPulsos4++; 
  else contadorPulsos4--; 
}

ISR(PCINT2_vect){ // D0-D7 - Detecta cambios en cualquier flanco
  uint8_t current = PIND;
  uint8_t changed = current ^ lastPortDState;
  
  // Encoder 2 (D4 = PD4) - detectar cualquier cambio
  if (changed & _BV(PD4)) {
    contarPulsos2();
  }
  
  // Encoder 3 (D6 = PD6) - detectar cualquier cambio
  if (changed & _BV(PD6)) {
    contarPulsos3();
  }
  
  lastPortDState = current;
}

ISR(PCINT0_vect){ // D8-D13 - Detecta cambios en cualquier flanco
  uint8_t current = PINB;
  uint8_t changed = current ^ lastPortBState;
  
  // Encoder 4 (D8 = PB0) - detectar cualquier cambio
  if (changed & _BV(PB0)) {
    contarPulsos4();
  }
  
  lastPortBState = current;
}

// ---------- SETUP ----------
void setup() {
  // M1..M4
  pinMode(IN1_1, OUTPUT); pinMode(IN2_1, OUTPUT);
  pinMode(IN1_2, OUTPUT); pinMode(IN2_2, OUTPUT);
  pinMode(IN1_3, OUTPUT); pinMode(IN2_3, OUTPUT);
  pinMode(IN1_4, OUTPUT); pinMode(IN2_4, OUTPUT);

  // Encoders (pullups)
  pinMode(encoderA1, INPUT_PULLUP); pinMode(encoderB1, INPUT_PULLUP);
  pinMode(encoderA2, INPUT_PULLUP); pinMode(encoderB2, INPUT_PULLUP);
  pinMode(encoderA3, INPUT_PULLUP); pinMode(encoderB3, INPUT_PULLUP);
  pinMode(encoderA4, INPUT_PULLUP); pinMode(encoderB4, INPUT_PULLUP);

  // Botones
  pinMode(BTN_MOVE,  INPUT_PULLUP);
  pinMode(BTN_DIR,   INPUT_PULLUP);

  // Interrupciones de encoder
  // Cambiar a CHANGE para detectar ambos flancos (más preciso)
  attachInterrupt(digitalPinToInterrupt(encoderA1), contarPulsos1, CHANGE);

  lastPortDState = PIND;
  lastPortBState = PINB;
  enablePcInt(encoderA2);
  enablePcInt(encoderA3);
  enablePcInt(encoderA4);

  Serial.begin(9600); // Mismo baudrate que ComprobadorComunicacion.ino

  // Arranque seguro: todo en LOW/coast
  digitalWrite(IN1_1, LOW); digitalWrite(IN2_1, LOW);
  digitalWrite(IN1_2, LOW); digitalWrite(IN2_2, LOW);
  digitalWrite(IN1_3, LOW); digitalWrite(IN2_3, LOW);
  digitalWrite(IN1_4, LOW); digitalWrite(IN2_4, LOW);

  setDireccion(direccionAdelante);

  Serial.println(F("Nano listo: M1..M4 en D10-D13 y A0-A3 con encoders D2-D9."));
  Serial.println(F("Comandos: F=adelante, B=atras, S=stop, Vxxx=velocidad (0-255)"));
  Serial.println(F("A=abrir dedos, C=cerrar dedos"));
  Serial.println(F("M0-M4 = seleccionar modo (0=toda la mano, 1-4=dedo individual)"));
  Serial.print(F("Modo inicial: "));
  if (modoControl == 0) {
    Serial.println(F("TODA LA MANO"));
  } else {
    Serial.print(F("DEDO M")); Serial.println(modoControl);
  }
  
  // Activar M1 y M2 por defecto al inicio (movimiento hacia adelante)
  direccionAdelante = true;
  pwmTarget1 = velocidad;
  pwmTarget2 = velocidad;
  pwmCmd1 = velocidad;
  pwmCmd2 = velocidad;
  aplicarPWM();
  Serial.println(F("M1 y M2 activados por defecto (adelante)"));
  
  printHelp();
  printCSVHeader();
}

// ---------- FUNCIONES DE SELECCIÓN DE MODO ----------
void setModoControl(int modo) {
  if (modo >= 0 && modo <= 4) {
    modoControl = modo;
    if (modo == 0) {
      Serial.println(F("Modo: TODA LA MANO"));
    } else {
      Serial.print(F("Modo: DEDO INDIVIDUAL M"));
      Serial.println(modo);
    }
  } else {
    Serial.print(F("ERROR: Modo invalido (0-4): "));
    Serial.println(modo);
  }
}

// ---------- FUNCIONES DE CONTROL DE DEDOS (como ComprobadorComunicacion.ino) ----------
void abrirDedos() {
  direccionAdelante = true;
  setDireccion(direccionAdelante);
  
  if (modoControl == 0) {
    // Modo toda la mano: activar todos los motores
    pwmTarget1 = velocidad;
    pwmTarget2 = velocidad;
    pwmTarget3 = velocidad;
    pwmTarget4 = velocidad;
    // Aplicar inmediatamente
    pwmCmd1 = velocidad;
    pwmCmd2 = velocidad;
    pwmCmd3 = velocidad;
    pwmCmd4 = velocidad;
    aplicarPWM();
    Serial.println(F("Toda la mano: dedos abriendo"));
  } else {
    // Modo dedo individual: activar solo el dedo seleccionado
    moverDedoIndividual(modoControl, true);
  }
}

void cerrarDedos() {
  direccionAdelante = false;
  setDireccion(direccionAdelante);
  
  if (modoControl == 0) {
    // Modo toda la mano: activar todos los motores
    pwmTarget1 = velocidad;
    pwmTarget2 = velocidad;
    pwmTarget3 = velocidad;
    pwmTarget4 = velocidad;
    // Aplicar inmediatamente
    pwmCmd1 = velocidad;
    pwmCmd2 = velocidad;
    pwmCmd3 = velocidad;
    pwmCmd4 = velocidad;
    aplicarPWM();
    Serial.println(F("Toda la mano: dedos cerrando"));
  } else {
    // Modo dedo individual: activar solo el dedo seleccionado
    moverDedoIndividual(modoControl, false);
  }
}

void detenerDedos() {
  if (modoControl == 0) {
    // Modo toda la mano: detener todos los motores
    pwmTarget1 = 0;
    pwmTarget2 = 0;
    pwmTarget3 = 0;
    pwmTarget4 = 0;
    // Aplicar inmediatamente
    pwmCmd1 = 0;
    pwmCmd2 = 0;
    pwmCmd3 = 0;
    pwmCmd4 = 0;
    aplicarPWM();
    Serial.println(F("Toda la mano: dedos detenidos"));
  } else {
    // Modo dedo individual: detener solo el dedo seleccionado
    detenerDedoIndividual(modoControl);
  }
}

// ---------- FUNCIONES DE CONTROL DE DEDO INDIVIDUAL ----------
void moverDedoIndividual(int dedo, bool adelante) {
  if (dedo < 1 || dedo > 4) {
    Serial.print(F("ERROR: Dedo invalido (1-4): "));
    Serial.println(dedo);
    return;
  }
  
  // Actualizar dirección global si es necesario
  if (adelante != direccionAdelante) {
    direccionAdelante = adelante;
    setDireccion(direccionAdelante);
  }
  
  // Activar solo el dedo especificado
  switch (dedo) {
    case 1: 
      pwmTarget1 = velocidad; pwmTarget2 = 0; pwmTarget3 = 0; pwmTarget4 = 0;
      pwmCmd1 = velocidad; pwmCmd2 = 0; pwmCmd3 = 0; pwmCmd4 = 0;
      break;
    case 2: 
      pwmTarget1 = 0; pwmTarget2 = velocidad; pwmTarget3 = 0; pwmTarget4 = 0;
      pwmCmd1 = 0; pwmCmd2 = velocidad; pwmCmd3 = 0; pwmCmd4 = 0;
      break;
    case 3: 
      pwmTarget1 = 0; pwmTarget2 = 0; pwmTarget3 = velocidad; pwmTarget4 = 0;
      pwmCmd1 = 0; pwmCmd2 = 0; pwmCmd3 = velocidad; pwmCmd4 = 0;
      break;
    case 4: 
      pwmTarget1 = 0; pwmTarget2 = 0; pwmTarget3 = 0; pwmTarget4 = velocidad;
      pwmCmd1 = 0; pwmCmd2 = 0; pwmCmd3 = 0; pwmCmd4 = velocidad;
      break;
  }
  
  aplicarPWM();
  
  Serial.print(F("Dedo M"));
  Serial.print(dedo);
  Serial.println(adelante ? F(" abriendo") : F(" cerrando"));
}

void detenerDedoIndividual(int dedo) {
  if (dedo < 1 || dedo > 4) {
    Serial.print(F("ERROR: Dedo invalido (1-4): "));
    Serial.println(dedo);
    return;
  }
  
  // Detener solo el dedo especificado
  switch (dedo) {
    case 1: 
      pwmTarget1 = 0; 
      pwmCmd1 = 0;
      break;
    case 2: 
      pwmTarget2 = 0; 
      pwmCmd2 = 0;
      break;
    case 3: 
      pwmTarget3 = 0; 
      pwmCmd3 = 0;
      break;
    case 4: 
      pwmTarget4 = 0; 
      pwmCmd4 = 0;
      break;
  }
  
  aplicarPWM();
  
  Serial.print(F("Dedo M"));
  Serial.print(dedo);
  Serial.println(F(" detenido"));
}

// ---------- LOOP ----------
void loop() {
  unsigned long now = millis();

  // --- Comandos Serial (estilo ComprobadorComunicacion.ino) ---
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    // Solo procesar si hay contenido
    if (cmd.length() > 0) {
      // Comandos principales (como ComprobadorComunicacion.ino)
      if (cmd == "F") {
        adelante();
      } else if (cmd == "B") {
        atras();
      } else if (cmd == "S") {
        stopMotor();
      } else if (cmd.startsWith("V")) {
        int val = cmd.substring(1).toInt();
        if (val >= 0 && val <= 255) {
          velocidad = val;
          Serial.print(F("Velocidad ajustada a: "));
          Serial.println(velocidad);
        }
      }
      // Comandos de dedos
      else if (cmd == "A" || cmd == "a") {
        abrirDedos();
      } else if (cmd == "C" || cmd == "c") {
        cerrarDedos();
      }
      // Comandos de selección de modo (M0, M1, M2, M3, M4)
      else if (cmd.length() == 2 && (cmd.startsWith("M") || cmd.startsWith("m"))) {
        int modo = cmd.substring(1).toInt();
        setModoControl(modo);
      }
      // Comandos adicionales (caracteres simples)
      else if (cmd.length() == 1) {
        char c = cmd.charAt(0);
        switch (c) {
          case 'p': case 'P': printPulsos(); break;
          case 'd': case 'D': diagnosticarEncoders(); break;
          case 'e': case 'E': pruebaEncoders(); break;
          case 'i': case 'I': pruebaInterrupciones(); break;
          case 'h': case 'H': printHelp(); break;
          case 't': streamOn = !streamOn; Serial.println(streamOn ? F("[STREAM ON]") : F("[STREAM OFF]")); break;
          case 'v': printCSVHeader(); break;
          case '2': samplePeriodMs = 20;  Serial.println(F("Fs=50 Hz")); break;
          case '5': samplePeriodMs = 10;  Serial.println(F("Fs=100 Hz (recom. 230400 baud)")); break;
          case '+': pwmMax += 10; if (pwmMax > 255) pwmMax = 255; Serial.print(F("pwmMax = ")); Serial.println(pwmMax); break;
          case '-': pwmMax -= 10; if (pwmMax < pwmMin + 10) pwmMax = pwmMin + 10; Serial.print(F("pwmMax = ")); Serial.println(pwmMax); break;
          default: Serial.print(F("Comando desconocido: ")); Serial.println(cmd); break;
        }
      } else {
        Serial.print(F("Comando desconocido: ")); Serial.println(cmd);
      }
    }
  }


  // --- Debounce y flanco para BTN_DIR (1..4) ---
  int reading = digitalRead(BTN_DIR);
  if (reading != dir_lastRead) { dir_lastChangeMs = now; dir_lastRead = reading; }
  if ((now - dir_lastChangeMs) >= debounceMs) {
    if (reading != dir_lastStable) {
      dir_lastStable = reading;
      if (dir_lastStable == LOW) {
        direccionAdelante = !direccionAdelante;
        setDireccion(direccionAdelante);
        Serial.println(direccionAdelante ? F(">> Adelante <<") : F("<< Atras >>"));
      }
    }
  }

  // --- Lógica de botón MOVE: mantener para mover (1..4) ---
  bool mover = (digitalRead(BTN_MOVE) == LOW);
  if (mover) {
    pwmTarget1 = pwmMax; pwmTarget2 = pwmMax; pwmTarget3 = pwmMax; pwmTarget4 = pwmMax;
  } else {
    pwmTarget1 = 0; pwmTarget2 = 0; pwmTarget3 = 0; pwmTarget4 = 0;
  }

  // --- Rampa de PWM independiente por canal ---
  if (now - tRamp >= rampDt) {
    tRamp = now;

    if (pwmCmd1 < pwmTarget1) { pwmCmd1 += rampStep; if (pwmCmd1 < pwmMin && pwmTarget1 > 0) pwmCmd1 = pwmMin; if (pwmCmd1 > pwmTarget1) pwmCmd1 = pwmTarget1; }
    else if (pwmCmd1 > pwmTarget1) { pwmCmd1 -= rampStep; if (pwmCmd1 < 0) pwmCmd1 = 0; }

    if (pwmCmd2 < pwmTarget2) { pwmCmd2 += rampStep; if (pwmCmd2 < pwmMin && pwmTarget2 > 0) pwmCmd2 = pwmMin; if (pwmCmd2 > pwmTarget2) pwmCmd2 = pwmTarget2; }
    else if (pwmCmd2 > pwmTarget2) { pwmCmd2 -= rampStep; if (pwmCmd2 < 0) pwmCmd2 = 0; }

    if (pwmCmd3 < pwmTarget3) { pwmCmd3 += rampStep; if (pwmCmd3 > pwmTarget3) pwmCmd3 = pwmTarget3; }
    else if (pwmCmd3 > pwmTarget3) { pwmCmd3 -= rampStep; if (pwmCmd3 < 0) pwmCmd3 = 0; }

    if (pwmCmd4 < pwmTarget4) { pwmCmd4 += rampStep; if (pwmCmd4 > pwmTarget4) pwmCmd4 = pwmTarget4; }
    else if (pwmCmd4 > pwmTarget4) { pwmCmd4 -= rampStep; if (pwmCmd4 < 0) pwmCmd4 = 0; }

    // === APLICAR SALIDAS (usar función centralizada) ===
    aplicarPWM();
  }

  // === Reporte de RPM cada segundo (como ComprobadorComunicacion.ino) ===
  if (millis() - lastTime >= 1000) {
    long delta1 = readAtomic(contadorPulsos1) - lastCount1;
    long delta2 = readAtomic(contadorPulsos2) - lastCount2;
    long delta3 = readAtomic(contadorPulsos3) - lastCount3;
    long delta4 = readAtomic(contadorPulsos4) - lastCount4;
    
    lastCount1 = readAtomic(contadorPulsos1);
    lastCount2 = readAtomic(contadorPulsos2);
    lastCount3 = readAtomic(contadorPulsos3);
    lastCount4 = readAtomic(contadorPulsos4);
    lastTime = millis();

    // Calcular RPM para cada motor
    float rpm1 = (TICKS_REV_1 > 0) ? (delta1 / TICKS_REV_1) * 60.0 : 0;
    float rpm2 = (TICKS_REV_2 > 0) ? (delta2 / TICKS_REV_2) * 60.0 : 0;
    float rpm3 = (TICKS_REV_3 > 0) ? (delta3 / TICKS_REV_3) * 60.0 : 0;
    float rpm4 = (TICKS_REV_4 > 0) ? (delta4 / TICKS_REV_4) * 60.0 : 0;
    
    Serial.print(F("Pulsos: M1=")); Serial.print(lastCount1);
    Serial.print(F(" M2=")); Serial.print(lastCount2);
    Serial.print(F(" M3=")); Serial.print(lastCount3);
    Serial.print(F(" M4=")); Serial.print(lastCount4);
    Serial.print(F(" | RPM: M1=")); Serial.print(rpm1, 1);
    Serial.print(F(" M2=")); Serial.print(rpm2, 1);
    Serial.print(F(" M3=")); Serial.print(rpm3, 1);
    Serial.print(F(" M4=")); Serial.println(rpm4, 1);
  }

  // === Muestreo / CSV ===
  if (streamOn) sampleAndPrint();
}

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// Configuración de comunicación
const long ESP32_BAUD = 115200;
const long UNO_BAUD = 9600;

// Configuración de servos
Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver();
unsigned int pos0 = 172;
unsigned int pos180 = 565;

// Variables del sistema
String inLine;
String ultimoComando = "";
unsigned long lastPingMs = 0;
bool modoSeguridad = true;
bool modoLento = true;
int velocidadMovimiento = 50; // ms entre movimientos


 

// Pines de servos (ajustar según tu configuración)
// Cuello
const int CUELLO_LATERAL = 3;   // Lateral (izq-der)
const int CUELLO_INFERIOR = 4;  // Inferior (arriba-abajo)
const int CUELLO_SUPERIOR = 5;  // Superior (rotación)

// Brazos
const int HIGH_DER = 1;  
const int BRAZO_IZQ = 8;        // Brazo izquierdo
const int FRENTE_IZQ = 7;       // Frente izquierdo

const int HIGH_IZQ = 6;   
const int BRAZO_DER = 9;        // Brazo derecho
const int FRENTE_DER = 0;       // Frente derecho
const int POLLO_DER = 2;

// Rangos de seguridad
const int CUELLO_LATERAL_MIN = 120;
const int CUELLO_LATERAL_MAX = 160;
const int CUELLO_INFERIOR_MIN = 60;
const int CUELLO_INFERIOR_MAX = 130;
const int CUELLO_SUPERIOR_MIN = 109;
const int CUELLO_SUPERIOR_MAX = 110;

const int BRAZO_IZQ_MIN = 10;
const int BRAZO_IZQ_MAX = 30;
const int FRENTE_IZQ_MIN = 60;
const int FRENTE_IZQ_MAX = 120;
const int HIGH_IZQ_MIN = 70;
const int HIGH_IZQ_MAX = 90;




const int BRAZO_DER_MIN = 0;
const int BRAZO_DER_MAX = 30;
const int FRENTE_DER_MIN = 70;
const int FRENTE_DER_MAX = 110;
const int HIGH_DER_MIN = 70;
const int HIGH_DER_MAX = 90;
const int POLLO_DER_MIN = 0;
const int POLLO_DER_MAX = 90;



// Posiciones de descanso
const int CUELLO_LATERAL_DESCANSO = 155;
const int CUELLO_INFERIOR_DESCANSO = 95;
const int CUELLO_SUPERIOR_DESCANSO = 105;

const int BRAZO_IZQ_DESCANSO = 0;
const int FRENTE_IZQ_DESCANSO = 100;
const int HIGH_IZQ_DESCANSO = 80;
const int BRAZO_DER_DESCANSO = 0;
const int FRENTE_DER_DESCANSO = 90;
const int HIGH_DER_DESCANSO = 80;
const int POLLO_DER_DESCANSO = 45;

void setup() {
  Serial.begin(115200);       // Monitor serie del MEGA (PC)
  Serial1.begin(UNO_BAUD);    // Hacia el UNO (TX1=18, RX1=19)
  Serial2.begin(ESP32_BAUD);  // Hacia el ESP32 (TX2=16, RX2=17)

  // Inicializar I2C (requerido para Adafruit_PWMServoDriver)
  Wire.begin();
  delay(100);

  // Inicializar servos
  servos.begin();
  servos.setPWMFreq(60);
  delay(100);

  Serial.println("🤖 Controlador MEGA - Brazos y Cuello");
  Serial.println("Serial2=115200 TX2=16 RX2=17");
  Serial.println("Serial1=9600 TX1=18 RX1=19");
  Serial.println("Inicializando servos...");

  // Posición inicial
  // posicionDescanso();
  
  Serial.println("✅ MEGA listo para recibir comandos");
  
  // Enviar confirmación al ESP32
  Serial2.println("MEGA:Iniciado y listo");
}

void loop() {
  // 1) Comandos desde ESP32 por Serial2
  if (Serial2.available()) {
    String linea = Serial2.readStringUntil('\n');
    linea.trim();
    procesarComando(linea);
  }

  // 2) Respuestas desde UNO por Serial1
  if (Serial1.available()) {
    String respuesta = Serial1.readStringUntil('\n');
    respuesta.trim();
    Serial.print("[UNO] "); Serial.println(respuesta);
    // Reenviar al ESP32
    Serial2.print("UNO:"); Serial2.println(respuesta);
  }

  // 3) Ping periódico
  if (millis() - lastPingMs > 10000) {
    lastPingMs = millis();
    Serial2.println("MEGA:PONG");
  }
}

// ===== FUNCIONES DE PROCESAMIENTO =====

void procesarComando(String comando) {
  ultimoComando = comando;
  Serial.print("[CMD] "); Serial.println(comando);

  // Extraer velocidad si está presente
  if (comando.indexOf("VEL=") >= 0) {
    int velIndex = comando.indexOf("VEL=");
    int velEnd = comando.indexOf(" ", velIndex);
    if (velEnd == -1) velEnd = comando.length();
    velocidadMovimiento = comando.substring(velIndex + 4, velEnd).toInt();
    comando = comando.substring(0, velIndex);
    comando.trim();
  }

  // Procesar comandos
  if (comando.startsWith("PING")) {
    Serial2.println("MEGA:PONG");
  }
  else if (comando.startsWith("RESET")) {
    resetRobot();
  }
  else if (comando.startsWith("SEGURIDAD")) {
    procesarSeguridad(comando);
  }
  else if (comando.startsWith("CUELLO")) {
    procesarCuello(comando);
  }
  else if (comando.startsWith("BRAZOS")) {
    procesarBrazos(comando);
  }
  else if (comando.startsWith("SERVO")) {
    procesarServoDirecto(comando);
  }
  else if (comando.startsWith("UNO:")) {
    // Reenviar al UNO
    String cmdUno = comando.substring(4);
    Serial1.println(cmdUno);
    Serial.print("[UNO TX] "); Serial.println(cmdUno);
  }
  // Detectar comandos específicos de manos/dedos/muñecas y pasarlos al UNO
  else if (comando.startsWith("MANO") ||
           comando.startsWith("DEDO") ||
           comando.startsWith("MUNECA") ||
           comando.startsWith("MUÑECA") ||
           comando.startsWith("GESTO")) {
    // Pasar comando de manos/dedos/muñecas al UNO
    Serial1.println(comando);
    Serial.print("[UNO TX] "); Serial.println(comando);
    Serial2.print("MEGA:Comando de manos/dedos/muñecas enviado al UNO: ");
    Serial2.println(comando);
  }
  else {
    Serial.print("Comando no reconocido: "); Serial.println(comando);
    Serial2.print("MEGA:ERROR - Comando no reconocido: ");
    Serial2.println(comando);
 
  }
}

// ===== FUNCIONES DE SEGURIDAD =====

void procesarSeguridad(String comando) {
  if (comando.indexOf("ON") >= 0 || comando.indexOf("ACTIVAR") >= 0) {
    modoSeguridad = true;
    Serial.println("MEGA: Modo seguridad ACTIVADO");
    Serial2.println("MEGA:Seguridad ACTIVADA");
  }
  else if (comando.indexOf("OFF") >= 0 || comando.indexOf("DESACTIVAR") >= 0) {
    modoSeguridad = false;
    Serial.println("MEGA: Modo seguridad DESACTIVADO");
    Serial2.println("MEGA:Seguridad DESACTIVADA");
  }
  else {
    // Enviar estado actual
    Serial2.print("MEGA:Seguridad actual: ");
    Serial2.println(modoSeguridad ? "ACTIVADA" : "DESACTIVADA");
  }
}

// ===== FUNCIONES DE CUELLO =====

void procesarCuello(String comando) {
  if (comando.indexOf("CENTRAR") >= 0) {
    moverCuello(CUELLO_LATERAL_DESCANSO, CUELLO_INFERIOR_DESCANSO, CUELLO_SUPERIOR_DESCANSO);
  }
  else if (comando.indexOf("ALEATORIO") >= 0) {
    cuelloAleatorio();
  }
  else if (comando.indexOf("SI") >= 0) {
    cuelloSi();
  }
  else if (comando.indexOf("NO") >= 0) {
    cuelloNo();
  }
  else {
    // Extraer parámetros L=, I=, S=
    int lateral = extraerParametro(comando, "L=", CUELLO_LATERAL_DESCANSO);
    int inferior = extraerParametro(comando, "I=", CUELLO_INFERIOR_DESCANSO);
    int superior = extraerParametro(comando, "S=", CUELLO_SUPERIOR_DESCANSO);
    
    moverCuello(lateral, inferior, superior);
  }
}

void moverCuello(int lateral, int inferior, int superior) {
  if (!validarCuello(lateral, inferior, superior)) return;
  
  Serial.print("Moviendo cuello - L:"); Serial.print(lateral);
  Serial.print(" I:"); Serial.print(inferior);
  Serial.print(" S:"); Serial.println(superior);
  
  setServo(CUELLO_LATERAL, lateral);
  delay(velocidadMovimiento);
  setServo(CUELLO_INFERIOR, inferior);
  delay(velocidadMovimiento);
  setServo(CUELLO_SUPERIOR, superior);
  
  Serial2.print("MEGA:Cuello movido L="); Serial2.print(lateral);
  Serial2.print(" I="); Serial2.print(inferior);
  Serial2.print(" S="); Serial2.println(superior);
}

void cuelloAleatorio() {
  int lateral = random(CUELLO_LATERAL_MIN, CUELLO_LATERAL_MAX);
  int inferior = random(CUELLO_INFERIOR_MIN, CUELLO_INFERIOR_MAX);
  int superior = random(CUELLO_SUPERIOR_MIN, CUELLO_SUPERIOR_MAX);
  
  moverCuello(lateral, inferior, superior);
}

void cuelloSi() {
  // Movimiento de "sí" (arriba-abajo)
  for (int i = 0; i < 3; i++) {
    setServo(CUELLO_INFERIOR, CUELLO_INFERIOR_MIN);
    delay(500);
    setServo(CUELLO_INFERIOR, CUELLO_INFERIOR_MAX);
    delay(500);
  }
  setServo(CUELLO_INFERIOR, CUELLO_INFERIOR_DESCANSO);
  Serial2.println("MEGA:Cuello - Sí completado");
}

void cuelloNo() {
  // Movimiento de "no" (izquierda-derecha)
  for (int i = 0; i < 3; i++) {
    setServo(CUELLO_LATERAL, CUELLO_LATERAL_MIN);
    delay(500);
    setServo(CUELLO_LATERAL, CUELLO_LATERAL_MAX);
    delay(500);
  }
  setServo(CUELLO_LATERAL, CUELLO_LATERAL_DESCANSO);
  Serial2.println("MEGA:Cuello - No completado");
}

// ===== FUNCIONES DE BRAZOS =====

void procesarBrazos(String comando) {
  if (comando.indexOf("DESCANSO") >= 0) {
    brazosDescanso();
  }
  else if (comando.indexOf("SALUDO") >= 0) {
    brazosSaludo();
  }
  else if (comando.indexOf("ABRAZAR") >= 0) {
    brazosAbrazar();
  }
  else {
    // Extraer parámetros BI=, FI=, HI=, BD=, FD=, HD=, PD=
    int bi = extraerParametro(comando, "BI=", BRAZO_IZQ_DESCANSO);
    int fi = extraerParametro(comando, "FI=", FRENTE_IZQ_DESCANSO);
    int hi = extraerParametro(comando, "HI=", HIGH_IZQ_DESCANSO);
    int bd = extraerParametro(comando, "BD=", BRAZO_DER_DESCANSO);
    int fd = extraerParametro(comando, "FD=", FRENTE_DER_DESCANSO);
    int hd = extraerParametro(comando, "HD=", HIGH_DER_DESCANSO);
    int pd = extraerParametro(comando, "PD=", POLLO_DER_DESCANSO);
    
    moverBrazos(bi, fi, hi, bd, fd, hd, pd);
  }
}

void moverBrazos(int bi, int fi, int hi, int bd, int fd, int hd, int pd) {
  if (!validarBrazos(bi, fi, hi, bd, fd, hd, pd)) return;
  
  Serial.print("Moviendo brazos - BI:"); Serial.print(bi);
  Serial.print(" FI:"); Serial.print(fi);
  Serial.print(" HI:"); Serial.print(hi);
  Serial.print(" BD:"); Serial.print(bd);
  Serial.print(" FD:"); Serial.print(fd);
  Serial.print(" HD:"); Serial.print(hd);
  Serial.print(" PD:"); Serial.println(pd);
  
  setServo(BRAZO_IZQ, bi);
  delay(velocidadMovimiento);
  setServo(FRENTE_IZQ, fi);
  delay(velocidadMovimiento);
  setServo(HIGH_IZQ, hi);
  delay(velocidadMovimiento);
  setServo(BRAZO_DER, bd);
  delay(velocidadMovimiento);
  setServo(FRENTE_DER, fd);
  delay(velocidadMovimiento);
  setServo(HIGH_DER, hd);
  delay(velocidadMovimiento);
  setServo(POLLO_DER, pd);
  
  Serial2.print("MEGA:Brazos movidos BI="); Serial2.print(bi);
  Serial2.print(" FI="); Serial2.print(fi);
  Serial2.print(" HI="); Serial2.print(hi);
  Serial2.print(" BD="); Serial2.print(bd);
  Serial2.print(" FD="); Serial2.print(fd);
  Serial2.print(" HD="); Serial2.print(hd);
  Serial2.print(" PD="); Serial2.println(pd);
}

void brazosDescanso() {
  moverBrazos(BRAZO_IZQ_DESCANSO, FRENTE_IZQ_DESCANSO, HIGH_IZQ_DESCANSO, BRAZO_DER_DESCANSO, FRENTE_DER_DESCANSO, HIGH_DER_DESCANSO, POLLO_DER_DESCANSO);
  Serial2.println("MEGA:Brazos en posición de descanso");
}

void brazosSaludo() {
  // Saludo con brazo derecho
  setServo(BRAZO_DER, 20);
  delay(500);
  setServo(FRENTE_DER, 110);
  delay(500);
  setServo(HIGH_DER, 85);
  delay(500);
  setServo(POLLO_DER, 60);
  delay(1000);
  
  // Movimiento de saludo
  for (int i = 0; i < 3; i++) {
    setServo(FRENTE_DER, 90);
    delay(300);
    setServo(FRENTE_DER, 110);
    delay(300);
  }
  
  brazosDescanso();
  Serial2.println("MEGA:Saludo completado");
}

void brazosAbrazar() {
  // Movimiento de abrazo
  setServo(BRAZO_IZQ, 30);
  setServo(BRAZO_DER, 30);
  delay(500);
  setServo(FRENTE_IZQ, 80);
  setServo(FRENTE_DER, 80);
  delay(500);
  setServo(HIGH_IZQ, 75);
  setServo(HIGH_DER, 75);
  delay(500);
  setServo(POLLO_DER, 30);
  delay(1000);
  
  // Simular abrazo
  for (int i = 0; i < 2; i++) {
    setServo(FRENTE_IZQ, 70);
    setServo(FRENTE_DER, 70);
    delay(500);
    setServo(FRENTE_IZQ, 80);
    setServo(FRENTE_DER, 80);
    delay(500);
  }
  
  brazosDescanso();
  Serial2.println("MEGA:Abrazo completado");
}

// ===== FUNCIONES DE SERVO DIRECTO =====

void procesarServoDirecto(String comando) {
  int canal = extraerParametro(comando, "CH=", 0);
  int angulo = extraerParametro(comando, "ANG=", 90);
  
  if (!validarServo(canal, angulo)) return;
  
  setServo(canal, angulo);
  Serial2.print("MEGA:Servo CH="); Serial2.print(canal);
  Serial2.print(" ANG="); Serial2.println(angulo);
}

// ===== FUNCIONES UTILITARIAS =====

int extraerParametro(String comando, String parametro, int valorDefault) {
  int index = comando.indexOf(parametro);
  if (index == -1) return valorDefault;
  
  int start = index + parametro.length();
  int end = comando.indexOf(" ", start);
  if (end == -1) end = comando.length();
  
  return comando.substring(start, end).toInt();
}

void setServo(uint8_t canal, int angulo) {
  int duty = map(angulo, 0, 180, pos0, pos180);
  servos.setPWM(canal, 0, duty);
  Serial.print("Servo "); Serial.print(canal);
  Serial.print(" -> "); Serial.print(angulo);
  Serial.print("° (duty: "); Serial.print(duty);
  Serial.println(")");
}

// ===== VALIDACIONES DE SEGURIDAD =====

bool validarCuello(int lateral, int inferior, int superior) {
  if (!modoSeguridad) return true;
  
  if (lateral < CUELLO_LATERAL_MIN || lateral > CUELLO_LATERAL_MAX) {
    Serial.println("ERROR: Lateral fuera de rango");
    return false;
  }
  if (inferior < CUELLO_INFERIOR_MIN || inferior > CUELLO_INFERIOR_MAX) {
    Serial.println("ERROR: Inferior fuera de rango");
    return false;
  }
  if (superior < CUELLO_SUPERIOR_MIN || superior > CUELLO_SUPERIOR_MAX) {
    Serial.println("ERROR: Superior fuera de rango");
    return false;
  }
  return true;
}

bool validarBrazos(int bi, int fi, int hi, int bd, int fd, int hd, int pd) {
  if (!modoSeguridad) return true;
  
  if (bi < BRAZO_IZQ_MIN || bi > BRAZO_IZQ_MAX) {
    Serial.println("ERROR: Brazo izquierdo fuera de rango");
    return false;
  }
  if (fi < FRENTE_IZQ_MIN || fi > FRENTE_IZQ_MAX) {
    Serial.println("ERROR: Frente izquierdo fuera de rango");
    return false;
  }
  if (hi < HIGH_IZQ_MIN || hi > HIGH_IZQ_MAX) {
    Serial.println("ERROR: High izquierdo fuera de rango");
    return false;
  }
  // if (bd < BRAZO_DER_MIN || bd > BRAZO_DER_MAX) {
  //   Serial.println("ERROR: Brazo derecho fuera de rango");
  //   return false;
  // }
  if (fd < FRENTE_DER_MIN || fd > FRENTE_DER_MAX) {
    Serial.println("ERROR: Frente derecho fuera de rango");
    return false;
  }
  if (hd < HIGH_DER_MIN || hd > HIGH_DER_MAX) {
    Serial.println("ERROR: High derecho fuera de rango");
    return false;
  }
  if (pd < POLLO_DER_MIN || pd > POLLO_DER_MAX) {
    Serial.println("ERROR: Pollo derecho fuera de rango");
    return false;
  }
  return true;
}

bool validarServo(int canal, int angulo) {
  if (!modoSeguridad) return true;
  
  if (canal < 0 || canal > 15) {
    Serial.println("ERROR: Canal fuera de rango");
    return false;
  }
  if (angulo < 0 || angulo > 180) {
    Serial.println("ERROR: Ángulo fuera de rango");
    return false;
  }
  return true;
}

void posicionDescanso() {
  Serial.println("Posicionando en descanso...");
  
  // Cuello centrado
  setServo(CUELLO_LATERAL, CUELLO_LATERAL_DESCANSO);
  setServo(CUELLO_INFERIOR, CUELLO_INFERIOR_DESCANSO);
  setServo(CUELLO_SUPERIOR, CUELLO_SUPERIOR_DESCANSO);
  
  // Brazos en descanso
  setServo(BRAZO_IZQ, BRAZO_IZQ_DESCANSO);
  setServo(FRENTE_IZQ, FRENTE_IZQ_DESCANSO);
  setServo(HIGH_IZQ, HIGH_IZQ_DESCANSO);
  setServo(BRAZO_DER, BRAZO_DER_DESCANSO);
  setServo(FRENTE_DER, FRENTE_DER_DESCANSO);
  setServo(HIGH_DER, HIGH_DER_DESCANSO);
  setServo(POLLO_DER, POLLO_DER_DESCANSO);
  
  Serial.println("Posición de descanso establecida");
}

void resetRobot() {
  Serial.println("🔄 Reset del robot...");
  posicionDescanso();
  Serial2.println("MEGA:Reset completado");
}

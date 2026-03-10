
const int IN1 = 10;  // DRV8833 IN1
const int IN2 = 11;  // DRV8833 IN2
const int IN3 = 12;  // DRV8833 IN3
const int IN4 = 13;  // DRV8833 IN4


// 
const int ENC_A = 6; // Encoder C1
const int ENC_B = 7; // Encoder C2

volatile long encoderCount = 0; // Contador de pulsos
int velocidad = 150;            // PWM inicial (0-255)
unsigned long lastTime = 0;
long lastCount = 0;

void setup() {
  Serial.begin(9600);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(ENC_A, INPUT_PULLUP);
  pinMode(ENC_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENC_A), encoderISR, CHANGE);

  Serial.println("Comandos: F=adelante, B=atras, S=stop, Vxxx=velocidad (0-255)");
}

void loop() {
  // Calcular RPM cada segundo
  if (millis() - lastTime >= 1000) {
    long delta = encoderCount - lastCount;
    lastCount = encoderCount;
    lastTime = millis();

    // Suponiendo encoder de 11 pulsos por vuelta (ajusta según tu modelo)
    float rpm = (delta / 11.0) * 60.0;
    Serial.print("Pulsos: ");
    Serial.print(encoderCount);
    Serial.print(" | RPM: ");
    Serial.println(rpm);
  }

  // Leer comandos por Serial
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

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
        Serial.print("Velocidad ajustada a: ");
        Serial.println(velocidad);
      }
    }
  }
}

// --- Funciones de control ---
void adelante() {
  analogWrite(IN1, velocidad);
  analogWrite(IN2, 0);
  analogWrite(IN3, velocidad);
  analogWrite(IN4, 0);
  Serial.println("Motor adelante");
}

void atras() {
  analogWrite(IN1, 0);
  analogWrite(IN2, velocidad);
  analogWrite(IN3, 0);
  analogWrite(IN4, velocidad);
  Serial.println("Motor atras");
}

void stopMotor() {
  analogWrite(IN1, 0);
  analogWrite(IN2, 0);
  analogWrite(IN3, 0);
  analogWrite(IN4, 0);
  Serial.println("Motor detenido");
}

// --- Interrupción del encoder ---
void encoderISR() {
  int bState = digitalRead(ENC_B);
  if (bState == HIGH) {
    encoderCount++;
  } else {
    encoderCount--;
  }
}
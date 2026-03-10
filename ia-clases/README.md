# 🤖 RobotAtlas - Sistema de Control de Robot

Sistema completo para controlar y gestionar el robot ADAI, incluyendo interfaz gráfica, aplicación móvil y comunicación con ESP32.

## 🚀 Inicio Rápido

### Instalación Automática

**Windows:**
```cmd
cd ia-clases
setup.bat
run.bat
```

**Linux / macOS:**
```bash
cd ia-clases
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

### Instalación Manual

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   ```

2. **Activar entorno virtual:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar:**
   ```bash
   python robot_gui_conmodulos.py
   ```

📖 **Para más detalles, consulta [INSTALACION.md](INSTALACION.md)**

## 📁 Estructura del Proyecto

```
RobotAtlas/
├── ia-clases/                    # Aplicación principal Python
│   ├── robot_gui_conmodulos.py   # Aplicación principal
│   ├── requirements.txt           # Dependencias Python
│   ├── setup.bat / setup.sh      # Scripts de instalación
│   ├── run.bat / run.sh          # Scripts de ejecución
│   ├── INSTALACION.md            # Guía completa de instalación
│   ├── clases/                   # Clases del robot
│   ├── modules/                  # Módulos reutilizables
│   ├── services/                 # Servicios (ESP32, etc.)
│   └── tabs/                     # Componentes de la interfaz
├── atlas/                         # Aplicación móvil (ReactLynx)
└── Controladores Robot/          # Código Arduino/ESP32
```

## 🎯 Características Principales

- ✅ **Interfaz Gráfica Completa** - Control total del robot desde una GUI
- ✅ **Aplicación Móvil** - Control remoto desde dispositivos móviles
- ✅ **Comunicación ESP32** - Control directo del hardware del robot
- ✅ **Sistema de Clases** - Gestión y ejecución de clases educativas
- ✅ **Reconocimiento Facial** - Identificación de estudiantes
- ✅ **Síntesis de Voz** - Comunicación verbal del robot
- ✅ **Detección de Objetos** - Visión por computadora
- ✅ **API REST** - Comunicación entre componentes

## 📚 Documentación

- **[INSTALACION.md](INSTALACION.md)** - Guía completa de instalación
- **[docs/EJEMPLOS_CONSULTAS_API.md](docs/EJEMPLOS_CONSULTAS_API.md)** - Ejemplos de consultas API
- **[documentacion/](documentacion/)** - Documentación adicional

## 🔧 Requisitos

- **Python 3.8 o superior**
- **Windows 10+ / Linux / macOS**
- **Conexión a internet** (para descargar dependencias)
- **Cámara web** (opcional, para funciones de visión)
- **Micrófono** (opcional, para reconocimiento de voz)

## 📦 Dependencias Principales

- `opencv-python` - Visión por computadora
- `numpy` - Cálculos numéricos
- `tkinter` - Interfaz gráfica (incluido con Python)
- `face-recognition` - Reconocimiento facial
- `pyttsx3` - Síntesis de voz
- `SpeechRecognition` - Reconocimiento de voz
- `requests` - Comunicación HTTP
- `matplotlib` - Visualización
- Y muchas más... (ver `requirements.txt`)

## 🚀 Uso

### Ejecutar la Aplicación Principal

```bash
# Activar entorno virtual primero
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python robot_gui_conmodulos.py
```

### Configuración Inicial

1. **Configurar IP del ESP32:**
   - Abre la pestaña "ESP32" en la aplicación
   - Ingresa la IP del ESP32 (ej: `192.168.1.100`)
   - Haz clic en "Conectar"

2. **Configurar Servidor Móvil:**
   - Abre la pestaña "Mobile App"
   - Verifica que el servidor esté corriendo
   - Anota la IP y puerto para la app móvil

3. **Configurar Cámara:**
   - Abre la pestaña "Main"
   - Haz clic en "Start Camera" si tienes cámara conectada

## 🔌 Comunicación

### App Móvil → Servidor Python
- **Protocolo:** HTTP REST API
- **Puerto:** 8000 (por defecto)
- **Formato:** JSON

### Servidor Python → ESP32
- **Protocolo:** HTTP REST API
- **Puerto:** 80 (por defecto)
- **Formato:** Form URL-encoded

📖 **Ver [docs/EJEMPLOS_CONSULTAS_API.md](docs/EJEMPLOS_CONSULTAS_API.md) para ejemplos completos**

## ⚠️ Solución de Problemas

### Error: "Python no encontrado"
- Asegúrate de tener Python 3.8+ instalado
- Verifica que Python esté en el PATH

### Error: "No module named 'cv2'"
- Activa el entorno virtual
- Ejecuta: `pip install opencv-python`

### Error al instalar dlib
- **Windows:** Instala Visual C++ Build Tools
- **Linux:** `sudo apt-get install cmake libopenblas-dev`
- **macOS:** `brew install cmake`

📖 **Más soluciones en [INSTALACION.md](INSTALACION.md)**

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es privado y de uso interno.

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación en `docs/` y `documentacion/`
2. Consulta [INSTALACION.md](INSTALACION.md) para problemas de instalación
3. Revisa los logs de la aplicación para errores específicos

---

**¡Disfruta usando RobotAtlas!** 🤖✨



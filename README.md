# RobotAtlas

Sistema de control robótico educativo que combina una aplicación de escritorio Python, un cliente móvil ReactLynx y firmware ESP32.

---

## Instalador Windows (Recomendado)

La forma más rápida de usar RobotAtlas en Windows:

1. Ve a [Releases](https://github.com/adairobotproject/ADAI/releases/latest)
2. Descarga `RobotAtlasSetup.exe`
3. Ejecuta el instalador y sigue las instrucciones
4. Abre RobotAtlas desde el acceso directo del escritorio

> El instalador incluye todas las dependencias. No necesitas instalar Python ni nada adicional.

---

## Instalación Manual (desde código fuente)

### Windows

1. **Instalar Python 3.12**: https://www.python.org/downloads/
   - Marca **"Add Python to PATH"**
   - Marca **"tcl/tk and IDLE"** (para la GUI)

2. **Instalar Visual C++ Build Tools** (opcional pero recomendado para dlib): https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Selecciona "Desktop development with C++"

3. **Configurar el proyecto:**
```cmd
cd ia-clases
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-windows.txt
```

4. **Ejecutar:**
```cmd
cd ia-clases
venv\Scripts\activate
python robot_gui_conmodulos.py
```

> Si usas PowerShell y da error al activar: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### MAC / Linux

```bash
brew install python@3.12
sudo chown -R $(whoami) /opt/homebrew/Cellar
cd ia-clases
./setup_python312.sh
```

```bash
cd ia-clases
chmod +x setup.sh run.sh
./setup.sh
./run.sh
```

**O manualmente:**
```bash
cd ia-clases
source venv/bin/activate
python robot_gui_conmodulos.py
```

---

## Configuración de API Keys

RobotAtlas usa OpenAI y ElevenLabs para IA y síntesis de voz. Configura tus claves antes de ejecutar:

**Windows:**
```cmd
cd ia-clases
copy env.example .env
```

**MAC/Linux:**
```bash
cd ia-clases
cp env.example .env
```

Edita `.env` con tus API keys:
```
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
```

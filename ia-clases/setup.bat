@echo off
REM ============================================
REM Script de Setup para Windows
REM RobotAtlas - Sistema de Control de Robot
REM Requiere Python 3.12
REM ============================================

echo.
echo ============================================
echo   RobotAtlas - Configuracion del Proyecto
echo ============================================
echo.

REM Desactivar cualquier venv que esté activo
if defined VIRTUAL_ENV (
    echo [INFO] Desactivando entorno virtual existente...
    call deactivate 2>nul
)

REM Buscar Python 3.12 o superior
set PYTHON_CMD=
if not "%ROBOTATLAS_PYTHON_CMD%"=="" (
    set "PYTHON_CMD=%ROBOTATLAS_PYTHON_CMD%"
    goto :found_python
)

where python3.12 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.12
    goto :found_python
)

where python3.11 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.11
    goto :found_python
)

where python3.10 >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3.10
    goto :found_python
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    REM Verificar versión
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
    for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VER%") do (
        set MAJOR=%%a
        set MINOR=%%b
    )
    if %MAJOR% equ 3 if %MINOR% geq 10 if %MINOR% leq 12 (
        set PYTHON_CMD=python
        goto :found_python
    )
)

echo [ERROR] Python compatible no detectado (se recomienda Python 3.12; soportado 3.10-3.12)
echo.
echo Por favor instala Python 3.12 desde:
echo   https://www.python.org/downloads/
echo.
echo Durante la instalacion, marca "Add Python to PATH"
echo.
if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause
exit /b 1

:found_python
echo [OK] Python detectado
%PYTHON_CMD% --version
echo.

REM Verificar pip
%PYTHON_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando pip...
    %PYTHON_CMD% -m ensurepip --upgrade
)

echo [OK] pip detectado
echo.

REM Verificar dependencias del sistema en Windows
echo [INFO] Verificando dependencias del sistema para Windows...
echo.
echo [INFO] Nota: En Windows, algunas dependencias pueden requerir:
echo   - Visual C++ Build Tools para compilar dlib
echo   - CMake para compilar algunos paquetes
echo.
echo Si tienes problemas con dlib o PyAudio, considera instalar:
echo   - Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
echo   - CMake: https://cmake.org/download/
echo.

REM Eliminar venv antiguo si existe
if exist "venv" (
    echo [INFO] Eliminando entorno virtual antiguo...
    rmdir /s /q venv
    echo [OK] Entorno virtual antiguo eliminado
)

REM Crear nuevo entorno virtual
echo [INFO] Creando entorno virtual...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual
    echo Asegurate de que %PYTHON_CMD% esta instalado correctamente
    if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause
    exit /b 1
)

echo [OK] Entorno virtual creado
echo.

REM Activar entorno virtual
echo [INFO] Activando entorno virtual...
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se pudo encontrar el script de activacion del venv
    if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Verificar versión
echo [INFO] Verificando Python en el entorno virtual...
python --version
if errorlevel 1 (
    echo [ERROR] Python no esta disponible en el entorno virtual
    if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause
    exit /b 1
)
echo.

REM Verificar tkinter (crítico para la GUI)
echo [INFO] Verificando soporte de tkinter...
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] tkinter no esta disponible en este Python
    echo.
    echo En Windows, tkinter generalmente viene incluido con Python.
    echo Si no esta disponible, reinstala Python desde python.org
    echo y asegurate de marcar la opcion "tcl/tk and IDLE"
    echo.
    if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause
    exit /b 1
) else (
    echo [OK] tkinter esta disponible
)
echo.

REM Actualizar pip
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Instalar dependencias
echo [INFO] Instalando dependencias desde requirements.txt...
echo Esto puede tardar varios minutos...
echo.

REM Instalar paquetes base primero
echo [INFO] Instalando paquetes base...
python -m pip install numpy scipy matplotlib pillow
if errorlevel 1 (
    echo [ADVERTENCIA] Algunos paquetes base fallaron
)

REM Instalar OpenCV
echo [INFO] Instalando OpenCV...
python -m pip install opencv-python opencv-contrib-python
if errorlevel 1 (
    echo [ADVERTENCIA] OpenCV fallo
)

REM Instalar resto de dependencias
echo [INFO] Instalando resto de dependencias...
if exist "requirements-windows.txt" (
    python -m pip install -r requirements-windows.txt
    if errorlevel 1 (
        echo [ADVERTENCIA] Algunos paquetes fallaron durante la instalacion
    )
) else (
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ADVERTENCIA] Algunos paquetes fallaron durante la instalacion
    )
)

REM Intentar instalar paquetes problemáticos después
echo.
echo [INFO] Intentando instalar paquetes que requieren compilacion...

REM Intentar instalar dlib (requiere Visual C++ Build Tools)
python -c "import dlib" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando dlib (puede tardar varios minutos)...
    echo [INFO] Nota: dlib requiere Visual C++ Build Tools en Windows
    python -m pip install dlib==19.24.6
    if errorlevel 1 (
        echo [ADVERTENCIA] dlib fallo. Asegurate de tener Visual C++ Build Tools instalado.
        echo   Descarga desde: https://visualstudio.microsoft.com/downloads/
    )
)

REM Intentar instalar PyAudio
python -c "import pyaudio" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando PyAudio...
    python -m pip install PyAudio==0.2.14
    if errorlevel 1 (
        echo [ADVERTENCIA] PyAudio fallo. Puede requerir dependencias adicionales.
    )
)

REM Intentar instalar face_recognition (depende de dlib)
python -c "import face_recognition" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando face_recognition...
    python -m pip install face-recognition==1.3.0
    if errorlevel 1 (
        echo [ADVERTENCIA] face_recognition fallo (requiere dlib).
    )
)

REM Intentar instalar mediapipe
python -c "import mediapipe" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando mediapipe...
    python -m pip install mediapipe==0.10.21
    if errorlevel 1 (
        echo [ADVERTENCIA] mediapipe fallo.
    )
)

REM Verificar instalación
echo.
set INSTALL_FAILED=0
echo [INFO] Verificando instalacion de paquetes criticos...
python -c "import cv2; print('OK OpenCV:', cv2.__version__)" 2>nul || (echo "ERROR OpenCV no instalado" & set INSTALL_FAILED=1)
python -c "import numpy; print('OK NumPy:', numpy.__version__)" 2>nul || echo "ERROR NumPy no instalado"
python -c "import matplotlib; print('OK Matplotlib:', matplotlib.__version__)" 2>nul || echo "ERROR Matplotlib no instalado"
python -c "import tkinter; print('OK tkinter instalado')" 2>nul || (echo "ERROR tkinter no instalado" & set INSTALL_FAILED=1)
python -c "from PIL import Image, ImageTk; print('OK Pillow instalado')" 2>nul || (echo "ERROR Pillow no instalado" & set INSTALL_FAILED=1)
python -c "import mediapipe; print('OK MediaPipe instalado')" 2>nul || echo "ERROR MediaPipe no instalado"
python -c "import face_recognition; print('OK Face Recognition instalado')" 2>nul || echo "ERROR Face Recognition no instalado"
python -c "import pygame; print('OK Pygame instalado')" 2>nul || echo "ERROR Pygame no instalado"
python -c "import dotenv; print('OK python-dotenv instalado')" 2>nul || echo "ERROR python-dotenv no instalado"
python -c "import openai; print('OK OpenAI instalado')" 2>nul || echo "ERROR OpenAI no instalado"
python -c "import fitz; print('OK PyMuPDF instalado')" 2>nul || echo "ERROR PyMuPDF no instalado"
python -c "import requests; print('OK Requests instalado')" 2>nul || echo "ERROR Requests no instalado"
if "%INSTALL_FAILED%"=="1" (
    echo.
    echo [ERROR] Instalacion incompleta: faltan dependencias criticas para iniciar RobotAtlas.
    exit /b 1
)

echo.
echo ============================================
echo   Configuracion Completada
echo ============================================
echo.
echo Para ejecutar el proyecto:
echo   1. Activa el entorno virtual: venv\Scripts\activate
echo   2. Ejecuta: python robot_gui_conmodulos.py
echo.
echo O usa el script run.bat
echo.
if /I not "%ROBOTATLAS_SILENT_SETUP%"=="1" pause




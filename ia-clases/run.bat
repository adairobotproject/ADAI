@echo off
REM ============================================
REM Script de Ejecucion para Windows
REM RobotAtlas - Sistema de Control de Robot
REM ============================================

REM Verificar que el entorno virtual existe
if not exist "venv" (
    echo [ERROR] El entorno virtual no existe
    echo Ejecuta setup.bat primero para configurar el proyecto
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar que el archivo principal existe
if not exist "robot_gui_conmodulos.py" (
    echo [ERROR] No se encuentra robot_gui_conmodulos.py
    echo Asegurate de estar en el directorio correcto
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Iniciando RobotAtlas...
echo ============================================
echo.

REM Ejecutar la aplicacion
python robot_gui_conmodulos.py

REM Si hay error, mantener la ventana abierta
if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion se cerro con errores
    pause
)

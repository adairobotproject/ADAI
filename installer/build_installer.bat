@echo off
setlocal EnableDelayedExpansion

:: ============================================================
:: RobotAtlas Installer Builder
:: Runs PyInstaller (spec file) then Inno Setup to produce
:: a single RobotAtlasSetup.exe installer.
::
:: Usage:  Run from the repository root directory.
::         installer\build_installer.bat
:: ============================================================

set "REPO_ROOT=%~dp0.."
set "SRC_DIR=%REPO_ROOT%\ia-clases"
set "INSTALLER_DIR=%REPO_ROOT%\installer"
set "SPEC_FILE=%INSTALLER_DIR%\robotatlas.spec"
set "ISS_FILE=%INSTALLER_DIR%\RobotAtlas.iss"
set "DIST_DIR=%SRC_DIR%\dist\RobotAtlas"

:: ---- Locate Inno Setup ----
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    where ISCC >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "delims=" %%I in ('where ISCC') do set "ISCC=%%I"
    )
)

if not defined ISCC (
    echo [ERROR] Inno Setup 6 not found. Install from https://jrsoftware.org/issetup.exe
    exit /b 1
)
echo [OK] Inno Setup found: %ISCC%

:: ---- Activate virtual environment ----
set "VENV_DIR=%SRC_DIR%\venv"
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call "%VENV_DIR%\Scripts\activate.bat"
) else (
    echo [WARN] No venv found at %VENV_DIR%. Using system Python.
)

:: ---- Verify PyInstaller ----
pyinstaller --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] PyInstaller not found. Install with: pip install pyinstaller
    exit /b 1
)
echo [OK] PyInstaller found.

:: ---- Step 1: Clean previous build artifacts ----
echo.
echo ============================================================
echo  Step 1/3: Cleaning previous build artifacts
echo ============================================================
if exist "%SRC_DIR%\build\robotatlas" (
    echo Removing build\robotatlas...
    rmdir /s /q "%SRC_DIR%\build\robotatlas"
)
if exist "%DIST_DIR%" (
    echo Removing dist\RobotAtlas...
    rmdir /s /q "%DIST_DIR%"
)
if exist "%INSTALLER_DIR%\Output" (
    echo Removing installer\Output...
    rmdir /s /q "%INSTALLER_DIR%\Output"
)
echo [OK] Clean complete.

:: ---- Step 2: Run PyInstaller ----
echo.
echo ============================================================
echo  Step 2/3: Building with PyInstaller
echo ============================================================
pushd "%SRC_DIR%"
pyinstaller "%SPEC_FILE%" --noconfirm
if !errorlevel! neq 0 (
    echo [ERROR] PyInstaller build failed.
    popd
    exit /b 1
)
popd

:: Verify dist was created
if not exist "%DIST_DIR%\RobotAtlas.exe" (
    echo [ERROR] Expected output not found: %DIST_DIR%\RobotAtlas.exe
    exit /b 1
)
echo [OK] PyInstaller build complete.

:: ---- Step 3: Run Inno Setup ----
echo.
echo ============================================================
echo  Step 3/3: Building installer with Inno Setup
echo ============================================================
"%ISCC%" "%ISS_FILE%"
if !errorlevel! neq 0 (
    echo [ERROR] Inno Setup compilation failed.
    exit /b 1
)

:: ---- Done ----
echo.
echo ============================================================
echo  BUILD COMPLETE
echo ============================================================
echo.
echo  Installer: %INSTALLER_DIR%\Output\RobotAtlasSetup.exe
echo.

:: Show file size
for %%F in ("%INSTALLER_DIR%\Output\RobotAtlasSetup.exe") do (
    set "SIZE=%%~zF"
    set /a "SIZE_MB=!SIZE! / 1048576"
    echo  Size: ~!SIZE_MB! MB
)
echo.

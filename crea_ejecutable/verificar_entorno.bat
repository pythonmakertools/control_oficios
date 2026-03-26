@echo off
echo ============================================
echo   VERIFICACIÓN DE ENTORNO
echo ============================================
echo.

REM Verificar si el ejecutable funciona
echo Probando ejecutable...
start /B "" "%~dp0GestionOficios_Cliente.exe" --help >nul 2>&1
if errorlevel 1 (
    echo ❌ Error al ejecutar la aplicación
    echo.
    echo Posibles soluciones:
    echo 1. Instalar Visual C++ Redistributable
    echo 2. Verificar que el archivo .env existe
    pause
    exit /b 1
) else (
    echo ✅ Aplicación funciona correctamente
)

echo.
echo ============================================
pause
@echo off
echo ============================================
echo   CONSTRUCCIÓN DE EJECUTABLES
echo ============================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instale Python 3.8 o superior.
    pause
    exit /b 1
)
echo ✅ Python encontrado

REM Instalar/Actualizar PyInstaller
echo.
echo [2/5] Instalando PyInstaller...
pip install --upgrade pyinstaller
echo ✅ PyInstaller instalado

REM Verificar archivos necesarios
echo.
echo [3/5] Verificando archivos...
if not exist "run_cliente.py" (
    echo ❌ No se encuentra run_cliente.py
    pause
    exit /b 1
)
if not exist "run_servidor.py" (
    echo ❌ No se encuentra run_servidor.py
    pause
    exit /b 1
)
echo ✅ Archivos verificados

REM Limpiar builds anteriores
echo.
echo [4/5] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo ✅ Limpieza completada

REM Construir cliente
echo.
echo [5/5] Construyendo ejecutables...
echo    → Construyendo Cliente...
pyinstaller cliente.spec --clean --noconfirm
if errorlevel 1 (
    echo    ❌ Error construyendo Cliente
    pause
    exit /b 1
)
echo    ✅ Cliente construido

REM Construir servidor
echo    → Construyendo Servidor...
pyinstaller servidor.spec --clean --noconfirm
if errorlevel 1 (
    echo    ❌ Error construyendo Servidor
    pause
    exit /b 1
)
echo    ✅ Servidor construido

echo.
echo ============================================
echo   CONSTRUCCIÓN COMPLETADA
echo ============================================
echo.
echo 📁 Ejecutables generados en carpeta 'dist/'
echo.
echo   Cliente: dist\GestionOficios_Cliente\GestionOficios_Cliente.exe
echo   Servidor: dist\GestionOficios_Servidor\GestionOficios_Servidor.exe
echo.
echo ⚠️  IMPORTANTE: Copiar el archivo .env a la carpeta del ejecutable
echo.
pause
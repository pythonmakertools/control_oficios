@echo off
echo Creando accesos directos en el escritorio...

REM Cliente
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $shortcut = $ws.CreateShortcut('%userprofile%\Desktop\GestionOficios_Cliente.lnk'); $shortcut.TargetPath = '%~dp0dist\GestionOficios_Cliente\GestionOficios_Cliente.exe'; $shortcut.WorkingDirectory = '%~dp0dist\GestionOficios_Cliente'; $shortcut.Description = 'Gestión de Oficios - Cliente'; $shortcut.Save()"
if errorlevel 1 (
    echo ❌ Error creando acceso directo del Cliente
) else (
    echo ✅ Acceso directo del Cliente creado
)

REM Servidor
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $shortcut = $ws.CreateShortcut('%userprofile%\Desktop\GestionOficios_Servidor.lnk'); $shortcut.TargetPath = '%~dp0dist\GestionOficios_Servidor\GestionOficios_Servidor.exe'; $shortcut.WorkingDirectory = '%~dp0dist\GestionOficios_Servidor'; $shortcut.Description = 'Gestión de Oficios - Servidor'; $shortcut.Save()"
if errorlevel 1 (
    echo ❌ Error creando acceso directo del Servidor
) else (
    echo ✅ Acceso directo del Servidor creado
)

echo.
echo Accesos directos creados en el escritorio.
pause
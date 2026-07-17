@echo off
title AI Meeting Assistant Launcher
color 0B

echo =========================================
echo    Iniciando AI Meeting Assistant...
echo =========================================
echo.

:: Cambiar al directorio donde se encuentra este archivo .bat
cd /d "%~dp0"

:: Ejecutar la interfaz grafica (mantendrá esta consola abierta por si hay errores)
python main_ui.py

echo.
echo La aplicacion se ha cerrado.
pause

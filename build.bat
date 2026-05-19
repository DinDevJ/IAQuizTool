@echo off
setlocal

echo === IAQuizTool Build Script ===
echo.

where pyinstaller >nul 2>nul
if errorlevel 1 (
    echo PyInstaller no encontrado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo Error instalando PyInstaller.
        exit /b 1
    )
)

echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error instalando dependencias.
    exit /b 1
)

echo.
echo Limpiando builds anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist IAQuizTool.spec del IAQuizTool.spec

echo.
echo Compilando ejecutable...
pyinstaller --onefile --windowed --name IAQuizTool main.py
if errorlevel 1 (
    echo.
    echo Error durante la compilacion.
    exit /b 1
)

echo.
echo === Build completado ===
echo Ejecutable generado: dist\IAQuizTool.exe
echo.
echo Copialo a una carpeta vacia (junto con contexto.txt si lo usas).
echo La primera vez que lo ejecutes te pedira tu API Key de Gemini
echo y la carpeta donde se guardan tus capturas de pantalla.
echo La configuracion se guardara en config.json junto al .exe.
echo.
pause

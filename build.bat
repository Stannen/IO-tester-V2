@echo off
REM build.bat - Maak een standalone distributie met PyInstaller en extra folders

setlocal

REM C:\Users\Hacker\OneDrive\Documenten\GitHub\IO-tester-V2

set PROJECT_PATH=%~dp0
set ENTRY=%PROJECT_PATH%\main.py
set APPNAME=mijn_app
set DIST_DIR=%PROJECT_PATH%\release
set EXTRA_DIRS=beckhoff;default;static;templates

echo ============================================
echo ">>> Start build voor %APPNAME%"
echo ============================================

REM Opruimen oude build
echo ">>> Opruimen oude build..."
rmdir /s /q "%PROJECT_PATH%\build" "%PROJECT_PATH%\dist" "%DIST_DIR%" 2>nul
del "%PROJECT_PATH%\*.spec" 2>nul

REM Bouwen met PyInstaller
echo ">>> Bouwen met PyInstaller..."
python -m PyInstaller --onefile --name %APPNAME% "%ENTRY%" >> build.log 2>&1
if errorlevel 1 (
    echo FOUT: PyInstaller build is mislukt.
    exit /b 1
)

REM Aanmaken distributiemap
echo ">>> Aanmaken distributiemap %DIST_DIR%..."
mkdir "%DIST_DIR%"

REM Kopiëren executable
echo ">>> Kopiëren executable..."
if exist "%PROJECT_PATH%\dist\%APPNAME%.exe" (
    copy "%PROJECT_PATH%\dist\%APPNAME%.exe" "%DIST_DIR%\" >> build.log 2>&1
) else (
    echo FOUT: Executable niet gevonden in dist\%APPNAME%.exe
    exit /b 1
)

REM Kopiëren extra folders
echo ">>> Kopiëren extra folders..."
for %%d in (%EXTRA_DIRS%) do (
    if exist "%PROJECT_PATH%\%%d" (
        echo - Kopieer %%d...
        xcopy "%PROJECT_PATH%\%%d" "%DIST_DIR%\%%d" /E /I /Y /Q >> build.log 2>&1
    ) else (
        echo Waarschuwing: folder %%d bestaat niet, overslaan.
    )
)

echo ============================================
echo ">>> Klaar! Alles staat in %DIST_DIR%\"
echo ============================================

REM Toon logbestand
notepad build.log


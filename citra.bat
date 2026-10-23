@echo off
setlocal
title Parallel Vision Workbench - FMIPA UNTAN
cls

echo ========================================================================
echo   Parallel Vision Workbench v2.5
echo   Laboratorium Komputasi Paralel ^& Pemrosesan Citra - FMIPA UNTAN
echo ========================================================================
echo.

:: Pindah ke direktori skrip ini berada (folder UTS)
cd /d "%~dp0"

:: Cek keberadaan virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv tidak ditemukan!
    echo Harap pastikan folder .venv sudah terpasang di folder UTS.
    echo.
    pause
    exit /b 1
)

echo [*] Membuka dashboard di browser: http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"

echo [*] Menjalankan backend server FastAPI (Uvicorn)...
echo [*] Tekan Ctrl+C di jendela ini jika ingin menghentikan server.
echo ========================================================================
echo.

".venv\Scripts\python.exe" web/run_server.py %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [INFO] Server dihentikan.
    pause
)
endlocal

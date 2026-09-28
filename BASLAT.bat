@echo off
chcp 65001 > nul
title @ya_da_psikoloji - İçerik Stüdyosu
cd /d "%~dp0"

echo ========================================================
echo   @ya_da_psikoloji - İÇERİK KEŞFİ VE KAROSEL STÜDYOSU
echo ========================================================
echo.

where py >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python sisteminizde bulunamadi!
    echo Lutfen python.org adresinden Python 3.10+ yukleyin ve "Add to PATH" secenegini isaretleyin.
    echo.
    pause
    exit /b
)

py -3 -c "import sys; assert sys.version_info >= (3, 10)" >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Python 3.10 veya daha yeni bir surum gerekli.
    echo.
    pause
    exit /b
)

if not exist ".venv\Scripts\python.exe" (
    echo [KURULUM] Projeye ozel Python ortami olusturuluyor...
    py -3 -m venv .venv
    if %errorlevel% neq 0 (
        echo [HATA] Python sanal ortami olusturulamadi.
        pause
        exit /b
    )
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env > nul
        echo [.env] Yapilandirma dosyasi hazirlandi.
    )
)

echo [KONTROL] Sistem ve bilesenler kontrol ediliyor...
.venv\Scripts\python.exe -c "import fastapi, uvicorn, google.genai, playwright" >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ========================================================
    echo   GEREKLI KUTUPHANELER KURULUYOR (Ilk Calistirma)
    echo   Bu islem internet hizina gore 1-2 dakika surebilir...
    echo ========================================================
    echo.
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe -m playwright install chromium
    echo.
    echo [BASARILI] Tum kurulumlar tamamlandi!
    echo.
)

.venv\Scripts\python.exe launcher.py
if %errorlevel% neq 0 (
    echo.
    echo [HATA] Uygulama calisirken bir sorun olustu.
    pause
)

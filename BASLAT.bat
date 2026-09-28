@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"

title YAPAY ZEKA ICERIK STUDYOSU
echo ========================================================
echo          YAPAY ZEKA ICERIK STUDYOSU
echo ========================================================
echo.
echo Bu uygulama ilk acilista su islemleri yapar:
echo   1. Projeye ozel Python ortami olusturur.
echo   2. Gerekli kutuphaneleri kurar.
echo   3. Karosel uretimi icin Playwright Chromium'u kurar.
echo.
echo Kurulum tamamlandiktan sonra .env dosyasina Gemini API anahtarinizi ekleyin.
echo Bu pencereyi kapatmayin; kurulum internet hizina gore birkac dakika surebilir.
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo [HATA] Python bulunamadi.
    echo Python 3.10 veya daha yeni bir surumu python.org adresinden kurun.
    echo Kurulumda Python Launcher secenegini etkinlestirin.
    pause
    exit /b 1
)

py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 (
    echo [HATA] Python 3.10 veya daha yeni bir surum gerekli.
    pause
    exit /b 1
)

if not exist "%PYTHON_EXE%" (
    echo [1/4] Projeye ozel Python ortami olusturuluyor...
    py -3 -m venv "%PROJECT_ROOT%.venv"
    if errorlevel 1 (
        echo [HATA] Python sanal ortami olusturulamadi.
        pause
        exit /b 1
    )
)

if not exist ".env" if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo [2/4] .env yapilandirma dosyasi olusturuldu.
)

findstr /c:"AIzaSy...1" ".env" >nul 2>nul
if not errorlevel 1 (
    echo.
    echo [UYARI] Gemini API anahtari henuz ayarlanmamis.
    echo .env dosyasini Not Defteri ile acip GEMINI_API_KEYS alanini doldurun.
    echo Ornek anahtari silip kendi Gemini API anahtarinizi yazin.
    echo Sonra BASLAT.bat dosyasini yeniden calistirin.
    pause
    exit /b 1
)

"%PYTHON_EXE%" -c "import fastapi, uvicorn, google.genai, playwright" >nul 2>nul
if errorlevel 1 (
    echo [3/4] Gerekli Python kutuphaneleri kuruluyor...
    echo Bu adim internet hizina gore birkac dakika surebilir.
    "%PYTHON_EXE%" -m pip install --upgrade pip
    if errorlevel 1 (
        echo [HATA] pip guncellenemedi. Internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
    "%PYTHON_EXE%" -m pip install -r "%PROJECT_ROOT%requirements.txt"
    if errorlevel 1 (
        echo [HATA] Python kutuphaneleri kurulamadi.
        pause
        exit /b 1
    )
) else (
    echo [3/4] Python kutuphaneleri hazir.
)

"%PYTHON_EXE%" -c "from pathlib import Path; from playwright.sync_api import sync_playwright; p=sync_playwright().start(); ready=Path(p.chromium.executable_path).exists(); p.stop(); raise SystemExit(0 if ready else 1)" >nul 2>nul
if errorlevel 1 (
    echo [4/4] Playwright Chromium kuruluyor...
    "%PYTHON_EXE%" -m playwright install chromium
    if errorlevel 1 (
        echo [HATA] Playwright Chromium kurulamadi.
        pause
        exit /b 1
    )
) else (
    echo [4/4] Playwright Chromium hazir.
)

echo.
echo .env dosyanizi kontrol edin ve GEMINI_API_KEYS alanini doldurun.
echo Uygulama baslatiliyor...
echo.
"%PYTHON_EXE%" "%PROJECT_ROOT%launcher.py"
if errorlevel 1 (
    echo.
    echo [HATA] Uygulama calisirken bir sorun olustu.
    pause
    exit /b 1
)

endlocal

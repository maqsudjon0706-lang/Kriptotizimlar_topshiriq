@echo off
chcp 65001 >nul
cls

echo ============================================================
echo MAQSUDJON - Kripto Tizimlar Loyihasi
echo ============================================================
echo.
echo Tanlang:
echo.
echo   1. Sertifikatlarni yaratish
echo   2. HTTP serverni ishga tushirish (test)
echo   3. HTTPS serverni ishga tushirish (administrator talab qilinadi)
echo   4. Serverni to'xtatish
echo   5. Chiqish
echo.
set /p choice="Raqamni kiriting (1-5): "

if "%choice%"=="1" goto certificates
if "%choice%"=="2" goto http_server
if "%choice%"=="3" goto https_server
if "%choice%"=="4" goto stop_server
if "%choice%"=="5" goto end

:certificates
echo.
echo ============================================================
echo Sertifikatlar yaratilmoqda...
echo ============================================================
python setup_certificates.py
pause
goto menu

:http_server
echo.
echo ============================================================
echo HTTP server ishga tushmoqda...
echo Manzil: http://localhost:5000
echo ============================================================
python app.py
pause
goto menu

:https_server
echo.
echo ============================================================
echo HTTPS server ishga tushmoqda...
echo DIQQAT: Administrator huquqlari talab qilinadi!
echo Manzil: https://localhost
echo ============================================================
python app.py --https
pause
goto menu

:stop_server
echo.
taskkill /F /FI "WindowTitle eq python*" 2>nul
echo Server to'xtatildi!
pause
goto menu

:menu
cls
goto start

:end
echo.
echo Rahmat! Xayr!
pause

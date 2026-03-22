@echo off
echo.
echo ========================================
echo    EscrowPay - Frontend Server
echo ========================================
echo.
echo Frontend running at: http://localhost:5500
echo.
echo Open your browser and go to:
echo http://localhost:5500
echo.
echo Press CTRL+C to stop
echo.
py -m http.server 5500
pause

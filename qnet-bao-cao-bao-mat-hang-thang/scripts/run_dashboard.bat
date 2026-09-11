@echo off
title QNet - Báo Cáo An Ninh Bảo Mật Hàng Tháng
cd /d "%~dp0"
echo =========================================================================
echo       KHOI CHAY HE THONG BAO CAO AN TOAN THONG TIN HANG THANG
echo                       QNET SECURITY DASHBOARD
echo =========================================================================
echo.
echo Dang khoi dong Web Dashboard tren Localhost (cong 8501)...
echo.

python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause

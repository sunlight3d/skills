@echo off
chcp 65001 >nul
echo ========================================================
echo   MathPlus Trả Lời Comment Tìm Lớp (Lớp 6 - Lớp 12)
echo ========================================================
py -3.14 "%~dp0scripts\commenter.py" %*

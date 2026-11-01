@echo off
chcp 65001 >nul
echo ========================================================
echo       MathPlus Seeding - Facebook Anonymous Poster
echo ========================================================
py -3.14 "%~dp0scripts\seeder.py" %*

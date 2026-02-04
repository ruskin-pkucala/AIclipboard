@echo off
chcp 65001 > nul
cd /d "%~dp0"
py -3.12 test_ai.py
pause

@echo off
title HumbleLegend API Server
cd /d "C:\Users\Grace Guo\Desktop\New\git\HumbleLegend"
echo ================================================
echo     HumbleLegend AI Agent - API模式
echo ================================================
echo.
echo 正在启动服务器...
echo 地址: http://localhost:8000
echo.
python main.py --mode api --host 0.0.0.0 --port 8000
echo.
echo 服务器已停止
pause
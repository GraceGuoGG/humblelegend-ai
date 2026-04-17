@echo off
cd /d "c:\Users\Grace Guo\Desktop\New\git\HumbleLegend"
echo ==============================================
echo HumbleLegend 服务器启动器
echo ==============================================
echo.
echo 检查并安装依赖...
python -m pip install -r requirements.txt
echo.
python -m pip install fastapi uvicorn
echo.
echo 启动服务器...
python main.py --mode api
echo.
echo 服务器已停止。
pause

@echo off
cd /d "C:\Users\Grace Guo\Desktop\New\git\HumbleLegend"
echo Starting HumbleLegend API server...
echo.
python main.py --mode api --host 0.0.0.0 --port 8000
echo.
echo Server stopped.
pause
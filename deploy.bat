@echo off
echo ================================
echo 部署脚本 - 用于自动化部署准备
echo ================================
echo.

setlocal

set PROJECT_DIR=%~dp0

echo 项目目录: %PROJECT_DIR%
echo.

echo 1. 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python
    exit /b 1
)

python --version
echo.

echo 2. 检查并安装依赖...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pip install -r requirements.txt
    exit /b 1
)

echo 依赖检查完成
echo.

echo 3. 运行项目检查...
python check_deploy.py
if errorlevel 1 (
    echo 错误: 项目检查失败
    exit /b 1
)

echo.
echo 4. 运行服务器测试...
echo 启动服务器...
start "HumbleLegend Server" /B python main.py --mode api --host 127.0.0.1 --port 8080

echo 等待服务器启动...
timeout /t 3 /nobreak >nul

echo 测试服务器...
python -c "
import requests
try:
    response = requests.get('http://127.0.0.1:8080/health')
    print('✅ 健康检查成功:', response.json())
    response = requests.post('http://127.0.0.1:8080/process', 
                           json={'user_id': 'test', 'input': '帮我记录'})
    print('✅ 命令处理成功:', response.json())
    print('✅ 服务器测试完成')
except Exception as e:
    print('❌ 服务器测试失败:', str(e))
    import sys
    sys.exit(1)
"

echo.
echo 5. 查找并停止服务器进程...
for /f "tokens=2" %%i in ('tasklist ^| findstr /r /i "python.*main.py"') do (
    taskkill /PID %%i /F >nul 2>&1
    echo 服务器进程已停止: %%i
)

echo.
echo ================================
echo 部署准备检查完成!
echo ================================
echo.
echo 现在您可以:
echo 1. 确保项目在GitHub上有.gitignore文件
echo 2. 推送到GitHub仓库
echo 3. 配置GitHub Actions自动部署
echo.
echo 部署平台推荐:
echo - Render.com (免费计划，稳定可靠)
echo - Vercel (简单易用)
echo - Railway (功能强大)
echo.
echo 飞书开放平台配置建议:
echo - 回调地址格式: https://{您的域名}/feishu/events
echo - 验证令牌从环境变量读取
echo - 服务器需要可公网访问的HTTPS地址
echo.

endlocal
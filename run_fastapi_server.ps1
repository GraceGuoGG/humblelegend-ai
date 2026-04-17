$ErrorActionPreference = "Stop"

# 设置目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
cd $scriptPath
Write-Host "=== 正在启动HumbleLegend服务器 ===" -ForegroundColor Cyan
Write-Host "当前目录: $($PWD.Path)" -ForegroundColor Gray

try {
    # 检查依赖是否已安装
    Write-Host "检查Python依赖..." -ForegroundColor Cyan
    $requirements = @("fastapi", "uvicorn", "requests", "python-dotenv")
    
    foreach ($pkg in $requirements) {
        $packageInfo = pip list | Select-String -Pattern $pkg
        if (-not $packageInfo) {
            Write-Host "安装缺失的依赖: $pkg" -ForegroundColor Yellow
            pip install $pkg
        } else {
            Write-Host "依赖已安装: $pkg" -ForegroundColor Green
        }
    }
    
    Write-Host "`n所有依赖检查完成" -ForegroundColor Green
    
    # 启动服务器
    Write-Host "`n启动服务器 (FastAPI)..." -ForegroundColor Cyan
    $pythonPath = (Get-Command python).Source
    
    Write-Host "使用Python解释器: $pythonPath" -ForegroundColor Gray
    
    $process = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList "main.py", "--mode", "api" `
        -WorkingDirectory $PWD.Path `
        -NoNewWindow `
        -PassThru
    
    Write-Host "服务器进程已启动，PID: $($process.Id)" -ForegroundColor Green
    
    # 等待服务器启动
    Write-Host "`n等待服务器启动..." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    
    # 测试服务器
    Write-Host "`n测试服务器连接..." -ForegroundColor Cyan
    
    $testUri = "http://localhost:8000/health"
    $healthResponse = Invoke-RestMethod -Uri $testUri -Method Get -TimeoutSec 5
    Write-Host "✅ 健康检查成功: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Green
    
    # 测试飞书配置
    Write-Host "`n测试飞书API配置..." -ForegroundColor Cyan
    $feishuTestUri = "http://localhost:8000/feishu/test"
    $feishuTestResponse = Invoke-RestMethod -Uri $feishuTestUri -Method Get -TimeoutSec 10
    Write-Host "✅ 飞书配置测试成功" -ForegroundColor Green
    Write-Host "配置信息:" -ForegroundColor Gray
    Write-Host "  - App ID: $($feishuTestResponse.config.app_id)"
    Write-Host "  - Token状态: $($feishuTestResponse.status)"
    Write-Host "  - Token: $($feishuTestResponse.token)"
    
    # 模拟飞书Challenge验证
    Write-Host "`n测试飞书Challenge验证..." -ForegroundColor Cyan
    $challengeData = @{
        schema = "2.0"
        header = @{
            event_type = "url_verification"
            token = "test_token"
            ts = [int][double](Get-Date -UFormat %s)
        }
        event = @{
            challenge = "test_challenge_" + (Get-Random -Minimum 10000 -Maximum 99999)
        }
    }
    
    $challengeResponse = Invoke-RestMethod -Uri "http://localhost:8000/feishu/events" -Method Post -ContentType "application/json" -Body ($challengeData | ConvertTo-Json)
    
    Write-Host "✅ Challenge验证成功" -ForegroundColor Green
    if ($challengeResponse.challenge -eq $challengeData.event.challenge) {
        Write-Host "返回的Challenge值正确" -ForegroundColor Green
    } else {
        Write-Host "❌ 返回的Challenge值不正确" -ForegroundColor Red
        Write-Host "期望: $($challengeData.event.challenge)"
        Write-Host "实际: $($challengeResponse.challenge)"
    }
    
    Write-Host "`n=== 服务器启动成功！ ===" -ForegroundColor Green
    Write-Host "服务器已成功运行在 http://localhost:8000"
    Write-Host "现在可以在飞书中测试了"
    Write-Host "`n按 Ctrl+C 停止服务器"
    
    # 保持脚本运行
    while ($true) {
        Start-Sleep -Seconds 5
    }
    
} catch {
    Write-Host "`n❌ 服务器启动失败: $_" -ForegroundColor Red
    
    if (Get-Variable -Name "process" -ErrorAction SilentlyContinue) {
        Write-Host "正在停止服务器进程..." -ForegroundColor Yellow
        $process | Stop-Process -Force -ErrorAction SilentlyContinue
    }
    
    $error[0].Exception | Format-List *
    
    Read-Host "按回车键退出"
}

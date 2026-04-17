$ErrorActionPreference = "Stop"

$pythonPath = (Get-Command python).Source
Write-Host "使用Python解释器: $pythonPath" -ForegroundColor Green

$argsList = @("main.py", "--mode", "api")

try {
    Write-Host "正在启动服务器..." -ForegroundColor Cyan
    $process = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList $argsList `
        -WorkingDirectory $PWD.Path `
        -NoNewWindow `
        -PassThru
    
    Write-Host "服务器进程启动成功，PID: $($process.Id)" -ForegroundColor Green
    
    # 等服务器启动
    Start-Sleep -Seconds 2
    
    # 检查进程是否还在运行
    if (-not (Get-Process -Id $process.Id -ErrorAction SilentlyContinue)) {
        Write-Host "服务器进程已意外终止" -ForegroundColor Red
        throw "服务器无法正常运行"
    }
    
    Write-Host "服务器正在运行" -ForegroundColor Green
    
    # 测试健康检查
    Write-Host "`n测试服务器健康检查..." -ForegroundColor Cyan
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ 健康检查成功: $($healthResponse | ConvertTo-Json -Compress)" -ForegroundColor Green
    
    # 测试飞书配置
    Write-Host "`n测试飞书API配置..." -ForegroundColor Cyan
    $feishuTestResponse = Invoke-RestMethod -Uri "http://localhost:8000/feishu/test" -Method Get -TimeoutSec 10
    Write-Host "✅ 飞书配置测试成功" -ForegroundColor Green
    Write-Host "`n服务器配置信息:" -ForegroundColor Yellow
    Write-Host "  - App ID: $($feishuTestResponse.config.app_id)"
    Write-Host "  - 连接状态: $($feishuTestResponse.status)"
    Write-Host "  - Token信息: $($feishuTestResponse.token)"
    
    Write-Host "`n=== 服务器启动成功！ ===" -ForegroundColor Green
    Write-Host "`n服务器运行在 http://localhost:8000" -ForegroundColor Cyan
    Write-Host "请在浏览器中访问 http://localhost:8000/ 来测试服务器" -ForegroundColor Gray
    
} catch {
    Write-Host "`n❌ 服务器启动失败" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.Exception.InnerException) {
        Write-Host $_.Exception.InnerException.Message -ForegroundColor Red
    }
    
    Write-Host "`n=== 错误详细信息 ===" -ForegroundColor Yellow
    $_.Exception | Format-List *
    
    if (-not (Get-Process -Id $process.Id -ErrorAction SilentlyContinue)) {
        Write-Host "`n❌ 服务器进程已退出" -ForegroundColor Red
    }
}

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

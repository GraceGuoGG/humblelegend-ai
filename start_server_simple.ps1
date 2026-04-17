$ErrorActionPreference = "Stop"

try {
    # 启动服务器
    Write-Host "启动服务器..." -ForegroundColor Green
    
    $pythonPath = (Get-Command python).Source
    $argsList = @("main.py", "--mode", "api")
    
    $process = Start-Process `
        -FilePath $pythonPath `
        -ArgumentList $argsList `
        -WorkingDirectory $PWD.Path `
        -NoNewWindow `
        -PassThru
    
    Write-Host "服务器已启动，PID: $($process.Id)" -ForegroundColor Yellow
    
    Start-Sleep -Seconds 3
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
        Write-Host "服务器响应: $($response.Content)" -ForegroundColor Green
        Write-Host "服务器状态: 正常运行" -ForegroundColor Green
    } catch {
        Write-Host "连接服务器失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    
} catch {
    Write-Host "启动服务器失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

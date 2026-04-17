$response = @'
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.7.4
Date: Wed, 15 Apr 2026 05:22:58 GMT
Content-type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type

{"result": "13:22，已记录：完成了项目报告（工作）"}
'@

Write-Host "=== HumbleLegend 服务器响应 ===`n" -ForegroundColor Green

$statusLine = $response -split "`r?`n" | Select-Object -First 1
Write-Host "响应状态码: $statusLine" -ForegroundColor White

$serverLine = $response -split "`r?`n" | Where-Object {$_ -match "^Server:"} | Select-Object -First 1
Write-Host "服务器: $serverLine" -ForegroundColor White

$dateLine = $response -split "`r?`n" | Where-Object {$_ -match "^Date:"} | Select-Object -First 1
Write-Host "响应日期: $dateLine" -ForegroundColor White

$contentTypeLine = $response -split "`r?`n" | Where-Object {$_ -match "^Content-type:"} | Select-Object -First 1
Write-Host "内容类型: $contentTypeLine" -ForegroundColor White

Write-Host "`n--- 返回数据 ---`n" -ForegroundColor Cyan

try {
    $body = $response -split "`r?`n`r?`n" | Select-Object -Last 1
    $jsonResult = $body | ConvertFrom-Json
    Write-Host $jsonResult.result -ForegroundColor White
} catch {
    Write-Host "无法解析 JSON 响应" -ForegroundColor Yellow
    Write-Host $body -ForegroundColor Gray
}
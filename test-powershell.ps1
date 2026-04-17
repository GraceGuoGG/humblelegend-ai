param(
    [string]$InputText = "帮我记录完成了项目报告"
)

# Use System.Net.WebRequest to send request (more reliable method)
$uri = "http://localhost:8000/process"
$testData = @{
    user_id = "test_user"
    input = $InputText
}

Write-Host "=== HumbleLegend API Test ==="
Write-Host "Input Text: '$InputText'"
Write-Host "Server Address: $uri"
Write-Host "---"

try {
    $request = [System.Net.HttpWebRequest]::Create($uri)
    $request.Method = "POST"
    $request.ContentType = "application/json; charset=utf-8"
    $jsonData = $testData | ConvertTo-Json
    
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($jsonData)
    $request.ContentLength = $bytes.Length
    
    $requestStream = $request.GetRequestStream()
    $requestStream.Write($bytes, 0, $bytes.Length)
    $requestStream.Close()

    $response = $request.GetResponse()
    $reader = New-Object System.IO.StreamReader($response.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $responseText = $reader.ReadToEnd()
    $reader.Close()
    $response.Close()
    
    Write-Host "Success"
    Write-Host "Status Code: $($response.StatusCode)"
    
    try {
        $result = $responseText | ConvertFrom-Json
        Write-Host "Result:"
        $result
    } catch {
        Write-Host "Raw Response: $responseText"
    }
}
catch {
    Write-Host "Error: $($_.Exception.Response.StatusCode)"
    $errorStream = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $errorContent = $errorStream.ReadToEnd()
    $errorStream.Close()
    Write-Host "Error Details: $errorContent"
}
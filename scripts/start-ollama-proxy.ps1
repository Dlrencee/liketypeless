param(
  [string]$ProxyUrl = "http://127.0.0.1:7897",
  [string]$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $OllamaExe)) {
  throw "Ollama executable not found: $OllamaExe"
}

Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force

$env:HTTP_PROXY = $ProxyUrl
$env:HTTPS_PROXY = $ProxyUrl
$env:ALL_PROXY = $ProxyUrl

$stdout = Join-Path (Get-Location) "ollama.proxy.out.log"
$stderr = Join-Path (Get-Location) "ollama.proxy.err.log"

Start-Process -FilePath $OllamaExe `
  -ArgumentList "serve" `
  -WorkingDirectory (Get-Location) `
  -WindowStyle Hidden `
  -RedirectStandardOutput $stdout `
  -RedirectStandardError $stderr

Start-Sleep -Seconds 2

Write-Host "Ollama serve restarted with proxy: $ProxyUrl"
Write-Host "Logs:"
Write-Host "  $stdout"
Write-Host "  $stderr"
Write-Host ""
Write-Host "Now run, for example:"
Write-Host "  ollama pull qwen2.5:1.5b"

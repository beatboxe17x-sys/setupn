# BRAX SUPPORT INSTALLER - IEX Loader
# Usage: irm https://raw.githubusercontent.com/beatboxe17x-sys/setupn/refs/heads/main/brax.ps1 | iex

$ErrorActionPreference = 'Stop'

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║  ERROR: Administrator privileges required!                   ║
║                                                              ║
║  Please right-click PowerShell and select                    ║
║  "Run as Administrator", then run this command again.        ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Red
    return
}

# Create temp directory
$tempDir = Join-Path $env:TEMP "BraxInstaller"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Download the Python script
$pyUrl = "https://raw.githubusercontent.com/beatboxe17x-sys/setupn/refs/heads/main/setup.py"
$pyPath = Join-Path $tempDir "setup.py"

Write-Host "[*] Downloading BRAX SUPPORT INSTALLER..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyPath -UseBasicParsing
    $size = (Get-Item $pyPath).Length
    Write-Host "[+] Downloaded: $size bytes" -ForegroundColor Green
} catch {
    Write-Host "[!] Download failed: $_" -ForegroundColor Red
    return
}

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "[!] Python not found! Installing..." -ForegroundColor Yellow
    
    $pyInstaller = Join-Path $tempDir "python_installer.exe"
    try {
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $pyInstaller -UseBasicParsing
        Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait
        $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
        $python = Get-Command python -ErrorAction SilentlyContinue
    } catch {
        Write-Host "[!] Python install failed. Download from python.org" -ForegroundColor Red
        return
    }
}

# Check tkinter
$tkCheck = & $python.Source -c "import tkinter" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Installing tkinter..." -ForegroundColor Cyan
    & $python.Source -m pip install tk 2>$null
}

# Launch
Write-Host "[*] Launching BRAX SUPPORT INSTALLER GUI..." -ForegroundColor Cyan
Start-Process -FilePath $python.Source -ArgumentList "`"$pyPath`"" -Wait

Write-Host @"
╔══════════════════════════════════════════════════════════════╗
║  [+] BRAX SUPPORT INSTALLER COMPLETE                         ║
╚══════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green
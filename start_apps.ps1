$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$python = Join-Path $root ".venv312\Scripts\python.exe"
$frontendDir = Join-Path $root "frontend"
$backendDir = Join-Path $root "backend"
$nlpDir = Join-Path $root "ml-services\nlp-service"
$visionDir = Join-Path $root "ml-services\vision-service"
$emotionDir = Join-Path $root "ml-services\emotion-service"
$speechDir = Join-Path $root "ml-services\speech-service"

function Stop-ListeningPortProcesses {
    param([int[]]$Ports)

    foreach ($port in $Ports) {
        $connections = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue
        $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($processId in $processIds) {
            if ($processId) {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

function Stop-ProjectProcesses {
    $processes = Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -and (
            $_.CommandLine -like "*$root*" -or
            $_.CommandLine -like "*uvicorn app.main:app*" -or
            $_.CommandLine -like "*uvicorn main:app*" -or
            $_.CommandLine -like "*next\\dist\\bin\\next*"
        )
    }

    foreach ($process in $processes) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Remove-IfExists {
    param([string]$Path)

    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
    }
}

function Start-ServiceProcess {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$LogPrefix
    )

    $stdout = Join-Path $WorkingDirectory "$LogPrefix.log"
    $stderr = Join-Path $WorkingDirectory "$LogPrefix.err.log"

    Remove-Item $stdout, $stderr -Force -ErrorAction SilentlyContinue

    return Start-Process -FilePath $FilePath `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr `
        -PassThru
}

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 3 | Out-Null
            return $true
        } catch {
            Start-Sleep -Milliseconds 500
        }
    }

    return $false
}

Write-Host "Cleaning up stale AI Interview Coach processes..."
Stop-ProjectProcesses
Stop-ListeningPortProcesses -Ports @(3000, 8000, 8101, 8102, 8103, 8104)
Start-Sleep -Seconds 1

Write-Host "Clearing frontend build cache..."
Remove-IfExists (Join-Path $frontendDir ".next")

Write-Host "Starting backend and AI services..."
$backend = Start-ServiceProcess -Name "Backend" -FilePath $python -Arguments @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000") -WorkingDirectory $backendDir -LogPrefix "session-backend"
$nlp = Start-ServiceProcess -Name "NLP" -FilePath $python -Arguments @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8101") -WorkingDirectory $nlpDir -LogPrefix "session-nlp"
$vision = Start-ServiceProcess -Name "Vision" -FilePath $python -Arguments @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8102") -WorkingDirectory $visionDir -LogPrefix "session-vision"
$emotion = Start-ServiceProcess -Name "Emotion" -FilePath $python -Arguments @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8103") -WorkingDirectory $emotionDir -LogPrefix "session-emotion"
$speech = Start-ServiceProcess -Name "Speech" -FilePath $python -Arguments @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8104") -WorkingDirectory $speechDir -LogPrefix "session-speech"

Write-Host "Starting frontend..."
$frontend = Start-ServiceProcess -Name "Frontend" -FilePath "npm.cmd" -Arguments @("run", "dev", "--", "--hostname", "127.0.0.1", "--port", "3000") -WorkingDirectory $frontendDir -LogPrefix "session-frontend"

$backendReady = Wait-ForUrl -Url "http://127.0.0.1:8000/health"
$nlpReady = Wait-ForUrl -Url "http://127.0.0.1:8101/health"
$visionReady = Wait-ForUrl -Url "http://127.0.0.1:8102/health"
$emotionReady = Wait-ForUrl -Url "http://127.0.0.1:8103/health"
$speechReady = Wait-ForUrl -Url "http://127.0.0.1:8104/health"
$frontendReady = Wait-ForUrl -Url "http://127.0.0.1:3000"

Write-Host ""
Write-Host "Backend PID: $($backend.Id)"
Write-Host "NLP PID: $($nlp.Id)"
Write-Host "Vision PID: $($vision.Id)"
Write-Host "Emotion PID: $($emotion.Id)"
Write-Host "Speech PID: $($speech.Id)"
Write-Host "Frontend PID: $($frontend.Id)"
Write-Host ""

if ($backendReady -and $nlpReady -and $visionReady -and $emotionReady -and $speechReady -and $frontendReady) {
    Write-Host "Application is ready."
    Write-Host "Frontend: http://127.0.0.1:3000"
    Write-Host "Backend:  http://127.0.0.1:8000/health"
} else {
    Write-Host "Startup completed with issues. Check session-*.log and session-*.err.log files."
}

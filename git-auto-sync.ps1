$ErrorActionPreference = "Stop"

param(
    [int]$IntervalSeconds = 10,
    [string]$CommitMessagePrefix = "auto-sync"
)

$repoRoot = $PSScriptRoot
Set-Location $repoRoot

$remote = git remote
if (-not $remote) {
    Write-Host "No git remote is configured. Add a remote before using auto-sync."
    exit 1
}

Write-Host "Watching $repoRoot every $IntervalSeconds seconds."
Write-Host "Press Ctrl+C to stop."

while ($true) {
    $status = git status --porcelain

    if ($status) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $commitMessage = "$CommitMessagePrefix $timestamp"

        git add -A

        $postAddStatus = git status --porcelain
        if ($postAddStatus) {
            git commit -m $commitMessage
            git push
            Write-Host "Pushed changes at $timestamp"
        }
    }

    Start-Sleep -Seconds $IntervalSeconds
}

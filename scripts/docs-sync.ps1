$ErrorActionPreference = "Stop"

$RepoDir = $env:DOCS_REPO_DIR ?? "Y:\foconnell\notebook"
$LogFile = $env:DOCS_SYNC_LOG ?? "$HOME\.local\log\docs-sync.log"
$Remote = "origin"
$Branch = "master"

$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Log($msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg" | Add-Content $LogFile
}

Set-Location $RepoDir

# commit any local changes
$status = git status --porcelain
if ($status) {
    git add -A
    git commit -m "sync $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Log "Committed local changes"
}

# pull with auto-merge for daily/weekly
git fetch $Remote 2>$null

$Local = git rev-parse "@"
$RemoteHead = git rev-parse "$Remote/$Branch"

if ($Local -eq $RemoteHead) {
    exit 0
}

$Base = git merge-base "@" "$Remote/$Branch"

if ($Local -eq $Base) {
    git pull --ff-only
    Log "Fast-forward pull"
    exit 0
}

if ($RemoteHead -eq $Base) {
    git push $Remote $Branch
    Log "Pushed"
    exit 0
}

# diverged - try merge
Log "Diverged: merging"
if (git pull --no-edit) {
    git push $Remote $Branch
    Log "Merged and pushed"
} else {
    # auto-resolve daily/weekly conflicts
    $conflicts = git diff --name-only --diff-filter=U
    foreach ($f in $conflicts) {
        if ($f -match "^daily/" -or $f -match "^weekly/") {
            git add $f
        } else {
            Log "MANUAL: $f"
        }
    }

    $remaining = git diff --name-only --diff-filter=U
    if (!$remaining) {
        git commit -m "auto-resolved merge"
        git push $Remote $Branch
        Log "Auto-resolved"
    } else {
        git merge --abort
        Log "NEEDS ATTENTION: $remaining"
        exit 1
    }
}

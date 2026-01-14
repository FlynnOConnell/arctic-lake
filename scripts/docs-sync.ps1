$ErrorActionPreference = "Stop"

$RepoDir = $env:DOCS_REPO_DIR ?? "$HOME\repos\docs"
$SharedDir = $env:DOCS_SHARED_DIR ?? "Y:\foconnell\notes"
$LogFile = $env:DOCS_SYNC_LOG ?? "$HOME\.local\log\docs-sync.log"
$Remote = "origin"
$Branch = "master"

$LogDir = Split-Path $LogFile -Parent
if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Log($msg) {
    "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg" | Add-Content $LogFile
}

if (!(Test-Path $SharedDir)) {
    Log "ERROR: Shared dir not accessible: $SharedDir"
    exit 1
}

Set-Location $RepoDir

# if shared is empty, just populate it from repo
$sharedFiles = Get-ChildItem $SharedDir -Recurse -File
if (!$sharedFiles) {
    Log "Initial sync: populating shared from repo"
    robocopy $RepoDir $SharedDir /MIR /XD .git /NFL /NDL /NJH /NJS /nc /ns /np
    exit 0
}

# pull changes from shared storage into git repo
robocopy $SharedDir $RepoDir /MIR /XD .git /NFL /NDL /NJH /NJS /nc /ns /np

# commit any local changes
$status = git status --porcelain
if ($status) {
    git add -A
    git commit -m "sync $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Log "Committed local changes"
}

git fetch $Remote 2>$null

$Local = git rev-parse "@"
$RemoteHead = git rev-parse "$Remote/$Branch"
$Base = git merge-base "@" "$Remote/$Branch"

function SyncBack {
    robocopy $RepoDir $SharedDir /MIR /XD .git /NFL /NDL /NJH /NJS /nc /ns /np
}

if ($Local -eq $RemoteHead) {
    SyncBack
    exit 0
}

if ($Local -eq $Base) {
    git merge --ff-only "$Remote/$Branch"
    Log "Fast-forward merge"
    SyncBack
    git push $Remote $Branch 2>$null
    exit 0
}

if ($RemoteHead -eq $Base) {
    git push $Remote $Branch
    Log "Pushed local commits"
    SyncBack
    exit 0
}

Log "Diverged: attempting merge"

$mergeResult = git merge "$Remote/$Branch" -m "auto-merge" 2>&1
if ($LASTEXITCODE -eq 0) {
    Log "Merge successful"
    git push $Remote $Branch
    SyncBack
    exit 0
}

$conflicts = git diff --name-only --diff-filter=U
Log "CONFLICTS: $conflicts"

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
    SyncBack
    Log "Auto-resolved and pushed"
} else {
    git merge --abort
    Log "NEEDS ATTENTION: $remaining"
    exit 1
}

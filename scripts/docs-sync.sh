#!/bin/bash
set -euo pipefail

REPO_DIR="${DOCS_REPO_DIR:-$HOME/docs}"
SHARED_DIR="${DOCS_SHARED_DIR:-/mnt/mbospace/foconnell/docs}"
LOG_FILE="${DOCS_SYNC_LOG:-$HOME/.local/log/docs-sync.log}"
REMOTE="origin"
BRANCH="master"

mkdir -p "$(dirname "$LOG_FILE")"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $1" >> "$LOG_FILE"; }

if [ ! -d "$SHARED_DIR" ]; then
    log "ERROR: Shared dir not mounted: $SHARED_DIR"
    exit 1
fi

cd "$REPO_DIR" || { log "ERROR: Cannot cd to $REPO_DIR"; exit 1; }

# pull changes from shared storage into git repo
rsync -a --delete --exclude='.git' "$SHARED_DIR/" "$REPO_DIR/"

# commit any local changes
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "sync $(date '+%Y-%m-%d %H:%M')"
    log "Committed local changes"
fi

git fetch "$REMOTE" 2>/dev/null

LOCAL=$(git rev-parse @)
REMOTE_HEAD=$(git rev-parse "$REMOTE/$BRANCH")
BASE=$(git merge-base @ "$REMOTE/$BRANCH")

if [ "$LOCAL" = "$REMOTE_HEAD" ]; then
    rsync -a --delete --exclude='.git' "$REPO_DIR/" "$SHARED_DIR/"
    exit 0
fi

if [ "$LOCAL" = "$BASE" ]; then
    git merge --ff-only "$REMOTE/$BRANCH" && log "Fast-forward merge"
    rsync -a --delete --exclude='.git' "$REPO_DIR/" "$SHARED_DIR/"
    git push "$REMOTE" "$BRANCH" 2>/dev/null || true
    exit 0
fi

if [ "$REMOTE_HEAD" = "$BASE" ]; then
    git push "$REMOTE" "$BRANCH" && log "Pushed local commits"
    rsync -a --delete --exclude='.git' "$REPO_DIR/" "$SHARED_DIR/"
    exit 0
fi

log "Diverged: attempting merge"

if git merge "$REMOTE/$BRANCH" -m "auto-merge"; then
    log "Merge successful"
    git push "$REMOTE" "$BRANCH"
    rsync -a --delete --exclude='.git' "$REPO_DIR/" "$SHARED_DIR/"
    exit 0
fi

CONFLICTS=$(git diff --name-only --diff-filter=U)
log "CONFLICTS:\n$CONFLICTS"

for f in $CONFLICTS; do
    if [[ "$f" == daily/* ]] || [[ "$f" == weekly/* ]]; then
        git add "$f"
    else
        log "MANUAL: $f"
    fi
done

REMAINING=$(git diff --name-only --diff-filter=U)
if [ -z "$REMAINING" ]; then
    git commit -m "auto-resolved merge"
    git push "$REMOTE" "$BRANCH"
    rsync -a --delete --exclude='.git' "$REPO_DIR/" "$SHARED_DIR/"
    log "Auto-resolved and pushed"
else
    git merge --abort
    log "NEEDS ATTENTION: $REMAINING"
    exit 1
fi

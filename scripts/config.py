"""
Configuration for docs export tools.

Edit PROJECTS to match your storage server structure.
"""

from pathlib import Path

# Storage server project root (Y: drive when mounted)
# Falls back to local ./exports if not available
PROJECT_ROOT = Path("Y:/projects")

# Map frontmatter 'project' values to folder names
# Add new projects here as needed
PROJECTS = {
    "lbm": "lbm",
    "isoview": "isoview",
    "explore": "explore",
    "processing": "processing",  # local docs repo, synced with weekly export
}

# Local docs repo path (for processing notebooks)
DOCS_REPO = Path.home() / "repos" / "docs"

# OneDrive paths for weekly exports
ONEDRIVE_ROOT = Path.home() / "OneDrive" / "MBO_DATA"
WEEKLY_MEETING_DIR = ONEDRIVE_ROOT / "weekly_meeting"

# Fallback when storage server unavailable
LOCAL_EXPORT_DIR = Path.home() / "repos" / "docs" / "exports"


def get_project_path(project_key: str) -> Path | None:
    """
    Get the export path for a project.

    Returns None if project not found in config.
    Falls back to local exports if Y: not mounted.
    """
    if project_key not in PROJECTS:
        return None

    folder = PROJECTS[project_key]

    # processing always goes to local docs repo
    if project_key == "processing":
        local_path = DOCS_REPO / "processing"
        local_path.mkdir(parents=True, exist_ok=True)
        return local_path

    server_path = PROJECT_ROOT / folder

    if server_path.exists():
        return server_path

    # Fallback to local
    local_path = LOCAL_EXPORT_DIR / folder
    local_path.mkdir(parents=True, exist_ok=True)
    return local_path


def list_available_projects() -> list[str]:
    """List all configured project keys."""
    return list(PROJECTS.keys())


def discover_server_projects() -> list[str]:
    """
    Discover project folders on storage server.

    Scans Y:/projects/ for directories (1 level deep).
    """
    if not PROJECT_ROOT.exists():
        return []

    return [
        d.name for d in PROJECT_ROOT.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]

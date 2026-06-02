"""Git-based sync for Data/events.json.

Requires the repo to have a remote configured (e.g. GitHub) and git credentials
available (SSH key or a stored HTTPS token).
"""
import subprocess
import os
from datetime import datetime, timezone

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DATA_FILE = os.path.join("Data", "events.json")


def _run(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command in the repo root and return the result."""
    return subprocess.run(
        args,
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def pull() -> str:
    """Pull the latest events.json from the remote branch via rebase."""
    result = _run(["git", "pull", "--rebase"], check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip() or "Already up to date."


def push() -> str:
    """Stage events.json, commit if changed, and push to the remote."""
    _run(["git", "add", _DATA_FILE])

    status = _run(["git", "status", "--porcelain", _DATA_FILE])
    if not status.stdout.strip():
        return "Nothing new to push — already in sync."

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    _run(["git", "commit", "-m", f"Sync events: {timestamp}"])

    result = _run(["git", "push"], check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip() or "Pushed successfully."

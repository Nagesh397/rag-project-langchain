import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from mcp.server import MCPServer

load_dotenv(Path(__file__).with_name(".env"))

mcp = MCPServer("ai-git-assistant")


def _repository() -> Path:
    configured_path = os.getenv("GIT_REPOSITORY_PATH")
    if not configured_path:
        raise ValueError("GIT_REPOSITORY_PATH is missing.")

    repository = Path(configured_path).expanduser().resolve()
    if not (repository / ".git").exists():
        raise ValueError(f"Not a Git repository: {repository}")
    return repository


def _run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=_repository(),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    output = result.stdout.strip()
    if result.returncode:
        error = result.stderr.strip() or output or "Git command failed."
        raise RuntimeError(error)
    return output


def _has_staged_changes() -> bool:
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=_repository(),
        timeout=30,
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError("Could not inspect staged changes.")
    return result.returncode == 1


def _safe_paths(paths: list[str]) -> list[str]:
    repository = _repository()
    safe_paths = []
    for value in paths:
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"Path must stay inside the repository: {value}")
        resolved = (repository / path).resolve()
        if resolved != repository and repository not in resolved.parents:
            raise ValueError(f"Path must stay inside the repository: {value}")
        safe_paths.append(path.as_posix())
    if not safe_paths:
        raise ValueError("Provide at least one path.")
    return safe_paths


@mcp.tool()
def git_status() -> str:
    """Return the current branch and working-tree changes."""
    branch = _run_git("branch", "--show-current") or "(detached HEAD)"
    changes = _run_git("status", "--short") or "clean"
    return f"Branch: {branch}\n{changes}"


@mcp.tool()
def git_diff(staged: bool = False) -> str:
    """Return unstaged changes, or staged changes when staged is true."""
    arguments = ["diff"]
    if staged:
        arguments.append("--cached")
    return _run_git(*arguments) or "No changes."


@mcp.tool()
def git_stage(paths: list[str]) -> str:
    """Stage only the explicitly provided repository-relative paths."""
    safe_paths = _safe_paths(paths)
    return _run_git("add", "--", *safe_paths) or f"Staged: {', '.join(safe_paths)}"


@mcp.tool()
def git_unstage(paths: list[str]) -> str:
    """Remove only the explicitly provided paths from the staging area."""
    safe_paths = _safe_paths(paths)
    return _run_git("restore", "--staged", "--", *safe_paths) or f"Unstaged: {', '.join(safe_paths)}"


@mcp.tool()
def git_commit(message: str) -> str:
    """Commit already-staged changes with a non-empty message."""
    if not message.strip():
        raise ValueError("Commit message cannot be empty.")
    if not _has_staged_changes():
        raise ValueError("No staged changes to commit.")
    return _run_git("commit", "-m", message)


@mcp.tool()
def git_push() -> str:
    """Push the current branch to its configured upstream remote."""
    return _run_git("push")


@mcp.tool()
def git_log(limit: int = 10) -> str:
    """Return recent commits, limited to a reasonable range."""
    if limit < 1 or limit > 50:
        raise ValueError("limit must be between 1 and 50.")
    return _run_git("log", f"-{limit}", "--oneline", "--decorate") or "No commits."


if __name__ == "__main__":
    mcp.run()
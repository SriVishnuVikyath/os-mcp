"""
OS-MCP — A Model Context Protocol server for laptop filesystem interaction.
Provides tools for an AI agent to:
  • create_directory   – create one or more nested directories
  • path_exists        – check whether a file or directory exists
  • copy_file          – copy a single file to a destination
  • copy_directory     – recursively copy an entire directory
"""

import os
import shutil
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# ── Server bootstrap ──────────────────────────────────────────────────────────
mcp = FastMCP(
    name="os-mcp",
    instructions=(
        "You are connected to the OS-MCP filesystem server. "
        "Use the available tools to manage directories and files on this machine. "
        "Always use absolute paths for reliability."
    ),
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _abs(p: str) -> Path:
    """Resolve a path to its absolute form."""
    return Path(p).expanduser().resolve()


# ── Tool 1 : create_directory ─────────────────────────────────────────────────

@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a directory (and any missing parent directories) at the given path.

    Args:
        path: Absolute or relative path of the directory to create.

    Returns:
        A success message with the resolved path, or an error description.
    """
    try:
        target = _abs(path)
        target.mkdir(parents=True, exist_ok=True)
        return f"✅ Directory created (or already exists): {target}"
    except PermissionError:
        return f"❌ Permission denied: cannot create '{path}'."
    except Exception as exc:
        return f"❌ Failed to create directory '{path}': {exc}"


# ── Tool 2 : path_exists ──────────────────────────────────────────────────────

@mcp.tool()
def path_exists(path: str) -> str:
    """
    Check whether a file or directory exists at the given path.

    Args:
        path: Absolute or relative path to inspect.

    Returns:
        A message indicating existence and type (file / directory / nothing).
    """
    target = _abs(path)
    if not target.exists():
        return f"❌ Nothing found at: {target}"
    kind = "directory" if target.is_dir() else "file"
    size_info = ""
    if target.is_file():
        size_bytes = target.stat().st_size
        size_info = f" ({_human_size(size_bytes)})"
    return f"✅ Found a {kind}{size_info} at: {target}"


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


# ── Tool 3 : copy_file ────────────────────────────────────────────────────────

@mcp.tool()
def copy_file(source: str, destination: str) -> str:
    """
    Copy a single file from *source* to *destination*.

    • If *destination* is an existing directory the file will be placed inside it.
    • Non-existent parent directories in *destination* are created automatically.
    • File metadata (timestamps, permissions) is preserved.

    Args:
        source:      Path of the file to copy.
        destination: Path of the copy target (file path or destination directory).

    Returns:
        A success message showing where the file was copied, or an error description.
    """
    try:
        src = _abs(source)
        dst = _abs(destination)

        if not src.exists():
            return f"❌ Source does not exist: {src}"
        if not src.is_file():
            return f"❌ Source is not a file: {src}. Use copy_directory for folders."

        # If destination is (or will be) a directory, put the file inside it
        if dst.is_dir():
            dst = dst / src.name

        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return f"✅ Copied file:\n   From : {src}\n   To   : {dst}"
    except PermissionError:
        return f"❌ Permission denied while copying '{source}'."
    except Exception as exc:
        return f"❌ Failed to copy file '{source}' → '{destination}': {exc}"


# ── Tool 4 : copy_directory ───────────────────────────────────────────────────

@mcp.tool()
def copy_directory(source: str, destination: str, overwrite: bool = False) -> str:
    """
    Recursively copy an entire directory from *source* to *destination*.

    Args:
        source:      Path of the directory to copy.
        destination: Target path for the copied directory.
        overwrite:   If True and *destination* already exists, it will be
                     removed before copying. Defaults to False.

    Returns:
        A success message with counts of copied items, or an error description.
    """
    try:
        src = _abs(source)
        dst = _abs(destination)

        if not src.exists():
            return f"❌ Source does not exist: {src}"
        if not src.is_dir():
            return f"❌ Source is not a directory: {src}. Use copy_file for files."

        if dst.exists():
            if overwrite:
                shutil.rmtree(dst)
            else:
                return (
                    f"❌ Destination already exists: {dst}. "
                    f"Pass overwrite=True to replace it."
                )

        shutil.copytree(src, dst)

        # Count copied items for a helpful summary
        files = sum(1 for _ in dst.rglob("*") if _.is_file())
        dirs  = sum(1 for _ in dst.rglob("*") if _.is_dir())
        return (
            f"✅ Copied directory:\n"
            f"   From  : {src}\n"
            f"   To    : {dst}\n"
            f"   Items : {files} file(s) across {dirs} sub-folder(s)"
        )
    except PermissionError:
        return f"❌ Permission denied while copying directory '{source}'."
    except Exception as exc:
        return f"❌ Failed to copy directory '{source}' → '{destination}': {exc}"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")

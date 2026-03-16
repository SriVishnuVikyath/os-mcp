"""
Standalone smoke-test for the OS-MCP server tools.

Imports and calls each tool function directly (no MCP transport needed).
All operations happen inside a throwaway temp directory.

Run with:
    .\\venv\\Scripts\\python.exe test_server.py
"""

import sys
import tempfile
import os
from pathlib import Path

# Make sure we can import from the project root
sys.path.insert(0, str(Path(__file__).parent))

from server import create_directory, path_exists, copy_file, copy_directory

PASS = "\033[92m✔\033[0m"
FAIL = "\033[91m✘\033[0m"
results: list[tuple[str, bool]] = []


def check(label: str, result: str, expect_ok: bool = True):
    ok = result.startswith("✅") if expect_ok else result.startswith("❌")
    status = PASS if ok else FAIL
    print(f"  {status}  {label}")
    print(f"     {result}")
    results.append((label, ok))


# ── Run all tests inside a temp directory ─────────────────────────────────────
with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp)
    print(f"\n🧪  Testing OS-MCP tools — temp dir: {base}\n")

    # --- create_directory ---
    print("── create_directory ─────────────────────────────────────────")
    new_dir = str(base / "projects" / "my_app" / "logs")
    check("Create nested directory", create_directory(new_dir))
    check("Create same dir twice (idempotent)", create_directory(new_dir))

    # --- path_exists ---
    print("\n── path_exists ──────────────────────────────────────────────")
    check("Existing directory is found", path_exists(new_dir))
    check("Non-existent path returns ❌", path_exists(str(base / "ghost")), expect_ok=False)

    # Create a test file
    test_file = base / "hello.txt"
    test_file.write_text("Hello, MCP world!")
    check("Existing file is found", path_exists(str(test_file)))

    # --- copy_file ---
    print("\n── copy_file ────────────────────────────────────────────────")
    dst_file = str(base / "copy_of_hello.txt")
    check("Copy file to new path", copy_file(str(test_file), dst_file))
    check("Copy file into a directory", copy_file(str(test_file), str(base / "projects")))
    check("Copy non-existent file returns ❌",
          copy_file(str(base / "ghost.txt"), dst_file), expect_ok=False)
    check("Copy a directory as file returns ❌",
          copy_file(str(base / "projects"), dst_file), expect_ok=False)

    # --- copy_directory ---
    print("\n── copy_directory ───────────────────────────────────────────")
    src_dir  = str(base / "projects")
    dst_dir  = str(base / "projects_backup")
    dst_dir2 = str(base / "projects_backup2")

    check("Copy directory", copy_directory(src_dir, dst_dir))
    check("Copy dir again without overwrite returns ❌",
          copy_directory(src_dir, dst_dir), expect_ok=False)
    check("Copy dir with overwrite=True", copy_directory(src_dir, dst_dir2, overwrite=False))
    # overwrite the first backup
    check("Overwrite existing destination", copy_directory(src_dir, dst_dir, overwrite=True))
    check("Copy non-existent directory returns ❌",
          copy_directory(str(base / "nope"), dst_dir, overwrite=True), expect_ok=False)

# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(1 for _, ok in results if ok)
total  = len(results)
color  = "\033[92m" if passed == total else "\033[91m"
reset  = "\033[0m"
print(f"\n{color}{'─'*50}")
print(f"  Results: {passed}/{total} tests passed")
print(f"{'─'*50}{reset}\n")
sys.exit(0 if passed == total else 1)

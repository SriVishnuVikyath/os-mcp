# OS-MCP — Laptop Filesystem MCP Server

An **MCP (Model Context Protocol)** server that gives any compatible AI agent the ability to interact with your laptop's filesystem safely and predictably.

---

## What it Does

| Tool | What the AI can do |
|---|---|
| `create_directory` | Create a folder (and any parent folders) anywhere on your system |
| `path_exists` | Check whether a file **or** directory exists at a given path |
| `copy_file` | Copy a single file from one location to another |
| `copy_directory` | Recursively copy an entire folder tree |

---

## Project Structure

```
os-mcp/
├── server.py          ← MCP server (all tools live here)
├── pyproject.toml     ← Package metadata
├── test_server.py     ← Quick sanity-check script
├── venv/              ← Python virtual environment
└── README.md          ← This file
```

---

## Quick Start

### 1 — Activate the virtual environment

```powershell
# from the os-mcp folder
.\venv\Scripts\Activate.ps1
```

### 2 — Run the server manually (stdio mode)

```powershell
python server.py
```

The server speaks the MCP stdio protocol—it waits for JSON-RPC messages from the host and replies on stdout. You won't see a prompt; that's normal.

### 3 — Wire it up to Claude Desktop (or any MCP host)

Add the following block to your Claude Desktop config file
(`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "os-mcp": {
      "command": "C:\\Users\\Samruddhi\\Documents\\CODING_AND_PROJECTS\\os-mcp\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\Samruddhi\\Documents\\CODING_AND_PROJECTS\\os-mcp\\server.py"
      ]
    }
  }
}
```

Restart Claude Desktop and the four tools will be available immediately.

---

## Tool Reference

### `create_directory`

```
create_directory(path: str) -> str
```

Creates the directory at `path` plus any missing parent directories (`mkdir -p` style).

**Example prompt:** *"Create the folder C:\Projects\MyApp\logs"*

---

### `path_exists`

```
path_exists(path: str) -> str
```

Returns whether a file or directory exists, along with its type and (for files) its size.

**Example prompt:** *"Does C:\Users\Samruddhi\Downloads\report.pdf exist?"*

---

### `copy_file`

```
copy_file(source: str, destination: str) -> str
```

Copies a single file. If `destination` is a directory, the file is placed inside it with its original name. Parent directories are created automatically. File metadata (timestamps, permissions) is preserved.

**Example prompt:** *"Copy C:\notes.txt to C:\Backup\notes.txt"*

---

### `copy_directory`

```
copy_directory(source: str, destination: str, overwrite: bool = False) -> str
```

Recursively copies an entire directory tree. Pass `overwrite=True` to replace an existing destination.

**Example prompt:** *"Copy my C:\Projects\OldApp folder to C:\Archive\OldApp"*

---

## Running the Test Suite

```powershell
.\venv\Scripts\python.exe test_server.py
```

All tests operate inside a throwaway temp directory and clean up after themselves.

# Development Scripts

This directory contains utility scripts for development and maintenance tasks.

## Files

### add_commands_quick.py
Script to quickly add AI custom commands to an existing `.tnp` project file.

**Usage:**
```bash
python scripts/add_commands_quick.py [path_to_project.tnp]
```

If no path is provided, it will use a default project path.

**What it does:**
- Opens an existing .tnp project file (which is a ZIP archive)
- Extracts the manifest.json
- Adds default AI commands from `managers/ai/default_commands.py`
- Creates a backup before modifying
- Recreates the .tnp file with the updated manifest

### add_commands_to_project.py
Similar to `add_commands_quick.py`, provides functionality to add AI commands to projects.

### replacements.txt
Contains regex patterns for sanitizing sensitive data (e.g., API keys) from logs or output.

Format:
```
regex:sk-[A-Za-z0-9_\-]{30,}==>REDACTED
```

## Notes

- These scripts are not part of the main application codebase
- They are ignored by git (see `.gitignore`)
- Each developer may have their own versions of these utilities
- These are meant for local development and testing only

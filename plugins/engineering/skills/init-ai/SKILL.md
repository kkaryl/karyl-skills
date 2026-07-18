---
name: init-ai
description: Initialize repository AI instructions and keep AGENTS.md and CLAUDE.md synchronized with a relative symlink. Use when setting up a repository for Codex and Claude, when either instruction file is missing, or when asked to run /init and share one instruction file between both agents.
---

# Initialize AI Instructions

Work in the repository root unless the user names another directory. Preserve existing instructions and use relative symlinks so the repository remains portable.

## Inspect the paths

Inspect both `AGENTS.md` and `CLAUDE.md` with checks that distinguish regular files, valid symlinks, broken symlinks, and absent paths. Do not treat a broken symlink as absent.

## Initialize or link

Apply the first matching case:

1. If neither path exists, invoke the host agent's `/init` command in the repository root. Do not pass `/init` to the shell. Reinspect both paths after initialization, then continue with the matching case below. If the host cannot invoke slash commands programmatically, tell the user to enter `/init`, stop without creating a substitute instruction file, and resume this workflow afterward.
2. If exactly one path is a regular file, create the missing path as a relative symlink to it:
   - `AGENTS.md` exists: run `ln -s AGENTS.md CLAUDE.md`.
   - `CLAUDE.md` exists: run `ln -s CLAUDE.md AGENTS.md`.
3. If both paths already resolve to the same file, make no change.
4. If both paths exist independently, compare their contents. Make no change when they differ; report the conflict and ask which file should be canonical. When they are identical, ask before replacing either file with a symlink.
5. If either path is a broken symlink, symlink cycle, directory, or other unexpected file type, make no change and report the exact condition.

## Verify

After any change:

- Confirm both names exist and resolve successfully.
- Confirm edits through either name reach the same underlying file.
- Report which file is canonical and the relative target returned by `readlink`.

Never overwrite, remove, or rename an existing instruction file without explicit user approval.

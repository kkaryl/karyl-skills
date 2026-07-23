#!/usr/bin/env python3
"""Create a dual-compatible skills marketplace and protected local worktree."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


PUBLIC_BRANCH = "master"
LOCAL_BRANCH = "local-skills"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ScaffoldError(RuntimeError):
    """A safe, user-actionable scaffold failure."""


def run(
    args: list[str],
    *,
    cwd: Path,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise ScaffoldError(f"Command failed: {' '.join(args)}\n{detail}")
    return result


def normalize_repository_name(raw_name: str) -> tuple[str, str]:
    normalized = re.sub(r"[^a-z0-9]+", "-", raw_name.strip().lower()).strip("-")
    normalized = re.sub(r"-{2,}", "-", normalized)
    if not normalized:
        raise ScaffoldError("Repository name must contain letters or digits.")
    repository_name = normalized if normalized.endswith("-skills") else f"{normalized}-skills"
    stem = repository_name.removesuffix("-skills")
    if not stem or NAME_RE.fullmatch(repository_name) is None:
        raise ScaffoldError("Repository name must normalize to lower-case kebab-case.")
    plugin_names = (f"{stem}-engineering", f"{stem}-productivity")
    if any(len(name) > 64 for name in plugin_names):
        raise ScaffoldError("Repository stem is too long; generated plugin names must be at most 64 characters.")
    return repository_name, stem


def git_config(key: str, cwd: Path) -> str | None:
    result = run(["git", "config", "--get", key], cwd=cwd, check=False)
    value = result.stdout.strip()
    return value or None


def write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, indent=2))


def codex_manifest(plugin_name: str, collection: str, author_name: str) -> dict[str, Any]:
    title = collection.title()
    if collection == "engineering":
        short_description = "Skills for building and maintaining software."
        long_description = (
            "A collection of engineering skills for designing, implementing, testing, "
            "debugging, and reviewing software."
        )
    else:
        short_description = "Skills for planning, focus, and communication."
        long_description = (
            "A collection of productivity skills for planning work, organizing information, "
            "communicating clearly, and staying focused."
        )
    return {
        "name": plugin_name,
        "version": "0.1.0",
        "description": f"Skills for {collection} work.",
        "author": {"name": author_name},
        "skills": "./skills/",
        "interface": {
            "displayName": title,
            "shortDescription": short_description,
            "longDescription": long_description,
            "developerName": author_name,
            "category": title,
            "capabilities": [],
            "defaultPrompt": f"Help me choose a {collection} skill for this task.",
        },
    }


def claude_manifest(plugin_name: str, collection: str, author_name: str) -> dict[str, Any]:
    return {
        "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
        "name": plugin_name,
        "displayName": collection.title(),
        "version": "0.1.0",
        "description": f"Skills for {collection} work.",
        "author": {"name": author_name},
    }


def codex_marketplace(repository_name: str, stem: str) -> dict[str, Any]:
    plugins = []
    for collection in ("engineering", "productivity"):
        plugins.append(
            {
                "name": f"{stem}-{collection}",
                "source": {"source": "local", "path": f"./plugins/{collection}"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": collection,
            }
        )
    return {
        "name": repository_name,
        "interface": {"displayName": repository_name.replace("-", " ")},
        "plugins": plugins,
    }


def claude_marketplace(
    repository_name: str,
    stem: str,
    author_name: str,
) -> dict[str, Any]:
    plugins = []
    for collection in ("engineering", "productivity"):
        plugins.append(
            {
                "name": f"{stem}-{collection}",
                "source": f"./plugins/{collection}",
                "description": f"Skills for {collection} work.",
                "category": collection,
            }
        )
    return {
        "$schema": "https://json.schemastore.org/claude-code-marketplace.schema.json",
        "name": repository_name,
        "description": f"{author_name}'s engineering and productivity skills.",
        "owner": {"name": author_name},
        "plugins": plugins,
    }


def agents_md(repository_name: str, stem: str) -> str:
    return f"""# Repository guidance

## Purpose

This repository contains the `{repository_name}` marketplace with two independently installable
plugins: `{stem}-engineering` and `{stem}-productivity`. Keep public authored skills on
`{PUBLIC_BRANCH}` and local-only skills on `{LOCAL_BRANCH}`.

## Choose the collection

- Put architecture, coding, testing, debugging, code review, infrastructure, and delivery skills
  in `plugins/engineering/skills/`.
- Put planning, research, writing, communication, organization, and focus skills in
  `plugins/productivity/skills/`.
- Classify a cross-cutting skill by its primary trigger. Do not duplicate it.

## Skill conventions

- Store each skill at `plugins/<collection>/skills/<skill-name>/SKILL.md`.
- Use matching lower-case kebab-case folder and frontmatter names.
- Keep skills valid for both Claude and Codex. Put product-specific metadata in the product's
  companion metadata files without forking the shared `SKILL.md`.
- Keep supporting scripts, references, and assets inside the skill folder.
- Validate each changed skill before finishing.

## Plugin conventions

- Preserve both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` in each plugin.
- Preserve both marketplace catalogs at `.agents/plugins/marketplace.json` and
  `.claude-plugin/marketplace.json`.
- Keep engineering before productivity in both catalogs.
- Keep marketplace sources mapped to `./plugins/engineering` and `./plugins/productivity`.

## Branch boundary

- Commit authored and publishable skills only on `{PUBLIC_BRANCH}`.
- Use the sibling worktree on `{LOCAL_BRANCH}` for local-only skills.
- Add `Local-Skill: true` to every local-only commit.
- Rebase a clean `{LOCAL_BRANCH}` onto local `{PUBLIC_BRANCH}` to receive public changes.
- Never push `{LOCAL_BRANCH}`, bypass the pre-push guard, or hide local skills with `.gitignore`.

## Verification

Before finishing a change:

1. Validate each changed skill.
2. Validate each affected Codex plugin.
3. Run `claude plugin validate .` when Claude Code is available.
4. Parse both marketplace files as JSON and confirm every local source path exists.
"""


def readme(repository_name: str, stem: str) -> str:
    return f"""# {repository_name.replace("-", " ")}

A Claude and Codex skills marketplace with separate engineering and productivity plugins.

## Layout

```text
.
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
└── plugins/
    ├── engineering/
    │   ├── .claude-plugin/plugin.json
    │   ├── .codex-plugin/plugin.json
    │   └── skills/
    └── productivity/
        ├── .claude-plugin/plugin.json
        ├── .codex-plugin/plugin.json
        └── skills/
```

## Branches and worktrees

- `{PUBLIC_BRANCH}` is the publishable branch for authored skills.
- `{LOCAL_BRANCH}` is checked out in the sibling `{repository_name}-local` worktree.
- Local-only commits carry a `Local-Skill: true` trailer and are blocked from pushes by a
  repository-local pre-push hook.

Rebase the clean local worktree after public changes:

```bash
git -C ../{repository_name}-local rebase {PUBLIC_BRANCH}
```

## Install with Codex

```bash
codex plugin marketplace add "$PWD"
codex plugin add {stem}-engineering@{repository_name}
codex plugin add {stem}-productivity@{repository_name}
```

## Install with Claude Code

Add this directory or its published GitHub repository as a marketplace, then install:

```text
/plugin marketplace add .
/plugin install {stem}-engineering@{repository_name}
/plugin install {stem}-productivity@{repository_name}
```
"""


def gitignore() -> str:
    return """# macOS
.DS_Store

# Editors and IDEs
.idea/
.vscode/
*.swp
*.swo
*~

# Local environment and secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.venv/
venv/

# JavaScript
node_modules/

# Build, coverage, and temporary output
build/
dist/
coverage/
.coverage
*.log
*.tmp

# Local agent state and generated caches
.codex/
.agents/.cache/
.claude/settings.local.json
plugins/**/.cache/
"""


def create_files(root: Path, repository_name: str, stem: str, author_name: str) -> None:
    write_text(root / "README.md", readme(repository_name, stem))
    write_text(root / "AGENTS.md", agents_md(repository_name, stem))
    write_text(root / ".gitignore", gitignore())
    (root / "CLAUDE.md").symlink_to("AGENTS.md")

    write_json(
        root / ".agents" / "plugins" / "marketplace.json",
        codex_marketplace(repository_name, stem),
    )
    write_json(
        root / ".claude-plugin" / "marketplace.json",
        claude_marketplace(repository_name, stem, author_name),
    )

    for collection in ("engineering", "productivity"):
        plugin_name = f"{stem}-{collection}"
        plugin_root = root / "plugins" / collection
        write_json(
            plugin_root / ".codex-plugin" / "plugin.json",
            codex_manifest(plugin_name, collection, author_name),
        )
        write_json(
            plugin_root / ".claude-plugin" / "plugin.json",
            claude_manifest(plugin_name, collection, author_name),
        )
        skills_root = plugin_root / "skills"
        skills_root.mkdir(parents=True, exist_ok=True)
        write_text(skills_root / ".gitkeep", "")


def install_push_guard(root: Path) -> Path:
    source = Path(__file__).with_name("pre-push-local-skills")
    if not source.is_file():
        raise ScaffoldError(f"Bundled pre-push guard is missing: {source}")
    git_dir_result = run(["git", "rev-parse", "--git-dir"], cwd=root)
    git_dir = Path(git_dir_result.stdout.strip())
    if not git_dir.is_absolute():
        git_dir = (root / git_dir).resolve()
    hook = git_dir / "hooks" / "pre-push"
    if hook.exists() or hook.is_symlink():
        raise ScaffoldError(f"Refusing to overwrite existing pre-push hook: {hook}")
    hook.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, hook)
    hook.chmod(hook.stat().st_mode | 0o111)
    return hook


def verify_scaffold(root: Path, worktree: Path) -> None:
    for relative in (
        ".agents/plugins/marketplace.json",
        ".claude-plugin/marketplace.json",
        "plugins/engineering/.codex-plugin/plugin.json",
        "plugins/engineering/.claude-plugin/plugin.json",
        "plugins/productivity/.codex-plugin/plugin.json",
        "plugins/productivity/.claude-plugin/plugin.json",
    ):
        path = root / relative
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ScaffoldError(f"Generated JSON is invalid: {path}") from error
        if not isinstance(payload, dict):
            raise ScaffoldError(f"Generated JSON must contain an object: {path}")

    if not (root / "CLAUDE.md").is_symlink() or os.readlink(root / "CLAUDE.md") != "AGENTS.md":
        raise ScaffoldError("CLAUDE.md is not the expected relative symlink to AGENTS.md.")
    if run(["git", "status", "--porcelain"], cwd=root).stdout.strip():
        raise ScaffoldError("The public worktree is unexpectedly dirty.")
    if run(["git", "branch", "--show-current"], cwd=root).stdout.strip() != PUBLIC_BRANCH:
        raise ScaffoldError(f"The public worktree is not on {PUBLIC_BRANCH}.")
    if run(["git", "status", "--porcelain"], cwd=worktree).stdout.strip():
        raise ScaffoldError("The local worktree is unexpectedly dirty.")
    if run(["git", "branch", "--show-current"], cwd=worktree).stdout.strip() != LOCAL_BRANCH:
        raise ScaffoldError(f"The local worktree is not on {LOCAL_BRANCH}.")


def paths_overlap(first: Path, second: Path) -> bool:
    try:
        first.relative_to(second)
        return True
    except ValueError:
        pass
    try:
        second.relative_to(first)
        return True
    except ValueError:
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Repository stem or name, such as acme or acme-skills")
    parser.add_argument("--parent", default=".", help="Parent directory for the public repository")
    parser.add_argument("--worktree-path", help="Custom path for the local-only worktree")
    parser.add_argument("--author-name", help="Display name for marketplace and plugin metadata")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if shutil.which("git") is None:
        raise ScaffoldError("Git is required but was not found on PATH.")

    repository_name, stem = normalize_repository_name(args.name)
    parent = Path(args.parent).expanduser().resolve()
    if not parent.is_dir():
        raise ScaffoldError(f"Parent directory does not exist: {parent}")
    root = parent / repository_name
    worktree = (
        Path(args.worktree_path).expanduser().resolve()
        if args.worktree_path
        else root.with_name(f"{repository_name}-local")
    )
    if paths_overlap(root, worktree):
        raise ScaffoldError("The public repository and local worktree paths must not overlap.")
    for destination in (root, worktree):
        if destination.exists() or destination.is_symlink():
            raise ScaffoldError(f"Refusing to overwrite existing destination: {destination}")
        if not destination.parent.is_dir():
            raise ScaffoldError(f"Destination parent does not exist: {destination.parent}")

    author_name = args.author_name or git_config("user.name", parent) or "Local developer"
    root_created = False
    try:
        root.mkdir()
        root_created = True
        create_files(root, repository_name, stem, author_name)
        run(["git", "init", "--initial-branch", PUBLIC_BRANCH], cwd=root)
        identity = run(["git", "var", "GIT_AUTHOR_IDENT"], cwd=root, check=False)
        if identity.returncode:
            raise ScaffoldError(
                "Git author identity is not configured. Set user.name and user.email, then retry."
            )
        hook = install_push_guard(root)
        run(["git", "add", "--all"], cwd=root)
        run(["git", "commit", "-m", f"chore: scaffold {repository_name} marketplace"], cwd=root)
        run(["git", "branch", LOCAL_BRANCH, PUBLIC_BRANCH], cwd=root)
        run(["git", "worktree", "add", str(worktree), LOCAL_BRANCH], cwd=root)
        verify_scaffold(root, worktree)
    except Exception:
        if worktree.exists() and not worktree.is_symlink():
            shutil.rmtree(worktree)
        if root_created and root.exists() and not root.is_symlink():
            shutil.rmtree(root)
        raise

    print(f"Created public repository: {root}")
    print(f"Created local-only worktree: {worktree}")
    print(f"Public branch: {PUBLIC_BRANCH}")
    print(f"Local-only branch: {LOCAL_BRANCH}")
    print(f"Installed pre-push guard: {hook}")


if __name__ == "__main__":
    try:
        main()
    except ScaffoldError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

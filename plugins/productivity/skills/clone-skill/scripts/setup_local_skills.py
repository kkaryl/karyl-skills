#!/usr/bin/env python3
"""Create the protected local-skills branch and sibling worktree."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


class SetupError(RuntimeError):
    """A safe, user-actionable setup failure."""


def run(args: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git(root: Path, *args: str) -> str:
    return run(["git", *args], cwd=root).stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--marketplace-root", default=".", help="Path to the main worktree")
    parser.add_argument("--worktree-path", help="Local worktree path; defaults to a sibling <marketplace>-local")
    return parser.parse_args()


def install_push_guard(root: Path) -> Path:
    common_dir = Path(git(root, "rev-parse", "--git-common-dir"))
    if not common_dir.is_absolute():
        common_dir = (root / common_dir).resolve()
    hooks_dir = common_dir / "hooks"
    hook = hooks_dir / "pre-push"
    if hook.exists() or hook.is_symlink():
        raise SetupError(f"Refusing to overwrite existing pre-push hook: {hook}")
    bundled_hook = Path(__file__).with_name("pre-push-local-skills")
    hooks_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bundled_hook, hook)
    hook.chmod(hook.stat().st_mode | 0o111)
    return hook


def main() -> None:
    args = parse_args()
    root = Path(args.marketplace_root).expanduser().resolve()
    try:
        top_level = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        raise SetupError(f"Not a Git worktree: {root}") from error
    if top_level != root:
        raise SetupError(f"Marketplace root must be the Git worktree root: {top_level}")
    if git(root, "branch", "--show-current") != "main":
        raise SetupError("Run setup from the main branch.")
    if git(root, "status", "--porcelain"):
        raise SetupError("Commit or remove all main-worktree changes before setup.")
    if run(["git", "rev-parse", "--verify", "HEAD"], cwd=root, check=False).returncode:
        raise SetupError("Create and review the initial main commit before setup.")
    if run(["git", "show-ref", "--verify", "--quiet", "refs/heads/local-skills"], cwd=root, check=False).returncode == 0:
        raise SetupError("Branch 'local-skills' already exists; no changes were made.")

    worktree = (
        Path(args.worktree_path).expanduser().resolve()
        if args.worktree_path
        else root.with_name(f"{root.name}-local")
    )
    if worktree.exists() or worktree.is_symlink():
        raise SetupError(f"Worktree destination already exists: {worktree}")

    hook = install_push_guard(root)
    branch_created = False
    try:
        run(["git", "branch", "local-skills", "main"], cwd=root)
        branch_created = True
        added = run(["git", "worktree", "add", str(worktree), "local-skills"], cwd=root, check=False)
        if added.returncode:
            raise SetupError(f"Could not create local worktree:\n{added.stderr.strip()}")
    except Exception:
        if branch_created:
            run(["git", "branch", "-D", "local-skills"], cwd=root, check=False)
        if hook.exists():
            hook.unlink()
        raise

    print(f"Created local-only worktree: {worktree}")
    print(f"Installed pre-push guard: {hook}")


if __name__ == "__main__":
    try:
        main()
    except SetupError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

#!/usr/bin/env python3
"""Clone one GitHub-hosted Codex skill into the local-skills worktree."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlparse

import yaml


ALLOWED_FRONTMATTER = {"name", "description", "license", "allowed-tools", "metadata"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---(?P<body>\n.*)?$", re.DOTALL)


class CloneError(RuntimeError):
    """A safe, user-actionable clone failure."""


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def git(root: Path, *args: str, check: bool = True) -> str:
    result = run(["git", *args], cwd=root, check=check)
    return result.stdout.strip()


def parse_repository_url(raw_url: str) -> tuple[str, str, str]:
    parsed = urlparse(raw_url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"github.com", "www.github.com"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        raise CloneError("Repository URL must be a plain HTTPS github.com URL.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2:
        raise CloneError("Repository URL must have the form https://github.com/owner/repository.")
    owner, repository = parts
    if repository.endswith(".git"):
        repository = repository[:-4]
    github_name = re.compile(r"^[A-Za-z0-9_.-]+$")
    if github_name.fullmatch(owner) is None or github_name.fullmatch(repository) is None:
        raise CloneError("GitHub owner and repository names contain unsupported characters.")
    canonical = f"https://github.com/{owner}/{repository}"
    return canonical, owner, repository


def normalize_skill_path(raw_path: str) -> PurePosixPath:
    path = PurePosixPath(raw_path or ".")
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise CloneError("--skill-path must be a relative path that does not contain '..'.")
    return path


def require_marketplace(root: Path, collection: str) -> Path:
    try:
        top_level = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    except (subprocess.CalledProcessError, FileNotFoundError) as error:
        raise CloneError(f"Not a Git worktree: {root}") from error
    if top_level != root:
        raise CloneError(f"Marketplace root must be the Git worktree root: {top_level}")
    if git(root, "branch", "--show-current") != "local-skills":
        raise CloneError("Cloning is allowed only from the local-skills branch.")
    if git(root, "status", "--porcelain"):
        raise CloneError("The local-skills worktree must be clean before cloning.")
    if run(["git", "show-ref", "--verify", "--quiet", "refs/heads/main"], cwd=root, check=False).returncode:
        raise CloneError("Local branch 'main' does not exist.")
    skills_root = root / "plugins" / collection / "skills"
    manifest = root / "plugins" / collection / ".codex-plugin" / "plugin.json"
    if not skills_root.is_dir() or not manifest.is_file():
        raise CloneError(f"Collection '{collection}' is not a valid marketplace plugin.")
    return skills_root


def rebase_onto_main(root: Path) -> None:
    result = run(["git", "rebase", "main"], cwd=root, check=False)
    if result.returncode == 0:
        return
    run(["git", "rebase", "--abort"], cwd=root, check=False)
    detail = (result.stderr or result.stdout).strip()
    raise CloneError(f"Could not rebase local-skills onto main; the rebase was aborted.\n{detail}")


def clone_repository(repository_url: str, ref: str | None, destination: Path) -> None:
    if ref is None:
        result = run(
            ["git", "clone", "--depth", "1", "--", repository_url, str(destination)],
            check=False,
        )
        if result.returncode:
            raise CloneError(f"Git clone failed:\n{result.stderr.strip()}")
        return

    result = run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", "--", repository_url, str(destination)],
        check=False,
    )
    if result.returncode:
        raise CloneError(f"Git clone failed:\n{result.stderr.strip()}")
    fetched = run(
        ["git", "fetch", "--depth", "1", "origin", ref],
        cwd=destination,
        check=False,
    )
    if fetched.returncode:
        raise CloneError(f"Could not fetch ref '{ref}':\n{fetched.stderr.strip()}")
    checked_out = run(
        ["git", "checkout", "--detach", "FETCH_HEAD"],
        cwd=destination,
        check=False,
    )
    if checked_out.returncode:
        raise CloneError(f"Could not check out ref '{ref}':\n{checked_out.stderr.strip()}")


def reject_unsafe_symlinks(skill_root: Path) -> None:
    for directory, dirnames, filenames in os.walk(skill_root, followlinks=False):
        base = Path(directory)
        for name in [*dirnames, *filenames]:
            candidate = base / name
            if not candidate.is_symlink():
                continue
            target = os.readlink(candidate)
            if Path(target).is_absolute():
                raise CloneError(f"Absolute symlink is not allowed: {candidate.relative_to(skill_root)}")
            resolved = (candidate.parent / target).resolve()
            try:
                resolved.relative_to(skill_root.resolve())
            except ValueError as error:
                raise CloneError(
                    f"Symlink escapes the selected skill: {candidate.relative_to(skill_root)}"
                ) from error


def load_and_update_manifest(skill_md: Path, source_url: str) -> tuple[str, str]:
    try:
        contents = skill_md.read_text(encoding="utf-8")
    except OSError as error:
        raise CloneError(f"Unable to read {skill_md}") from error
    match = FRONTMATTER_RE.fullmatch(contents)
    if match is None:
        raise CloneError("SKILL.md must contain closed YAML frontmatter at the start of the file.")
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise CloneError(f"SKILL.md frontmatter is invalid YAML: {error}") from error
    if not isinstance(frontmatter, dict):
        raise CloneError("SKILL.md frontmatter must be a YAML mapping.")
    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER)
    if unexpected:
        raise CloneError(f"Unsupported SKILL.md frontmatter keys: {', '.join(unexpected)}")
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or NAME_RE.fullmatch(name) is None or len(name) > 64:
        raise CloneError("Skill frontmatter name must be matching lower-case kebab-case, up to 64 characters.")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        raise CloneError("Skill frontmatter description must be a non-empty string up to 1024 characters.")
    metadata = frontmatter.get("metadata")
    if metadata is None:
        metadata = {}
        frontmatter["metadata"] = metadata
    if not isinstance(metadata, dict):
        raise CloneError("Skill frontmatter metadata must be a mapping before source can be added.")
    metadata["source"] = source_url
    body = match.group("body") or "\n"
    rendered = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).rstrip()
    return name, f"---\n{rendered}\n---{body}"


def canonical_source_url(repository_url: str, commit: str, skill_path: PurePosixPath) -> str:
    suffix = "" if str(skill_path) == "." else "/" + "/".join(quote(part, safe="") for part in skill_path.parts)
    return f"{repository_url}/tree/{quote(commit, safe='')}{suffix}"


def codex_system_skill_root(skill_name: str) -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "skills" / ".system" / skill_name


def validate_copied_skill(destination: Path, plugin_root: Path) -> None:
    quick_validator = codex_system_skill_root("skill-creator") / "scripts" / "quick_validate.py"
    plugin_validator = codex_system_skill_root("plugin-creator") / "scripts" / "validate_plugin.py"
    for validator in (quick_validator, plugin_validator):
        if not validator.is_file():
            raise CloneError(f"Required Codex validator is unavailable: {validator}")

    result = run([sys.executable, str(quick_validator), str(destination)], check=False)
    if result.returncode:
        detail = (result.stdout or result.stderr).strip()
        raise CloneError(f"Copied skill failed quick validation: {detail}")
    result = run([sys.executable, str(plugin_validator), str(plugin_root)], check=False)
    if result.returncode:
        detail = (result.stdout or result.stderr).strip()
        raise CloneError(f"Copied skill made the plugin invalid: {detail}")


def copy_and_commit(
    root: Path,
    skills_root: Path,
    source_skill: Path,
    name: str,
    rendered_manifest: str,
    source_url: str,
) -> Path:
    destination = skills_root / name
    if destination.exists() or destination.is_symlink():
        raise CloneError(f"Destination already exists: {destination}")
    relative_destination = destination.relative_to(root)
    tracked = run(
        ["git", "ls-files", "--error-unmatch", "--", relative_destination.as_posix()],
        cwd=root,
        check=False,
    )
    if tracked.returncode == 0:
        raise CloneError(f"Destination is already tracked: {relative_destination}")

    staging = skills_root / f".clone-skill-{name}-{os.getpid()}"
    committed = False
    try:
        shutil.copytree(
            source_skill,
            staging,
            symlinks=True,
            ignore=shutil.ignore_patterns(".git"),
        )
        (staging / "SKILL.md").write_text(rendered_manifest, encoding="utf-8")
        os.replace(staging, destination)
        validate_copied_skill(destination, skills_root.parent)
        run(["git", "add", "--", relative_destination.as_posix()], cwd=root)
        message = (
            f"chore(local-skill): clone {name}\n\n"
            f"Source: {source_url}\n"
            "Local-Skill: true"
        )
        result = run(["git", "commit", "-m", message, "--", relative_destination.as_posix()], cwd=root, check=False)
        if result.returncode:
            raise CloneError(f"Could not commit cloned skill:\n{result.stderr.strip()}")
        committed = True
        return destination
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if destination.exists() and not committed:
            run(["git", "restore", "--staged", "--", relative_destination.as_posix()], cwd=root, check=False)
            shutil.rmtree(destination)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_url", help="HTTPS GitHub repository URL")
    parser.add_argument("--collection", choices=("engineering", "productivity"), required=True)
    parser.add_argument("--skill-path", default=".", help="Relative path to the skill in the repository")
    parser.add_argument("--ref", help="Optional branch, tag, or commit")
    parser.add_argument("--marketplace-root", default=".", help="Path to the local-skills worktree")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.marketplace_root).expanduser().resolve()
    repository_url, _, _ = parse_repository_url(args.repository_url)
    skill_path = normalize_skill_path(args.skill_path)
    skills_root = require_marketplace(root, args.collection)

    with tempfile.TemporaryDirectory(prefix="clone-skill-") as temp_dir:
        checkout = Path(temp_dir) / "repository"
        clone_repository(repository_url, args.ref, checkout)
        commit = git(checkout, "rev-parse", "HEAD")
        source_skill = (checkout / Path(*skill_path.parts)).resolve()
        try:
            source_skill.relative_to(checkout.resolve())
        except ValueError as error:
            raise CloneError("Selected skill path escapes the cloned repository.") from error
        if not source_skill.is_dir() or not (source_skill / "SKILL.md").is_file():
            raise CloneError(f"No SKILL.md found at repository path '{skill_path}'.")
        reject_unsafe_symlinks(source_skill)
        source_url = canonical_source_url(repository_url, commit, skill_path)
        name, rendered = load_and_update_manifest(source_skill / "SKILL.md", source_url)
        rebase_onto_main(root)
        destination = copy_and_commit(root, skills_root, source_skill, name, rendered, source_url)

    print(f"Cloned and locally committed skill: {destination}")
    print(f"Source: {source_url}")


if __name__ == "__main__":
    try:
        main()
    except CloneError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error

---
name: scaffold-skills-repo
description: Scaffold a new dual-compatible Claude and Codex skills marketplace with separate engineering and productivity plugins, a pushable master branch, and a protected local-only skills worktree. Use only when the user explicitly invokes $scaffold-skills-repo; never invoke this skill implicitly.
---

# Scaffold Skills Repository

Create a `<name>-skills` repository whose `master` branch contains publishable authored skills and whose sibling local worktree contains both public and local-only skills.

## Collect the inputs

Require a repository name or stem. Accept either `acme` or `acme-skills`; the helper normalizes both to `acme-skills`.

Use the current directory as the parent unless the user gives another location. Use the configured Git user name in generated metadata unless the user supplies `--author-name`.

Do not ask about options that are already clear from the request. Do not create or publish a remote repository unless the user explicitly requests it.

## Run the scaffold

Resolve this skill's directory from the loaded `SKILL.md`, then run:

```bash
python3 <skill-root>/scripts/scaffold_skills_repo.py <name> \
  --parent /path/to/parent
```

Optional arguments:

```bash
--author-name "Display Name"
--worktree-path /custom/path/to/name-skills-local
```

The helper refuses to overwrite either destination. It creates:

- `master` as the pushable branch for authored skills.
- `local-skills` in a sibling `<name>-skills-local` worktree.
- A pre-push hook that rejects the `local-skills` branch and any commit carrying `Local-Skill: true`.
- Codex marketplace and plugin manifests under `.agents/` and `.codex-plugin/`.
- Claude marketplace and plugin manifests under `.claude-plugin/`.
- Independent `engineering` and `productivity` plugins.
- Canonical `AGENTS.md` guidance with `CLAUDE.md` as a relative symlink.
- An initial commit so the local worktree can be created immediately.

If the helper reports an existing target, Git identity problem, or filesystem conflict, stop and report it. Never delete, merge into, or overwrite the existing path.

## Verify the result

Inspect the helper's output, then confirm:

```bash
git -C /path/to/name-skills status --short
git -C /path/to/name-skills branch --list
git -C /path/to/name-skills worktree list
readlink /path/to/name-skills/CLAUDE.md
```

Both worktrees must be clean, the public worktree must be on `master`, the local worktree must be on `local-skills`, and `CLAUDE.md` must target `AGENTS.md`.

## Preserve the branch boundary

Create and commit authored skills only on `master`. Rebase the clean `local-skills` worktree onto local `master` to receive authored changes:

```bash
git -C /path/to/name-skills-local rebase master
```

Commit local-only skills only from the local worktree and include this trailer:

```text
Local-Skill: true
```

Never bypass the pre-push hook, push `local-skills`, or place local skills in `.gitignore`.

## Publish only when requested

When the user explicitly asks for a public GitHub repository, resolve the exact owner and repository name, verify that no conflicting remote exists, and create or attach the remote from the public worktree. Push only `master`; never use `--all`.

After publishing, report the remote URL and reiterate that the sibling worktree and `local-skills` branch remain local.

---
name: clone-skill
description: Clone an open-source Codex skill from GitHub into a protected local-only Git branch and worktree while keeping authored skills on the pushable main branch. Use when copying a third-party skill for personal use, recording its upstream source, setting up the local-skills worktree, or refreshing local cloned-skill history without publishing it.
---

# Clone Skill

Keep authored skills on `main` and third-party copies on `local-skills`. The local worktree contains both: it inherits authored skills from `main` and adds clone commits that must never be pushed.

## Set up the local worktree

Require the marketplace repository to have an initial commit on `main`. Run the setup helper from the main worktree:

```bash
python3 <clone-skill-root>/scripts/setup_local_skills.py \
  --marketplace-root /path/to/karyl-skills
```

Resolve `<clone-skill-root>` to the directory containing this `SKILL.md`; do not assume the user's current directory contains the bundled scripts.

The helper creates a sibling `karyl-skills-local` worktree by default and installs a local pre-push guard. Never overwrite an existing worktree, branch, or pre-push hook. If one exists, inspect it and resolve the conflict with the user.

## Choose the clone target

Ask the user to choose `engineering` or `productivity` for every clone. Classify by the copied skill's primary trigger, following the target marketplace's `AGENTS.md`. Do not infer the collection silently.

Accept an HTTPS GitHub repository URL. Use `--skill-path` when `SKILL.md` is below the repository root and `--ref` when the user requests a branch, tag, or commit instead of the default branch.

## Clone and commit

Run the helper against the local worktree, not the main worktree:

```bash
python3 <clone-skill-root>/scripts/clone_skill.py \
  https://github.com/owner/repository \
  --collection engineering \
  --skill-path path/to/skill \
  --marketplace-root /path/to/karyl-skills-local
```

The helper requires a clean `local-skills` branch, rebases it onto local `main`, validates the upstream skill, records a commit-pinned GitHub link in `metadata.source`, copies the skill, validates the result, and creates a commit with the `Local-Skill: true` trailer.

Never run upstream scripts during cloning. Never overwrite, rename, or update an existing destination automatically. Never add cloned skills to `.gitignore`: ignored files cannot also be committed. The branch and pre-push guard provide the separation.

## Handle failures

- If setup reports that `main` has no commit, ask the user to review and create the initial commit first.
- If rebasing conflicts, the helper aborts the rebase. Report the conflicting paths; do not resolve them without the user.
- If the upstream manifest is incompatible with the marketplace validator, leave the repository unchanged and report the rejected keys or values.
- If the destination exists, stop and ask whether the user wants a separate update workflow. Do not delete it.
- If the push guard blocks a push, keep the local commits local. Do not bypass the hook or force-push them.

## Keep the worktrees synchronized

Create and commit authored skills only in the main worktree. Before each clone, the clone helper rebases clean local-only commits onto the current local `main`, so authored changes become visible in the local worktree without entering local-only history.

# Repository guidance

## Purpose

This repository contains the `karyl skills` marketplace for Codex and Claude Code, with two independently installable plugins: `karyl-engineering` and `karyl-productivity`. Preserve the distinction between engineering work and general productivity work.

## Worktrees

- This repository has a separate local-only worktree at `../karyl-skills-local`.

## Choose the collection

- Put software-development skills in `plugins/engineering/skills/`. This includes architecture, coding, testing, debugging, code review, infrastructure, and delivery workflows.
- Put general workflow skills in `plugins/productivity/skills/`. This includes planning, research, writing, communication, organization, and focus workflows.
- If a skill spans both, place it according to its primary trigger and keep it in one collection. Do not duplicate skills.

## Skill conventions

- Store each skill at `plugins/<collection>/skills/<skill-name>/SKILL.md`.
- Use lower-case kebab-case for the folder and frontmatter `name`; they must match.
- Give the frontmatter `description` enough trigger context for Codex to decide when to use the skill.
- Keep instructions focused, composable, and free of placeholder text.
- Put supporting scripts, references, and assets inside the skill folder unless they are shared by the whole plugin.
- Validate every added or changed skill with the skill-creator `quick_validate.py` helper.

## Marketplace conventions

- Keep the marketplace name `karyl` and display name `karyl skills` in `.agents/plugins/marketplace.json`.
- Keep the Claude Code marketplace at `.claude-plugin/marketplace.json` alongside the Codex marketplace.
- Keep the marketplace plugin names `karyl-engineering` and `karyl-productivity` mapped to `plugins/engineering/` and `plugins/productivity/`, respectively. These directories are plugin roots; keep each `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` present and valid.
- Keep marketplace entries in both catalogs ordered as they should appear in their respective clients.
- Marketplace source paths remain `./plugins/engineering` for `karyl-engineering` and `./plugins/productivity` for `karyl-productivity`.
- Every marketplace entry must retain `policy.installation`, `policy.authentication`, and `category`.
- Do not create another top-level plugin for a single skill unless it genuinely needs to be installed independently.
- Use the plugin-creator helpers when adding or updating marketplace-backed plugins; do not hand-edit existing marketplace entries during an update flow.

## Verification

Before finishing a change:

1. Validate each changed skill.
2. Validate each affected plugin with `validate_plugin.py`.
3. Run `claude plugin validate .` when Claude Code is available.
4. Parse both marketplace files as JSON and confirm every local source path exists.

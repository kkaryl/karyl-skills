# Builder Notes

## 2026-08-01

### karyl-skills/plugins

- **Intent:** I wanted a lightweight, invoke-only way to capture the lessons from projects I build with coding agents, so each experiment leaves a durable record of what I explored and decided. **Process:** I worked with Codex to shape the note format, define strict evidence and privacy boundaries, settle project and date grouping, and establish completion and deduplication rules before authorizing implementation. **Output:** A reusable `builder-notes` skill records source-grounded builder journeys in `BUILDER_NOTES.md`.
- **Intent:** I wanted PR updates that let me quickly assess the complete change: its scope, decisions, and reviewer follow-through. **Process:** I worked with Codex to tighten the summary standard, apply it to the current PR, and extend the workflow to assign me and select existing labels from the full change. **Output:** An `update-pr-summary` skill regenerates whole-PR titles and descriptions, then verifies the assignee and labels.

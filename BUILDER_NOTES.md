# Builder Notes

## 2026-08-01

### karyl-skills/plugins

- **Intent:** I wanted an invoke-only way to preserve my journey when building projects with agentic coding. **Process:** I worked through the note format, evidence boundaries, project grouping, chronological ordering, completion criteria, semantic deduplication, and privacy safeguards with Codex. **Output:** A reusable `builder-notes` skill now records completed builder journeys in `BUILDER_NOTES.md`.
- **Intent:** I wanted future PR descriptions to be concise, meaningful, and useful to me as a direct staff-engineer reviewer. **Process:** I worked iteratively with Codex to tighten the summary standard, apply it to the current PR, and extend the workflow to assign me and select appropriate existing labels from the complete change. **Output:** An `update-pr-summary` skill regenerates whole-PR titles and descriptions, then verifies the assignee and labels.

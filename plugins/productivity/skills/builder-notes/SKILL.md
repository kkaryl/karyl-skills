---
name: builder-notes
description: Capture completed, user-driven work from the current chat as concise input-to-outcome entries in the active repository's BUILDER_NOTES.md. Use only when the user explicitly invokes `$builder-notes` by name at the end of a work session. Never invoke implicitly for changelogs, summaries, retrospectives, or ordinary project work.
---

# Builder Notes

Record durable source material for a future build narrative. Treat the current chat as the authority for intent, decisions, iteration, and reported outcomes.

## 1. Establish the destination

Locate the active repository root. Prefer the Git root; otherwise use the current workspace root only when it is unambiguous. Do not guess across multiple repositories.

Use `<repository-root>/BUILDER_NOTES.md`. On first creation, start with only:

```markdown
# Builder Notes
```

Use the user's local calendar date in `YYYY-MM-DD` form.

## 2. Extract completed workstreams

Read the current chat up to the invocation. Treat these as authoritative:

- the user's prompts, reasoning, corrections, and accepted decisions
- the LLM's descriptions of its process
- the LLM's completion summaries of what it produced
- meaningful changes of direction caused by user-LLM iteration

Create one entry per completed logical workstream, not per prompt. Merge follow-ups and revisions that serve the same intent.

Include a workstream only when it is user-driven and the LLM reported a completed outcome. Skip pending, blocked, abandoned, and unsuccessful workstreams. A failed attempt may appear only as a deviation within work that ultimately completed.

Do not inspect the repository to reconstruct missing rationale or claim unreported outcomes. Use repository paths only to locate the destination and determine project folders. If the chat does not support a detail, omit it.

Exclude routine tool calls, implementation minutiae, transient errors, and suggestions the user neither accepted nor acted on.

## 3. Assign project sections

Under the date, group entries by project folder:

- For nested work, use the exact basename of the first directory beneath the repository root that contains the work.
- For root-level or cross-project work, use the exact repository-root basename.
- When one workstream has distinct completed outcomes in multiple project folders, split it only when each result stands alone clearly.

Use project headings in order of their first appearance that day. Preserve existing project order. Within each project, keep bullets in the order the workstreams occurred; append later sessions after earlier ones.

## 4. Write concise entries

Write each entry as one compact bullet, ideally 60-100 words:

```markdown
- **Input:** <the user's intent or deciding thought> **Process:** <the accepted approach and important iteration> **Deviation:** <material change of direction, when present> **Outcome:** <what the LLM reported producing> **Learning:** <supported takeaway, when present>
```

Always include `Input`, `Process`, and `Outcome`. Include `Deviation` only for a material change in direction. Include `Learning` only when supported by the user's decisions, the accepted iteration path, or the LLM's completion summary.

Keep the emphasis on the user's thought process and decisions. Never invent motivation, reflection, hindsight, learning, or completion claims.

Remove or generalize secrets, credentials, private identifiers, financial identifiers, and raw sensitive data. Do not copy sensitive values even when they appeared in the chat.

## 5. Merge into the file

Use this hierarchy:

```markdown
# Builder Notes

## YYYY-MM-DD

### project-folder

- **Input:** ... **Process:** ... **Outcome:** ...
```

Keep date sections reverse chronological. When adding a new date, place it among existing `## YYYY-MM-DD` headings in descending order without rewriting other dates.

Before adding a bullet, compare it semantically with bullets under the same date and project. Treat matching intent and outcome as the same workstream even when phrasing differs. Enrich or correct that bullet in place and keep its original position. Do not merge distinct workstreams merely because they touch the same feature.

Make the smallest surgical edit. Preserve unrelated wording, formatting, manual edits, dates, project sections, and bullets. Never normalize or rewrite older content for style consistency.

If the chat contains no qualifying completed workstream, leave `BUILDER_NOTES.md` unchanged and report that no entry was added.

## 6. Report completion

State whether the file was created, updated, or left unchanged. Briefly identify the date and project sections touched, without repeating the full notes.

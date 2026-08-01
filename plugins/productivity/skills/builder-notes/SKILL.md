---
name: builder-notes
description: Capture the user's builder journey from completed work in the current chat as concise Intent–Process–Output entries in the active repository's BUILDER_NOTES.md. Identify the coding agent hosting the chat, preserve the originating session date, and record how the user partnered with that agent. Use only when the user explicitly invokes `$builder-notes` by name; never invoke implicitly for changelogs, summaries, retrospectives, or ordinary project work.
---

# Builder Notes

Record durable source material for a future build narrative. Capture why the user started, how working with the active coding agent shaped the journey, and what meaningful result emerged. Do not write a changelog or implementation inventory.

## 1. Identify the active coding agent

Before doing anything else, determine which coding agent is hosting the current chat. Prefer, in order:

1. Host or session metadata that names the agent.
2. System or developer instructions that identify the agent or product.
3. The agent's explicit self-identification in the current chat.

Use the agent's canonical product name when it is known, such as `Codex` or `Claude`. Do not infer the agent from repository files, because the same repository may be used by different agents. If the identity remains ambiguous, ask the user before writing.

Treat the identified agent as the primary collaborator throughout the notes. Mention another agent only when the chat shows that it materially contributed to the completed workstream and supports its identity.

## 2. Establish the destination and date

Locate the active repository root. Prefer the Git root; otherwise use the current workspace root only when it is unambiguous. Do not guess across multiple repositories.

Use `<repository-root>/BUILDER_NOTES.md`. On first creation, start with only:

```markdown
# Builder Notes
```

Date each workstream using the user's local date of the first qualifying message that began it, not the date `$builder-notes` was invoked or the file was updated. Prefer, in order:

1. Chat or turn timestamps exposed by the host.
2. Dated environment context associated with the first qualifying request.
3. A date explicitly stated by the user.
4. The current local date only when the skill is invoked immediately at the end of the same uninterrupted session.

If no reliable originating date is available and the invocation may be delayed, ask the user before writing. Do not infer the date from file metadata or Git history.

## 3. Extract the builder journey

Read the current chat up to the invocation. Treat these as authoritative:

- the user's intent, reasoning, corrections, and accepted decisions
- named skills or workflows the user chose to use with the active coding agent
- meaningful questions, discoveries, and changes of direction from the collaboration
- the active coding agent's reported completed outcomes

Create one entry per completed logical workstream, not per prompt. Merge follow-ups and revisions that serve the same intent.

Capture three things:

- **Intent:** why the user wanted to undertake the work.
- **Process:** how the user partnered with the active coding agent, including named skills and only the decisions or discoveries that meaningfully shaped the result.
- **Output:** the principal artifact, capability, or achieved state and what it enables.

Include a workstream only when it is user-driven and the active coding agent reported a completed outcome. Skip pending, blocked, abandoned, and unsuccessful workstreams. Mention a failed attempt only when it materially changed the successful approach.

Do not inspect the repository to reconstruct missing rationale or claim unreported outcomes. Use repository paths only to locate the destination and determine project folders. If the chat does not support a detail, omit it.

## 4. Assign project sections

Under the date, group entries by project location:

- For nested work, use `<repository-root-basename>/<first-directory-basename>`, where the directory is the first one beneath the repository root that contains the work.
- For root-level or cross-project work, use the exact repository-root basename.
- When one workstream has distinct completed outcomes in multiple project folders, split it only when each result stands alone clearly.

Use project headings in order of their first appearance that day. Preserve existing project order. Within each project, keep bullets in the order the workstreams occurred; append later sessions after earlier ones.

## 5. Write concise entries

Write each entry as one compact bullet, ideally 45-80 words:

```markdown
- **Intent:** <why I wanted to do this> **Process:** <how I partnered with the active coding agent and what the collaboration surfaced> **Output:** <the principal result and what it enables>
```

Write `Intent` and `Process` from the user's first-person perspective when supported by the chat: “I wanted…”, “I used…”, and “I worked with <agent-name>…”. Replace `<agent-name>` with the coding agent identified in step 1. Prefer the user's language and silently correct obvious spelling or grammar errors without changing meaning.

Keep `Output` result-centered and independent of who produced it. Lead with the artifact, capability, or achieved state, and use a direct present-tense statement when describing lasting behavior. Do not begin with “We produced” or repeat collaboration already captured in `Process`. Avoid prospective language such as “would” or “could” for completed work.

Keep `Output` to one grammatical sentence describing one principal result, with at most three tightly related capabilities or deliverables. Incorporate a meaningful change of direction into `Process`; do not add separate `Deviation` or `Learning` labels.

Exclude:

- file inventories, repository boilerplate, and implementation minutiae
- routine tool calls, validation commands, Git operations, symlinks, and transient errors
- long catalogs of technical decisions that do not explain the user's journey
- adjectives such as “production-grade”, “Staff-level”, or “decision-complete” unless central to the user's stated intent
- suggestions the user neither accepted nor acted on

Never invent motivation, reflection, hindsight, learning, or completion claims.

Remove or generalize secrets, credentials, private identifiers, financial identifiers, and raw sensitive data. Do not copy sensitive values even when they appeared in the chat.

Example:

```markdown
- **Intent:** I wanted to build mini projects to learn agent security in depth. **Process:** I used the Grilling skill to work iteratively with <LLM>, deepening the scope and surfacing important trust, approval, and verification decisions. **Output:** The first project specification defines the design and establishes its repository scaffold.
```
Replace `<LLM>` with the coding agent identified in step 1.

## 6. Merge into the file

Use this hierarchy:

```markdown
# Builder Notes

## YYYY-MM-DD

### repository-name/project-folder

- **Intent:** ... **Process:** ... **Output:** ...
```

Keep date sections reverse chronological. When adding a new date, place it among existing `## YYYY-MM-DD` headings in descending order without rewriting other dates.

Before adding a bullet, compare it semantically with bullets under the same date and project. Treat matching intent and output as the same workstream even when phrasing differs. Enrich or correct that bullet in place and keep its original position. Do not merge distinct workstreams merely because they touch the same feature.

Make the smallest surgical edit. Preserve unrelated wording, formatting, manual edits, dates, project sections, and bullets. Never normalize or rewrite older content for style consistency.

If the chat contains no qualifying completed workstream, leave `BUILDER_NOTES.md` unchanged and report that no entry was added.

## 7. Report completion

State whether the file was created, updated, or left unchanged. Briefly identify the date and project sections touched, without repeating the full notes.

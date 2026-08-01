---
name: update-pr-summary
description: Regenerate the current GitHub pull request title and description from the complete, latest branch diff against its actual target branch, then assign the authenticated GitHub user and add appropriate existing repository labels. Use only when the user explicitly invokes `$update-pr-summary` to replace an existing PR summary with the concise What–Why–How format and update its metadata; never append to the current description or summarize only the latest commit.
---

# Update PR Summary

Replace the current PR title and description with a concise account of the PR as a whole. Write the description for an impatient, direct staff engineer who already has access to the changed-files view.

## 1. Resolve the PR

Work from the active Git repository and require an authenticated GitHub CLI session.

1. Identify the current branch, its upstream, and the open PR with `gh pr view`.
2. Read the PR number, URL, base branch, head branch, current title, and current body.
3. Stop if the branch has no open PR or the target branch cannot be determined. Do not guess the target.

Treat the existing body as context only. It may contain useful issue or validation information, but it is not the structure to preserve.

## 2. Read the remote PR state

Treat the PR's remote base and head as the source of truth. The local working tree may be dirty and the current branch may contain unpushed commits; neither is part of the published PR.

1. Fetch the latest target branch and PR head into refs that do not update or check out the current branch. Prefer GitHub's pull-request head ref; use `gh pr diff` or the GitHub API when that ref is unavailable.
2. Confirm the fetched base and head belong to the resolved PR.
3. Use those remote refs for all commit and diff inspection. Never use local `HEAD` unless its commit exactly matches the remote PR head.
4. Stop if the remote base or head cannot be resolved. Do not substitute stale local refs.

Never stash, discard, commit, push, pull, merge, rebase, or check out user work.

## 3. Understand the whole PR

Compare the remote target ref to the remote PR head with a three-dot diff. Inspect:

- the full commit range from target to head
- the diff summary and changed areas
- the substantive diff for every logical area
- repository instructions and relevant validation already documented or run
- linked issue context when it explains the motivation

Base the summary on the entire PR, not the latest commit, most recently edited files, or the previous description. Group related edits into a few key behavioral changes. Derive the `Why` from evidence that explains the purpose of the `What`, such as linked issue context, commit rationale, or behavioral intent in the diff. If that purpose is not supported, ask the user one concise question before updating the PR.

## 4. Write for the reviewer

Generate a Conventional Commit title:

```text
<type>(<scope>): <concise imperative description>
```

Choose the type and scope from the PR's dominant purpose. Use standard types such as `feat`, `fix`, `refactor`, `docs`, `test`, `build`, `ci`, `perf`, or `chore`. Keep the title specific, lower-case after the colon, free of a trailing period, and at most 72 characters.

Apply a reviewer-novelty test before drafting. Keep only information that synthesizes purpose, behavioral impact, relationships between changes, non-obvious decisions, scope boundaries, trade-offs, or risk coverage. Remove anything directly available from the PR title, metadata, changed-files view, commit list, or checks. A fact visible in the diff belongs in the summary only when interpreting it saves the reviewer meaningful reconstruction work.

Use this body structure. Omit `Validation` entirely when there is no reviewer-relevant behavioral evidence beyond the PR's visible checks:

```markdown
## Summary

### What

<short, concise paragraph>

### Why

<short, concise paragraph>

### How

- <key implementation behavior or decision>
- <key implementation behavior or decision>

## Validation

- <behavior or risk exercised and the outcome>
```

Apply these constraints:

- Keep `What` to a short, direct paragraph describing the resulting behavior or capability and its scope, not the files or components changed.
- Keep `Why` to a short, direct paragraph explaining the purpose of the `What`: why the changed behavior exists and what actual user, product, or engineering need it serves. Do not restate `What`, describe `How`, invent motivation, or substitute a generic benefit.
- Keep `How` to one to three bullets covering only non-obvious decisions, invariants, constraints, trade-offs, or deliberate scope boundaries that help review the change.
- Follow repository instructions such as `AGENTS.md` when selecting relevant validation to run. Include `Validation` only for behavioral scenarios or risks exercised during this invocation, and state what the evidence established. Consolidate related evidence into one to three concise bullets.
- Do not report commands, validators, test suites, or CI as merely passing. Do not narrate GitHub check state, including that no checks are reported; reviewers can see it on the PR.
- Prefer evidence such as `Confirmed repeated updates preserve unrelated entries` over status such as `Tests passed`. Never claim behavioral coverage that was not observed.
- Keep the summary below 150 words unless a breaking change genuinely requires more context. Never pad it to reach a target length.
- Do not enumerate changed files, commits, housekeeping, version bumps, configuration boilerplate, or implementation details already obvious from the diff.
- Do not add throat-clearing, generic benefits, exhaustive checklists, tables, emojis, or a concluding recap.
- Include a material limitation or unusual choice in `How` only when it affects reviewer judgment; never force a caveat.

Delete any sentence that merely repeats another sentence, renames the section, or does not help the reviewer judge the change.

## 5. Replace and verify

Create the title and body from scratch. Do not append, patch individual sections, preserve stale prose by default, or post the summary as a comment.

Update both PR fields in one `gh pr edit` operation using a temporary body file. Keep the title out of the body. Then read the PR back with `gh pr view` and confirm the stored title and body match the generated values.

## 6. Assign and label

After verifying the title and body:

1. Read the repository's available labels and their descriptions with `gh label list`.
2. Select only existing labels clearly supported by the full PR diff and purpose. Include a collection- or area-specific label when one matches, plus a change-type label when its definition applies. Do not create, rename, delete, or remove labels, and do not choose labels from the title alone.
3. Assign the authenticated GitHub user with `--add-assignee @me` and add the selected labels in one `gh pr edit` operation. Preserve current assignees and labels. If no existing label clearly applies, assign the user without inventing or forcing a label.
4. Read the PR back with `gh pr view` and confirm the title, body, authenticated assignee, and selected labels were stored.

Report the updated title, PR URL, assignee, and labels without repeating the full description.

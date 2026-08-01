---
name: update-pr-summary
description: Regenerate an existing GitHub pull request title and description from the complete, latest branch diff against its actual target branch, then assign the authenticated GitHub user and add appropriate existing repository labels. If the current branch has no PR, draft the same summary and propose creating one, but wait for explicit confirmation before pushing or creating it. Use only when the user explicitly invokes `$update-pr-summary`; never append to an existing description or summarize only the latest commit.
---

# Update PR Summary

Replace the current PR title and description with a concise account of the PR as a whole. Write the description for an impatient, direct staff engineer who already has access to the changed-files view.

## 1. Resolve the PR

Work from the active Git repository and require an authenticated GitHub CLI session.

1. Identify the current branch, its upstream, and any open PR with `gh pr view`.
2. If an open PR exists, read its number, URL, base branch, head branch, current title, and current body.
3. If no open PR exists, enter creation-proposal mode. Resolve the proposed base from an explicit user choice, the branch's configured `gh-merge-base`, or the repository's default branch, in that order. State the proposed base and ask the user if the target remains ambiguous; do not guess.

When a body exists, treat it as context only. It may contain useful issue or validation information, but it is not the structure to preserve.

## 2. Resolve the comparison state

For an existing PR, treat its remote base and head as the source of truth. The local working tree may be dirty and the current branch may contain unpushed commits; neither is part of the published PR.

1. Fetch the latest target branch and PR head into refs that do not update or check out the current branch. Prefer GitHub's pull-request head ref; use `gh pr diff` or the GitHub API when that ref is unavailable.
2. Confirm the fetched base and head belong to the resolved PR.
3. Use those remote refs for all commit and diff inspection. Never use local `HEAD` unless its commit exactly matches the remote PR head.
4. Stop if the remote base or head cannot be resolved. Do not substitute stale local refs.

For a proposed PR, fetch the proposed base without updating or checking out the current branch, then identify the exact committed head to summarize:

1. Use the published branch head when it matches local `HEAD`.
2. If local `HEAD` contains committed, unpushed work, use it only for the proposal and disclose that creating the PR requires pushing those commits.
3. Stop and ask the user how to proceed if local and remote branch histories have diverged. Never force-push or choose one history implicitly.
4. Exclude uncommitted working-tree changes and stop if the proposed branch contains no commits relative to the base.

Never stash, discard, commit, pull, merge, rebase, or check out user work. Never push unless the user explicitly confirms a creation proposal that identifies the remote and branch to push.

## 3. Understand the whole PR

Compare the resolved target ref to the exact head being summarized with a three-dot diff. Inspect:

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
- For workflow or automation changes, derive `Why` from the recurring task or user need the workflow enables. Prefer the purpose repeatedly emphasized across the complete diff over motivations inferred from secondary safeguards or the latest commit. Reuse key terms from `What` when they express the actual need; do not invent a different motivation merely to avoid textual overlap.
- Keep `How` to one to three bullets covering only non-obvious decisions, invariants, constraints, trade-offs, or deliberate scope boundaries that help review the change.
- Follow repository instructions such as `AGENTS.md` when selecting relevant validation to run. Include `Validation` only for behavioral scenarios or risks exercised during this invocation, and state what the evidence established. Consolidate related evidence into one to three concise bullets.
- Do not report commands, validators, test suites, or CI as merely passing. Do not narrate GitHub check state, including that no checks are reported; reviewers can see it on the PR.
- Prefer evidence such as `Confirmed repeated updates preserve unrelated entries` over status such as `Tests passed`. Never claim behavioral coverage that was not observed.
- Keep the summary below 150 words unless a breaking change genuinely requires more context. Never pad it to reach a target length.
- Do not enumerate changed files, commits, housekeeping, version bumps, configuration boilerplate, or implementation details already obvious from the diff.
- Do not add throat-clearing, generic benefits, exhaustive checklists, tables, emojis, or a concluding recap.
- Include a material limitation or unusual choice in `How` only when it affects reviewer judgment; never force a caveat.

Delete any sentence that merely repeats another sentence, renames the section, or does not help the reviewer judge the change.

## 5. Update or propose creation

Create the title and body from scratch. Do not append, patch individual sections, preserve stale prose by default, or post the summary as a comment.

If an open PR exists, update both fields in one `gh pr edit` operation using a temporary body file. Keep the title out of the body. Then read the PR back with `gh pr view` and confirm the stored title and body match the generated values.

If no open PR exists:

1. Present a creation proposal containing the base, head, generated title, full generated body, and whether a push is required.
2. Ask for explicit confirmation to create the PR. If a push is required, identify the remote and branch in the confirmation request. Do not push or create the PR before the user confirms.
3. After confirmation, perform only the disclosed push when required, then create the PR with explicit `--base`, `--head`, `--title`, and `--body-file` values. Do not use commit autofill in place of the generated summary.
4. Read the new PR back with `gh pr view` and confirm the stored base, head, title, and body match the proposal.

## 6. Assign and label

After verifying the title and body of the existing or newly created PR:

1. Read the repository's available labels and their descriptions with `gh label list`.
2. Select only existing labels supported by the full PR diff and purpose:
   - Add a collection- or area-specific label when one matches.
   - Add `enhancement` when the Conventional Commit title type is `feat` and that label exists.
   - Add `documentation` when the title type is `docs` or any changed path ends in `.md` and that label exists.
   - Never map `fix` to `bug`. Add `bug` only when the full diff or linked issue clearly shows a correction to defective behavior, a regression, or a failing scenario. Do not add it for incremental improvements, refinements, clarifications, or merely patch-sized changes.
   - Add any other change-type label only when its definition applies. Except for the explicit mappings above, do not choose labels from the title alone.
3. Assign the authenticated GitHub user with `--add-assignee @me` and add the selected labels in one `gh pr edit` operation. Preserve current assignees and labels. If no existing label clearly applies, assign the user without inventing or forcing a label.
4. Read the PR back with `gh pr view` and confirm the title, body, authenticated assignee, and selected labels were stored.

Report whether the PR was updated or created, followed by its title, URL, assignee, and labels without repeating the full description.

# Report structure and release audit

Use a stable core plus topic-specific modules. Omit empty or irrelevant sections. Do not force a person timeline, interview section, or technical architecture onto a topic that does not need it.

## Stable core

```markdown
# <Topic>: <current, useful framing>

**Research date:** <Month D, YYYY, local timezone>
**Research brief:** <confirmed brief without the confirmation question>
**Recency window:** <effective current-first window and why>

## Executive synthesis

## Key findings

## What is happening now

## What to take away

## Conflicting evidence and uncertainty

## Coverage and limitations

## Further reading and viewing

## Methodology
```

Keep `Methodology` short. State the source hierarchy, research date, media limitations, and any meaningful multilingual interpretation. Do not repeat every inline citation in a bibliography.

## Adaptive modules

Choose only modules that answer the confirmed brief. Examples include:

- Recent projects and what they are trying to achieve
- Evolving ideas and how they connect
- Current influence on a field or community
- Key interview insights
- Architecture and system model
- Recent releases and ecosystem state
- Tradeoffs, implementation patterns, and failure modes
- Organization strategy and active products
- Event chronology, stakeholders, causes, and consequences
- Open questions and emerging direction

For people, prioritize recent projects, ideas, influence, and direct media. Include career history only where it explains the present.

## Citation rules

- Put descriptive Markdown links next to the factual claim they support.
- Cite the accessible original source whenever available.
- Do not cite search results, snippets, evidence packets, or agent summaries.
- Treat several reports derived from one origin as a single evidentiary chain.
- Corroborate consequential or disputed claims when practical.
- Label source opinion, synthesis, inference, and speculation distinctly.
- Do not cite inaccessible content as substantive evidence.

## Writing rules

- Prefer synthesis over source-by-source summaries.
- Use exact dates for current-state claims.
- Define specialized terms only when needed.
- Keep sections short, direct, and non-repetitive.
- Use minimal to no em dashes.
- Use occasional short quotes only when the exact wording matters.
- Include no timestamps in interview summaries.
- Use no word-count target.

## Release audit

Do not hand off the report until every applicable check passes:

- The report directly answers the confirmed brief.
- The report's framing, section structure, or cross-section synthesis reflects every anchor source's central ideas; a dedicated anchor section is not required.
- Every central item from the anchor-source coverage map appears substantively or is explicitly accounted for in `Coverage and limitations`.
- Important workflows, design patterns, and conceptual models were not displaced solely by newer job news, formal projects, repository metrics, or easier corroboration.
- Every central idea nominated by media analysis appears substantively or is explicitly accounted for in `Coverage and limitations`.
- Current developments receive the priority required by the dynamic recency policy.
- The research date, effective recency window, and exact dates are present.
- Every meaningful factual claim has nearby accessible evidence.
- No inaccessible source substantiates a claim.
- Facts, source opinions, synthesis, inference, and speculation are distinguishable.
- Consequential contradictions are resolved or exposed clearly.
- Every summarized interview was materially analyzed using `$youtube-notes` standards.
- Coverage gaps and limitations are honest and specific.
- No sensitive personal information, leaked material, or invasive speculation appears.
- Technical claims remain evidence-based; untested synthesized code is labeled.
- The report is concise, non-repetitive, and uses minimal to no em dashes.
- The destination is a new append-only run directory.
- Only polished artifacts are present; no notes, logs, packets, or raw transcripts were saved.

If a check fails near the deadline, narrow, qualify, or remove the affected claim. Never lower the evidence standard to make the report appear complete.

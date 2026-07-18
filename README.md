# karyl skills

`karyl skills` is a repo-local Codex marketplace organized into separate engineering and productivity collections.

## Collections

- **Engineering** contains skills for code, architecture, testing, debugging, delivery, and other software-development work.
- **Productivity** contains skills for planning, research, writing, communication, organization, and general workflows.

Each collection is an independently installable Codex plugin: `karyl-engineering` or `karyl-productivity`.

## Layout

```text
.
├── .agents/plugins/marketplace.json
├── AGENTS.md
└── plugins/
    ├── engineering/
    │   ├── .codex-plugin/plugin.json
    │   └── skills/
    │       └── <skill-name>/SKILL.md
    └── productivity/
        ├── .codex-plugin/plugin.json
        └── skills/
            └── <skill-name>/SKILL.md
```

## Add a skill

Create a lower-case, hyphenated folder in the appropriate collection:

```text
plugins/engineering/skills/<skill-name>/SKILL.md
plugins/productivity/skills/<skill-name>/SKILL.md
```

Every `SKILL.md` should start with YAML frontmatter containing a matching `name` and a concise `description` that explains when the skill should be used.

## Validate the collections

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  "$PWD/plugins/engineering"

python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  "$PWD/plugins/productivity"
```

Validate an individual skill with:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  "$PWD/plugins/<collection>/skills/<skill-name>"
```

## Install karyl skills

The `karyl skills` catalog is repo-local rather than the default marketplace at `~/.agents/plugins/marketplace.json`, so add this repository explicitly:

```bash
codex plugin marketplace add "$PWD"
```

You can then install the `karyl-engineering` and `karyl-productivity` plugins independently.
```bash
codex plugin add karyl-engineering@karyl-skills
codex plugin add karyl-productivity@karyl-skills
```
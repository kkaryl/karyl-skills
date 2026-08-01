# karyl skills

`karyl skills` is a personal marketplace of reusable skills for Codex and Claude Code. It is organized as two independently installable plugins so you can install only the collection that fits your needs.

## Included plugins

| Plugin | Focus | Skills |
| --- | --- | --- |
| `karyl-engineering` | Software development workflows | `init-ai`, `scaffold-skills-repo` |
| `karyl-productivity` | Research and personal workflows | `clone-skill`, `deep-research`, `youtube-notes` |

## Install in Codex

Clone this repository, then add it as a Codex marketplace:

```bash
git clone <repository-url> karyl-skills
cd karyl-skills
codex plugin marketplace add "$PWD"
```

Install either plugin, or both:

```bash
codex plugin add karyl-engineering@karyl-skills
codex plugin add karyl-productivity@karyl-skills
```

## Install in Claude Code

Add this repository as a Claude Code marketplace, then install either plugin, or both:

```bash
claude plugin marketplace add .
claude plugin install karyl-engineering@karyl-skills
claude plugin install karyl-productivity@karyl-skills
```

## Repository layout

```text
.
├── .agents/plugins/marketplace.json
├── plugins/
│   ├── engineering/
│   │   ├── .codex-plugin/plugin.json
│   │   └── skills/
│   └── productivity/
│       ├── .codex-plugin/plugin.json
│       └── skills/
└── AGENTS.md
```

Each skill lives at `plugins/<collection>/skills/<skill-name>/SKILL.md`.

## Add or update a skill

Use a lower-case, hyphenated skill name and place the skill in the collection that best matches its primary use:

- `plugins/engineering/skills/<skill-name>/SKILL.md` for software-development work.
- `plugins/productivity/skills/<skill-name>/SKILL.md` for research, writing, planning, and other general workflows.

Every `SKILL.md` needs YAML frontmatter with a matching `name` and a concise `description` that explains when Codex should use it. See [AGENTS.md](AGENTS.md) for the repository conventions.

## Validate changes

Validate each changed skill:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  "$PWD/plugins/<collection>/skills/<skill-name>"
```

Then validate both plugins:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  "$PWD/plugins/engineering"

python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  "$PWD/plugins/productivity"
```

Finally, confirm that `.agents/plugins/marketplace.json` parses as JSON and that every local plugin source path exists.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). You may copy, modify, and distribute it under the GPLv3 terms. Distributed modified versions must remain available under the same license.

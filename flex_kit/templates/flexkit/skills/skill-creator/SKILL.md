---
name: skill-creator
description: Author a new flex-kit skill. Explains the SKILL.md format and the source-then-gen workflow. Use when creating, editing, or improving a skill for this project.
---

# Skill Creator

A skill teaches the agent how to do one kind of task well. In flex-kit a skill is a
directory under `.flexkit/skills/<id>/` with a `SKILL.md`. flex-kit generates the
host-native copies (`.claude/skills/`, `.agents/skills/`) from it.

## Format

```
.flexkit/skills/<id>/
  SKILL.md            required: frontmatter (name, description) + markdown body
  references/         optional: longer docs, copied verbatim to every host
```

Frontmatter:

- `name` must equal the directory `<id>`.
- `description` should say, in one line, what the skill does + **when to use it** - phrase
  the trigger explicitly (`"… Use when <situation>"`). The agent reads it to decide whether
  to apply the skill.

## Workflow: edit the source, then generate

1. Edit `.flexkit/skills/<id>/SKILL.md` - this is the single source of truth.
2. Run `flex-kit gen` to regenerate the host surfaces.
3. Never hand-edit `.claude/skills/` or `.agents/skills/`; they are generated.
   `flex-kit doctor` fails if a generated file drifts from its source.

## Writing principles

- **One skill = one job.** Keep the description trigger-focused, not a feature list.
- **Token-conscious.** Every section must change the agent's behavior - if removing it
  wouldn't, cut it. Favor process over reference dumps, specific over general.
- **Progressive disclosure.** Keep `SKILL.md` tight (aim < ~150 lines). Move a section past
  ~100 lines into `references/<topic>.md` and link it from the body - loaded on demand.
- **High-stakes skills** (a quality gate, a destructive op) earn a short `## Red Flags`
  list - observable signs the skill is being violated ("marked done with no evidence") - so
  the agent can self-correct mid-task.
- Run `flex-kit doctor` before committing to confirm everything is in sync.

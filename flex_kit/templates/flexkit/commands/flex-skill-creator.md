---
name: flex-skill-creator
description: Create, audit, or update a .flexkit skill so it follows the kit's format - name == dir, a "use when" description, a tight token-conscious body, references/ for long sections. Use to add a skill or fix skill drift.
argument-hint: [audit|create|update] [id]
---

Create, audit, or update a `.flexkit/skills/` skill for: **$ARGUMENTS** (default: `audit`).

## Purpose

A skill teaches the agent how to do one kind of task well. In flex-kit a skill is
`.flexkit/skills/<id>/SKILL.md` (+ optional `references/`); `gen` produces the host copies
(`.claude/skills/`, `.agents/skills/`). This command keeps every skill on one format so
none drifts, and audits the existing ones against it.

It owns the **prose contract**. Mechanical checks (kebab name, description length,
generated-in-sync) stay in `flex-kit doctor` - audit defers to it, never restates it.

## The skill contract

```
.flexkit/skills/<id>/
  SKILL.md       required: frontmatter (name, description) + a markdown body
  references/    optional: long-form docs / checklists, read on demand
  scripts/       optional: executable code for a deterministic step (run it, don't reason it)
```

Frontmatter:

| Field | Rule |
|---|---|
| `name` | kebab-case, **== the directory `<id>`**, and **group-prefixed** (`<group>-<topic>`) - see below |
| `description` | third-person summary of *what it does* + **concrete trigger phrases the user would actually say** (`"… Use when the user asks to X, Y, or mentions Z"`) + **exclusions** (`"not for W"`). It is the discovery hook (always in the system prompt), so: trigger-focused not a feature list, ≤ 1024 chars, and **no process steps** - put those in the body, or the agent follows the summary instead of the skill |

**Naming & grouping.** Skills `gen`-flatten into one host namespace (`.claude/skills/<id>/`),
so an id must be globally unique. Convention: a **pack is a discipline group**, and a **skill
id is `<group>-<topic>`** - e.g. `architecture-design-patterns`, `backend-restful-api`. The
prefix prevents collisions and makes the flat list self-grouping. Groups:

| prefix | scope |
|---|---|
| `architecture-` | code & system structure: design patterns, layering, domain modeling, boundaries |
| `engineering-` | implementation craft (language-agnostic): errors, concurrency, testing, observability, performance |
| `backend-` | server-side: api, data, caching, auth (+ `backend-<lang>` for implementation) |
| `frontend-` | client-side: components, state, a11y, performance (+ `frontend-<framework>`) |
| `ai-` | AI/LLM: prompting, RAG, evals, agents, context engineering |
| `database-` | persistence design (engine-agnostic): schema, indexing, migrations, transactions, query tuning |
| `security-` | hardening, authz, token/key handling, threat modeling |
| `infra-` | build / ship / run: CI/CD, deploy, observability, IaC |
| `product-` | discovery, spec, requirements |

The kit's own **base process skills** (`navigator`, `verify-fix-loop`, …) are exempt - they
are operating-system skills, not a discipline, so they keep bare names.

**Two more axes - language & framework.** Discipline groups above are language-agnostic;
tech-specific content gets its own prefix on a parallel axis, one prefix per pack:

- **Language**: `rust-`, `go-`, `python-`, `typescript-`, `java-` - idioms, naming, syntax.
- **Framework**: `svelte-`, `react-`, `vue-`, `django-` - that framework's APIs and patterns.
- **Engine** (database): `postgresql-`, `mysql-`, `mongodb-`, `redis-`, `sqlite-` - that engine's features and idioms.

They compose: a Rust + Tauri + Postgres service adds `engineering` + `backend` + `database`
+ `rust` + `tauri` + `postgresql`.

**Split rule.** A rule true in *every* language / engine -> a **discipline** skill
(`engineering-error-handling`, `database-schema-design`). *How a specific tech expresses it*
(an idiom, a feature, syntax, naming) -> a **language / framework / engine** skill
(`rust-error-handling`, `svelte-error-handling`, `postgresql-jsonb`). Cross-reference between
layers; never duplicate.

Body - principles, not a rigid template:

- **One skill = one job.**
- **Token-conscious** - every section must change the agent's behavior; if removing it
  wouldn't, cut it. Process over reference dumps, specific over general.
- **Imperative + the why.** Write steps as instructions ("Run X", "Verify Y") and give the
  reason, not a bare rule - the agent generalizes from *why* better than from rote MUST/NEVER.
- **Progressive disclosure (3 tiers).** Content loads at three times: **metadata** (name +
  description, *always* in the system prompt - keep it tiny), **instructions** (the `SKILL.md`
  body, loaded when the skill triggers - keep it tight, aim under ~250 lines), **resources**
  (`references/`, `scripts/`, loaded on demand - effectively unbounded). Move any section past
  ~100 lines into `references/<topic>.md` and link it; put a deterministic step in `scripts/`.
- **High-stakes skills** (a quality gate, a destructive op, a skip-prone multi-step process)
  earn a short `## Red Flags` (observable signs it is being violated) and/or
  `## Rationalizations` - a 2-column table `excuse -> why that's wrong`, with a rebuttal that
  bites (`"I'll add tests later" -> "the bug ships; later never comes"`). Low-stakes advisory
  skills omit both.

## Flow

1. **Audit.** Read the target skill(s) against the contract. List drift: `name` != dir, a
   missing or wrong **group prefix**, a vague description (no concrete trigger phrases, or it
   carries process steps), a bloated body, a >100-line section that should be a `references/`
   file, a high-stakes skill with no Red Flags. Report it - do not fix in audit.
2. **Plan + confirm.** For create / update, present the frontmatter + body outline, one
   line of reason each. **Wait for approval before writing.**
3. **Write.** Create or edit `.flexkit/skills/<id>/SKILL.md` to the contract. For update,
   make the smallest diff that closes the drift.
4. **Verify.** `flex-kit gen` + `flex-kit doctor` - the mechanical floor + that the host
   surfaces are in sync. Never hand-edit `.claude/skills/` or `.agents/skills/`.

## Rules

- The command owns format / prose; `doctor` owns the mechanical floor - delegate, don't duplicate.
- Conditional sections: don't add a Red Flags / Rationalizations block to a low-stakes
  skill - it is noise.
- Keep bodies tight - trust the agent, cut padding. Confirm the plan before writing.

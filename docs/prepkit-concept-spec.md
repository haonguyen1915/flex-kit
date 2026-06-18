# PrepKit Concept Spec (faithful, reverse-engineered)

> Blueprint for a faithful Python clone of prep-kit's **core** operating model.
>
> Every claim below traces to files under
> `/Users/haonv/workspace/Projects/Personal/TOOLS/prep-kit` (version 1.61.2),
> read on 2026-06-18. Items we could not confirm are marked **[?]**.

## Scope decisions (resolved 2026-06-18)

flex-kit clones the **concept/mechanism**, not prep-kit bug-for-bug. Resolved:

- **(B) Faithful concept, keep flex-kit's two improvements** — NOT a literal copy.
  1. **Convention-discovery** for "what exists" (scan the skills dir) instead of a
     hand-maintained manifest registry; per-capability metadata lives in each
     item's own frontmatter (`tier: router`), not a separate list. Eliminates the
     dual-source drift prep-kit must patch with its "unregistered surface" check.
  2. **Neutral source** (`.flexkit/`): source ≠ any host. Every host dir
     (`.claude/`, `.codex/`) is pure generated output. prep-kit instead authors in
     `.claude/skills/` (Claude doubles as source + surface), which the spec found
     genuinely tangled (§2, [?]).
- **Right-sized to stages 1-4** (§8). Build: manifest(convention) + capability
  model (skills + agents) → host surfaces → drift check → validate, plus a thin
  `gen`/`doctor` CLI.
- **OUT of the core clone (reference only, not implemented):**
  - **Plan lifecycle + plan/status/next-step/close CLI** (§7) — FlexTable already
    owns plans via `no_commit/draft-plans/` (`[backlog]`/`[done]`). Cloning would
    collide. Kept in §7 as reference.
  - **Hooks** (§4) — least portable; Codex has **no native hook system** (it natively
    loads *skills* from `.agents/skills/`, but exposes no event-hook contract). Defer
    until each host's hook contract is known.
  - Stages 5-6 of §8, and all DEFER items below.
- **DEFER (out):** packs, personas, learning flywheel, semantic-memory MCP,
  model-routing, trajectory.

---

## 0. The operating model in one picture

```
        AUTHORED                 BUILD                 GENERATED                RUNTIME
  .prepkit/kit.manifest.json  ──prepkit──▶  .claude/ (Claude surface)   ──hooks fire──▶ inject
  + content files             ──build───▶  .codex/ + .agents/ (Codex)   ──on events──▶ context
  (.prepkit/tools, .claude/                 + .prepkit/active.manifest    + guard +
   skills, agent-templates,                 + generated docs/indexes        validate
   commands, workflows)                     + .prepkit/generated-digests
```

Three legs:
1. **Manifest + build** — one source of truth, generate every host surface, never hand-edit generated (digest-enforced). → §1, §3, §6
2. **Files = durable state** — plans/, docs/, knowledge/, session-state/. → §4, §7
3. **Hooks = active bridge** — inject the right slice of state at each event. → §4

A faithful core clone must reproduce legs 1+2 fully; leg 3 (hooks) is host-specific and is the hardest to port (see §4, §8).

---

## 1. Manifest schema

### 1.1 The three manifest files

| File | Role | Source/Generated |
|---|---|---|
| `.prepkit/kit.manifest.json` | **Authored source of truth** (1341 lines) | hand-authored |
| `.prepkit/active.manifest.json` | **Resolved** manifest = core + selected packs, written by `composeManifest()` at build | generated |
| `.prepkit/resolved.manifest.json` | **NOT used** — no script reads/writes it. Ignore. | n/a |

Composition: `build-kit.mjs` → `composeManifest({coreManifestPath, packNames, preset})` (`.prepkit/scripts/lib/manifest-composer.mjs:380`) merges core + each `.prepkit/packs/<name>/pack.manifest.json` via `mergeIdList()` (capabilities/agents/commands/workflows) and `mergeHooks()` (dedupe by `(matcher,command)`), writes `active.manifest.json`. Runtime reads the active one (`manifest-paths.cjs:resolveRuntimeManifestPath`).

### 1.2 Top-level keys (32)

Required (build fails if absent — `manifest-validator.mjs:40`): `name, version, settings, documentation, validation, paths, plan, delivery, context, runtimePolicy, optionalAdapters, guardrails, agents, commands, workflows, hooks`.

| Key | Type | Purpose (core-clone relevance) |
|---|---|---|
| `name`/`displayName`/`version`/`description` | str | identity |
| **`paths`** | obj | 20 path mappings: `docs`, `plans`, `activePlans:"plans/active"`, `archivedPlans:"plans/archive"`, `knowledgeBase`, … **(CORE)** |
| **`capabilities`** | obj | `{toolAdapters:[], skills:{domain:[],process:[]}}` **(CORE)** → §2 |
| **`agents`** | arr | `{id,path,sourcePath,lane,contextPrefix?}` **(CORE)** → §2 |
| **`commands`** | arr | `{id,path,tier,nextSteps?,sideEffects?}` **(CORE)** → §2 |
| **`workflows`** | arr | `{id,path}` **(CORE)** → §2 |
| **`hooks`** | obj | event → `[{matcher,command}]` **(CORE)** → §4 |
| **`validation`** | obj | plan/spec heading + metadata rules **(CORE)** → §5 |
| **`organization`** | obj | docs/plans dir structure, archive grouping **(CORE)** |
| **`delivery`** | obj | modes (patch/build/design), intents, routing, checkpoints **(CORE)** |
| `settings` | obj | `{includeCoAuthoredBy:false}` |
| `claude` | obj | `{commandScope:"core-only"\|"selected-packs"\|"all"}` |
| `codex` | obj | `{skillScope:"core-only"\|"routers"\|"selected-packs"\|"all"}` |
| `runtimePolicy` | obj | `primaryHost`, `branchFreshness`, `events`, per-host reminder policy |
| `context` | obj | token budgets (`mainBudgetTokens:1600`, `subagentBudgetTokens:400`, advisory) |
| `guardrails` | obj | `blockedPaths`, `sensitivePatterns`, `longRunningPatterns` |
| `composition` | obj | **generated** at build (selectedPacks, packAliases, autoIncludeRules…) |
| `hookProfiles` | obj | tiers minimal/standard/strict + `envVar:"PREP_HOOK_PROFILE"` |
| `modelProfiles`/`defaultModelProfile`/`modelRouting` | — | model assignment (DEFER) |
| `personas`/`planPresets`/`outputStyles` | — | DEFER (pack/persona layer) |
| `optionalAdapters`/`trajectory`/`memory`/`proposeLessons` | — | DEFER |
| `documentation` | obj | `{maxLoc:600}` |

### 1.3 Capability entry shapes (real)

```jsonc
// capabilities.toolAdapters[]
{ "id": "workspace-files", "path": ".prepkit/tools/workspace-files.md", "kind": "local-tool" }
// capabilities.skills.domain[]
{ "id": "kit-architecture", "path": ".claude/skills/domain/kit-architecture/SKILL.md" }
// capabilities.skills.process[]   (tier optional)
{ "id": "context-collection", "path": ".claude/skills/process/context-collection/SKILL.md", "tier": "router" }
// agents[]
{ "id": "planner", "path": ".claude/agents/planner.md",
  "sourcePath": ".claude/agent-templates/planner.md", "lane": "build", "contextPrefix": "…" }
// commands[]
{ "id": "prep-plan", "path": ".claude/commands/prep-plan.md", "tier": "essential",
  "nextSteps": [{"command":"prep-implement","label":"start implementation"}],
  "sideEffects": ["git-commit"] }
// workflows[]
{ "id": "primary-workflow", "path": ".claude/workflows/primary-workflow.md" }
// hooks
"SessionStart": [{ "matcher":"startup|resume|clear|compact", "command":"node .claude/hooks/session-init.cjs" }]
```

---

## 2. Capability taxonomy

Six declared types. **Key distinction**: most types are authored-in-place (the manifest `path` IS the source); only **agents** have a separate template→generated split.

| Type | Declared in | Source content | Generated surface | Distinguishing metadata |
|---|---|---|---|---|
| **Tool adapter** | `capabilities.toolAdapters[]` | `.prepkit/tools/<id>.md` (markdown reference card, ~13 lines) | listed in `capabilities.json` | `kind` = local-tool/external-tool/internal-tool. Passive (no activation). |
| **Domain skill** | `capabilities.skills.domain[]` | `.claude/skills/domain/<id>/SKILL.md` (+`references/`) | symlinked into Codex `.agents/skills/` | frontmatter `triggers[]`, `globs[]`; subject expertise |
| **Process skill** | `capabilities.skills.process[]` | `.claude/skills/process/<id>/SKILL.md` | same | `tier:"router"` = runtime-priority |
| **Agent** | `agents[]` | **template** `.claude/agent-templates/<id>.md` | `.claude/agents/<id>.md` (Claude) + `.codex/agents/<id>.toml` (Codex) | `lane` build/research/review; `contextPrefix`; `<!-- SKILLS -->` placeholder injected at build |
| **Command** | `commands[]` | `.claude/commands/<id>.md` (prose, frontmatter `description`,`argument-hint`) | symlinked/scoped per host | `tier` essential/secondary/advanced; `nextSteps[]`; `sideEffects[]` |
| **Workflow** | `workflows[]` | `.claude/workflows/<id>.md` (prose playbook) | referenced | none (pure descriptive flow) |

Notes:
- Skill SKILL.md frontmatter (core): `name`, `description`, domain adds `triggers[]`. Body sections validated: `## Gotchas` (≥3 bullets), ≤500 lines, kebab `name` == folder.
- Commands/workflows are **prose instruction sets**, not code — read by the model, not executed.
- For the clone, the **skill** type is the MVP (what flex-kit v0 already does). Agents (template→2 outputs) are the next type.

---

## 3. Build pipeline (`prepkit build` → `.prepkit/scripts/build-kit.mjs:main`)

### 3.1 Ordered steps (distilled)
1. **Resolve** manifest (core, or `composeManifest()` if packs).
2. **Freshness gate** `canSkipBuild()` — compare current disk digests vs `.prepkit/generated-digests.json`; skip if unchanged.
3. **Scaffold** dirs from `paths.*`.
4. **Core JSON**: `.claude/settings.json` (hooks), `.claude/.prep.json` (delivery/routing), `.claude/metadata.json`, `.claude/capabilities.json`, `.prepkit/active.manifest.json`, `.prepkit/generated/hook-runtime.json` (compact hot-path projection).
5. **Docs/indexes** (each carries a "Generated … do not edit" marker): `capability-index.md`, `organization-policy.md`, `knowledge/INDEX.md`, `docs/INDEX.md`, `plans/INDEX.md`, Codex `codex-catalog.md`.
6. **Entry surfaces**: `CLAUDE.md`, `AGENTS.md`.
7. **Validate** (hook targets exist, skill files exist, agent templates exist) — hard exit on failure.
8. **Generate agents**: render `.claude/agents/<id>.md` from templates (resolve `model`, inject skill catalog into `<!-- SKILLS -->`); render `.codex/agents/<id>.toml` (Codex-normalized model + `sandbox_mode`).
9. **Symlinks**: Codex skills → `.agents/skills/<id>` (flat); pack skills/commands → `.claude/`.
10. **Command index** `.prepkit/generated/command-index.json`.
11. **Fingerprint + digests**: write `.prepkit/.build-fingerprint` (SHA of manifest+packs+hook files) and `.prepkit/generated-digests.json` (MD5 per generated file, volatile timestamps stripped).

### 3.2 Per-host transforms
- **Claude**: agents get `model:` frontmatter + skill catalog; skills/commands placed under `.claude/skills/{domain,process}/` and `.claude/commands/`.
- **Codex**: skills filtered by `codex.skillScope` then symlinked **flat** into `.agents/skills/` (NOT nested by category); agents emitted as `.codex/agents/<id>.toml` with `developer_instructions`, `model` (normalized e.g. opus→gpt-5.x), `sandbox_mode`, `model_reasoning_effort`. `AGENTS.md` is the entry doc.

### 3.3 Drift protection (the "never hand-edit generated" mechanism)
- `.prepkit/generated-digests.json` = `{ "<path>": "<md5>", …, "_inputFingerprint": "<sha>" }`.
- Validate/doctor recompute digests: input-fingerprint changed → rebuild needed; fingerprint same but a file's hash differs → **hand-edit violation**.
- Enforcement is **post-hoc advisory** (markers + validation), not write-protection.

> **Clone takeaway**: the digest+fingerprint pair is the faithful drift mechanism. flex-kit's `generated-in-sync` check already does the equivalent (re-render and compare) — a simpler, equally faithful variant.

---

## 4. Hooks (runtime injection)

### 4.1 Events → dispatch
prep-kit wires ~10 events; most route to a **single dispatch hub** that runs many sub-hooks in-process (perf: one node spawn).

| Event | Dispatch hub | Notable sub-hooks |
|---|---|---|
| SessionStart (`startup\|resume\|clear\|compact`) | `session-init.cjs` (+`pre-compact-snapshot.cjs` on `compact`) | auto-build, plan/branch context, env injection |
| UserPromptSubmit | `user-prompt-dispatch.cjs` | `dev-rules-reminder` (plan status block, cheap dedup), learning |
| PreToolUse (`Bash\|…\|Write`) | `pre-tool-dispatch.cjs` | `pre-tool-guard` (privacy/secret BLOCK), naming, commit-quality, secret-detection |
| PostToolUse | `post-tool-dispatch.cjs` | plan-status-guard, post-edit-nudge, usage-awareness, permission-denied |
| Stop | `stop-dispatch.cjs` | session-state-persist, format/typecheck, capture |
| SubagentStart | `subagent-init.cjs` | scoped context (goal, in-scope files, budget-fit) |
| FileChanged/Worktree*/CwdChanged | `lifecycle-observer.cjs` | advisory rebuild nudge (<100ms) |

### 4.2 The critical 6 (80% of semantics)
- **session-init** — at session start: detect stale build (fingerprint) → auto-build; emit a contract block (branch, active plan, mode, next step); restore compact snapshot; write `PREP_*` env vars.
- **dev-rules-reminder** — every prompt: a compact plan-status reminder; **cheap dedup** via a hash of (git HEAD, plan.md mtime, manifest mtime, …) → returns nothing when unchanged.
- **pre-tool-guard** — before tools: BLOCK access to secrets/prod env, BLOCK self-approval; advise on long-running cmds.
- **pre-compact-snapshot** — before compaction: write `.prepkit/session-state/compact-snapshot.json` so orientation survives.
- **subagent-init** — inject a *smaller* scoped context to subagents (budget ~400 tokens).
- **dispatch hubs** — aggregate sub-hooks, cap output (e.g. PostToolUse ≤3 msgs/600 chars).

### 4.3 State + profiles
- Durable state: `.prepkit/session-state/<id>.json` (snapshot, approvals, dedup hashes), `.prepkit/kit-state.json` (stack, persona, onboarding), `plans/active/<id>/plan.md`.
- Hook profiles (cumulative): `minimal ⊂ standard(default) ⊂ strict`; selected by `PREP_HOOK_PROFILE` > persona > manifest default. Disable via `PREP_DISABLED_HOOKS` env or `.prepkit/hook-overrides.json {disabled:[…]}`. Core hooks (session-init, dev-rules-reminder, pre-tool-guard, subagent-init) are non-toggleable.

> **Clone caveat**: Claude Code hooks are `.cjs` invoked by the host. Codex's hook model differs. A Python clone's hooks must target whatever each host's hook contract is — this is the **least portable** leg and should be staged last (see §8).

---

## 5. Validation (`prepkit validate` → `.prepkit/scripts/validate-kit.mjs`)

Comprehensive consistency checker. ~80 checks; categories:

| Category | Examples | Severity |
|---|---|---|
| Manifest structure | required keys present; valid JSON; no duplicate ids (adapters/skills/agents/commands/workflows/modes) | error → exit 1 |
| Entry files exist | every capability/agent/command/workflow `path` exists on disk | error |
| Skill contract | `## Gotchas` ≥3 bullets; ≤500 lines; kebab `name`==folder; description 20..MAX chars; domain `triggers[]`≥4 | error |
| References resolve | `(references|assets|scripts)/…` paths in bodies exist; knowledge links exist | error |
| Plan/spec structure | `requiredPlanMetadata`, `allowedPlanStatusValues`, per-mode `planHeadings`, `specTaskChecklist` | error |
| Hook wiring | every hook command target file exists; PostToolUse matcher matches registry | error |
| Generated freshness | digest vs `generated-digests.json`; input fingerprint | error |
| Runtime surfaces | expected symlinks present + correct target; no stray host entries; context-surface budgets | error (budget configurable to warn) |
| Quality | knowledge metadata schema, complexity-threshold breach, plan ownership overlap | warning → exit 0 |

Output: human (`- error` / `⚠ warn`) or `--json` (`{ok,errorCount,warningCount,errors,warnings}`). Exit 1 on any error; warnings never block. `prepkit doctor` = lighter runtime-health subset (pass/warn/fail), always exit 0 ("orientation must survive failure").

---

## 6. Generated surfaces (exact layout)

### Claude (`.claude/`)
```
.claude/
  settings.json        # hooks wiring (event→{matcher,command}) + statusLine
  .prep.json           # delivery modes, routing, paths, context budgets
  metadata.json        # name, version, selectedPacks, resolvedFrom
  capabilities.json    # toolAdapters[], domainSkills[], processSkills[]
  commands/<id>.md     # frontmatter: description, argument-hint
  skills/domain/<id>/SKILL.md     # frontmatter: name, description, triggers[]
  skills/process/<id>/SKILL.md    # frontmatter: name, description (tier in manifest)
  agents/<id>.md       # generated from template; frontmatter incl. model
  agent-templates/<id>.md         # SOURCE for agents (has <!-- SKILLS -->)
  hooks/*.cjs          # runtime scripts (+ hooks/lib/)
  workflows/<id>.md  rules/*.md
```

### Codex (`.codex/` + `.agents/`)
```
.agents/skills/<id>/SKILL.md   # CODEX-NATIVE skill location (frontmatter: name, description)
.agents/skills/<id>/{references,scripts,assets}/   # optional, copied verbatim
.agents/skills/<id>/agents/openai.yaml             # optional: invocation policy
.codex/agents/<id>.toml        # subagents (separate from skills)
AGENTS.md                      # short entry doc (optional human-facing catalog)
```
**Authoritative (https://developers.openai.com/codex/skills, 2026-06-18)**: Codex
**natively discovers skills** by scanning, in order: `$CWD/.agents/skills`,
`$REPO_ROOT/.agents/skills`, `$HOME/.agents/skills`, `/etc/codex/skills`, plus bundled.
SKILL.md frontmatter = `name` + `description` (description drives implicit triggering —
"explain exactly when this skill should and should not trigger"). Invoke explicitly via
`/skills` or `$skill-name`, or implicitly by description match. (The `codex` CLI help omits
skills because discovery is a runtime/model feature, not a subcommand — this misled an
earlier draft.)

**flex-kit decision (final)**: codex host `BASE_DIR = .agents/skills/` (Codex-native; a
`.codex/skills/` dir is NOT scanned and is invisible to Codex). SKILL.md format already
matches (name + description) — no block scalar required (that was hand-styling). The user's
current `.codex/skills/` must migrate to `.agents/skills/` at cutover.

### Shared generated docs
`.prepkit/active.manifest.json`, `.prepkit/generated/{hook-runtime,command-index}.json`,
`.prepkit/docs/reference/{capability-index,organization-policy,codex-catalog}.md`,
`docs/INDEX.md`, `plans/INDEX.md`, `.prepkit/docs/reference/knowledge/INDEX.md`,
`.prepkit/generated-digests.json`, `.prepkit/.build-fingerprint`.

> **Same skill, two hosts**: body identical; only frontmatter format + file location differ. (This is exactly the flex-kit v0 transform — confirmed faithful, except flex-kit currently targets `.codex/skills/` instead of `.agents/skills/`.)

---

## 7. CLI

Dual surface: **(canonical)** `prepkit-cli.mjs` subcommands (host-agnostic, used by Codex/terminal) and **(wrapper)** `.claude/commands/*.md` slash commands (Claude UI grammar over the CLI).

### 7.1 prepkit-cli subcommands (core set)
| cmd | effect |
|---|---|
| `build` | resolve+generate all surfaces |
| `validate` | §5 checks |
| `doctor` | runtime-health subset, exit 0 |
| `plan <title> [--mode][--focus]` | scaffold `plans/active/<date>-<slug>/{plan.md,decisions.md}` + bind active |
| `next-step` / `status` | compute current state from active plan + session-state |
| `bind <plan>` | set active plan for session |
| `init-spec` | scaffold `spec/{proposal,design,tasks}.md` |
| `close [--confirm][--reopen]` | validate → archive `plans/active`→`plans/archive/<bucket>` |
| `capture-lesson <text>` | write to knowledge base |
| `setup`/`new`/`init` | scaffold prep-kit into a project |

### 7.2 Plan lifecycle state machine
```
CREATED ──plan──▶ ACTIVE(plans/active/)
  ├─ design? ──change/init-spec──▶ spec/{proposal,design,tasks} ──approve──▶ IMPLEMENT
  └─ IMPLEMENT ──implement [--full]──▶ decisions.md, tasks ticked
       └─▶ REVIEWED ──close──▶ CLOSE_PREPARED ──close --confirm──▶ ARCHIVED(plans/archive/)
                                   └─ close --reopen ──▶ back to ACTIVE
```
State sources: `PREP_*` env (injected by hooks) + `.prepkit/session-state/<id>` + `plans/active/<id>/{plan.md,spec/tasks.md}`. Mode auto-escalates patch→build→design when complexity thresholds (steps>15, phases>4) trip.

### 7.3 Slash↔CLI mapping
1:1 delegates (`/prep-plan`↔`plan`, `/prep-status`↔`status`, `/prep-close`↔`close`, `/prep-doctor`↔`doctor`); hybrid (`/prep-implement` uses CLI for context + runtime agent for execution); skill-only (`/prep-learn`, `/prep-brainstorm` — no CLI). Slash frontmatter: `description`, `argument-hint`. The CLI is canonical.

---

## 8. What a faithful CORE clone must implement (build order)

Right-sized to flex-kit's real problem (2-host capability drift). **Stages 1-4 = IN**;
stages 5-6 = reference only (see Scope decisions). Each stage runnable + faithful, none
speculative:

1. **Capability model (convention-discovered)** — discover skills + agents from
   `.flexkit/`; metadata in each item's frontmatter (no separate registry). Real entry
   semantics per §2. **[IN]**
2. **Build → generated surfaces** — source → `.claude/skills/` + `.codex/skills/`
   (skills); `.claude/agents/<id>.md` + `.codex/agents/<id>.toml` (agents, one source →
   two host forms); + managed skills-catalog block in `AGENTS.md`. Per-host transforms
   (§3.2, §6). **[IN]**
3. **Drift check** — flex-kit's `generated-in-sync` (re-render + compare) ≈ prep-kit's
   digest mechanism, simpler + faithful (§3.3). **[IN]**
4. **Validate** — structural + skill-contract checks (`## Gotchas` ≥3, description length,
   domain `triggers[]`, refs resolve) (§5). **[IN]**
5. **CLI plan lifecycle** (`plan`/`status`/`next-step`/`close` + `active`→`archive`) — **[OUT]**
   FlexTable owns plans. flex-kit CLI stays `gen`/`doctor` only.
6. **Hooks** — **[OUT]** host-specific; Codex has no native hook loader. Defer.

### Relationship to flex-kit v0 (already built)
flex-kit v0 = a correct **subset** of stages 1-4 for the **skill** type only (neutral source → 2 hosts, `generated-in-sync` ≈ digest check). To make it a faithful core clone: generalize the manifest/capability model (add agents, commands, workflows, tool adapters), add the Codex `.agents/skills/` target (one-line `BASE_DIR` fix — v0 currently uses `.codex/skills/`), then layer build-of-non-skill-types, validate, CLI, hooks.

---

## 9. Flagged uncertainties [?]
- `resolved.manifest.json` appears unused (only `active.manifest.json` is read/written).
- `.prepkit/skills/process/` exists alongside `.claude/skills/process/` — relationship unclear (possibly dev scratch / pack authoring). Manifest skill `path`s point at `.claude/skills/...`.
- Exact `skill-eval-suite.mjs` contract, `build-fingerprint.cjs` hash algorithm, and `verifySharedReferences()` marker syntax live in modules not fully read.
- Codex `.toml` field semantics (`sandbox_mode`, `model_reasoning_effort`) vs runtime effect not documented.
- Hook execution semantics on non-Claude hosts (Codex/Gemini/Antigravity) — prep-kit references them but the per-host hook contract was not fully traced.

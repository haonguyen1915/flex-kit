# flex-kit workflows

One file per automated flow. Each explains: how it **starts**, **who** does the work
(CLI / host agent / subagent / hook), how it **navigates**, what **state/memory** it
reads and writes, how it **loops back**, and how **review** (and any external/Codex
review) is invoked.

| Workflow | Trigger | Kind |
|---|---|---|
| [delivery](delivery.md) | `/flex-implement` | one-command multi-agent loop |
| [design-first](design-first.md) | `/flex-change` + `flex-kit spec` | spec-then-build |
| [review](review.md) | `/flex-review` | standalone review (host subagent) |
| [codex-review](codex-review.md) | `/flex-codex-review` | cross-model review (Codex CLI) |
| [plan-lifecycle](plan-lifecycle.md) | `flex-kit plan/status/next-step/close` | stateful CLI |
| [hooks-runtime](hooks-runtime.md) | host events (automatic) | passive runtime |
| [build-sync](build-sync.md) | `flex-kit gen` / `doctor` | content build |

## The one rule behind every flow

> flex-kit is **build-time**; the **host** (Claude Code) is **run-time**. flex-kit
> generates the material - skills, agents, commands, the hook wiring - and the host
> *runs* it using its native subagents and prose execution. There is no flex-kit
> orchestration engine: a "workflow" is a protocol (a command/skill the agent
> follows) plus state files, executed by the host.

### Who does what

| Actor | What it is | How it runs |
|---|---|---|
| **CLI** (`flex-kit ...`) | Python binary | you (or an agent's Bash call) run it in a terminal |
| **Slash command** (`/flex-*`) | generated `.claude/commands/<id>.md` prose | the main host agent follows it |
| **Subagent** (`implementer`/`reviewer`/`tester`) | generated `.claude/agents/<id>.md` | the host spawns it via its Task tool |
| **Hook** (`flex-kit hook <event>`) | CLI subcommand | the host fires it on an event (settings.json) |

### How subagents communicate: files, not messages

Subagents never talk directly. They hand off through files under the active plan's
`handoffs/` directory:

- `handoffs/review-input.md` - the caller writes the scope for the verifiers.
- `handoffs/review-verdict.md` - the `reviewer` writes its verdict.
- `handoffs/test-report.md` - the `tester` writes pass/fail.

The reviewer's verdict is authoritative; the loop reads these files to decide.

### Codex / external review

There are two kinds of review:

- **Same-host review** - the `reviewer` subagent spawned by the host (Claude Code's
  Task tool). Used by the [delivery](delivery.md) and [review](review.md) flows.
- **Cross-model review** - [`/flex-codex-review`](codex-review.md) shells out to the
  Codex CLI (`codex exec`) for an independent second opinion from a *different* model,
  saved as a report. Faithful to prep-kit's `/prep-codex-review`.

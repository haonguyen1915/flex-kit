# Workflow: hooks runtime (automatic)

The passive layer that keeps the agent oriented and guarded **without you asking**.
These are the only flows you never trigger - the host fires them on events.

## How it starts

The claude host's `emit_global()` writes `.claude/settings.json` wiring three events
to `flex-kit hook <event>`. When Claude Code hits an event it runs that subcommand,
passing a JSON payload on stdin.

| Event | Command | Matcher |
|---|---|---|
| SessionStart | `flex-kit hook session-start` | `startup\|resume\|clear\|compact` |
| UserPromptSubmit | `flex-kit hook user-prompt` | (all) |
| PreToolUse | `flex-kit hook pre-tool` | `Bash\|Read\|Edit\|Write\|Glob\|Grep` |

## Who does the work

The **`flex-kit` CLI** (the `hook` subcommand, logic in `hooks.py`). No agent, no
subagent - just the binary reading state and printing context or a decision. **This
requires `flex-kit` to be on the host's PATH** (`pipx install`, or symlink).

## Flow - per event

**session-start** (orient + survive compaction)
```
host fires on open / resume / after compaction
 -> read git branch + .flexkit/state.json (active plan) + plan.md (steps, mode)
 -> print "flex-kit: branch X; plan Y (build, 1/3 steps); next: Z"
 -> Claude Code injects stdout into the session context
```
Because it also matches `compact`, orientation is rebuilt from durable files after a
compaction - no separate snapshot is needed.

**user-prompt** (deduped plan reminder)
```
host fires on every prompt you send
 -> compute signature: plan id | effective mode | done/total | next step
 -> compare to last_reminder in .flexkit/state.json
 -> changed?  print the reminder + record the new signature
    unchanged? print nothing (dedup, so it fires only when progress advances)
```

**pre-tool** (secret guard)
```
host fires before Bash/Read/Edit/Write/...
 -> read tool_input from the stdin payload
 -> match a secret/credential regex (.env / *.key / credentials / prod-secrets / id_*)
 -> match -> print a deny JSON  (host blocks the call)
    no match -> print nothing  (allowed)
```

## Navigation / routing

There is no routing - each event maps to exactly one hook. The matcher in
settings.json decides which tool calls / session sources the hook runs for.

## State / memory

| File | Read | Written |
|---|---|---|
| `.flexkit/state.json` | active plan, `last_reminder` | `last_reminder` (by user-prompt) |
| `plans/active/<id>/plan.md` | steps, mode, progress | - |
| git | current branch | - |

The hooks are the **active bridge**: they turn the durable plan files into context the
agent sees automatically, every turn.

## Loop-back

None - hooks are fire-and-forget per event. The "loop" they enable is implicit: each
new session/prompt re-reads the latest state, so the agent is always re-oriented to
current reality rather than stale chat memory.

## Review / Codex

Not applicable. Hooks don't review; the pre-tool guard is the only one that *blocks*
(secret access), and it does so by output decision, not by a subagent.

#!/usr/bin/env bash
# Reproducible flex-kit demo: 7 scenarios, real CLI, real output.
#
#   ./demo/run.sh
#
# Rebuilds demo/sandbox/proj from scratch each run. Requires `flex-kit` on PATH
# (`make install` or `pipx install .`). `codex` CLI is NOT required - the
# cross-model review runs in --dry-run mode.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
P="$ROOT/demo/sandbox/proj"
hr() { printf '\n\033[1m############## %s\033[0m\n' "$*"; }

rm -rf "$P" && mkdir -p "$P"

hr "SCENARIO 1 — init: one neutral source -> two host surfaces"
flex-kit init -p "$P"
echo "--- SOURCE (.flexkit, the only thing you author) ---"
( cd "$P" && find .flexkit -type f | sort )
echo "--- GENERATED Claude surface (.claude) ---"
( cd "$P" && find .claude -type f | sort )
echo "--- GENERATED Codex surface (.agents + .codex) ---"
( cd "$P" && find .agents .codex -type f | sort )

hr "SCENARIO 2 — same source, two host dialects + the drift guard"
echo "--- Claude agent: .md, markdown kept, model alias passed through ---"
sed -n '1,4p' "$P/.claude/agents/reviewer.md"
echo "--- SAME source as Codex .toml: model opus -> gpt-5.5 ---"
sed -n '1,4p' "$P/.codex/agents/reviewer.toml"
echo "--- doctor: clean ---"
flex-kit doctor -p "$P"
echo "--- hand-edit a GENERATED file, doctor catches it ---"
printf '\n<!-- sneaky hand edit -->\n' >> "$P/.claude/agents/reviewer.md"
flex-kit doctor -p "$P" || true
echo "--- re-gen from source fixes it ---"
flex-kit gen -p "$P" >/dev/null && flex-kit doctor -p "$P" | tail -1

hr "SCENARIO 3 — plan lifecycle: plan / status / next-step / close"
flex-kit plan "Add OAuth login" --mode build -p "$P"
PLANMD="$(ls "$P"/plans/active/*add-oauth*/plan.md)"
python3 - "$PLANMD" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); t = p.read_text()
t = t.replace("## Steps\n\n- [ ] first step\n",
              "## Steps\n\n- [x] design schema\n- [ ] add /auth routes\n- [ ] wire session cookie\n")
p.write_text(t)
PY
flex-kit status -p "$P"
echo "next-step ->"; flex-kit next-step -p "$P"
echo "close without --confirm (guarded) ->"; flex-kit close -p "$P"

hr "SCENARIO 4 — mode escalation: scope can't balloon silently"
flex-kit plan "Tiny typo fix" --mode patch -p "$P" >/dev/null
PLANMD="$(ls -t "$P"/plans/active/*tiny-typo*/plan.md | head -1)"
python3 - "$PLANMD" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); t = p.read_text()
t = t.replace("## Steps\n\n- [ ] first step\n", "## Steps\n\n- [ ] s1\n- [ ] s2\n- [ ] s3\n- [ ] s4\n- [ ] s5\n")
p.write_text(t)
PY
echo "declared patch, but 5 steps > patch budget (3) -> status surfaces the escalation:"
flex-kit status -p "$P"

hr "SCENARIO 5 — hooks runtime (what the host fires automatically)"
echo "5a session-start (orientation injected at session open):"
flex-kit hook session-start -p "$P"
echo "5b pre-tool secret guard — deny .env.production:"
echo '{"tool_input":{"file_path":".env.production"}}' | flex-kit hook pre-tool -p "$P"
echo "    normal file (blank line = allowed):"
echo '{"tool_input":{"file_path":"src/app.py"}}' | flex-kit hook pre-tool -p "$P"
echo "5c codex-review --dry-run (prints the codex exec command, runs nothing):"
flex-kit codex-review --dry-run -p "$P"

hr "SCENARIO 6 — add: opt-in domain pack (domain is NOT in base)"
flex-kit add -p "$P"            # list packs
flex-kit add api-design -p "$P"

hr "SCENARIO 7 — design-first: spec scaffold before code"
flex-kit plan "Redesign billing API" --mode design -p "$P" >/dev/null
flex-kit spec -p "$P"
PLANDIR="$(ls -td "$P"/plans/active/*redesign* | head -1)"
find "$PLANDIR" -type f | sort

hr "DONE — explore the generated project at demo/sandbox/proj"

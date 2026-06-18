# Solution Design

Before committing to an approach, compare alternatives.

1. Generate 2-3 alternatives for the core decision.
2. Compare them:

| Dimension | A | B | C |
|---|---|---|---|
| Complexity | moving parts? | | |
| Risk | what could go wrong? | | |
| Reversibility | how easy to undo? | | |
| Time | rough step count | | |
| Maintenance | ongoing burden | | |

3. Pick one with explicit rationale.
4. Record the rejected alternatives in the plan's `decisions.md`.

**Use** when the plan affects architecture (new systems, data flows, contracts), two or
more plausible approaches exist, or the choice is hard to reverse after implementation
starts. **Skip** when the approach is obvious and low-risk, or only one option is viable.

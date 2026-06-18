---
name: flex-status
description: Show the active plan, its effective mode, and the next step. Use to re-orient on where the work stands.
---

Run `flex-kit status` and report where the work stands: the active plan, step
progress, and the next step. If `flex-kit status` shows the mode escalated (e.g.
`patch -> build`), surface that. If there is no active plan, suggest
`/flex-plan "<task>"` to start one.

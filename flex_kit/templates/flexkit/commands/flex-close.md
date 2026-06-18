---
name: flex-close
description: Archive the active plan once its steps are complete. Use to finish a piece of work.
---

1. Run `flex-kit status` and confirm every step is `- [x]`.
2. If complete, run `flex-kit close --confirm` to move the plan to `plans/archive/`.
3. If steps remain, list the incomplete ones and do **not** close - finish or
   `/flex-implement` them first.

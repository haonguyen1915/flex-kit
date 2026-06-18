# Các workflow của flex-kit

Mỗi flow tự động một file. Mỗi file giải thích: **bắt đầu** thế nào, **ai** làm
(CLI / agent host / subagent / hook), **điều hướng** ra sao, đọc/ghi **state-memory**
gì, **loop-back** thế nào, và **review** (kể cả review cross-model/Codex) gọi qua đâu.

## Thứ tự đọc

Bảng xếp **foundation → advanced** - đọc từ trên xuống. Mỗi flow dựa trên các flow
phía trên: nền build trước, rồi state bền nó sinh ra, runtime phơi state đó, primitive
review, và cuối cùng là các vòng đầy đủ ghép tất cả lại.

| # | Workflow | Trigger | Loại | Dựa trên |
|---|---|---|---|---|
| 1 | [build-sync](1-build-sync.md) | `flex-kit gen` / `doctor` | build nội dung | - (nền) |
| 2 | [plan-lifecycle](2-plan-lifecycle.md) | `flex-kit plan/status/next-step/close` | CLI có state | 1 |
| 3 | [hooks-runtime](3-hooks-runtime.md) | sự kiện host (tự động) | runtime thụ động | 1, 2 |
| 4 | [review](4-review.md) | `/flex-review` | review độc lập (subagent host) | 1 |
| 5 | [codex-review](5-codex-review.md) | `/flex-codex-review` | review cross-model (Codex CLI) | 4 |
| 6 | [delivery](6-delivery.md) | `/flex-implement` | vòng multi-agent một lệnh | 2, 3, 4 |
| 7 | [design-first](7-design-first.md) | `/flex-change` + `flex-kit spec` | spec-rồi-build | 6 |

Vội? Đọc **1 → 2 → 6**; đó là xương sống (build surface, track việc, chạy delivery
loop). Phần còn lại lấp runtime, review, và đường spec-first.

## Một nguyên tắc xuyên suốt mọi flow

> flex-kit là **build-time**; **host** (Claude Code) là **run-time**. flex-kit sinh ra
> material - skills, agents, commands, wiring của hook - và host *chạy* nó bằng
> subagent native + thực thi prose. **Không có engine orchestration trong flex-kit**:
> một "workflow" = một protocol (command/skill mà agent đi theo) + file state, do host
> thực thi.

### Ai làm gì

| Actor | Là gì | Chạy thế nào |
|---|---|---|
| **CLI** (`flex-kit ...`) | binary Python | bạn (hoặc Bash của agent) gõ trong terminal |
| **Slash command** (`/flex-*`) | prose generated `.claude/commands/<id>.md` | agent host chính đọc và đi theo |
| **Subagent** (`implementer`/`reviewer`/`tester`) | generated `.claude/agents/<id>.md` | host spawn qua Task tool |
| **Hook** (`flex-kit hook <event>`) | subcommand CLI | host bắn khi có sự kiện (settings.json) |

### Subagent trao đổi: qua FILE, không phải message

Subagent **không nói chuyện trực tiếp**. Chúng handoff qua file trong thư mục
`handoffs/` của plan đang active:

- `handoffs/review-input.md` - caller ghi phạm vi cho verifier.
- `handoffs/review-verdict.md` - `reviewer` ghi verdict.
- `handoffs/test-report.md` - `tester` ghi pass/fail.

Verdict của reviewer là authoritative; loop đọc các file này để quyết định.

### Codex / review bên ngoài

Có 2 kiểu review:

- **Same-host review** - subagent `reviewer` do host spawn (Task tool của Claude
  Code). Dùng bởi flow [delivery](6-delivery.md) và [review](4-review.md).
- **Cross-model review** - [`/flex-codex-review`](5-codex-review.md) shell ra Codex CLI
  (`codex exec`) lấy ý kiến độc lập từ một **model khác**, lưu thành report. Faithful
  với `/prep-codex-review` của prep-kit.

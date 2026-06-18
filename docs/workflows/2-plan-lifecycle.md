# Workflow: plan lifecycle (`flex-kit plan` / `status` / `next-step` / `close`)

> Thứ tự đọc **2 / 7** · trước: [build-sync](1-build-sync.md) · sau: [hooks-runtime](3-hooks-runtime.md)

Xương sống bền mà mọi flow khác đọc vào. Một plan là state công việc nhiều bước, sống
sót qua reset context.

## Bắt đầu thế nào

Hai cách gọi cho cùng một việc:

| CLI (bạn gõ ở terminal) | Slash (agent trong host) | Làm gì |
|---|---|---|
| `flex-kit plan "<task>" [--mode]` | `/flex-plan` | tạo + activate plan |
| `flex-kit status` | `/flex-status` | hiện tiến độ + effective mode |
| `flex-kit next-step` | `/flex-next-step` | hiện step chưa xong kế tiếp |
| `flex-kit close [--confirm]` | `/flex-close` | archive plan |

`status` / `next-step` / `close` thì slash ≈ wrapper 1:1 của CLI. Nhưng **`/flex-plan`
không phải wrapper mỏng**: nó còn chứa bước agent tự lên plan (xem "Cơ chế" bên dưới).

## Ai làm

Hai vai tách bạch - đừng nhầm:

- **Agent (chủ thể lên plan).** Phần "nghĩ" là của agent: đọc task, chọn mode, **chia
  task thành các step cụ thể**, viết Goal và Files In Scope. Đây là công việc trí tuệ,
  CLI không làm thay được. `/flex-plan` chính là *protocol agent theo*: chạy CLI để dựng
  khung, rồi **mở `plan.md` và điền nội dung thật** (xem Flow).
- **CLI `flex-kit` (plumbing bền).** CLI cố tình "ngu": chỉ (1) scaffold một `plan.md`
  **rỗng** (placeholder `- [ ] first step`), (2) đặt con trỏ `active_plan` trong
  `state.json`, (3) parse lại checklist cho `status`/`next-step`, (4) di chuyển thư mục
  khi `close`. Nó **không** sinh step, không suy luận - đó là việc của agent.

Không có subagent ở flow này: agent chính (đang theo `/flex-plan`) tự lên plan; các
subagent (`implementer`…) chỉ vào cuộc ở [delivery](6-delivery.md).

## Flow

```
[CLI]    flex-kit plan "<task>" --mode build
           -> tạo plans/active/<YYMMDD-HHmm-slug>/plan.md  (khung rỗng: Goal/Steps/Files/Done,
              Steps chỉ có 1 placeholder "- [ ] first step")
           -> ghi .flexkit/state.json { "active_plan": "<id>" }

[AGENT]  mở plan.md và LÊN PLAN THẬT  <-- phần cốt lõi, không phải CLI
           -> viết Goal (kết quả mong đợi)
           -> thay placeholder bằng checklist step cụ thể suy ra từ task
           -> điền Files In Scope (chi phối cả escalation theo file ở mode)

[CLI]    flex-kit status / next-step
           -> đọc plan active, parse checklist - [ ] / - [x]
           -> tính effective mode (modes.effective_mode) và surface escalation

[CLI]    flex-kit close --confirm
           -> mv plans/active/<id>  ->  plans/archive/<id>
           -> xóa active_plan khỏi state.json
```

## Cơ chế: cái gì điều phối [CLI] ↔ [AGENT]

Không có engine, không có code nào "gọi agent". Thứ điều phối cả chuỗi trên là **prose
của slash command** - file `.claude/commands/flex-plan.md` được `gen` sinh ra từ
`.flexkit/commands/flex-plan.md`. Host (Claude Code) đọc file đó như một danh sách việc
và làm tuần tự; trong danh sách đó, **vài bước là "chạy lệnh CLI", một bước là "đến lượt
mày, agent, viết plan thật"**. Nội dung `/flex-plan` đúng 3 bước:

```
1. Chạy `flex-kit plan "<task>"` ở terminal (thêm --mode nếu task gợi ý kích cỡ).   [CLI]
2. Mở plans/active/<id>/plan.md, thay placeholder bằng checklist `## Steps` cụ thể     [AGENT]
   suy ra từ task, rồi điền `## Goal` và `## Files In Scope`.
3. Chạy `flex-kit status` để xác nhận, rồi gợi ý `/flex-implement` để giao việc.        [CLI]
```

Nói cách khác:

- **Bước 1 và 3** là agent gọi CLI (qua Bash tool) - CLI làm phần plumbing.
- **Bước 2** không có lệnh nào để gọi: nó là chỉ thị bằng văn xuôi yêu cầu *chính agent*
  dùng năng lực đọc-hiểu của mình để biến task thành step. Đây chính là chỗ "lên plan".
- Bỏ slash đi, tự gõ `flex-kit plan` ở terminal: bạn chỉ nhận khung rỗng và **bạn** phải
  tự điền bước 2. `/flex-plan` chỉ đóng gói "scaffold + điền + xác nhận" thành chỉ thị để
  agent làm trọn trong một lượt - bản chất handoff [CLI]↔[AGENT] là vậy, không phải magic.

## Điều hướng / routing

`status` và `next-step` suy ra mọi thứ từ `plan.md` (checklist) + `state.json` (plan
nào). "Next step" đơn giản là item chưa tick đầu tiên - **không có router**. `status`
còn chạy `modes.effective_mode()` để báo mode khai báo có escalate không (vd
`patch -> build` khi vượt budget step/file).

## State / memory

| File | Vai trò | Ai ghi |
|---|---|---|
| `plans/active/<id>/plan.md` | plan + checklist step | agent (lên plan); `implementer` tick box khi delivery |
| `.flexkit/state.json` | pointer `active_plan` + hash dedup `last_reminder` | CLI + hooks |
| `plans/archive/<id>/` | plan đã đóng, giữ tham khảo | `close --confirm` |

Đây là memory của project: bền, inspect được, và là **nguồn duy nhất** mà cả hooks lẫn
delivery loop đọc.

## Loop-back

Không có vòng nội bộ - là state machine: `active -> (làm) -> archived`. Việc lặp (và
tick dần các box) xảy ra bên trong [delivery](6-delivery.md), không phải ở đây.

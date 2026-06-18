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

Ba vai tách bạch - đừng nhầm:

- **`planner` (subagent lên plan).** Phần "nghĩ" giao cho subagent `planner`: scout
  file liên quan, **chia task thành step cụ thể kèm acceptance**, viết Goal / Files In
  Scope / Done, đề xuất mode. Đây là công việc trí tuệ, CLI không làm thay được.
- **Main agent (điều phối + duyệt).** Đi theo `/flex-plan`: chạy CLI dựng khung, **spawn
  `planner` để draft**, rồi cùng user xem lại và chốt. Không tự tay nghĩ plan - giao
  planner (đối xứng với việc giao `implementer`/`reviewer`/`tester` ở delivery).
- **CLI `flex-kit` (plumbing bền).** Cố tình "ngu": chỉ (1) scaffold một `plan.md`
  **rỗng** (placeholder `- [ ] first step`), (2) đặt con trỏ `active_plan` trong
  `state.json`, (3) parse lại checklist cho `status`/`next-step`, (4) di chuyển thư mục
  khi `close`. Nó **không** sinh step, không suy luận.

`planner` là subagent đầu tiên vào cuộc; `implementer`/`reviewer`/`tester` vào ở
[delivery](6-delivery.md).

## Flow

```
[CLI]    flex-kit plan "<task>" --mode build
           -> tạo plans/active/<YYMMDD-HHmm-slug>/plan.md  (khung rỗng: Goal/Steps/Files/Done,
              Steps chỉ có 1 placeholder "- [ ] first step")
           -> ghi .flexkit/state.json { "active_plan": "<id>" }

[PLANNER] main agent spawn `planner` -> nó DRAFT plan.md  <-- phần cốt lõi, không phải CLI
           -> scout file liên quan
           -> viết Goal + checklist Steps (kèm acceptance) + Files In Scope + Done
           -> đề xuất mode; main agent + user xem lại và chốt

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
và làm tuần tự; trong danh sách đó, **vài bước là "chạy lệnh CLI", một bước là "spawn
`planner` để nó draft plan thật"**. Nội dung `/flex-plan` (1 bước route tùy chọn + 3 chính):

```
0. (tùy chọn) Hướng chưa rõ? áp skill navigator để route - có thể đẩy sang      [AGENT]
   /flex-fix, /flex-change hoặc /flex-review thay vì plan thường.
1. Chạy `flex-kit plan "<task>"` ở terminal (thêm --mode nếu task gợi ý kích cỡ).   [CLI]
2. Spawn `planner` -> nó draft plan.md (Goal + Steps kèm acceptance + Files + Done),  [PLANNER]
   đề xuất mode; main agent + user xem lại.
3. Chạy `flex-kit status` để xác nhận, rồi gợi ý `/flex-implement` để giao việc.        [CLI]
```

Nói cách khác:

- **Bước 1 và 3** là main agent gọi CLI (qua Bash tool) - CLI làm phần plumbing.
- **Bước 2** không có lệnh CLI nào để gọi: nó là chỉ thị bằng văn xuôi yêu cầu main agent
  **spawn subagent `planner`** để biến task thành plan. Đây chính là chỗ "lên plan", và
  nó là một *agent* làm - không phải CLI.
- Bỏ slash đi, tự gõ `flex-kit plan` ở terminal: bạn chỉ nhận khung rỗng và **bạn** phải
  tự đóng vai planner điền bước 2. `/flex-plan` chỉ đóng gói "scaffold + spawn planner +
  duyệt" thành chỉ thị để làm trọn trong một lượt - bản chất handoff vẫn là CLI lo
  plumbing, agent lo phần nghĩ.

## Điều hướng / routing

`status` và `next-step` suy ra mọi thứ từ `plan.md` (checklist) + `state.json` (plan
nào). "Next step" đơn giản là item chưa tick đầu tiên - **không có router**. `status`
còn chạy `modes.effective_mode()` để báo mode khai báo có escalate không (vd
`patch -> build` khi vượt budget step/file).

## State / memory

| File | Vai trò | Ai ghi |
|---|---|---|
| `plans/active/<id>/plan.md` | plan + checklist step | `planner` (draft); `implementer` tick box khi delivery |
| `.flexkit/state.json` | pointer `active_plan` + hash dedup `last_reminder` | CLI + hooks |
| `plans/archive/<id>/` | plan đã đóng, giữ tham khảo | `close --confirm` |

Đây là memory của project: bền, inspect được, và là **nguồn duy nhất** mà cả hooks lẫn
delivery loop đọc.

## Loop-back

Không có vòng nội bộ - là state machine: `active -> (làm) -> archived`. Việc lặp (và
tick dần các box) xảy ra bên trong [delivery](6-delivery.md), không phải ở đây.

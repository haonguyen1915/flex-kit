# Workflow: plan lifecycle (`flex-kit plan` / `status` / `next-step` / `close`)

> Thứ tự đọc **2 / 7** · trước: [build-sync](1-build-sync.md) · sau: [hooks-runtime](3-hooks-runtime.md)

Xương sống bền mà mọi flow khác đọc vào. Một plan là state công việc nhiều bước, sống
sót qua reset context.

## Bắt đầu thế nào

Một lệnh terminal hoặc slash wrapper của nó:

| CLI | Slash | Làm gì |
|---|---|---|
| `flex-kit plan "<task>" [--mode]` | `/flex-plan` | tạo + activate plan |
| `flex-kit status` | `/flex-status` | hiện tiến độ + effective mode |
| `flex-kit next-step` | `/flex-next-step` | hiện step chưa xong kế tiếp |
| `flex-kit close [--confirm]` | `/flex-close` | archive plan |

## Ai làm

**CLI `flex-kit`** (Python) thao tác file trực tiếp. Slash command là wrapper mỏng:
agent host chạy CLI giúp bạn + thêm hướng dẫn (vd scaffold steps từ task). Không có
subagent.

## Flow

```
flex-kit plan "<task>" --mode build
  -> tạo plans/active/<YYMMDD-HHmm-slug>/plan.md
     (frontmatter: id, created, mode, status; section: Goal / Steps / Files / Done)
  -> ghi .flexkit/state.json { "active_plan": "<id>" }

flex-kit status / next-step
  -> đọc plan active, parse checklist - [ ] / - [x]
  -> tính effective mode (modes.effective_mode) và surface escalation

flex-kit close --confirm
  -> mv plans/active/<id>  ->  plans/archive/<id>
  -> xóa active_plan khỏi state.json
```

## Điều hướng / routing

`status` và `next-step` suy ra mọi thứ từ `plan.md` (checklist) + `state.json` (plan
nào). "Next step" đơn giản là item chưa tick đầu tiên - **không có router**. `status`
còn chạy `modes.effective_mode()` để báo mode khai báo có escalate không (vd
`patch -> build` khi vượt budget step/file).

## State / memory

| File | Vai trò | Ai ghi |
|---|---|---|
| `plans/active/<id>/plan.md` | plan + checklist step | bạn (và implementer tick box) |
| `.flexkit/state.json` | pointer `active_plan` + hash dedup `last_reminder` | CLI + hooks |
| `plans/archive/<id>/` | plan đã đóng, giữ tham khảo | `close --confirm` |

Đây là memory của project: bền, inspect được, và là **nguồn duy nhất** mà cả hooks lẫn
delivery loop đọc.

## Loop-back

Không có vòng nội bộ - là state machine: `active -> (làm) -> archived`. Việc lặp xảy
ra bên trong [delivery](6-delivery.md), nơi tick các box của plan này.

## Review / Codex

Không áp dụng - plan lifecycle không review. Review thuộc flow
[delivery](6-delivery.md) và [review](4-review.md).

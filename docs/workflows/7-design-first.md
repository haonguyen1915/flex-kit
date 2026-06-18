# Workflow: design-first (`/flex-change` + `flex-kit spec`)

> Thứ tự đọc **7 / 7** · trước: [delivery](6-delivery.md) · sau: -

Cho việc mơ hồ hoặc cross-cutting: chốt một spec (proposal -> design -> tasks) và lấy
duyệt **trước khi** viết code. Việc build sau đó đi theo delivery loop.

## Bắt đầu thế nào

Gõ **`/flex-change <task>`** trong Claude Code. Nó chạy `.claude/commands/flex-change.md`,
lái các bước dưới; phần scaffold spec là một lệnh CLI (`flex-kit spec`).

## Ai làm

| Bước | Actor |
|---|---|
| Gỡ quyết định (nếu mơ hồ) | **agent chính** áp skill `decision-interview` cùng user |
| Tạo plan + scaffold spec | **agent chính** chạy CLI (`flex-kit plan` / `flex-kit spec`) |
| Điền proposal / design / tasks | **agent chính**, user duyệt |
| Implement (sau duyệt) | loop [delivery](6-delivery.md) (`implementer` / `reviewer` / `tester`) |

Không subagent nào chạy trong pha design - chỉ agent chính + user.

## Flow

```
/flex-change <task>
 0. FRAME    việc mơ hồ/cross-cutting? áp skill decision-interview để chốt hướng +
             ghi lý do vào decisions.md  (bỏ qua nếu hướng đã rõ)
 1. PLAN     flex-kit plan "<task>" --mode design          (CLI)
 2. SCAFFOLD flex-kit spec                                  (CLI)
             -> plans/active/<id>/spec/{proposal,design,tasks}.md
 3. FILL     proposal.md  (Problem -> Chosen Direction)
             design.md    (System Shape, Data And Contracts, Validation Plan, Risks)
             tasks.md      (checklist); log quyết định vào decisions.md
 4. APPROVE  present [A] Approve / [R] Revise  <-- hard gate, không sang code tới khi A
 5. HAND OFF suy plan.md ## Steps từ spec/tasks.md
 6. BUILD    /flex-implement   -> delivery loop
```

## Điều hướng / routing

Thứ tự cố định bởi prose command: proposal -> design -> tasks -> duyệt -> implement.
Bước 4 là **hard checkpoint** - flow không sang code cho tới khi user duyệt. Mode
`design` (đặt ở bước 1) là tín hiệu "cần spec"; scope gate của delivery loop cũng tôn
trọng nó.

## State / memory

| File | Vai trò |
|---|---|
| `plans/active/<id>/plan.md` | plan (mode `design`); steps đến từ tasks.md |
| `plans/active/<id>/spec/proposal.md` | problem + chosen direction |
| `plans/active/<id>/spec/design.md` | system shape, contracts, validation plan, risks |
| `plans/active/<id>/spec/tasks.md` | checklist task trở thành plan steps |
| `plans/active/<id>/decisions.md` | nhật ký quyết định từ decision-interview + lúc fill spec |

Spec bền trên đĩa, nên design sống sót qua reset và là tham chiếu delivery loop build
theo.

## Loop-back

Trong pha design không có loop tự động - user tự lặp trên các file spec. Sau khi duyệt,
flow nhập vào loop [delivery](6-delivery.md), nơi sở hữu vòng implement↔verify.

## Review / Codex

Bản design được **user** review tại gate bước 4 (không subagent). Khi bắt đầu
implement, review là subagent `reviewer` như trong delivery loop. Hôm nay chưa có bước
review external/Codex trong pha này.

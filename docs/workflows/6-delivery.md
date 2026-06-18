# Workflow: delivery (`/flex-implement`)

> Thứ tự đọc **6 / 7** · trước: [codex-review](5-codex-review.md) · sau: [design-first](7-design-first.md)

Vòng multi-agent chính: implement plan active, verify (review + test song song), fix
chỗ sai, lặp tới khi sạch, rồi đóng.

## Bắt đầu thế nào

Gõ **`/flex-implement`** (hoặc `/flex-implement --full`) trong Claude Code. Nó chạy
prose generated `.claude/commands/flex-implement.md` - agent host chính đọc và lái flow
dưới đây. (Không có engine; agent thực thi protocol.)

## Ai làm

| Bước | Actor |
|---|---|
| Orient, quyết định, spawn | **agent host chính** (đi theo command) |
| Viết code | subagent **`implementer`** (Task tool host) |
| Review thay đổi | subagent **`reviewer`** |
| Chạy test | subagent **`tester`** |

Skill `verify-fix-loop` là protocol agent chính áp ở bước 4.

## Flow

```
/flex-implement [--full]
 1. ORIENT      chạy `flex-kit status` + `flex-kit next-step` (CLI).
                không plan active -> dừng, gợi ý /flex-plan.
 2. SCOPE GATE  status báo mode escalate (patch -> build)? surface + confirm
                trước khi chạy autonomous lâu.
 3. IMPLEMENT   mặc định: spawn `implementer` cho step kế.
                --full : walk hết step chưa xong, tick - [x] trong plan.md.
 4. VERIFY      (verify-fix-loop) spawn `reviewer` VÀ `tester` song song:
                  reviewer -> handoffs/review-verdict.md (approve|revise + findings)
                  tester   -> handoffs/test-report.md   (pass|fail)
 5. DECIDE      verdict revise HOẶC có test fail -> bước 6.
                approve + chỉ low/medium + test pass -> bước 7.
 6. FIX         spawn `implementer` kèm verdict + test report -> về bước 4.
                cap: 2 vòng (--full: 3), rồi giao phần còn lại cho user.
 7. CLOSE OUT   mọi step - [x] và sạch -> tóm tắt, mời /flex-close.
```

## Điều hướng / routing

- **Làm gì kế** đến từ `flex-kit next-step` đọc checklist plan - không phải từ router
  skill. **Plan chính là routing.**
- **Subagent dùng skill nào** do host quyết: body mỗi subagent liệt kê skill có sẵn
  (inject tại `<!-- SKILLS -->`), host load cái nào có `description` khớp task. Không
  cần navigator/dispatch skill.

## State / memory

| File | Vai trò |
|---|---|
| `plans/active/<id>/plan.md` | các step; `- [x]` tick khi từng cái xong (tiến độ bền) |
| `.flexkit/state.json` | plan nào đang active |
| `plans/active/<id>/handoffs/review-input.md` | phạm vi giao cho verifier |
| `plans/active/<id>/handoffs/review-verdict.md` | verdict reviewer (authoritative) |
| `plans/active/<id>/handoffs/test-report.md` | tester pass/fail |

Vì tiến độ sống trong `plan.md` (không phải chat), loop sống sót qua reset: session mới
re-orient từ plan (xem [hooks-runtime](3-hooks-runtime.md)).

## Loop-back

Vòng fix↔verify là bước 6 -> bước 4. Chỉ thoát khi: verdict sạch + test pass, chỉ còn
low/medium, hoặc chạm `maxIterations` (lúc đó user quyết). Mỗi vòng ghi lại
`review-verdict.md` / `test-report.md`, nên quyết định luôn dựa trên file mới nhất,
không bao giờ từ memory.

## Review / Codex

Review là subagent **`reviewer`** spawn trên host; file verdict của nó là authoritative
và một lần `tester` fail tính là finding phải fix. Muốn ý kiến độc lập từ model khác,
chạy [`/flex-codex-review`](5-codex-review.md) và merge findings critical/high vào
`review-verdict.md`.

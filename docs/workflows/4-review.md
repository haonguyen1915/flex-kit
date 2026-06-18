# Workflow: review độc lập (`/flex-review`)

> Thứ tự đọc **4 / 7** · trước: [hooks-runtime](3-hooks-runtime.md) · sau: [codex-review](5-codex-review.md)

Review code của thay đổi hiện tại **không cần** plan - lấy thêm một cặp mắt nhìn diff
nhanh.

## Bắt đầu thế nào

Gõ **`/flex-review [target]`** trong Claude Code. Nó chạy
`.claude/commands/flex-review.md`. Không có target thì review git diff của working
tree; có target thì review cái đó.

## Ai làm

| Bước | Actor |
|---|---|
| Scope diff, ghi input | **agent chính** |
| Review | subagent **`reviewer`** (Task tool của host) |
| Report / fix tùy chọn | **agent chính** (và `implementer` chỉ khi bạn yêu cầu) |

## Flow

```
/flex-review [target]
 1. SCOPE   ghi handoffs/review-input.md theo template trong skill verify-fix-loop
            (goal, files changed, checks run, key decisions, read-these-first)
 2. REVIEW  spawn `reviewer` -> handoffs/review-verdict.md (verdict + findings)
                              + bản bền reports/review-<ts>.md
 3. REPORT  surface findings. Mời fix bằng `implementer`, hoặc giao user.
            (chỉ review: không đổi code trừ khi bạn yêu cầu)
```

## Điều hướng / routing

Tuyến tính, một phát - không loop, không phụ thuộc plan. Nó tái dùng đúng agent
`reviewer` và đúng file verdict `handoffs/` như delivery loop, nên một finding ở đây
đọc giống hệt finding sinh ra trong delivery.

## State / memory

| File | Vai trò |
|---|---|
| `handoffs/review-input.md` | phạm vi diff giao cho reviewer (theo template skill) |
| `handoffs/review-verdict.md` | verdict + findings hiện hành của reviewer |
| `reports/review-<ts>.md` | bản sao bền có timestamp |

Nếu không có plan active, các file này ghi ở `handoffs/` của repo root. Không đọc/ghi
plan state - flow này cố ý stateless.

## Loop-back

Mặc định không - một pass review duy nhất. Để xử findings: tự fix, gọi `implementer`,
hoặc gói thay đổi vào một plan rồi dùng [delivery](6-delivery.md) (loop review↔fix tự
động).

## Review / Codex

Review là subagent `reviewer` trên host. Muốn ý kiến độc lập từ một **model khác**,
dùng [`/flex-codex-review`](5-codex-review.md) - nó gửi đúng diff đó sang Codex CLI và
lưu findings thành report.

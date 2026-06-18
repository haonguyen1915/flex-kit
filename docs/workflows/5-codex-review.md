# Workflow: review cross-model (`/flex-codex-review`)

> Thứ tự đọc **5 / 7** · trước: [review](4-review.md) · sau: [delivery](6-delivery.md)

**Ý kiến độc lập từ một model KHÁC**: gửi plan active, diff, hoặc file sang Codex CLI
và lấy review của nó về. Mọi flow khác review bằng subagent `reviewer` của chính host;
flow này vươn ra *ngoài* host.

## Bắt đầu thế nào

Gõ **`/flex-codex-review [--type plan|diff|file] [target]`** trong Claude Code. Nó chạy
`.claude/commands/flex-codex-review.md`, gọi CLI: `flex-kit codex-review ...`.

## Ai làm

| Bước | Actor |
|---|---|
| Build prompt + chạy codex | **CLI `flex-kit`** (`codex_review.py`) |
| Bản review | **Codex CLI** (`codex exec`) - một *model khác* (mặc định `gpt-5.5`) |
| Tóm tắt + xử findings | **agent host chính** |

Đây không phải subagent host - nó shell ra một process riêng chạy model khác. Cần
`codex` CLI đã cài và login.

## Flow

```
/flex-codex-review [--type plan|diff|file] [target]
 1. BUILD PROMPT   plan (mặc định): plan.md đang active
                   --type diff   : git diff của working tree
                   --type file P : file P
                   bọc trong instruction "independent reviewer, report by severity"
 2. RUN CODEX      subprocess: codex exec -m <model> -c reasoning.effort="<effort>" --full-auto -
                   (prompt qua stdin; --dry-run in lệnh thay vì chạy)
 3. CAPTURE        ghi stdout của Codex vào plans/active/<id>/reports/codex-review.md
 4. ACT            agent tóm tắt findings và mời xử, hoặc merge critical/high vào
                   handoffs/review-verdict.md
```

## Điều hướng / routing

Tuyến tính, một phát. `--type` chọn gửi cái gì; không loop. Nó cố ý mirror dạng output
của subagent `reviewer` (findings theo severity) để kết quả khớp đúng chỗ.

## State / memory

| File | Vai trò |
|---|---|
| `plans/active/<id>/reports/codex-review.md` | review của Codex, lưu tham khảo |
| (`reports/codex-review.md` ở repo root nếu không có plan active) | tương tự, không plan |

Nó đọc plan active (cho type `plan`) nhưng chỉ ghi report - không động plan state.

## Loop-back

Không có nội bộ. Để xử findings của Codex: tự fix, hoặc merge critical/high vào
`handoffs/review-verdict.md` - cái này feed `implementer` của loop
[delivery](6-delivery.md) để chạy vòng fix↔verify tự động.

## Review / Codex

Đây **chính là** flow Codex review. Cơ chế là `codex exec` (chế độ non-interactive của
Codex): flex-kit pipe nội dung qua stdin và capture review của model qua stdout.
Faithful với `/prep-codex-review` của prep-kit, làm bằng subprocess Python thay vì
script Node.

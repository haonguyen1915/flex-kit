# Workflow: hooks runtime (tự động)

> Thứ tự đọc **3 / 7** · trước: [plan-lifecycle](2-plan-lifecycle.md) · sau: [review](4-review.md)

Tầng thụ động giữ agent oriented + được guard **mà bạn không cần yêu cầu**. Đây là các
flow duy nhất bạn không bao giờ trigger - host bắn chúng theo sự kiện.

## Bắt đầu thế nào

`emit_global()` của host claude ghi `.claude/settings.json` wiring ba sự kiện tới
`flex-kit hook <event>`. Khi Claude Code gặp sự kiện, nó chạy subcommand đó, đẩy payload
JSON qua stdin.

| Event | Command | Matcher |
|---|---|---|
| SessionStart | `flex-kit hook session-start` | `startup\|resume\|clear\|compact` |
| UserPromptSubmit | `flex-kit hook user-prompt` | (tất cả) |
| PreToolUse | `flex-kit hook pre-tool` | `Bash\|Read\|Edit\|Write\|Glob\|Grep` |

## Ai làm

**CLI `flex-kit`** (subcommand `hook`, logic ở `hooks.py`). Không agent, không
subagent - chỉ binary đọc state rồi in context hoặc một quyết định. **Cần `flex-kit`
nằm trên PATH của host** (`pipx install`, hoặc symlink).

## Flow - từng event

**session-start** (orient + sống sót compaction)
```
host bắn khi mở / resume / sau compaction
 -> đọc git branch + .flexkit/state.json (plan active) + plan.md (steps, mode)
 -> in "flex-kit: branch X; plan Y (build, 1/3 steps); next: Z"
 -> Claude Code inject stdout vào context session
```
Vì matcher cũng có `compact`, orientation được dựng lại từ file bền sau compaction -
không cần snapshot riêng.

**user-prompt** (nhắc plan có dedup)
```
host bắn mỗi prompt bạn gửi
 -> tính signature: plan id | effective mode | done/total | next step
 -> so với last_reminder trong .flexkit/state.json
 -> khác?  in reminder + ghi signature mới
    giống? im (dedup, chỉ bắn khi tiến độ thay đổi)
```

**pre-tool** (guard secret)
```
host bắn trước Bash/Read/Edit/Write/...
 -> đọc tool_input từ payload stdin
 -> match regex secret (.env / *.key / credentials / prod-secrets / id_*)
 -> match -> in deny JSON  (host CHẶN call)
    không match -> im  (cho qua)
```

## Điều hướng / routing

Không có routing - mỗi event map tới đúng một hook. Matcher trong settings.json quyết
định hook chạy cho những tool call / nguồn session nào.

## State / memory

| File | Đọc | Ghi |
|---|---|---|
| `.flexkit/state.json` | plan active, `last_reminder` | `last_reminder` (bởi user-prompt) |
| `plans/active/<id>/plan.md` | steps, mode, tiến độ | - |
| git | branch hiện tại | - |

Hooks là **cây cầu chủ động**: biến file plan bền thành context agent thấy tự động,
mỗi lượt.

## Loop-back

Không - hook là fire-and-forget mỗi event. "Vòng" chúng tạo ra là ngầm: mỗi
session/prompt mới đọc lại state mới nhất, nên agent luôn re-orient theo thực tại hiện
tại thay vì memory chat cũ.

## Review / Codex

Không áp dụng. Hook không review; pre-tool guard là cái duy nhất *chặn* (truy cập
secret), và làm bằng output decision, không phải subagent.

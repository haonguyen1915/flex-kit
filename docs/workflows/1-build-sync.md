# Workflow: build / sync (`flex-kit gen` / `doctor`)

> Thứ tự đọc **1 / 7** · trước: - · sau: [plan-lifecycle](2-plan-lifecycle.md)

Workflow nội dung: biến nguồn trung lập trong `.flexkit/` thành surface native cho
host, và validate chúng không bao giờ lệch. Đây là nền mọi flow khác đứng lên.

## Bắt đầu thế nào

Một lệnh terminal (cũng được `flex-kit init` và `flex-kit add` chạy giúp):

```bash
flex-kit gen       # source -> host surfaces
flex-kit doctor    # validate source + surface đồng bộ chưa
```

## Ai làm

**CLI `flex-kit`**. Không agent - `gen` discover + emit, `doctor` chạy check. Output
theo từng host do **host adapter** (`flex_kit/hosts/claude.py`, `codex.py`) sinh, mỗi
adapter chỉ emit những loại capability nó hỗ trợ.

## Flow - gen

```
flex-kit gen
 1. load .flexkit/flexkit.config.json (hosts, thư mục nguồn)
 2. discover skills (.flexkit/skills/), agents (.flexkit/agents/), commands (.flexkit/commands/)
 3. cho mỗi host:
      dọn các dir nó sở hữu (skills/agents/commands)
      emit_skill   -> .claude/skills/   + .agents/skills/ (Codex-native)
      emit_agent   -> .claude/agents/*.md + .codex/agents/*.toml   (inject skill catalog)
      emit_command -> .claude/commands/*.md      (chỉ Claude)
      emit_global  -> .claude/settings.json      (wiring hooks; chỉ Claude)
```

## Flow - doctor

```
flex-kit doctor   (check của tool + project check từ .flexkit/checks/)
  source-valid       mỗi skill/agent/command: name == id, description không rỗng
  skill-contract     độ dài description (20..1024), name kebab-case
  skill-refs         link markdown trong body resolve được
  generated-in-sync  re-emit trong memory rồi so với đĩa; báo drift + file lạ
```

## Điều hướng / routing

`gen` lặp `hosts x capabilities`; mỗi host adapter chỉ được hỏi những loại nó cài
(`hasattr(host, "emit_agent")` / `emit_command` / `emit_global`). Thêm host hay thêm
loại capability là **additive** - không đổi logic routing.

## State / memory

| Path | Vai trò | Sửa? |
|---|---|---|
| `.flexkit/skills` `/agents` `/commands` | **nguồn** sự thật | có |
| `.claude/` `.agents/` `.codex/` | surface **generated** | không bao giờ (chạy `gen`) |

Không có build cache hay file digest; `gen` luôn re-emit, và check `generated-in-sync`
của `doctor` **chính là** bộ chống drift (re-render + so sánh), đơn giản hơn cơ chế
digest lưu trữ.

## Loop-back

Vòng author chặt và thủ công: **sửa `.flexkit/` -> `flex-kit gen` -> `flex-kit
doctor`**. `doctor` fail (drift, file lạ, frontmatter sai) đẩy bạn về sửa nguồn rồi
re-gen. Đừng sửa file generated - `generated-in-sync` sẽ bắt.

## Review / Codex

Không áp dụng - flow này không có bước review. Thuần generate + validate deterministic.

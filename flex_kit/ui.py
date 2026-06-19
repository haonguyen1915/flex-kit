"""Console output helpers - a thin rich wrapper.

rich is already in the tree (Typer depends on it), so this adds no install
footprint. `rich.Console` auto-disables styling when stdout is not a terminal, so
output the host/agent consumes (piped into context) stays clean - no hand-rolled
TTY checks. Messages are rendered as `Text` (not markup) so brackets in paths or
content (e.g. `[claude, codex]`) are never mis-parsed.
"""

from __future__ import annotations

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

_theme = Theme(
    {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red bold",
        "accent": "cyan bold",
        "dim": "dim",
    }
)
console = Console(theme=_theme, highlight=False)


def _print(text: Text) -> None:
    console.print(text, soft_wrap=True)


def _line(symbol: str, style: str, msg: str) -> None:
    _print(Text(symbol, style=style).append(" " + msg))


def success(msg: str) -> None:
    _line("✓", "success", msg)


def error(msg: str) -> None:
    _line("✗", "error", msg)


def warn(msg: str) -> None:
    _line("!", "warning", msg)


def info(msg: str) -> None:
    _line("ℹ", "info", msg)


def header(text: str) -> None:
    _print(Text(text, style="accent"))


def detail(label: str, value: str) -> None:
    """An indented `label value` line; label is dimmed. Empty label -> plain indent."""
    text = Text("  ")
    if label:
        text.append(label, style="dim").append(" ")
    text.append(value)
    _print(text)


def hint(msg: str) -> None:
    _print(Text(msg, style="dim"))


def blank() -> None:
    console.print()

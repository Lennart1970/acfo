"""Split a SQL script into statements without breaking dollar-quoted bodies."""

from __future__ import annotations

import re

_DOLLAR = re.compile(r"\$[A-Za-z0-9_]*\$")


def split_sql(script: str) -> list[str]:
    statements: list[str] = []
    buf: list[str] = []
    i = 0
    dollar: str | None = None
    in_single = False
    while i < len(script):
        if dollar is not None:
            end = script.find(dollar, i)
            if end == -1:
                buf.append(script[i:])
                break
            buf.append(script[i : end + len(dollar)])
            i = end + len(dollar)
            dollar = None
            continue
        if in_single:
            if script.startswith("''", i):
                buf.append("''")
                i += 2
                continue
            char = script[i]
            buf.append(char)
            if char == "'":
                in_single = False
            i += 1
            continue
        if script.startswith("--", i):
            newline = script.find("\n", i)
            i = len(script) if newline == -1 else newline + 1
            continue
        match = _DOLLAR.match(script, i)
        if match:
            dollar = match.group(0)
            buf.append(dollar)
            i = match.end()
            continue
        char = script[i]
        if char == "'":
            in_single = True
            buf.append(char)
            i += 1
            continue
        if char == ";":
            statement = "".join(buf).strip()
            if statement:
                statements.append(statement)
            buf = []
            i += 1
            continue
        buf.append(char)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements

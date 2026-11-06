"""Basic repository-wide Markdown/MathJax compatibility check (stdlib only).

Usage: python scripts/check_markdown.py [repository-root]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


OPEN_FENCE = re.compile(r"^\s*(`{3,}|~{3,})([\w-]*)")
INLINE_CODE = re.compile(r"`[^`\n]*`")
UNBRACED_FRAC = re.compile(r"\\(?:d?frac)(?!\s*\{)")
HTML_ENTITY = re.compile(r"&(?:gt|lt|amp);", re.IGNORECASE)
CHINESE_TEXT = re.compile(r"\\text\{[^}]*[\u4e00-\u9fff]")


def math_braces_balanced(expression: str) -> bool:
    depth = 0
    for index, char in enumerate(expression):
        if char not in "{}" or (index and expression[index - 1] == "\\"):
            continue
        depth += 1 if char == "{" else -1
        if depth < 0:
            return False
    return depth == 0


def check_document(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    fence_char: str | None = None
    fence_size = 0
    math_lines: list[str] = []
    math_start = 0
    math_count = 0

    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if fence_char is None:
            match = OPEN_FENCE.match(line)
            if match:
                fence_char = match.group(1)[0]
                fence_size = len(match.group(1))
                if match.group(2).lower() == "math":
                    math_lines = []
                    math_start = number
                    math_count += 1
                else:
                    math_start = 0
                continue

            visible = INLINE_CODE.sub("", line)
            if "**" in visible:
                errors.append(f"line {number}: star-based emphasis delimiter")
            if "$" in visible:
                errors.append(f"line {number}: raw math delimiter")
        else:
            stripped = line.strip()
            if (
                stripped.startswith(fence_char * fence_size)
                and stripped.strip(fence_char) == ""
            ):
                if math_start:
                    expression = "\n".join(math_lines)
                    if not math_braces_balanced(expression):
                        errors.append(f"line {math_start}: unbalanced math braces")
                    if UNBRACED_FRAC.search(expression):
                        errors.append(f"line {math_start}: fraction without braces")
                    if HTML_ENTITY.search(expression):
                        errors.append(f"line {math_start}: HTML entity in math")
                    if CHINESE_TEXT.search(expression):
                        errors.append(f"line {math_start}: Chinese text inside math text command")
                fence_char = None
                math_start = 0
            elif math_start:
                math_lines.append(line)

    if fence_char is not None:
        errors.append("end of file: unclosed code/math fence")
    return errors, math_count


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    files = sorted(root.rglob("*.md"))
    if not files:
        print(f"No Markdown files found in {root}")
        return 1

    violations = 0
    formulas = 0
    for path in files:
        errors, count = check_document(path)
        formulas += count
        for issue in errors:
            print(f"FAIL {path.relative_to(root)}: {issue}")
            violations += 1

    if violations:
        print(f"FAILED: {violations} Markdown formatting issue(s) in {len(files)} files")
        return 1

    print(f"PASS: {len(files)} Markdown files checked, {formulas} math blocks validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

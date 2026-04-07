#!/usr/bin/env python3
"""Insert explicit visible pair gaps before English blocks that follow Chinese blocks."""

from __future__ import annotations

import argparse
from pathlib import Path

from check_bilingual_format import classify, iter_targets, split_blocks


MARKER = "\\bipairgap"


def previous_nonempty_line(lines: list[str], index: int) -> str | None:
    for i in range(index - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped:
            return stripped
    return None


def rewrite_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    if not blocks:
        return False

    lines = text.splitlines()
    insert_before: list[int] = []

    for prev, curr in zip(blocks, blocks[1:]):
        if classify(prev) == "zh" and classify(curr) == "en":
            prev_line = previous_nonempty_line(lines, curr.start_line - 1)
            if prev_line != MARKER:
                insert_before.append(curr.start_line)

    if not insert_before:
        return False

    for start_line in sorted(insert_before, reverse=True):
        lines.insert(start_line - 1, "")
        lines.insert(start_line - 1, MARKER)

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Insert explicit visible pair gaps into bilingual TeX files."
    )
    parser.add_argument("paths", nargs="*", help="Files to rewrite. Defaults to chapters_bilingual/*.tex")
    args = parser.parse_args()

    changed = 0
    for path in iter_targets(args.paths):
        if rewrite_file(path):
            changed += 1
            print(f"[UPDATED] {path}")
        else:
            print(f"[OK]      {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

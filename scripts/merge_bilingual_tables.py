#!/usr/bin/env python3
"""Merge paired EN/ZH tables into single bilingual tables.

The project currently contains many tables as two adjacent table renderings:
an English table followed by a Chinese translation. This script collapses
those pairs into a single table by interleaving rows:

  English row
  Chinese row

It intentionally only touches nearby pairs that have the same number of
top-level tabular rows and where the first table looks Latin-heavy while the
second looks CJK-heavy.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TABLE_MARKERS = (
    "\\begin{table}",
    "\\begin{englishtableblock}",
    "\\begin{chinesetableblock}",
    "\\begin{bilingualtableblock}",
    "\\begin{tabularx}",
    "\\begin{tabular}",
    "\\begin{longtable}",
)
TABLEBLOCK_RE = re.compile(r"\\begin\{(?:english|chinese)tableblock\}")
RULE_COMMANDS = (
    "\\toprule",
    "\\midrule",
    "\\bottomrule",
    "\\cmidrule",
    "\\addlinespace",
    "\\morecmidrules",
)
LATIN_RE = re.compile(r"[A-Za-z]{3,}")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
BETWEEN_RE = re.compile(r"(?:\s|%[^\n]*\n|\\(?:medskip|smallskip)\s*)*")


@dataclass
class TabularParts:
    env_name: str
    begin_start: int
    begin_end: int
    body_start: int
    body_end: int
    end_start: int
    end_end: int
    begin_tag: str
    body: str
    end_tag: str


@dataclass
class Construct:
    start: int
    end: int
    outer_env: str
    text: str
    tabular: TabularParts
    latin_count: int
    cjk_count: int
    row_count: int
    tokens: list[tuple[str, str]]


def find_matching_end(text: str, start: int, env_name: str) -> int:
    end_marker = f"\\end{{{env_name}}}"
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"Unclosed environment {env_name!r} at offset {start}")
    return end + len(end_marker)


def consume_group(text: str, pos: int, opening: str, closing: str) -> int:
    if pos >= len(text) or text[pos] != opening:
        raise ValueError(f"Expected {opening!r} at {pos}")
    depth = 1
    pos += 1
    while pos < len(text) and depth:
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
        pos += 1
    if depth:
        raise ValueError(f"Unclosed group starting with {opening!r}")
    return pos


def extract_tabular(text: str) -> TabularParts | None:
    match = re.search(r"\\begin\{(tabularx|tabular|longtable)\}", text)
    if not match:
        return None

    env_name = match.group(1)
    pos = match.end()
    required = 2 if env_name == "tabularx" else 1

    while pos < len(text) and text[pos].isspace():
        pos += 1
    while pos < len(text) and text[pos] == "[":
        pos = consume_group(text, pos, "[", "]")
        while pos < len(text) and text[pos].isspace():
            pos += 1
    for _ in range(required):
        while pos < len(text) and text[pos].isspace():
            pos += 1
        pos = consume_group(text, pos, "{", "}")

    begin_start = match.start()
    begin_end = pos
    end_marker = f"\\end{{{env_name}}}"
    end_start = text.find(end_marker, begin_end)
    if end_start == -1:
        raise ValueError(f"Missing {end_marker} for inner tabular")
    end_end = end_start + len(end_marker)

    return TabularParts(
        env_name=env_name,
        begin_start=begin_start,
        begin_end=begin_end,
        body_start=begin_end,
        body_end=end_start,
        end_start=end_start,
        end_end=end_end,
        begin_tag=text[begin_start:begin_end],
        body=text[begin_end:end_start],
        end_tag=text[end_start:end_end],
    )


def split_tokens(body: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    buf = ""
    depth = 0
    i = 0

    while i < len(body):
        if depth == 0 and not buf.strip():
            while i < len(body) and body[i].isspace():
                buf += body[i]
                i += 1
            if i >= len(body):
                break
            matched_rule = None
            for command in RULE_COMMANDS:
                if body.startswith(command, i):
                    matched_rule = command
                    break
            if matched_rule:
                j = i + len(matched_rule)
                while j < len(body) and body[j] != "\n":
                    j += 1
                if j < len(body):
                    j += 1
                tokens.append(("struct", buf + body[i:j]))
                buf = ""
                i = j
                continue

        ch = body[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)

        if depth == 0 and body.startswith("\\\\", i):
            j = i + 2
            if j < len(body) and body[j] == "[":
                j = consume_group(body, j, "[", "]")
            while j < len(body) and body[j].isspace():
                j += 1
            buf += body[i:j]
            tokens.append(("row", buf))
            buf = ""
            i = j
            continue

        buf += ch
        i += 1

    if buf:
        tokens.append(("struct", buf))

    return tokens


def classify_construct(text: str, start: int, end: int, outer_env: str) -> Construct | None:
    chunk = text[start:end]
    tabular = extract_tabular(chunk)
    if not tabular:
        return None

    tokens = split_tokens(tabular.body)
    row_count = sum(1 for kind, _ in tokens if kind == "row")
    latin_count = len(LATIN_RE.findall(tabular.body))
    cjk_count = len(CJK_RE.findall(tabular.body))

    return Construct(
        start=start,
        end=end,
        outer_env=outer_env,
        text=chunk,
        tabular=tabular,
        latin_count=latin_count,
        cjk_count=cjk_count,
        row_count=row_count,
        tokens=tokens,
    )


def find_constructs(text: str) -> list[Construct]:
    constructs: list[Construct] = []
    pos = 0

    while True:
        candidates = [(text.find(marker, pos), marker) for marker in TABLE_MARKERS]
        candidates = [(idx, marker) for idx, marker in candidates if idx != -1]
        if not candidates:
            break

        start, marker = min(candidates, key=lambda item: item[0])
        if marker == "\\begin{table}":
            outer_env = "table"
            end = find_matching_end(text, start, outer_env)
        elif marker == "\\begin{englishtableblock}":
            outer_env = "englishtableblock"
            end = find_matching_end(text, start, outer_env)
        elif marker == "\\begin{chinesetableblock}":
            outer_env = "chinesetableblock"
            end = find_matching_end(text, start, outer_env)
        elif marker == "\\begin{tabularx}":
            outer_env = "tabularx"
            end = find_matching_end(text, start, outer_env)
        elif marker == "\\begin{tabular}":
            outer_env = "tabular"
            end = find_matching_end(text, start, outer_env)
        elif marker == "\\begin{longtable}":
            outer_env = "longtable"
            end = find_matching_end(text, start, outer_env)
        else:
            outer_env = "bilingualtableblock"
            end = find_matching_end(text, start, outer_env)

        construct = classify_construct(text, start, end, outer_env)
        if construct:
            constructs.append(construct)
        pos = end

    return constructs


def looks_englishish(construct: Construct) -> bool:
    return construct.latin_count >= 3 and construct.cjk_count <= max(6, construct.latin_count // 6)


def looks_chineseish(construct: Construct) -> bool:
    return construct.cjk_count >= 6


def merge_tokens(english_tokens: list[tuple[str, str]], chinese_tokens: list[tuple[str, str]]) -> str:
    chinese_rows = [text for kind, text in chinese_tokens if kind == "row"]
    chinese_iter = iter(chinese_rows)
    merged_parts: list[str] = []

    for kind, text in english_tokens:
        if kind == "row":
            merged_parts.append(text)
            merged_parts.append(next(chinese_iter))
        else:
            merged_parts.append(text)

    return "".join(merged_parts)


def between_is_formatting(between: str) -> bool:
    if BETWEEN_RE.fullmatch(between):
        return True

    stripped = re.sub(r"%[^\n]*", " ", between)
    stripped = re.sub(r"\\[A-Za-z@]+(?:\*?)", " ", stripped)
    stripped = re.sub(r"\\.", " ", stripped)
    stripped = re.sub(r"[{}\\[\\]()$&_^~0-9.,;:!+=\\-/|<>]*", " ", stripped)
    latin = len(LATIN_RE.findall(stripped))
    cjk = len(CJK_RE.findall(stripped))
    return latin <= 3 and cjk == 0 and len(between) < 800


def pairable(first: Construct, second: Construct, between: str) -> bool:
    same_shape = (
        first.tabular.env_name == second.tabular.env_name
        and first.tabular.begin_tag == second.tabular.begin_tag
        and first.row_count == second.row_count
        and first.row_count > 0
    )
    return (
        same_shape
        and between_is_formatting(between)
        and looks_englishish(first)
        and looks_chineseish(second)
    )


def find_pairable_pairs(text: str) -> list[tuple[Construct, Construct]]:
    constructs = find_constructs(text)
    pairs: list[tuple[Construct, Construct]] = []
    i = 0

    while i + 1 < len(constructs):
        first = constructs[i]
        second = constructs[i + 1]
        between = text[first.end : second.start]
        if pairable(first, second, between):
            pairs.append((first, second))
            i += 2
            continue
        i += 1

    return pairs


def convert_to_bilingual_env(text: str) -> str:
    text = re.sub(
        r"\\begin\{(?:english|chinese)tableblock\}",
        r"\\begin{bilingualtableblock}",
        text,
        count=1,
    )
    text = re.sub(
        r"\\end\{(?:english|chinese)tableblock\}",
        r"\\end{bilingualtableblock}",
        text,
        count=1,
    )
    return text


def merge_pair(first: Construct, second: Construct) -> str:
    merged_body = merge_tokens(first.tokens, second.tokens)
    merged_text = (
        first.text[: first.tabular.body_start]
        + merged_body
        + first.text[first.tabular.body_end :]
    )
    return convert_to_bilingual_env(merged_text)


def rows_from_tokens(tokens: list[tuple[str, str]]) -> list[str]:
    return [text for kind, text in tokens if kind == "row"]


def rebuild_body(
    english_template_tokens: list[tuple[str, str]],
    english_rows: list[str],
    chinese_rows: list[str],
) -> str:
    english_iter = iter(english_rows)
    chinese_iter = iter(chinese_rows)
    parts: list[str] = []

    for kind, text in english_template_tokens:
        if kind == "row":
            parts.append(next(english_iter))
            parts.append(next(chinese_iter))
        else:
            parts.append(text)

    return "".join(parts)


def merged_constructs(text: str) -> list[Construct]:
    return [construct for construct in find_constructs(text) if "\\begin{bilingualtableblock}" in construct.text]


def git_head_text(path: Path) -> str | None:
    rel = path.relative_to(ROOT).as_posix()
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def repair_file_from_head(path: Path) -> int:
    current_text = path.read_text(encoding="utf-8")
    head_text = git_head_text(path)
    if head_text is None:
        return 0

    head_constructs = find_constructs(head_text)
    base_pairs = find_pairable_pairs(head_text)
    current_targets = merged_constructs(current_text)
    if not head_constructs or not current_targets:
        return 0

    repairs: list[tuple[int, int, str]] = []
    repaired = 0

    ordered_pairs: list[tuple[Construct | None, Construct | None, Construct]]
    if len(base_pairs) == len(current_targets):
        ordered_pairs = [(first, second, current) for (first, second), current in zip(base_pairs, current_targets)]
    else:
        ordered_pairs = [(None, None, current) for current in current_targets]

    for base_first, base_second, current_construct in ordered_pairs:
        current_rows = rows_from_tokens(current_construct.tokens)
        if not current_rows:
            continue

        if base_first is None or base_second is None:
            for idx, candidate in enumerate(head_constructs):
                candidate_rows = rows_from_tokens(candidate.tokens)
                if not candidate_rows:
                    continue
                if not looks_englishish(candidate):
                    continue
                if candidate.tabular.env_name != current_construct.tabular.env_name:
                    continue
                if candidate_rows[0] != current_rows[0]:
                    continue

                for follower in head_constructs[idx + 1 :]:
                    follower_rows = rows_from_tokens(follower.tokens)
                    if not follower_rows:
                        continue
                    if (
                        looks_chineseish(follower)
                        and follower.tabular.env_name == candidate.tabular.env_name
                        and len(follower_rows) == len(candidate_rows)
                    ):
                        base_first = candidate
                        base_second = follower
                        break
                if base_first and base_second:
                    break

        if base_first is None or base_second is None:
            continue

        base_rows = rows_from_tokens(base_first.tokens)
        base_chinese_rows = rows_from_tokens(base_second.tokens)

        if len(base_rows) != len(base_chinese_rows):
            continue
        if len(current_rows) >= (2 * len(base_rows)):
            continue

        current_norm = [" ".join(row.split()) for row in current_rows]
        base_norm = [" ".join(row.split()) for row in base_rows]
        english_rows: list[str] = []
        cursor = 0
        failed = False
        for expected in base_norm:
            while cursor < len(current_norm) and current_norm[cursor] != expected:
                cursor += 1
            if cursor >= len(current_norm):
                failed = True
                break
            english_rows.append(current_rows[cursor])
            cursor += 1

        if failed or len(english_rows) != len(base_rows):
            english_rows = [row for row in current_rows if not CJK_RE.search(row)]
            if len(english_rows) != len(base_rows):
                continue

        repaired_body = rebuild_body(base_first.tokens, english_rows, base_chinese_rows)
        repaired_text = (
            current_construct.text[: current_construct.tabular.body_start]
            + repaired_body
            + current_construct.text[current_construct.tabular.body_end :]
        )
        repairs.append((current_construct.start, current_construct.end, repaired_text))
        repaired += 1

    if not repairs:
        return 0

    new_text = current_text
    for start, end, replacement in reversed(repairs):
        new_text = new_text[:start] + replacement + new_text[end:]

    path.write_text(new_text, encoding="utf-8")
    return repaired


def merge_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    constructs = find_constructs(original)
    replacements: list[tuple[int, int, str]] = []
    merged_pairs = 0
    i = 0

    while i + 1 < len(constructs):
        first = constructs[i]
        second = constructs[i + 1]
        between = original[first.end : second.start]

        if pairable(first, second, between):
            replacements.append((first.start, second.end, merge_pair(first, second)))
            merged_pairs += 1
            i += 2
            continue

        i += 1

    if not replacements:
        return 0

    new_text = original
    for start, end, replacement in reversed(replacements):
        new_text = new_text[:start] + replacement + new_text[end:]

    path.write_text(new_text, encoding="utf-8")
    return merged_pairs


def target_files(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(p).resolve() for p in paths]
    return sorted((ROOT / "chapters_bilingual").glob("*.tex"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional files to process.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply modifications in place. Without this flag, only report candidates.",
    )
    parser.add_argument(
        "--repair-from-head",
        action="store_true",
        help="Repair merged tables by restoring missing initial Chinese rows from HEAD.",
    )
    args = parser.parse_args()

    files = target_files(args.paths)
    if args.apply and args.repair_from_head:
        parser.error("--apply and --repair-from-head are mutually exclusive")

    if args.repair_from_head:
        total = 0
        for path in files:
            count = repair_file_from_head(path)
            if count:
                total += count
                print(f"{path}: repaired {count} merged table(s)")
        print(f"Total repaired tables: {total}")
        return 0

    if not args.apply:
        total = 0
        for path in files:
            text = path.read_text(encoding="utf-8")
            preview_count = len(find_pairable_pairs(text))
            if preview_count:
                total += preview_count
                print(f"{path}: {preview_count} pair(s)")
        print(f"Total mergeable pairs: {total}")
        return 0

    total = 0
    for path in files:
        count = merge_file(path)
        if count:
            total += count
            print(f"{path}: merged {count} pair(s)")
    print(f"Total merged pairs: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

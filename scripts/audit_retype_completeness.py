#!/usr/bin/env python3
"""Audit the English LaTeX retype against the source PDF."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SOURCE_PDF = "Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf"
STRUCTURED_ENVS = (
    "tabularx",
    "tabular",
    "longtable",
    "bilingualtableblock",
    "figure",
    "table",
    "center",
    "minipage",
    "multicols",
)
SIMPLE_TEXT_COMMANDS = (
    "chapter",
    "section",
    "subsection",
    "textbf",
    "textit",
    "emph",
    "textsc",
    "url",
    "caption",
    "rawfigurecaption",
    "rawtablecaption",
    "footnote",
)


@dataclass
class AuditIssue:
    category: str
    message: str


@dataclass
class AnchorResult:
    path: Path
    label: str
    text: str
    source_strength: str
    main_strength: str


@dataclass
class AuditSummary:
    source_pages: int
    main_pages: int
    source_words: int
    main_words: int
    title_count: int
    anchor_count: int
    anchor_strengths: Counter[tuple[str, str]]
    issues: list[AuditIssue]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_command(args: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required command not found: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip()
        stdout = exc.stdout.strip()
        detail = stderr or stdout or "command failed"
        raise RuntimeError(f"{' '.join(args)} failed: {detail}") from exc
    return completed.stdout


def build_main_pdf(root: Path, main_tex: Path) -> None:
    run_command(
        ["latexmk", "-xelatex", "-interaction=nonstopmode", main_tex.name],
        cwd=root,
    )


def pdf_page_count(path: Path) -> int:
    output = run_command(["pdfinfo", str(path)])
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not read page count from {path}")
    return int(match.group(1))


def extract_pdf_text(path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        run_command(["pdftotext", "-nopgbrk", str(path), str(tmp_path)])
        return tmp_path.read_text(encoding="utf-8", errors="ignore")
    finally:
        tmp_path.unlink(missing_ok=True)


def normalize_text(text: str) -> str:
    text = (
        text.replace("—", "-")
        .replace("–", "-")
        .replace("−", "-")
        .replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace("…", "...")
        .replace("\\&", "&")
        .replace("\\%", "%")
        .replace("\\$", "$")
    )
    text = re.sub(r"\s+", " ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9%&$€£]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_main_inputs(main_tex: Path) -> list[Path]:
    text = main_tex.read_text(encoding="utf-8")
    inputs = re.findall(r"\\input\{(chapters/[^}]+)\}", text)
    return [project_root() / f"{item}.tex" for item in inputs]


def top_level_title(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")

    chapter_match = re.search(r"\\chapter\*?\{([^}]+)\}", text)
    if chapter_match:
        return chapter_match.group(1).strip()

    part_match = re.search(r"\\parttitleblock\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}", text)
    if part_match:
        first = part_match.group(1).strip()
        second = part_match.group(2).strip()
        return first or second or None

    return None


def strip_structured_envs(text: str) -> str:
    for env in STRUCTURED_ENVS:
        text = re.sub(
            r"\\begin\{" + env + r"\*?\}(?:.|\n)*?\\end\{" + env + r"\*?\}",
            "\n\n",
            text,
        )
    return text


def strip_tex_preserve_blocks(text: str) -> list[str]:
    text = re.sub(r"(?<!\\)%.*", " ", text)
    text = strip_structured_envs(text)

    text = re.sub(
        r"\\parttitleblock\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}",
        lambda match: "\n\n" + " ".join(part for part in match.groups()[:2] if part.strip()) + "\n\n",
        text,
    )
    text = re.sub(
        r"\\(?:markboth|addcontentsline)\*?(?:\[[^\]]*\])?\{[^{}]*\}\{[^{}]*\}(?:\{[^{}]*\})?",
        " ",
        text,
    )

    changed = True
    while changed:
        changed = False
        for command in SIMPLE_TEXT_COMMANDS:
            new_text = re.sub(
                r"\\" + command + r"\*?(?:\[[^\]]*\])?\{([^{}]*)\}",
                r" \1 ",
                text,
            )
            if new_text != text:
                changed = True
                text = new_text

    text = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"\\.", " ", text)
    text = text.replace("{", " ").replace("}", " ")

    blocks = [normalize_text(block) for block in re.split(r"\n\s*\n+", text)]
    return [block for block in blocks if block]


def pick_anchor_from_block(words: list[str]) -> list[str] | None:
    if len(words) < 22:
        return None

    best_score: float | None = None
    best_window: list[str] | None = None
    target = max(0, len(words) // 2 - 14)

    for start in range(0, len(words) - 28 + 1, 4):
        window = words[start : start + 28]
        alpha = sum(any("a" <= char <= "z" for char in word) for word in window)
        numeric = sum(any(char.isdigit() for char in word) for word in window)
        short = sum(len(word) <= 2 for word in window)
        score = alpha * 5 - numeric * 6 - short - abs(start - target) / 6

        if alpha < 20:
            continue

        if best_score is None or score > best_score:
            best_score = score
            best_window = window

    return best_window


def choose_anchor(blocks: list[str], fraction: float) -> list[str] | None:
    block_words = [block.split() for block in blocks]
    total_words = sum(len(words) for words in block_words)
    if total_words < 40:
        return None

    target = total_words * fraction
    seen = 0
    candidates: list[tuple[float, list[str]]] = []
    for words in block_words:
        midpoint = seen + len(words) / 2
        candidates.append((abs(midpoint - target), words))
        seen += len(words)

    for _, words in sorted(candidates, key=lambda item: item[0]):
        anchor = pick_anchor_from_block(words)
        if anchor:
            return anchor

    return None


def match_strength(window: list[str], text: str) -> str:
    for n in (12, 11):
        total = len(window) - n + 1
        if total > 0 and any(" ".join(window[i : i + n]) in text for i in range(total)):
            return "strong"

    for n, threshold in ((10, 2), (8, 4), (6, 6)):
        total = len(window) - n + 1
        if total <= 0:
            continue
        hits = sum(" ".join(window[i : i + n]) in text for i in range(total))
        if hits >= threshold:
            return "weak"

    return "none"


def audit_file(path: Path, source_text: str, main_text: str) -> list[AnchorResult]:
    blocks = strip_tex_preserve_blocks(path.read_text(encoding="utf-8"))
    labels = ("18%", "45%", "72%", "88%")
    anchors = [choose_anchor(blocks, fraction) for fraction in (0.18, 0.45, 0.72, 0.88)]

    results: list[AnchorResult] = []
    for label, anchor in zip(labels, anchors):
        if not anchor:
            continue
        anchor_text = " ".join(anchor)
        results.append(
            AnchorResult(
                path=path,
                label=label,
                text=anchor_text,
                source_strength=match_strength(anchor, source_text),
                main_strength=match_strength(anchor, main_text),
            )
        )

    return results


def summarize_audit(
    *,
    source_pdf: Path,
    main_pdf: Path,
    main_tex: Path,
) -> AuditSummary:
    source_pages = pdf_page_count(source_pdf)
    main_pages = pdf_page_count(main_pdf)

    source_raw = extract_pdf_text(source_pdf)
    main_raw = extract_pdf_text(main_pdf)
    source_text = normalize_text(source_raw)
    main_text = normalize_text(main_raw)

    source_words = len(source_raw.split())
    main_words = len(main_raw.split())

    issues: list[AuditIssue] = []
    if source_pages != main_pages:
        issues.append(
            AuditIssue(
                category="formatting_only",
                message=f"Page count differs (source={source_pages}, main={main_pages})",
            )
        )

    title_count = 0
    for path in extract_main_inputs(main_tex):
        title = top_level_title(path)
        if not title:
            continue
        title_count += 1
        normalized_title = normalize_text(title)
        in_source = normalized_title in source_text
        in_main = normalized_title in main_text

        if not in_main and in_source:
            issues.append(
                AuditIssue(
                    category="confirmed_omission",
                    message=f"{path}: top-level title missing from main PDF | {title}",
                )
            )
        elif not in_main and not in_source:
            issues.append(
                AuditIssue(
                    category="needs_visual_review",
                    message=f"{path}: top-level title not reliably extractable from either PDF | {title}",
                )
            )
        elif in_main and not in_source:
            issues.append(
                AuditIssue(
                    category="formatting_only",
                    message=f"{path}: source PDF only weakly exposes top-level title in text extraction | {title}",
                )
            )

    anchor_results: list[AnchorResult] = []
    for path in extract_main_inputs(main_tex):
        anchor_results.extend(audit_file(path, source_text, main_text))

    anchor_strengths: Counter[tuple[str, str]] = Counter()
    for result in anchor_results:
        anchor_strengths[(result.source_strength, result.main_strength)] += 1
        if result.main_strength == "none" and result.source_strength != "none":
            issues.append(
                AuditIssue(
                    category="confirmed_omission",
                    message=(
                        f"{result.path} [{result.label}] missing from main PDF | "
                        f"{result.text[:140]}"
                    ),
                )
            )
        elif result.main_strength == "none" and result.source_strength == "none":
            issues.append(
                AuditIssue(
                    category="needs_visual_review",
                    message=(
                        f"{result.path} [{result.label}] not reliably extractable from either PDF | "
                        f"{result.text[:140]}"
                    ),
                )
            )
        elif result.source_strength == "none" and result.main_strength != "none":
            issues.append(
                AuditIssue(
                    category="formatting_only",
                    message=(
                        f"{result.path} [{result.label}] source PDF only weakly exposes a summary/structured anchor | "
                        f"{result.text[:140]}"
                    ),
                )
            )

    return AuditSummary(
        source_pages=source_pages,
        main_pages=main_pages,
        source_words=source_words,
        main_words=main_words,
        title_count=title_count,
        anchor_count=len(anchor_results),
        anchor_strengths=anchor_strengths,
        issues=issues,
    )


def print_summary(summary: AuditSummary, *, show_issue_details: bool) -> None:
    print(
        "Pages: "
        f"source={summary.source_pages}, main={summary.main_pages}"
    )
    print(
        "Words: "
        f"source={summary.source_words}, main={summary.main_words}, "
        f"delta={summary.main_words - summary.source_words:+d}"
    )
    print(f"Top-level titles checked: {summary.title_count}")
    print(f"Narrative anchors checked: {summary.anchor_count}")

    if summary.anchor_strengths:
        parts = [
            f"{source}->{main}: {count}"
            for (source, main), count in sorted(summary.anchor_strengths.items())
        ]
        print("Anchor match strengths: " + ", ".join(parts))

    issues_by_category: Counter[str] = Counter(issue.category for issue in summary.issues)
    print(
        "Issue counts: "
        + ", ".join(
            f"{category}={issues_by_category.get(category, 0)}"
            for category in ("confirmed_omission", "needs_visual_review", "formatting_only")
        )
    )

    if show_issue_details:
        for category in ("confirmed_omission", "needs_visual_review", "formatting_only"):
            category_issues = [issue for issue in summary.issues if issue.category == category]
            if not category_issues:
                continue
            print(f"[{category}]")
            for issue in category_issues:
                print(f"  - {issue.message}")

    if issues_by_category.get("confirmed_omission", 0) == 0:
        print("[OK] No confirmed omissions detected.")
    else:
        print("[FAIL] Confirmed omissions detected.")

    if issues_by_category.get("needs_visual_review", 0) == 0:
        print("[OK] No unresolved visual-review items.")
    else:
        print("[WARN] Some items still need visual review.")


def main() -> int:
    root = project_root()

    parser = argparse.ArgumentParser(
        description="Audit whether the English LaTeX retype matches the source PDF closely enough to rule out obvious omissions."
    )
    parser.add_argument(
        "--source-pdf",
        default=DEFAULT_SOURCE_PDF,
        help="Path to the original source PDF. Defaults to the project source PDF in the repo root.",
    )
    parser.add_argument(
        "--main-tex",
        default="main.tex",
        help="Path to the English main TeX entry point. Defaults to main.tex.",
    )
    parser.add_argument(
        "--main-pdf",
        default="main.pdf",
        help="Path to the compiled English PDF. Defaults to main.pdf.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Compile the English PDF with latexmk before auditing.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Only print the global summary and issue counts.",
    )
    args = parser.parse_args()

    source_pdf = Path(args.source_pdf)
    if not source_pdf.is_absolute():
        source_pdf = root / source_pdf
    main_tex = Path(args.main_tex)
    if not main_tex.is_absolute():
        main_tex = root / main_tex
    main_pdf = Path(args.main_pdf)
    if not main_pdf.is_absolute():
        main_pdf = root / main_pdf

    if args.build:
        build_main_pdf(root, main_tex)

    if not source_pdf.exists():
        print(f"Source PDF not found: {source_pdf}", file=sys.stderr)
        return 1
    if not main_tex.exists():
        print(f"Main TeX file not found: {main_tex}", file=sys.stderr)
        return 1
    if not main_pdf.exists():
        print(f"Main PDF not found: {main_pdf}. Build it first or pass --build.", file=sys.stderr)
        return 1

    try:
        summary = summarize_audit(
            source_pdf=source_pdf,
            main_pdf=main_pdf,
            main_tex=main_tex,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_summary(summary, show_issue_details=not args.summary)
    confirmed = any(issue.category == "confirmed_omission" for issue in summary.issues)
    review = any(issue.category == "needs_visual_review" for issue in summary.issues)
    return 1 if confirmed or review else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Audit whether consecutive source paragraphs were merged into one TeX paragraph."""

from __future__ import annotations

import argparse
import re
import statistics
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SOURCE_PDF = (
    "Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf"
)


@dataclass(frozen=True)
class SourceParagraph:
    page_number: int
    sequence: int
    text: str
    anchor: str


@dataclass(frozen=True)
class MergeCandidate:
    file_path: Path
    first: SourceParagraph
    second: SourceParagraph
    tex_paragraph_index: int


@dataclass(frozen=True)
class TextLine:
    top: int
    left: int
    text: str


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


ROOT = project_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_retype_completeness import strip_tex_preserve_blocks
from scripts.sync_pdf_bold_spans import PAGE_RANGES


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


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
    )
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(text))


def file_for_page(root: Path, page: int) -> Path | None:
    for start, end, rel in PAGE_RANGES:
        if start <= page <= end:
            return root / rel
    return None


def choose_anchor(text: str, width: int = 12) -> str | None:
    token_list = words(text)
    if len(token_list) < 8:
        return None
    return " ".join(token_list[: min(width, len(token_list))])


def is_probably_running_header(line: str) -> bool:
    lowered = normalize_text(line)
    if not lowered:
        return True
    if lowered in {"systematic trading", "preface", "introduction"}:
        return True
    if lowered.startswith("chapter ") or lowered.startswith("appendix "):
        return True
    if lowered in {"contents", "acknowledgements", "glossary", "index"}:
        return True
    return False


def is_probably_noise(line: TextLine, page_height: int) -> bool:
    text = normalize_text(line.text)
    if not text:
        return True
    if line.top < 90 and is_probably_running_header(text):
        return True
    if line.top > page_height - 120:
        if re.fullmatch(r"[ivxlcdm0-9]+", text):
            return True
        if re.match(r"^\d+\.", text):
            return True
    return False


def extract_source_paragraphs(root: Path, pdf_path: Path) -> dict[Path, list[SourceParagraph]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "out.xml"
        run_command(["pdftohtml", "-xml", str(pdf_path), str(xml_path)])
        tree = ET.parse(xml_path)

    paragraphs_by_file: dict[Path, list[SourceParagraph]] = {}
    sequence_by_file: dict[Path, int] = {}

    for page in tree.getroot().findall("page"):
        page_number = int(page.attrib["number"])
        file_path = file_for_page(root, page_number)
        if file_path is None:
            continue

        page_height = int(page.attrib["height"])
        lines: list[TextLine] = []
        for node in page.findall("text"):
            line = TextLine(
                top=int(node.attrib["top"]),
                left=int(node.attrib["left"]),
                text="".join(node.itertext()),
            )
            if is_probably_noise(line, page_height):
                continue
            lines.append(line)

        if not lines:
            continue

        lines.sort(key=lambda item: (item.top, item.left))

        grouped_lines: list[list[TextLine]] = []
        current_group = [lines[0]]
        current_top = lines[0].top
        for line in lines[1:]:
            if abs(line.top - current_top) <= 2:
                current_group.append(line)
                continue
            grouped_lines.append(current_group)
            current_group = [line]
            current_top = line.top
        grouped_lines.append(current_group)

        flattened: list[TextLine] = []
        for group in grouped_lines:
            group.sort(key=lambda item: item.left)
            flattened.append(
                TextLine(
                    top=group[0].top,
                    left=min(item.left for item in group),
                    text=" ".join(item.text for item in group),
                )
            )

        gaps = [next_line.top - line.top for line, next_line in zip(flattened, flattened[1:])]
        baseline = statistics.median(gaps) if gaps else 20
        gap_threshold = max(24, int(baseline + 5))

        para_lines: list[TextLine] = [flattened[0]]
        for prev, line in zip(flattened, flattened[1:]):
            gap = line.top - prev.top
            if gap > gap_threshold:
                text = " ".join(item.text for item in para_lines)
                anchor = choose_anchor(text)
                if anchor:
                    seq = sequence_by_file.get(file_path, 0)
                    paragraphs_by_file.setdefault(file_path, []).append(
                        SourceParagraph(
                            page_number=page_number,
                            sequence=seq,
                            text=normalize_text(text),
                            anchor=anchor,
                        )
                    )
                    sequence_by_file[file_path] = seq + 1
                para_lines = [line]
            else:
                para_lines.append(line)

        text = " ".join(item.text for item in para_lines)
        anchor = choose_anchor(text)
        if anchor:
            seq = sequence_by_file.get(file_path, 0)
            paragraphs_by_file.setdefault(file_path, []).append(
                SourceParagraph(
                    page_number=page_number,
                    sequence=seq,
                    text=normalize_text(text),
                    anchor=anchor,
                )
            )
            sequence_by_file[file_path] = seq + 1

    return paragraphs_by_file


def tex_paragraphs(file_path: Path) -> list[str]:
    text = file_path.read_text(encoding="utf-8")
    return strip_tex_preserve_blocks(text)


def paragraph_index_for_anchor(anchor: str, paragraphs: list[str]) -> int | None:
    matches = [idx for idx, paragraph in enumerate(paragraphs) if anchor in paragraph]
    if len(matches) == 1:
        return matches[0]
    return None


def audit_merges(root: Path, pdf_path: Path) -> list[MergeCandidate]:
    source_paras = extract_source_paragraphs(root, pdf_path)
    candidates: list[MergeCandidate] = []

    for file_path, paras in sorted(source_paras.items()):
        tex_paras = tex_paragraphs(file_path)
        if not tex_paras:
            continue

        mapped: list[tuple[SourceParagraph, int] | None] = []
        for para in paras:
            idx = paragraph_index_for_anchor(para.anchor, tex_paras)
            mapped.append((para, idx) if idx is not None else None)

        for current, nxt in zip(mapped, mapped[1:]):
            if current is None or nxt is None:
                continue
            first, first_idx = current
            second, second_idx = nxt
            if first_idx != second_idx:
                continue
            if first.page_number != second.page_number:
                continue
            candidates.append(
                MergeCandidate(
                    file_path=file_path,
                    first=first,
                    second=second,
                    tex_paragraph_index=first_idx,
                )
            )

    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", default=DEFAULT_SOURCE_PDF)
    parser.add_argument("--top", type=int, default=20, help="Show at most N candidates.")
    args = parser.parse_args()

    root = project_root()
    pdf_path = (root / args.source_pdf).resolve()
    candidates = audit_merges(root, pdf_path)

    print(f"Merge candidates: {len(candidates)}")
    for candidate in candidates[: args.top]:
        rel = candidate.file_path.relative_to(root)
        print(
            f"{rel}: p.{candidate.first.page_number} tex_par={candidate.tex_paragraph_index + 1}"
        )
        print(f"  first:  {candidate.first.anchor}")
        print(f"  second: {candidate.second.anchor}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

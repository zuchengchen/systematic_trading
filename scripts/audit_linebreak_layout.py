#!/usr/bin/env python3
"""Audit page-by-page line-break fidelity between the source PDF and main.pdf."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


DEFAULT_SOURCE_PDF = (
    "Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf"
)
DEFAULT_MAIN_PDF = "main.pdf"


@dataclass
class TextNode:
    top: int
    left: int
    text: str


@dataclass
class PageComparison:
    page_number: int
    source_line_count: int
    main_line_count: int
    exact_match: bool
    overlap_ratio: float
    differing_lines: int


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


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


def extract_pages_as_lines(pdf_path: Path) -> dict[int, list[str]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "out.xml"
        run_command(["pdftohtml", "-xml", str(pdf_path), str(xml_path)])
        tree = ET.parse(xml_path)

    pages: dict[int, list[str]] = {}
    for page in tree.getroot().findall("page"):
        page_number = int(page.attrib["number"])
        text_nodes: list[TextNode] = []
        for node in page.findall("text"):
            raw = "".join(node.itertext())
            text = normalize_text(raw)
            if not text:
                continue
            text_nodes.append(
                TextNode(
                    top=int(node.attrib["top"]),
                    left=int(node.attrib["left"]),
                    text=text,
                )
            )

        if not text_nodes:
            pages[page_number] = []
            continue

        text_nodes.sort(key=lambda item: (item.top, item.left))
        grouped: list[list[TextNode]] = []
        current_group: list[TextNode] = [text_nodes[0]]
        current_top = text_nodes[0].top

        for node in text_nodes[1:]:
            if abs(node.top - current_top) <= 2:
                current_group.append(node)
                continue
            grouped.append(current_group)
            current_group = [node]
            current_top = node.top
        grouped.append(current_group)

        lines: list[str] = []
        for group in grouped:
            group.sort(key=lambda item: item.left)
            line = normalize_text(" ".join(item.text for item in group))
            if line:
                lines.append(line)
        pages[page_number] = lines

    return pages


def compare_pages(source_pages: dict[int, list[str]], main_pages: dict[int, list[str]]) -> list[PageComparison]:
    all_page_numbers = sorted(set(source_pages) | set(main_pages))
    comparisons: list[PageComparison] = []
    for page_number in all_page_numbers:
        source_lines = source_pages.get(page_number, [])
        main_lines = main_pages.get(page_number, [])

        overlap = 0.0
        if source_lines or main_lines:
            source_set = set(source_lines)
            main_set = set(main_lines)
            union = source_set | main_set
            overlap = len(source_set & main_set) / len(union) if union else 1.0

        max_len = max(len(source_lines), len(main_lines))
        differing = 0
        for idx in range(max_len):
            source_line = source_lines[idx] if idx < len(source_lines) else ""
            main_line = main_lines[idx] if idx < len(main_lines) else ""
            if source_line != main_line:
                differing += 1

        comparisons.append(
            PageComparison(
                page_number=page_number,
                source_line_count=len(source_lines),
                main_line_count=len(main_lines),
                exact_match=source_lines == main_lines,
                overlap_ratio=overlap,
                differing_lines=differing,
            )
        )
    return comparisons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", default=DEFAULT_SOURCE_PDF)
    parser.add_argument("--main-pdf", default=DEFAULT_MAIN_PDF)
    parser.add_argument("--top", type=int, default=12, help="Show the worst N pages.")
    args = parser.parse_args()

    root = project_root()
    source_pdf = (root / args.source_pdf).resolve()
    main_pdf = (root / args.main_pdf).resolve()

    source_pages = extract_pages_as_lines(source_pdf)
    main_pages = extract_pages_as_lines(main_pdf)
    comparisons = compare_pages(source_pages, main_pages)

    exact_match_count = sum(page.exact_match for page in comparisons)
    overlap_values = [page.overlap_ratio for page in comparisons]
    differing_values = [page.differing_lines for page in comparisons]

    print(
        f"Pages compared: source={len(source_pages)}, main={len(main_pages)}, total={len(comparisons)}"
    )
    print(f"Exact page line-break matches: {exact_match_count}/{len(comparisons)}")
    print(f"Average line overlap ratio: {mean(overlap_values):.3f}")
    print(f"Average differing lines per page: {mean(differing_values):.2f}")

    worst_pages = sorted(
        comparisons,
        key=lambda item: (-item.differing_lines, item.overlap_ratio, item.page_number),
    )[: args.top]
    print("Worst pages:")
    for page in worst_pages:
        print(
            "  "
            f"p.{page.page_number}: "
            f"exact={page.exact_match}, "
            f"src_lines={page.source_line_count}, "
            f"main_lines={page.main_line_count}, "
            f"differing={page.differing_lines}, "
            f"overlap={page.overlap_ratio:.3f}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "extracted" / "systematic_trading_layout.txt"
CHAPTERS = ROOT / "chapters"


CONFIGS = [
    {
        "file": "chapter_four.tex",
        "kind": "chapter",
        "title": "Portfolio Allocation",
        "toc_label": "Chapter Four. Portfolio Allocation",
        "start": 3012,
        "end": 3960,
    },
    {
        "file": "chapter_five.tex",
        "kind": "chapter",
        "title": "Framework Overview",
        "toc_label": "Chapter Five. Framework Overview",
        "start": 3960,
        "end": 4263,
    },
    {
        "file": "chapter_six.tex",
        "kind": "chapter",
        "title": "Instruments",
        "toc_label": "Chapter Six. Instruments",
        "start": 4263,
        "end": 4590,
    },
    {
        "file": "chapter_seven.tex",
        "kind": "chapter",
        "title": "Forecasts",
        "toc_label": "Chapter Seven. Forecasts",
        "start": 4590,
        "end": 5274,
    },
    {
        "file": "chapter_eight.tex",
        "kind": "chapter",
        "title": "Combined Forecasts",
        "toc_label": "Chapter Eight. Combined Forecasts",
        "start": 5274,
        "end": 5691,
    },
    {
        "file": "chapter_nine.tex",
        "kind": "chapter",
        "title": "Volatility targeting",
        "toc_label": "Chapter Nine. Volatility targeting",
        "start": 5691,
        "end": 6501,
    },
    {
        "file": "chapter_ten.tex",
        "kind": "chapter",
        "title": "Position Sizing",
        "toc_label": "Chapter Ten. Position Sizing",
        "start": 6501,
        "end": 6972,
    },
    {
        "file": "chapter_eleven.tex",
        "kind": "chapter",
        "title": "Portfolios",
        "toc_label": "Chapter Eleven. Portfolios",
        "start": 6972,
        "end": 7523,
    },
    {
        "file": "chapter_twelve.tex",
        "kind": "chapter",
        "title": "Speed and Size",
        "toc_label": "Chapter Twelve. Speed and Size",
        "start": 7523,
        "end": 9001,
    },
    {
        "file": "chapter_thirteen.tex",
        "kind": "chapter",
        "title": "Semi-automatic Trader",
        "toc_label": "Chapter Thirteen. Semi-automatic Trader",
        "start": 9005,
        "end": 9738,
    },
    {
        "file": "chapter_fourteen.tex",
        "kind": "chapter",
        "title": "Asset Allocating Investor",
        "toc_label": "Chapter Fourteen. Asset Allocating Investor",
        "start": 9738,
        "end": 10664,
    },
    {
        "file": "chapter_fifteen.tex",
        "kind": "chapter",
        "title": "Staunch Systems Trader",
        "toc_label": "Chapter Fifteen. Staunch Systems Trader",
        "start": 10664,
        "end": 11283,
    },
    {
        "file": "epilogue.tex",
        "kind": "star",
        "title": "Epilogue",
        "toc_title": "Epilogue. What Makes a Good Systematic Trader?",
        "toc_label": "Epilogue. What Makes a Good Systematic Trader?",
        "start": 11283,
        "end": 11343,
    },
    {
        "file": "glossary.tex",
        "kind": "raw_star",
        "title": "Glossary",
        "toc_title": "Glossary",
        "start": 11343,
        "end": 11914,
    },
    {
        "file": "appendix_a.tex",
        "kind": "appendix",
        "title": "Resources",
        "toc_label": "Appendix A. Resources",
        "start": 11914,
        "end": 12112,
    },
    {
        "file": "appendix_b.tex",
        "kind": "appendix",
        "title": "Trading Rules",
        "toc_label": "Appendix B. Trading Rules",
        "start": 12112,
        "end": 12516,
    },
    {
        "file": "appendix_c.tex",
        "kind": "appendix",
        "title": "Portfolio Optimisation",
        "toc_label": "Appendix C. Portfolio Optimisation",
        "start": 12516,
        "end": 12819,
    },
    {
        "file": "appendix_d.tex",
        "kind": "appendix",
        "title": "Framework Details",
        "toc_label": "Appendix D. Framework Details",
        "start": 12819,
        "end": 12914,
    },
    {
        "file": "acknowledgements.tex",
        "kind": "star",
        "title": "Acknowledgements",
        "toc_title": "Acknowledgements",
        "start": 12914,
        "end": 12946,
    },
    {
        "file": "index.tex",
        "kind": "raw_star",
        "title": "Index",
        "toc_title": "Index",
        "start": 12946,
        "end": 13304,
    },
]


FIGURE_MAP = {
    14: "img-014.png",
    15: "img-015.png",
    16: "img-016.png",
    17: "img-017.png",
    18: "img-018.png",
    19: "img-019.png",
    20: "img-020.png",
    21: "img-021.png",
    22: "img-022.png",
    23: "img-023.png",
}


KNOWN_AUDIENCE_TITLES = {
    "Semi-automatic Trader",
    "Semi-automatic trader",
    "Asset Allocating Investor",
    "Asset allocating investor",
    "Staunch Systems Trader",
    "Staunch systems trader",
    "This section is relevant to all readers",
    "This section is suitable for all readers",
}

SECTION_MAP = {
    "Chapter Four. Portfolio Allocation": [
        "Chapter overview",
        "Optimising gone bad",
        "Saving optimisation from itself",
        "Making weights by hand",
        "Incorporating Sharpe ratios",
    ],
    "Chapter Five. Framework Overview": [
        "Chapter overview",
        "A bad example",
        "Why a modular framework?",
        "The elements of the framework",
    ],
    "Chapter Six. Instruments": [
        "Chapter overview",
        "Necessities",
        "Instrument choice and trading style",
        "Access",
        "Summary of instrument choice",
    ],
    "Chapter Seven. Forecasts": [
        "Chapter overview",
        "What makes a good forecast",
        "Discretionary trading with stop losses",
        "The asset allocating investor's 'no-rule' rule",
        "Two example systematic rules",
        "Adapting and creating trading rules",
        "Selecting trading rules and variations",
        "Summary of trading rules and forecasts",
    ],
    "Chapter Eight. Combined Forecasts": [
        "Chapter overview",
        "Combining with forecast weights",
        "Choosing the forecast weights",
        "Getting to 10",
        "Capped at 20",
        "Summary for combining forecasts",
    ],
    "Chapter Nine. Volatility targeting": [
        "Chapter overview",
        "The importance of risk targeting",
        "Setting a volatility target",
        "Rolling up profits and losses",
        "What percentage of capital per trade?",
        "Summary of volatility targeting",
    ],
    "Chapter Ten. Position Sizing": [
        "Chapter overview",
        "How risky is it?",
        "Volatility target and position risk",
        "From forecast to position",
        "Summary for position sizing",
    ],
    "Chapter Eleven. Portfolios": [
        "Chapter overview",
        "Portfolios and instrument weights",
        "Instrument weights -- asset allocators and systems traders",
        "Instrument weights -- semi-automatic trading",
        "Instrument diversification multiplier",
        "A portfolio of positions and trades",
        "Summary for creating a portfolio of trading subsystems",
    ],
    "Chapter Twelve. Speed and Size": [
        "Chapter overview",
        "Speed of trading",
        "Calculating the cost of trading",
        "Using trading costs to make design decisions",
        "Trading with more or less capital",
        "Determining overall portfolio size",
        "Summary of tailoring systems for costs and capital",
    ],
    "Chapter Thirteen. Semi-automatic Trader": [
        "Chapter overview",
        "Who are you?",
        "Using the framework",
        "Process",
        "Trading diary",
    ],
    "Chapter Fourteen. Asset Allocating Investor": [
        "Chapter overview",
        "Who are you?",
        "Using the framework",
        "Weekly process",
        "Trading diary",
    ],
    "Chapter Fifteen. Staunch Systems Trader": [
        "Chapter overview",
        "Who are you?",
        "Using the framework",
        "Daily process",
        "Trading diary",
    ],
    "Appendix A. Resources": [
        "Further reading",
        "Sources of free data",
        "Brokers and platforms",
        "Automation and coding",
    ],
    "Appendix B. Trading Rules": [
        "The A and B system: Early profit taker and early loss taker",
        "The exponentially weighted moving average crossover (EWMAC) rule",
        "The carry trading rule",
    ],
    "Appendix C. Portfolio Optimisation": [
        "More details on bootstrapping",
        "Rule of thumb correlations",
    ],
    "Appendix D. Framework Details": [
        "Rescaling forecasts",
        "Calculation of diversification multiplier",
        "Calculating price volatility from historic data",
    ],
}


RAW_TABLE_NOTES = (
    "The table shows",
    "Numbers shown",
    "Correlations are",
    "Values in table",
    "Calculation of weights",
    "The table is using",
    "The figure shows",
    "Source:",
)


DROP_CAP_RE = re.compile(r"^[A-Z]\s{2,}[A-Z]")
FIGURE_RE = re.compile(r"^FIGURE\s+(\d+):\s*(.*)$")
TABLE_RE = re.compile(r"^TABLE\s+(\d+):\s*(.*)$")
FOOTNOTE_RE = re.compile(r"^(\d+)\.\s+(.*)$")
ENUM_RE = re.compile(r"^(\d+)\.\s+(.*)$")


def basic_clean(raw: str) -> str:
    text = raw.replace("\ufeff", "").replace("\x08", "").replace("\x0c", "")
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    return text.rstrip("\n")


def normalized(text: str) -> str:
    text = basic_clean(text).strip()
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    text = text.replace("–", "--").replace("—", "---")
    while True:
        updated = re.sub(r"^([A-Z])\s{2,}([A-Z])", r"\1\2", text)
        if updated == text:
            break
        text = updated
    return re.sub(r"\s+", " ", text).strip()


def is_intro_start(item: dict[str, object]) -> bool:
    raw = basic_clean(str(item["raw"])).lstrip()
    text = str(item["text"])
    if DROP_CAP_RE.match(raw):
        return True
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    uppercase_ratio = sum(ch.isupper() for ch in letters) / len(letters)
    return uppercase_ratio > 0.8 and len(text.split()) >= 6


def escape_text(text: str) -> str:
    text = text.replace("\\", r"\textbackslash{}")
    text = text.replace("&", r"\&")
    text = text.replace("%", r"\%")
    text = text.replace("$", r"\$")
    text = text.replace("#", r"\#")
    text = text.replace("_", r"\_")
    return text


def parse_toc(lines: list[str]) -> dict[str, list[str]]:
    toc: dict[str, list[str]] = {}
    current: str | None = None
    for raw in lines[289:445]:
        text = normalized(raw)
        if not text:
            continue
        text = re.sub(r"\s+\d+\s*$", "", text)
        if text.startswith("Part "):
            current = None
            continue
        if text in {"Glossary", "Appendices", "Acknowledgements", "Index"}:
            current = text
            toc.setdefault(text, [])
            continue
        if (
            text.startswith("Chapter ")
            or text.startswith("Appendix ")
            or text.startswith("Epilogue.")
        ):
            current = text
            toc.setdefault(text, [])
            continue
        if current is not None:
            toc[current].append(text)
    return toc


def load_slice(all_lines: list[str], start: int, end: int) -> list[dict[str, object]]:
    items = []
    for raw in all_lines[start - 1 : end - 1]:
        items.append(
            {
                "raw": basic_clean(raw),
                "text": normalized(raw),
                "had_formfeed": "\x0c" in raw,
            }
        )
    return items


def should_drop_header(text: str, full_label: str, short_title: str) -> bool:
    if not text:
        return False
    if text in {
        "Systematic Trading",
        "Contents",
        "Glossary",
        "Index",
        "Framework",
        "Practice",
        "Toolbox",
        "Theory",
        "Appendices",
    }:
        return True
    if text == full_label or text == short_title:
        return True
    if text.startswith("Chapter ") and short_title in text:
        return True
    if text.startswith("Appendix ") and short_title in text:
        return True
    return bool(re.fullmatch(r"\d{1,4}", text))


def extract_footnotes(
    items: list[dict[str, object]], full_label: str, short_title: str
) -> tuple[list[dict[str, object]], dict[str, str]]:
    kept: list[dict[str, object]] = []
    footnotes: dict[str, str] = {}
    i = 0
    while i < len(items):
        text = str(items[i]["text"])
        if should_drop_header(text, full_label, short_title):
            i += 1
            continue
        match = FOOTNOTE_RE.match(text)
        if match:
            lookahead = items[i + 1 : i + 6]
            if any(
                item["had_formfeed"] or re.fullmatch(r"\d{1,4}", str(item["text"]))
                for item in lookahead
            ):
                number = match.group(1)
                parts = [match.group(2)]
                j = i + 1
                while j < len(items):
                    next_text = str(items[j]["text"])
                    if not next_text:
                        j += 1
                        continue
                    if should_drop_header(next_text, full_label, short_title):
                        break
                    if FOOTNOTE_RE.match(next_text):
                        break
                    parts.append(next_text)
                    j += 1
                footnotes[number] = " ".join(parts)
                i = j
                continue
        kept.append(items[i])
        i += 1
    return kept, footnotes


def apply_footnotes(text: str, footnotes: dict[str, str]) -> str:
    placeholders: dict[str, str] = {}
    token_idx = 0
    for number, note in sorted(footnotes.items(), key=lambda item: -len(item[0])):
        token = f"FOOTNOTEPLACEHOLDER{token_idx}"
        repl = rf"\footnote{{{escape_text(note)}}}"
        patterns = [
            re.compile(rf"(?<=[^\s\d]){re.escape(number)}(?=\s)"),
            re.compile(rf"(?<=[^\s\d]){re.escape(number)}(?=[\.,;:!\?])"),
        ]
        for pattern in patterns:
            if pattern.search(text):
                text = pattern.sub(token, text, count=1)
                placeholders[token] = repl
                token_idx += 1
                break
    text = escape_text(text)
    for token, repl in placeholders.items():
        text = text.replace(token, repl)
    return text


def join_paragraph(lines: list[str], footnotes: dict[str, str]) -> str:
    parts: list[str] = []
    for line in lines:
        line = normalized(line)
        if not line:
            continue
        if not parts:
            parts.append(line)
            continue
        if re.search(r"[A-Za-z]-$", parts[-1]) and not parts[-1].endswith("--"):
            parts[-1] = parts[-1][:-1] + line
        else:
            parts.append(line)
    return apply_footnotes(" ".join(parts), footnotes)


def collect_caption(items: list[dict[str, object]], i: int, initial: str) -> tuple[str, int]:
    caption = [initial]
    i += 1
    while i < len(items):
        text = str(items[i]["text"])
        if not text:
            break
        if any(ch.islower() for ch in text):
            break
        if FIGURE_RE.match(text) or TABLE_RE.match(text):
            break
        caption.append(text)
        i += 1
    return " ".join(caption), i


def looks_like_heading(text: str) -> bool:
    if not text or text.endswith("."):
        return False
    if text in KNOWN_AUDIENCE_TITLES:
        return False
    if FIGURE_RE.match(text) or TABLE_RE.match(text):
        return False
    if ENUM_RE.match(text):
        return False
    if len(text.split()) > 8:
        return False
    if len(text) > 60:
        return False
    return text[0].isupper() and any(ch.islower() for ch in text)


def next_nonempty_index(items: list[dict[str, object]], i: int) -> int | None:
    while i < len(items):
        if str(items[i]["text"]):
            return i
        i += 1
    return None


def looks_like_subheading(
    items: list[dict[str, object]], i: int, section_titles: set[str]
) -> bool:
    text = str(items[i]["text"])
    if not looks_like_heading(text):
        return False
    nxt_idx = next_nonempty_index(items, i + 1)
    if nxt_idx is None:
        return True
    nxt = str(items[nxt_idx]["text"])
    if nxt in section_titles or nxt in KNOWN_AUDIENCE_TITLES:
        return True
    if FIGURE_RE.match(nxt) or TABLE_RE.match(nxt):
        return True
    first_word = nxt.split()[0] if nxt.split() else ""
    if first_word and first_word[0].islower():
        return False
    return True


def next_nonempty(items: list[dict[str, object]], i: int) -> str:
    while i < len(items):
        text = str(items[i]["text"])
        if text:
            return text
        i += 1
    return ""


def collect_raw_block(
    items: list[dict[str, object]],
    i: int,
    stop_titles: set[str],
) -> tuple[list[str], int]:
    raw_lines: list[str] = []
    while i < len(items):
        text = str(items[i]["text"])
        raw = str(items[i]["raw"]).replace("\x0c", "")
        if text in stop_titles or FIGURE_RE.match(text) or TABLE_RE.match(text):
            break
        if not text:
            nxt = next_nonempty(items, i + 1)
            if not nxt:
                break
            if nxt in stop_titles or FIGURE_RE.match(nxt) or TABLE_RE.match(nxt):
                break
            if nxt in KNOWN_AUDIENCE_TITLES:
                break
            if any(nxt.startswith(prefix) for prefix in RAW_TABLE_NOTES):
                break
            raw_lines.append("")
            i += 1
            continue
        if any(text.startswith(prefix) for prefix in RAW_TABLE_NOTES):
            break
        raw_lines.append(raw.rstrip())
        i += 1
    while raw_lines and not raw_lines[-1]:
        raw_lines.pop()
    return raw_lines, i


def collect_enumerate(
    items: list[dict[str, object]], i: int, footnotes: dict[str, str]
) -> tuple[list[str], int]:
    entries: list[list[str]] = []
    current: list[str] = []
    while i < len(items):
        text = str(items[i]["text"])
        if not text:
            if current:
                entries.append(current)
                current = []
            i += 1
            nxt = next_nonempty(items, i)
            if not ENUM_RE.match(nxt):
                break
            continue
        match = ENUM_RE.match(text)
        if match:
            if current:
                entries.append(current)
            current = [match.group(2)]
        else:
            if current:
                current.append(text)
            else:
                break
        i += 1
    if current:
        entries.append(current)
    rendered = [r"\begin{enumerate}"]
    for entry in entries:
        rendered.append(f"  \\item {join_paragraph(entry, footnotes)}")
    rendered.append(r"\end{enumerate}")
    return rendered, i


def collect_audience_box(
    items: list[dict[str, object]], i: int, section_titles: set[str]
) -> tuple[str, int]:
    titles = []
    while i < len(items):
        text = str(items[i]["text"])
        if text in KNOWN_AUDIENCE_TITLES and not text.startswith("This section is"):
            titles.append(text)
            i += 1
            while i < len(items) and not str(items[i]["text"]):
                i += 1
            continue
        break
    if not titles and i < len(items):
        text = str(items[i]["text"])
        if text.startswith("This section is"):
            titles.append(text)
            i += 1
    description: list[str] = []
    while i < len(items):
        text = str(items[i]["text"])
        if not text:
            nxt = next_nonempty(items, i + 1)
            next_is_intro = i + 1 < len(items) and is_intro_start(items[i + 1])
            if (
                not nxt
                or next_is_intro
                or nxt in section_titles
                or nxt in KNOWN_AUDIENCE_TITLES
                or FIGURE_RE.match(nxt)
                or TABLE_RE.match(nxt)
                or looks_like_heading(nxt)
            ):
                break
            i += 1
            continue
        if is_intro_start(items[i]):
            break
        if text in section_titles:
            break
        if text in KNOWN_AUDIENCE_TITLES and description:
            break
        if FIGURE_RE.match(text) or TABLE_RE.match(text):
            break
        description.append(text)
        i += 1
    title = " / ".join(titles) if titles else "Audience"
    body = escape_text(" ".join(description))
    if len(body.split()) > 80:
        return rf"\subsection*{{{escape_text(title)}}}" + "\n\n" + body, i
    return rf"\audiencebox{{{escape_text(title)}}}{{{body}}}", i


def render_parsed(config: dict[str, object], items: list[dict[str, object]], sections: list[str]) -> str:
    full_label = str(config.get("toc_label", config["title"]))
    short_title = str(config["title"])
    items, footnotes = extract_footnotes(items, full_label, short_title)
    out: list[str] = []
    kind = str(config["kind"])
    if kind == "chapter":
        out.extend([rf"\chapter{{{escape_text(short_title)}}}", ""])
    elif kind == "appendix":
        out.extend([rf"\chapter{{{escape_text(short_title)}}}", ""])
    else:
        toc_title = str(config["toc_title"])
        out.extend(
            [
                rf"\chapter*{{{escape_text(short_title)}}}",
                r"\phantomsection",
                rf"\addcontentsline{{toc}}{{chapter}}{{{escape_text(toc_title)}}}",
                rf"\markboth{{{escape_text(short_title)}}}{{{escape_text(short_title)}}}",
                "",
            ]
        )

    section_titles = set(sections)
    i = 0
    intro_started = kind == "appendix"
    while i < len(items):
        text = str(items[i]["text"])
        raw = str(items[i]["raw"])
        if not intro_started:
            if not text:
                i += 1
                continue
            if text in KNOWN_AUDIENCE_TITLES:
                audience_box, i = collect_audience_box(items, i, section_titles)
                out.extend([audience_box, ""])
                continue
            if is_intro_start(items[i]):
                intro_started = True
            else:
                i += 1
                continue

        if not text:
            i += 1
            continue

        if text in section_titles:
            out.extend(
                [
                    rf"\section*{{{escape_text(text)}}}",
                    r"\phantomsection",
                    rf"\addcontentsline{{toc}}{{section}}{{{escape_text(text)}}}",
                    "",
                ]
            )
            if text == "Chapter overview":
                i += 1
                raw_lines, i = collect_raw_block(items, i, section_titles)
                if raw_lines:
                    out.extend([r"\begin{OCRVerbatim}"])
                    out.extend(raw_lines)
                    out.extend([r"\end{OCRVerbatim}", ""])
                continue
            i += 1
            continue

        if text in KNOWN_AUDIENCE_TITLES:
            audience_box, i = collect_audience_box(items, i, section_titles)
            out.extend([audience_box, ""])
            continue

        figure_match = FIGURE_RE.match(text)
        if figure_match:
            number = int(figure_match.group(1))
            caption, i = collect_caption(items, i, figure_match.group(2))
            if number in FIGURE_MAP:
                out.extend(
                    [
                        r"\begin{figure}[htbp]",
                        r"  \centering",
                        rf"  \includegraphics[width=\textwidth]{{figures/raw/{FIGURE_MAP[number]}}}",
                        rf"  \caption{{{escape_text(caption)}}}",
                        r"\end{figure}",
                        "",
                    ]
                )
            else:
                out.extend(
                    [
                        rf"\rawfigurecaption{{{escape_text(caption)}}}",
                        r"\begin{OCRVerbatim}",
                    ]
                )
                raw_lines, i = collect_raw_block(items, i, section_titles)
                out.extend(raw_lines)
                out.extend([r"\end{OCRVerbatim}", ""])
            continue

        table_match = TABLE_RE.match(text)
        if table_match:
            caption, i = collect_caption(items, i, table_match.group(2))
            out.extend(
                [
                    rf"\rawtablecaption{{{escape_text(caption)}}}",
                    r"\begin{OCRVerbatim}",
                ]
            )
            raw_lines, i = collect_raw_block(items, i, section_titles)
            out.extend(raw_lines)
            out.extend([r"\end{OCRVerbatim}", ""])
            continue

        if looks_like_subheading(items, i, section_titles):
            out.extend([rf"\subsection*{{{escape_text(text)}}}", ""])
            i += 1
            continue

        if ENUM_RE.match(text):
            enum_block, i = collect_enumerate(items, i, footnotes)
            out.extend(enum_block)
            out.append("")
            continue

        paragraph_lines = [raw]
        i += 1
        while i < len(items):
            next_text = str(items[i]["text"])
            if not next_text:
                break
            if (
                next_text in section_titles
                or next_text in KNOWN_AUDIENCE_TITLES
                or FIGURE_RE.match(next_text)
                or TABLE_RE.match(next_text)
                or looks_like_subheading(items, i, section_titles)
                or ENUM_RE.match(next_text)
            ):
                break
            paragraph_lines.append(str(items[i]["raw"]))
            i += 1
        out.extend([join_paragraph(paragraph_lines, footnotes), ""])

    return "\n".join(out).strip() + "\n"


def render_raw_star(config: dict[str, object], items: list[dict[str, object]]) -> str:
    title = str(config["title"])
    toc_title = str(config["toc_title"])
    lines = [
        rf"\chapter*{{{escape_text(title)}}}",
        r"\phantomsection",
        rf"\addcontentsline{{toc}}{{chapter}}{{{escape_text(toc_title)}}}",
        rf"\markboth{{{escape_text(title)}}}{{{escape_text(title)}}}",
        "",
        r"\begin{OCRVerbatim}",
    ]
    for item in items:
        text = str(item["text"])
        if should_drop_header(text, toc_title, title):
            continue
        raw = str(item["raw"]).replace("\x0c", "")
        lines.append(raw.rstrip())
    lines.extend([r"\end{OCRVerbatim}", ""])
    return "\n".join(lines)


def postprocess_rendered(config: dict[str, object], rendered: str) -> str:
    if config["file"] != "appendix_d.tex":
        return rendered
    replacements = {
        "1/SQRT(MMULT(TRANSPOSE(F1:F3), MMULT(A1:C3,F1:F3)))": (
            "\\begin{OCRVerbatim}\n"
            "1/SQRT(MMULT(TRANSPOSE(F1:F3), MMULT(A1:C3,F1:F3)))\n"
            "\\end{OCRVerbatim}"
        ),
        "B2 = (A2 -- A1) / A1, B3 = (A3 -- A2) / A2, ...": (
            "\\begin{OCRVerbatim}\n"
            "B2 = (A2 - A1) / A1, B3 = (A3 - A2) / A2, ...\n"
            "\\end{OCRVerbatim}"
        ),
        "C26=STDEV(B2:B26), C27=STDEV(B3:B27), ...": (
            "\\begin{OCRVerbatim}\n"
            "C26=STDEV(B2:B26), C27=STDEV(B3:B27), ...\n"
            "\\end{OCRVerbatim}"
        ),
        "(A × Xt) + [Et-1 (1-A)]": (
            "\\begin{OCRVerbatim}\n"
            "(A × Xt) + [Et-1 (1-A)]\n"
            "\\end{OCRVerbatim}"
        ),
        "C2 = B2 ^ 2, C3 = B3 ^ 2, …": (
            "\\begin{OCRVerbatim}\n"
            "C2 = B2 ^ 2, C3 = B3 ^ 2, ...\n"
            "\\end{OCRVerbatim}"
        ),
        "D2 = C2": "\\begin{OCRVerbatim}\nD2 = C2\n\\end{OCRVerbatim}",
        "D3 = C3 × AA1 + ((1 -- AA1) × D2)\n\nD4 = C4 × AA1 + ((1 -- AA1) × D3) ...": (
            "\\begin{OCRVerbatim}\n"
            "D3 = C3 × AA1 + ((1 - AA1) × D2)\n\n"
            "D4 = C4 × AA1 + ((1 - AA1) × D3) ...\n"
            "\\end{OCRVerbatim}"
        ),
        "E2 = SQRT(D2), E3 = SQRT(D3), ...": (
            "\\begin{OCRVerbatim}\n"
            "E2 = SQRT(D2), E3 = SQRT(D3), ...\n"
            "\\end{OCRVerbatim}"
        ),
    }
    for old, new in replacements.items():
        rendered = rendered.replace(old, new)
    return rendered


def write_static_pages() -> None:
    CHAPTERS.joinpath("part_three.tex").write_text(
        "\n".join(
            [
                r"\cleardoublepage",
                r"\thispagestyle{empty}",
                r"\phantomsection",
                r"\addcontentsline{toc}{part}{Part Three. Framework}",
                "",
                r"\begin{center}",
                r"  \vspace*{0.28\textheight}",
                r"  {\Huge\bfseries PART THREE.\par}",
                r"  \vspace{1.2em}",
                r"  {\huge Framework\par}",
                r"\end{center}",
                "",
                r"\clearpage",
                "",
            ]
        ),
        encoding="utf-8",
    )
    CHAPTERS.joinpath("part_four.tex").write_text(
        "\n".join(
            [
                r"\cleardoublepage",
                r"\thispagestyle{empty}",
                r"\phantomsection",
                r"\addcontentsline{toc}{part}{Part Four. Practice}",
                "",
                r"\begin{center}",
                r"  \vspace*{0.28\textheight}",
                r"  {\Huge\bfseries PART FOUR.\par}",
                r"  \vspace{1.2em}",
                r"  {\huge Practice\par}",
                r"\end{center}",
                "",
                r"\clearpage",
                "",
            ]
        ),
        encoding="utf-8",
    )
    CHAPTERS.joinpath("appendices.tex").write_text(
        "\n".join(
            [
                r"\cleardoublepage",
                r"\thispagestyle{empty}",
                r"\phantomsection",
                r"\addcontentsline{toc}{chapter}{Appendices}",
                "",
                r"\begin{center}",
                r"  \vspace*{0.28\textheight}",
                r"  {\Huge\bfseries Appendices\par}",
                r"\end{center}",
                "",
                r"\clearpage",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    all_lines = LAYOUT.read_text(encoding="utf-8").split("\n")
    write_static_pages()
    for config in CONFIGS:
        items = load_slice(all_lines, int(config["start"]), int(config["end"]))
        out_path = CHAPTERS / str(config["file"])
        kind = str(config["kind"])
        if kind == "raw_star":
            rendered = render_raw_star(config, items)
        else:
            sections = SECTION_MAP.get(str(config.get("toc_label", "")), [])
            rendered = render_parsed(config, items, sections)
        rendered = postprocess_rendered(config, rendered)
        out_path.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()

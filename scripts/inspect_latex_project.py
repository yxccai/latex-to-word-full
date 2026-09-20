#!/usr/bin/env python3
"""Inventory an academic source project before generating a functional DOCX.

This is intentionally conservative: it reports likely structures and missing
assets without claiming to be a complete TeX/Markdown parser.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


TEXT_EXTENSIONS = {".tex", ".md", ".markdown", ".qmd", ".rst", ".bib", ".bbl", ".csl", ".json"}
ASSET_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg", ".svg", ".eps", ".webp")


def unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def choose_entry(path: Path) -> Path:
    if path.is_file():
        return path
    candidates = [
        path / "main.tex",
        path / "main.md",
        path / "main.qmd",
        path / "README.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    discovered = sorted(
        p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in {".tex", ".md", ".qmd"}
    )
    if discovered:
        return discovered[0]
    raise FileNotFoundError(f"No TeX/Markdown entry point found under {path}")


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def split_keys(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def resolve_candidate(
    raw: str,
    source_file: Path,
    root: Path,
    extra_roots: Iterable[str] = (),
) -> Path | None:
    raw_path = raw.strip().strip('"\'')
    if raw_path.startswith("http://") or raw_path.startswith("https://") or raw_path.startswith("data:"):
        return None
    candidates = [source_file.parent / raw_path]
    candidates.extend(source_file.parent / base / raw_path for base in extra_roots)
    candidates.extend([root / raw_path])
    candidates.extend(root / base / raw_path for base in extra_roots)
    if not Path(raw_path).suffix:
        candidates.extend(source_file.parent / (raw_path + ext) for ext in ASSET_EXTENSIONS)
        candidates.extend(source_file.parent / base / (raw_path + ext) for base in extra_roots for ext in ASSET_EXTENSIONS)
        candidates.extend(root / (raw_path + ext) for ext in ASSET_EXTENSIONS)
        candidates.extend(root / base / (raw_path + ext) for base in extra_roots for ext in ASSET_EXTENSIONS)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def scan_file(path: Path, root: Path, visited: set[Path]) -> tuple[dict, list[Path]]:
    path = path.resolve()
    if path in visited:
        return {}, []
    visited.add(path)
    text = read_text(path)

    labels = re.findall(r"\\label\{([^{}]+)\}", text)
    includes = re.findall(r"\\(?:input|include)\{([^{}]+)\}", text)
    cite_keys: list[str] = []
    cite_pattern = re.compile(r"\\(?:cite|citep|citet|citeauthor|citeyear)[A-Za-z*]*(?:\[[^]]*\])?\s*\{([^{}]+)\}")
    for match in cite_pattern.finditer(text):
        cite_keys.extend(split_keys(match.group(1)))
    cite_keys.extend(re.findall(r"@([A-Za-z][A-Za-z0-9_:.\-/]*)", text))

    figures = re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^{}]+)\}", text)
    figures.extend(re.findall(r"!\[[^]]*\]\(([^)\s]+)", text))
    graphic_roots: list[str] = []
    for match in re.finditer(r"\\graphicspath\s*\{((?:\{[^}]*\}\s*)+)\}", text):
        graphic_roots.extend(re.findall(r"\{([^}]*)\}", match.group(1)))
    captions = re.findall(r"\\caption\{([^{}]*)\}", text)
    captions.extend(re.findall(r"^\s*(?:Table|Figure)\s*:?\s*(.+)$", text, flags=re.MULTILINE | re.IGNORECASE))
    equations = re.findall(r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?)\}", text)
    equations += re.findall(r"(?<!\\)\\\[|(?<!\\)\$\$", text)
    tables = re.findall(r"\\begin\{(table\*?|tabular\*?|longtable)\}", text)
    markdown_table_rows = [line for line in text.splitlines() if line.strip().startswith("|") and "|" in line.strip()[1:]]
    headings = re.findall(r"\\(?:part|chapter|section|subsection|subsubsection|paragraph)\*?\s*\{", text)
    headings += re.findall(r"^\s{0,3}#{1,6}\s+", text, flags=re.MULTILINE)

    assets: list[str] = []
    missing_assets: list[str] = []
    for raw in figures:
        resolved = resolve_candidate(raw, path, root, graphic_roots)
        if resolved is None:
            missing_assets.append(raw)
        else:
            assets.append(str(resolved))

    child_paths: list[Path] = []
    for raw in includes:
        include = raw.strip()
        candidate = resolve_candidate(include, path, root)
        if candidate is None:
            for ext in (".tex", ".md", ".qmd"):
                maybe = path.parent / (include + ext)
                if maybe.exists():
                    candidate = maybe.resolve()
                    break
        if candidate is not None and candidate.suffix.lower() in {".tex", ".md", ".qmd"}:
            child_paths.append(candidate)

    result = {
        "files": [str(path)],
        "labels": labels,
        "citations": cite_keys,
        "includes": includes,
        "figures": figures,
        "captions": captions,
        "equation_environments": equations,
        "table_environments": tables,
        "markdown_table_rows": len(markdown_table_rows),
        "heading_markers": len(headings),
        "assets": assets,
        "missing_assets": missing_assets,
    }
    return result, child_paths


def merge_reports(reports: list[dict]) -> dict:
    merged: dict[str, object] = {
        "files": [],
        "labels": [],
        "citations": [],
        "includes": [],
        "figures": [],
        "captions": [],
        "equation_environments": [],
        "table_environments": [],
        "markdown_table_rows": 0,
        "heading_markers": 0,
        "assets": [],
        "missing_assets": [],
    }
    list_keys = [
        "files", "labels", "citations", "includes", "figures", "captions",
        "equation_environments", "table_environments", "assets", "missing_assets",
    ]
    for report in reports:
        for key in list_keys:
            merged[key] = unique([*merged[key], *report.get(key, [])])  # type: ignore[index]
        merged["markdown_table_rows"] += int(report.get("markdown_table_rows", 0))
        merged["heading_markers"] += int(report.get("heading_markers", 0))
    return merged


def bibliography_inventory(root: Path) -> dict[str, object]:
    bib_files = sorted(root.rglob("*.bib"))
    keys: list[str] = []
    for bib in bib_files:
        text = read_text(bib)
        keys.extend(re.findall(r"@\w+\s*\{\s*([^,\s]+)", text))
    return {"files": [str(p.resolve()) for p in bib_files], "keys": unique(keys)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="entry .tex/.md file or project directory")
    parser.add_argument("--json-out", type=Path, help="write the inventory as JSON")
    args = parser.parse_args()

    try:
        entry = choose_entry(args.input)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    root = entry.parent if args.input.is_file() else args.input
    visited: set[Path] = set()
    queue = [entry]
    reports: list[dict] = []
    while queue:
        current = queue.pop(0)
        report, children = scan_file(current, root.resolve(), visited)
        if report:
            reports.append(report)
        queue.extend(child for child in children if child not in visited)

    inventory = {
        "entry": str(entry.resolve()),
        "root": str(root.resolve()),
        "source": merge_reports(reports),
        "bibliography": bibliography_inventory(root.resolve()),
        "notes": [
            "This is a preflight inventory, not a full TeX/Markdown parser.",
            "Inspect custom macros, generated assets, and source-specific build steps before conversion.",
        ],
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")

    source = inventory["source"]
    bibliography = inventory["bibliography"]
    print(f"entry: {inventory['entry']}")
    print(f"source files: {len(source['files'])}")
    print(f"headings: {source['heading_markers']}")
    print(f"labels: {len(source['labels'])}")
    print(f"citations: {len(source['citations'])} references to {len(unique(source['citations']))} keys")
    print(f"figures/assets: {len(source['figures'])} / {len(source['assets'])} resolved")
    print(f"captions: {len(source['captions'])}")
    print(f"equation markers: {len(source['equation_environments'])}")
    print(f"table environments: {len(source['table_environments'])}; Markdown table rows: {source['markdown_table_rows']}")
    print(f"bibliography files: {len(bibliography['files'])}; keys: {len(bibliography['keys'])}")
    if source["missing_assets"]:
        print("missing assets:")
        for item in source["missing_assets"]:
            print(f"  - {item}")
    if args.json_out:
        print(f"json: {args.json_out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

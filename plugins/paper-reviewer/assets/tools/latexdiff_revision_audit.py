#!/usr/bin/env python3
"""Build latexdiff and structured change artifacts for draft-paper-reviewer."""

from __future__ import annotations

import argparse
import csv
import difflib
import re
import shutil
import subprocess
import sys
from pathlib import Path


INPUT_COMMAND_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")

CHANGE_FIELDS = [
    "change_id",
    "change_type",
    "old_start_line",
    "old_end_line",
    "new_start_line",
    "new_end_line",
    "old_source_location",
    "new_source_location",
    "old_excerpt",
    "new_excerpt",
    "scope_guess",
    "latexdiff_hint",
    "review_trace_hint",
    "needs_agent_recheck",
    "notes",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def resolve_tex_reference(reference: str, base_dir: Path) -> Path | None:
    reference = reference.strip()
    if not reference:
        return None
    candidate = (base_dir / reference).expanduser()
    candidates = [candidate]
    if candidate.suffix == "":
        candidates.append(candidate.with_suffix(".tex"))
    for item in candidates:
        if item.exists() and item.is_file():
            return item.resolve()
    return None


def flatten_tex_units(path: Path, stack: tuple[Path, ...] = ()) -> list[dict[str, str]]:
    path = path.resolve()
    if path in stack:
        return [
            {
                "text": f"% draft-paper-reviewer skipped recursive input: {path}",
                "source": str(path),
                "line": "",
            }
        ]

    units: list[dict[str, str]] = []
    for line_number, line in enumerate(read_text(path).splitlines(), start=1):
        units.append({"text": line, "source": str(path), "line": str(line_number)})
        stripped = line.lstrip()
        if stripped.startswith("%"):
            continue
        for match in INPUT_COMMAND_RE.finditer(line):
            included = resolve_tex_reference(match.group(1), path.parent)
            if included is None:
                units.append(
                    {
                        "text": f"% draft-paper-reviewer unresolved input: {match.group(1)}",
                        "source": str(path),
                        "line": str(line_number),
                    }
                )
                continue
            units.extend(flatten_tex_units(included, stack + (path,)))
    return units


def flatten_tex_text(path: Path) -> str:
    return "\n".join(unit["text"] for unit in flatten_tex_units(path))


def find_tex_root(path: Path) -> Path:
    path = path.resolve()
    if path.is_file():
        if path.suffix.lower() != ".tex":
            raise SystemExit(f"Expected a .tex file: {path}")
        return path
    if not path.is_dir():
        raise SystemExit(f"TeX path not found: {path}")

    candidates = sorted(path.rglob("*.tex"))
    roots = []
    for candidate in candidates:
        text = read_text(candidate)
        if "\\documentclass" in text:
            roots.append(candidate)
    if len(roots) == 1:
        return roots[0]
    if roots:
        roots.sort(key=lambda item: (len(item.parts), str(item)))
        return roots[0]
    if len(candidates) == 1:
        return candidates[0]
    raise SystemExit(f"Could not infer TeX root under: {path}")


def scope_guess(lines: list[str]) -> str:
    joined = "\n".join(lines)
    patterns = [
        (r"\\section\*?\{([^}]+)\}", "section"),
        (r"\\subsection\*?\{([^}]+)\}", "subsection"),
        (r"\\begin\{abstract\}", "abstract"),
        (r"\\begin\{table", "table"),
        (r"\\begin\{figure", "figure"),
        (r"\\begin\{equation", "equation"),
        (r"\\begin\{algorithm", "algorithm"),
    ]
    for pattern, label in patterns:
        match = re.search(pattern, joined, flags=re.IGNORECASE)
        if not match:
            continue
        if match.groups():
            return f"{label}:{match.group(1).strip()}"
        return label
    if "\\cite" in joined:
        return "citation_context"
    if "\\caption" in joined:
        return "caption"
    if "$" in joined or "\\[" in joined or "\\(" in joined:
        return "math_or_notation"
    return "text"


def clean_excerpt(lines: list[str], max_chars: int = 900) -> str:
    text = "\n".join(line.rstrip("\n") for line in lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


def source_span(units: list[dict[str, str]]) -> str:
    if not units:
        return ""

    spans: list[tuple[str, str, str]] = []
    current_source = ""
    start_line = ""
    end_line = ""

    for unit in units:
        source = unit["source"]
        line = unit["line"]
        if source != current_source or (end_line.isdigit() and line.isdigit() and int(line) != int(end_line) + 1):
            if current_source:
                spans.append((current_source, start_line, end_line))
            current_source = source
            start_line = line
            end_line = line
        else:
            end_line = line

    if current_source:
        spans.append((current_source, start_line, end_line))

    formatted = []
    for source, start, end in spans[:5]:
        if start and end and start != end:
            formatted.append(f"{source}:{start}-{end}")
        elif start:
            formatted.append(f"{source}:{start}")
        else:
            formatted.append(source)
    if len(spans) > 5:
        formatted.append(f"... +{len(spans) - 5} more spans")
    return "; ".join(formatted)


def build_changes(old_units: list[dict[str, str]], new_units: list[dict[str, str]]) -> list[dict[str, str]]:
    old_lines = [unit["text"] for unit in old_units]
    new_lines = [unit["text"] for unit in new_units]
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    rows: list[dict[str, str]] = []
    counter = 1
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        old_chunk = old_lines[i1:i2]
        new_chunk = new_lines[j1:j2]
        old_chunk_units = old_units[i1:i2]
        new_chunk_units = new_units[j1:j2]
        change_type = {"replace": "REPLACE", "delete": "DELETE", "insert": "ADD"}.get(tag, tag.upper())
        old_start = "" if i1 == i2 else str(i1 + 1)
        old_end = "" if i1 == i2 else str(i2)
        new_start = "" if j1 == j2 else str(j1 + 1)
        new_end = "" if j1 == j2 else str(j2)
        rows.append(
            {
                "change_id": f"CHG-{counter:04d}",
                "change_type": change_type,
                "old_start_line": old_start,
                "old_end_line": old_end,
                "new_start_line": new_start,
                "new_end_line": new_end,
                "old_source_location": source_span(old_chunk_units),
                "new_source_location": source_span(new_chunk_units),
                "old_excerpt": clean_excerpt(old_chunk),
                "new_excerpt": clean_excerpt(new_chunk),
                "scope_guess": scope_guess(new_chunk or old_chunk),
                "latexdiff_hint": latexdiff_hint(change_type),
                "review_trace_hint": "",
                "needs_agent_recheck": "UNKNOWN",
                "notes": "",
            }
        )
        counter += 1
    return rows


def latexdiff_hint(change_type: str) -> str:
    if change_type == "ADD":
        return "New text should appear as DIFadd in latexdiff output."
    if change_type == "DELETE":
        return "Removed text should appear as DIFdel in latexdiff output."
    if change_type == "REPLACE":
        return "Replacement should contain nearby DIFdel and DIFadd blocks."
    return "Inspect latexdiff output."


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHANGE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def write_markdown(
    rows: list[dict[str, str]],
    path: Path,
    status: str,
    old_root: Path,
    new_root: Path,
    diff_path: Path,
    pdf_path: Path,
    pdf_status: str,
    pdf_notes: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["change_type"]] = counts.get(row["change_type"], 0) + 1
    lines = [
        "# 100 Latexdiff Change Extraction",
        "",
        "## STATUS",
        f"STATUS: {status}",
        "",
        "## Inputs",
        f"- Old TeX Root: `{old_root}`",
        f"- New TeX Root: `{new_root}`",
        f"- Latexdiff TeX: `{diff_path}`",
        f"- Latexdiff PDF: `{pdf_path}`",
        f"- PDF Compile Status: `{pdf_status}`",
        "- Structured line numbers refer to the flattened TeX stream; source-location columns identify the original TeX file spans.",
    ]
    if pdf_notes:
        lines.extend(["", "## PDF Compile Notes", "```text", pdf_notes, "```"])
    lines.extend(
        [
            "",
            "## Change Counts",
            f"- ADD: {counts.get('ADD', 0)}",
            f"- DELETE: {counts.get('DELETE', 0)}",
            f"- REPLACE: {counts.get('REPLACE', 0)}",
            f"- Total: {len(rows)}",
            "",
            "## Change Index",
            "| Change ID | Type | Old Lines | New Lines | Source Location | Scope Guess |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in rows:
        old_lines = line_range(row["old_start_line"], row["old_end_line"])
        new_lines = line_range(row["new_start_line"], row["new_end_line"])
        source_location = row["new_source_location"] or row["old_source_location"]
        lines.append(
            f"| {row['change_id']} | {row['change_type']} | {old_lines} | {new_lines} | "
            f"{md_cell(source_location)} | {md_cell(row['scope_guess'])} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_tex_summary(
    rows: list[dict[str, str]],
    path: Path,
    status: str,
    old_root: Path,
    new_root: Path,
    diff_path: Path,
    pdf_path: Path,
    pdf_status: str,
    pdf_notes: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [
        r"\documentclass{article}",
        r"\usepackage[margin=1in]{geometry}",
        r"\usepackage{longtable}",
        r"\usepackage[T1]{fontenc}",
        r"\begin{document}",
        r"\section*{100 Latexdiff Change Extraction}",
        rf"\textbf{{STATUS:}} {latex_escape(status)}\\",
        rf"\textbf{{Old TeX Root:}} \texttt{{{latex_escape(str(old_root))}}}\\",
        rf"\textbf{{New TeX Root:}} \texttt{{{latex_escape(str(new_root))}}}\\",
        rf"\textbf{{Latexdiff TeX:}} \texttt{{{latex_escape(str(diff_path))}}}\\",
        rf"\textbf{{Latexdiff PDF:}} \texttt{{{latex_escape(str(pdf_path))}}}\\",
        rf"\textbf{{PDF Compile Status:}} {latex_escape(pdf_status)}",
        r"\par Structured line numbers refer to the flattened TeX stream; source locations identify original TeX file spans.",
    ]
    if pdf_notes:
        body.extend(
            [
                r"\subsection*{PDF Compile Notes}",
                r"\begin{verbatim}",
                pdf_notes[:3000],
                r"\end{verbatim}",
            ]
        )
    body.extend(
        [
            r"\begin{longtable}{llllp{0.42\linewidth}}",
            r"Change ID & Type & Old Lines & New Lines & Source Location \\",
            r"\hline",
        ]
    )
    for row in rows:
        source_location = row["new_source_location"] or row["old_source_location"]
        body.append(
            " & ".join(
                [
                    latex_escape(row["change_id"]),
                    latex_escape(row["change_type"]),
                    latex_escape(line_range(row["old_start_line"], row["old_end_line"])),
                    latex_escape(line_range(row["new_start_line"], row["new_end_line"])),
                    latex_escape(source_location),
                ]
            )
            + r" \\"
        )
    body.extend([r"\end{longtable}", r"\end{document}"])
    path.write_text("\n".join(body) + "\n", encoding="utf-8")


def line_range(start: str, end: str) -> str:
    if not start:
        return ""
    if start == end:
        return start
    return f"{start}-{end}"


def wrap_unified_diff_as_latex(diff_text: str, old_root: Path, new_root: Path) -> str:
    return "\n".join(
        [
            r"\documentclass{article}",
            r"\usepackage[margin=0.7in]{geometry}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[utf8]{inputenc}",
            r"\begin{document}",
            r"\section*{Latexdiff Unavailable: Unified Diff Fallback}",
            rf"\textbf{{Old TeX Root:}} \texttt{{{latex_escape(str(old_root))}}}\\",
            rf"\textbf{{New TeX Root:}} \texttt{{{latex_escape(str(new_root))}}}",
            r"\par This PDF is a unified-diff fallback because the system latexdiff command was unavailable.",
            r"\small",
            r"\begin{verbatim}",
            diff_text,
            r"\end{verbatim}",
            r"\end{document}",
        ]
    )


def run_latexdiff(old_root: Path, new_root: Path, diff_path: Path) -> tuple[str, str]:
    latexdiff = shutil.which("latexdiff")
    if not latexdiff:
        fallback = "\n".join(
            difflib.unified_diff(
                flatten_tex_text(old_root).splitlines(),
                flatten_tex_text(new_root).splitlines(),
                fromfile=f"{old_root} (flattened)",
                tofile=f"{new_root} (flattened)",
                lineterm="",
            )
        )
        diff_path.parent.mkdir(parents=True, exist_ok=True)
        diff_path.write_text(wrap_unified_diff_as_latex(fallback, old_root, new_root) + "\n", encoding="utf-8")
        return "LATEXDIFF_UNAVAILABLE_FALLBACK_WRITTEN", "latexdiff executable not found"
    command = [latexdiff, "--flatten", str(old_root), str(new_root)]
    result = subprocess.run(command, cwd=str(new_root.parent), text=True, capture_output=True, check=False)
    diff_path.parent.mkdir(parents=True, exist_ok=True)
    if result.stdout:
        diff_path.write_text(result.stdout, encoding="utf-8")
    else:
        diff_path.write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        return "LATEXDIFF_FAILED_OUTPUT_CAPTURED", result.stderr.strip()
    return "LATEXDIFF_READY", ""


def output_tail(result: subprocess.CompletedProcess[str]) -> str:
    output = "\n".join(part for part in [result.stdout, result.stderr] if part).strip()
    if len(output) > 3000:
        return output[-3000:]
    return output


def run_compile_command(command: list[str], cwd: Path) -> tuple[int, str]:
    try:
        result = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, check=False, timeout=120)
    except subprocess.TimeoutExpired as exc:
        output = "\n".join(part for part in [exc.stdout or "", exc.stderr or ""] if part).strip()
        return 124, f"Command timed out after 120 seconds.\n{output}"
    return result.returncode, output_tail(result)


def clean_latex_aux_files(diff_path: Path) -> None:
    for suffix in [".aux", ".fls", ".fdb_latexmk", ".log", ".out", ".toc", ".synctex.gz"]:
        aux_path = diff_path.with_suffix(suffix)
        if aux_path.exists():
            aux_path.unlink()


def compile_latexdiff_pdf(diff_path: Path, new_root: Path, status: str) -> tuple[Path, str, str]:
    pdf_path = diff_path.with_suffix(".pdf")
    if status not in {"LATEXDIFF_READY", "LATEXDIFF_UNAVAILABLE_FALLBACK_WRITTEN"}:
        return pdf_path, "PDF_SKIPPED_DIFF_NOT_COMPILABLE", f"latexdiff status was {status}"

    diff_dir = diff_path.parent.resolve()
    cwd = new_root.parent.resolve()
    attempts: list[tuple[str, list[str]]] = []

    latexmk = shutil.which("latexmk")
    if latexmk:
        attempts.append(
            (
                "latexmk",
                [
                    latexmk,
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    f"-outdir={diff_dir}",
                    str(diff_path.resolve()),
                ],
            )
        )

    for engine_name in ["pdflatex", "xelatex", "lualatex"]:
        engine = shutil.which(engine_name)
        if not engine:
            continue
        attempts.append(
            (
                engine_name,
                [
                    engine,
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-file-line-error",
                    "-output-directory",
                    str(diff_dir),
                    str(diff_path.resolve()),
                ],
            )
        )

    if not attempts:
        return pdf_path, "PDF_COMPILER_UNAVAILABLE", "No LaTeX PDF compiler found: latexmk, pdflatex, xelatex, or lualatex."

    failure_notes = []
    for label, command in attempts:
        returncode, output = run_compile_command(command, cwd)
        if returncode == 0 and pdf_path.exists():
            clean_latex_aux_files(diff_path)
            return pdf_path, "PDF_READY", f"Compiled with {label}."
        failure_notes.append(f"[{label}] exit={returncode}\n{output}")

    notes = "\n\n".join(failure_notes)
    if len(notes) > 5000:
        notes = notes[-5000:]
    return pdf_path, "PDF_COMPILE_FAILED", notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old-root", required=True, type=Path, help="Original TeX root file or source directory.")
    parser.add_argument("--new-root", required=True, type=Path, help="Revised TeX root file or source directory.")
    parser.add_argument("--out-root", default=Path("workspace/work/paper-reviewer"), type=Path)
    args = parser.parse_args()

    old_root = find_tex_root(args.old_root)
    new_root = find_tex_root(args.new_root)
    out_root = args.out_root
    diff_path = out_root / "diff" / "latexdiff.tex"
    pdf_path = out_root / "diff" / "latexdiff.pdf"
    csv_path = out_root / "reports" / "100_latexdiff_changes.csv"
    md_path = out_root / "reports" / "100_latexdiff_extraction.md"
    tex_summary_path = out_root / "reports" / "100_latexdiff_extraction.tex"

    status, notes = run_latexdiff(old_root, new_root, diff_path)
    pdf_path, pdf_status, pdf_notes = compile_latexdiff_pdf(diff_path, new_root, status)
    rows = build_changes(flatten_tex_units(old_root), flatten_tex_units(new_root))
    if notes:
        for row in rows:
            row["notes"] = notes
    write_csv(rows, csv_path)
    write_markdown(rows, md_path, status, old_root, new_root, diff_path, pdf_path, pdf_status, pdf_notes)
    write_tex_summary(rows, tex_summary_path, status, old_root, new_root, diff_path, pdf_path, pdf_status, pdf_notes)
    print(f"Latexdiff status: {status}")
    print(f"Wrote diff TeX: {diff_path}")
    print(f"PDF compile status: {pdf_status}")
    print(f"Wrote diff PDF: {pdf_path}")
    print(f"Wrote change CSV: {csv_path}")
    print(f"Wrote extraction report: {md_path}")
    return 0 if status in {"LATEXDIFF_READY", "LATEXDIFF_UNAVAILABLE_FALLBACK_WRITTEN"} else 2


if __name__ == "__main__":
    sys.exit(main())

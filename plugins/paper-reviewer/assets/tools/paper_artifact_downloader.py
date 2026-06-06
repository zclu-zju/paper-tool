#!/usr/bin/env python3
"""Download related-paper artifacts for draft-paper-reviewer.

The script is intentionally conservative:
- it downloads only http(s) URLs from the literature candidate CSV;
- it never executes downloaded code;
- it extracts source archives only as files for reading;
- it can run without optional PDF text dependencies, but uses pypdf when available.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POLICY_DEFAULT = "DOWNLOAD_ALL_DISCOVERED_PUBLIC_ARTIFACTS"
TOP_X_PER_TOPIC_DEFAULT = 20
TOP_X_OVERALL_DEFAULT = 40

OUTPUT_FIELDS = [
    "paper_id",
    "topic_id",
    "topic_label",
    "topic_rank_by_citations",
    "overall_rank_by_citations",
    "download_policy",
    "artifact_requested",
    "request_reason",
    "title",
    "year",
    "paper_url",
    "pdf_url",
    "tex_source_url",
    "pdf_download_status",
    "local_pdf_path",
    "tex_download_status",
    "local_tex_source_path",
    "text_extraction_status",
    "local_text_path",
    "metadata_path",
    "downstream_uses",
    "artifact_gap_severity",
    "notes",
]

REQUIRED_EVIDENCE_CATEGORIES = {
    "DIRECT_COMPETITOR",
    "RECENT_SOTA",
    "CONTRADICTORY_EVIDENCE",
    "METHOD_NORM",
    "DATASET_OR_BENCHMARK",
    "TERMINOLOGY_NORM",
    "FIELD_STYLE_EXEMPLAR",
    "ABSTRACT_EXEMPLAR",
    "INTRODUCTION_EXEMPLAR",
    "CONTRIBUTION_FRAMING_EXEMPLAR",
    "METHOD_EXPOSITION_EXEMPLAR",
    "EXPERIMENT_NARRATIVE_EXEMPLAR",
    "RESULTS_TABLE_EXEMPLAR",
    "LIMITATION_FRAMING_EXEMPLAR",
    "TERM_USAGE_EXEMPLAR",
}


@dataclass
class RequirementConfig:
    policy: str
    top_x: int | None


def read_requirements(path: Path) -> RequirementConfig:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    policy = extract_markdown_value(text, "Related Paper Artifact Retrieval Policy") or extract_markdown_value(
        text, "Related Paper Artifact Retrieval"
    )
    policy = normalize_policy(policy or POLICY_DEFAULT)
    top_x = parse_top_x(extract_markdown_value(text, "Artifact Download Top X"))
    if top_x is None and policy == "DOWNLOAD_TOP_CITED_PER_TOPIC":
        top_x = TOP_X_PER_TOPIC_DEFAULT
    if top_x is None and policy == "DOWNLOAD_TOP_CITED_OVERALL":
        top_x = TOP_X_OVERALL_DEFAULT
    return RequirementConfig(policy=policy, top_x=top_x)


def extract_markdown_value(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^\s*[-|]?\s*{re.escape(key)}\s*:?\s*\|?\s*(.+?)\s*(?:\||$)", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return None
    value = match.group(1).strip()
    value = re.sub(r"\s*\|.*$", "", value).strip()
    return value or None


def normalize_policy(value: str) -> str:
    token = value.strip().split()[0].strip("`[]")
    aliases = {
        "DOWNLOAD_PDFS": "DOWNLOAD_REQUIRED_EVIDENCE_ONLY",
        "DOWNLOAD_TEX": "DOWNLOAD_REQUIRED_EVIDENCE_ONLY",
        "DOWNLOAD_PDF_AND_TEX": "DOWNLOAD_ALL_DISCOVERED_PUBLIC_ARTIFACTS",
        "DOWNLOAD_WHEN_NEEDED_FOR_EVIDENCE": "DOWNLOAD_REQUIRED_EVIDENCE_ONLY",
    }
    return aliases.get(token, token)


def parse_top_x(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else None


def read_candidates(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: value for key, value in row.items()} for row in reader]


def safe_id(value: str) -> str:
    value = value.strip() or "unknown"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)[:120] or "unknown"


def title_dir(row: dict[str, str]) -> str:
    """Use the paper title as the shared artifact directory key."""
    title = row.get("title") or row_id(row)
    token = safe_id(title)
    arxiv_id = safe_id(row.get("arxiv_id", ""))
    if arxiv_id and arxiv_id != "unknown":
        return f"{token}__{arxiv_id}"[:160]
    return token


def parse_int(value: str | None, default: int = 10**12) -> int:
    if not value:
        return default
    match = re.search(r"\d+", str(value).replace(",", ""))
    return int(match.group(0)) if match else default


def citation_count(row: dict[str, str]) -> int:
    value = row.get("citation_count", "")
    parsed = parse_int(value, default=-1)
    return parsed


def rank_value(row: dict[str, str], field: str) -> int:
    value = parse_int(row.get(field), default=10**12)
    if value != 10**12:
        return value
    count = citation_count(row)
    return -count if count >= 0 else 10**12


def in_scope(row: dict[str, str]) -> bool:
    status = (row.get("status") or "").upper()
    scope = (row.get("scope_match") or "").upper()
    return status != "OUT_OF_SCOPE" and scope not in {"OUT_OF_SCOPE", "NO", "FALSE"}


def public_artifact_available(row: dict[str, str]) -> bool:
    return bool((row.get("pdf_url") or "").strip() or (row.get("tex_source_url") or "").strip())


def select_rows(rows: list[dict[str, str]], config: RequirementConfig) -> set[str]:
    candidates = [row for row in rows if in_scope(row)]
    selected: set[str] = set()
    policy = config.policy
    if policy == "DO_NOT_DOWNLOAD":
        return selected
    if policy == "DOWNLOAD_ALL_DISCOVERED_PUBLIC_ARTIFACTS":
        return {row_id(row) for row in candidates}
    if policy == "DOWNLOAD_TOP_CITED_PER_TOPIC":
        top_x = config.top_x or TOP_X_PER_TOPIC_DEFAULT
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in candidates:
            grouped.setdefault(row.get("topic_id") or "T01", []).append(row)
        for items in grouped.values():
            sorted_items = sorted(items, key=lambda row: (rank_value(row, "topic_rank_by_citations"), -citation_count(row)))
            for row in sorted_items[:top_x]:
                selected.add(row_id(row))
        return selected
    if policy == "DOWNLOAD_TOP_CITED_OVERALL":
        top_x = config.top_x or TOP_X_OVERALL_DEFAULT
        sorted_items = sorted(
            candidates,
            key=lambda row: (rank_value(row, "overall_rank_by_citations"), -citation_count(row)),
        )
        return {row_id(row) for row in sorted_items[:top_x]}
    if policy == "DOWNLOAD_REQUIRED_EVIDENCE_ONLY":
        for row in candidates:
            category = (row.get("evidence_use_category") or "").upper()
            status = (row.get("status") or "").upper()
            priority = (row.get("download_priority") or "").upper()
            if category in REQUIRED_EVIDENCE_CATEGORIES or status == "NEEDS_LOCAL_ARTIFACT" or priority:
                selected.add(row_id(row))
        return selected
    return selected


def row_id(row: dict[str, str]) -> str:
    return row.get("paper_id") or safe_id(row.get("title", "unknown"))


def download_url(url: str, dst: Path, timeout: int = 45) -> tuple[str, str]:
    if not url:
        return "SKIPPED_NO_URL", "missing URL"
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "FAILED", f"unsupported URL scheme: {parsed.scheme}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return "EXISTS_REUSED", ""
    request = urllib.request.Request(url, headers={"User-Agent": "draft-paper-reviewer/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, dst.open("wb") as handle:
            shutil.copyfileobj(response, handle)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return "FAILED", str(exc)
    if not dst.exists() or dst.stat().st_size == 0:
        return "FAILED", "empty download"
    return "DOWNLOADED", ""


def extract_tex_archive(path: Path, out_dir: Path) -> Path:
    extracted = out_dir / "source_extracted"
    if extracted.exists():
        return extracted
    extracted.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            archive.extractall(extracted)
        return extracted
    try:
        if tarfile.is_tarfile(path):
            with tarfile.open(path) as archive:
                archive.extractall(extracted)
            return extracted
    except tarfile.TarError:
        pass
    return path


def extract_pdf_text(pdf_path: Path, text_path: Path) -> tuple[str, str]:
    if not pdf_path.exists():
        return "SKIPPED_NO_ARTIFACT", "missing PDF"
    if text_path.exists() and text_path.stat().st_size > 0:
        return "EXISTS_REUSED", ""
    text_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return "FAILED", "pypdf not installed"
    try:
        reader = PdfReader(str(pdf_path))
        chunks = []
        for page in reader.pages:
            chunks.append(page.extract_text() or "")
        text = "\n\n".join(chunks).strip()
        if not text:
            return "FAILED", "no extractable text"
        text_path.write_text(text, encoding="utf-8")
    except Exception as exc:  # pragma: no cover - depends on target PDFs
        return "FAILED", str(exc)
    return "EXTRACTED", ""


def write_metadata(path: Path, row: dict[str, str], output_row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"candidate": row, "artifact": output_row}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def process_rows(rows: list[dict[str, str]], selected: set[str], config: RequirementConfig) -> list[dict[str, str]]:
    outputs: list[dict[str, str]] = []
    for row in rows:
        pid = safe_id(row_id(row))
        title_key = title_dir(row)
        requested = pid in {safe_id(item) for item in selected} or row_id(row) in selected
        request_reason = row.get("download_required_reason") or row.get("evidence_use_category") or ""
        pdf_path = Path("workspace/paper/pdf") / title_key / "paper.pdf"
        tex_dir = Path("workspace/paper/tex") / title_key
        tex_path = tex_dir / "source"
        summary_dir = Path("workspace/paper/summary") / title_key
        text_path = summary_dir / "extracted.txt"
        metadata_path = summary_dir / "artifact.json"

        pdf_status = "NOT_REQUESTED"
        tex_status = "NOT_REQUESTED"
        text_status = "NOT_REQUESTED"
        notes: list[str] = []
        local_tex_path = ""

        if requested:
            pdf_status, pdf_note = download_url((row.get("pdf_url") or "").strip(), pdf_path)
            if pdf_note:
                notes.append(f"pdf: {pdf_note}")
            tex_status, tex_note = download_url((row.get("tex_source_url") or "").strip(), tex_path)
            if tex_note:
                notes.append(f"tex: {tex_note}")
            if tex_status in {"DOWNLOADED", "EXISTS_REUSED"}:
                local_tex_path = str(extract_tex_archive(tex_path, tex_dir))
            if pdf_status in {"DOWNLOADED", "EXISTS_REUSED"}:
                text_status, text_note = extract_pdf_text(pdf_path, text_path)
                if text_note:
                    notes.append(f"text: {text_note}")
            elif tex_status in {"DOWNLOADED", "EXISTS_REUSED"}:
                text_status = "SKIPPED_NO_ARTIFACT"
                notes.append("text: PDF unavailable; inspect local TeX/source")
            else:
                text_status = "SKIPPED_NO_ARTIFACT"

        artifact_gap = "NONE"
        if requested and pdf_status not in {"DOWNLOADED", "EXISTS_REUSED"} and tex_status not in {"DOWNLOADED", "EXISTS_REUSED"}:
            artifact_gap = "HIGH"
        elif requested and text_status not in {"EXTRACTED", "EXISTS_REUSED"}:
            artifact_gap = "MEDIUM"

        output = {
            "paper_id": row_id(row),
            "topic_id": row.get("topic_id", ""),
            "topic_label": row.get("topic_label", ""),
            "topic_rank_by_citations": row.get("topic_rank_by_citations", ""),
            "overall_rank_by_citations": row.get("overall_rank_by_citations", ""),
            "download_policy": config.policy,
            "artifact_requested": "YES" if requested else "NO",
            "request_reason": request_reason,
            "title": row.get("title", ""),
            "year": row.get("year", ""),
            "paper_url": row.get("paper_url", ""),
            "pdf_url": row.get("pdf_url", ""),
            "tex_source_url": row.get("tex_source_url", ""),
            "pdf_download_status": pdf_status,
            "local_pdf_path": str(pdf_path) if pdf_path.exists() else "",
            "tex_download_status": tex_status,
            "local_tex_source_path": local_tex_path or (str(tex_path) if tex_path.exists() else ""),
            "text_extraction_status": text_status,
            "local_text_path": str(text_path) if text_path.exists() else "",
            "metadata_path": str(metadata_path),
            "downstream_uses": row.get("evidence_use_category", ""),
            "artifact_gap_severity": artifact_gap,
            "notes": "; ".join(notes),
        }
        write_metadata(metadata_path, row, output)
        outputs.append(output)
    return outputs


def write_outputs(rows: list[dict[str, str]], report_root: Path, config: RequirementConfig) -> None:
    report_root.mkdir(parents=True, exist_ok=True)
    csv_path = report_root / "04_paper_artifacts.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    requested = [row for row in rows if row["artifact_requested"] == "YES"]
    pdf_count = sum(row["pdf_download_status"] in {"DOWNLOADED", "EXISTS_REUSED"} for row in requested)
    tex_count = sum(row["tex_download_status"] in {"DOWNLOADED", "EXISTS_REUSED"} for row in requested)
    text_count = sum(row["text_extraction_status"] in {"EXTRACTED", "EXISTS_REUSED"} for row in requested)
    failed = sum(row["artifact_gap_severity"] == "HIGH" for row in requested)
    status = "READY"
    if not requested:
        status = "NOT_REQUIRED" if config.policy == "DO_NOT_DOWNLOAD" else "PARTIAL"
    elif failed:
        status = "PARTIAL"

    topic_stats: dict[str, dict[str, Any]] = {}
    for row in requested:
        topic = row["topic_id"] or "T01"
        stats = topic_stats.setdefault(
            topic,
            {"label": row["topic_label"], "required": 0, "downloaded": 0, "failed": 0},
        )
        stats["required"] += 1
        if row["pdf_download_status"] in {"DOWNLOADED", "EXISTS_REUSED"} or row["tex_download_status"] in {
            "DOWNLOADED",
            "EXISTS_REUSED",
        }:
            stats["downloaded"] += 1
        if row["artifact_gap_severity"] == "HIGH":
            stats["failed"] += 1

    md_path = report_root / "04_paper_artifacts.md"
    lines = [
        "## STATUS",
        f"STATUS: {status}",
        "",
        "## Artifact Summary",
        f"- Artifact Retrieval Policy: {config.policy}",
        f"- Artifact Download Top X: {config.top_x or ''}",
        f"- Topic Group Count: {len(topic_stats)}",
        f"- Target Paper Count: {len(requested)}",
        f"- PDF Downloaded Or Reused Count: {pdf_count}",
        f"- TeX/Source Downloaded Or Reused Count: {tex_count}",
        f"- Text Extracted Count: {text_count}",
        f"- Failed Count: {failed}",
        "",
        "## Policy Compliance By Topic",
        "| Topic ID | Topic Label | Required Downloads | Downloaded/Reused | Failed | Policy Status |",
        "|---|---|---:|---:|---:|---|",
    ]
    for topic, stats in sorted(topic_stats.items()):
        policy_status = "READY" if stats["failed"] == 0 else "PARTIAL"
        lines.append(
            f"| {topic} | {stats['label']} | {stats['required']} | {stats['downloaded']} | {stats['failed']} | {policy_status} |"
        )
    lines.extend(
        [
            "",
            "## Missing Artifacts",
            "| Paper ID | Needed For | Missing Artifact | Consequence | Suggested Loopback |",
            "|---|---|---|---|---|",
        ]
    )
    for row in requested:
        if row["artifact_gap_severity"] == "HIGH":
            lines.append(
                f"| {row['paper_id']} | {row['downstream_uses']} | PDF and TeX/source | local convention/evidence cannot rely on this paper | Stage 4 or Stage 5 |"
            )
    lines.extend(
        [
            "",
            "## Writing Exemplar Artifacts",
            "| Paper ID | Exemplar Role | Local Text Available | Local PDF | Local TeX/Source | Downstream Use |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in requested:
        role = row["downstream_uses"]
        if "EXEMPLAR" in role or "NORM" in role or "TABLE" in role:
            lines.append(
                f"| {row['paper_id']} | {role} | {row['text_extraction_status']} | {row['local_pdf_path']} | {row['local_tex_source_path']} | {row['downstream_uses']} |"
            )
    lines.extend(
        [
            "",
            "## Durable Local Corpus Contract",
            "- Downstream agents may use non-downloaded papers for metadata-only background: Yes",
            "- Downstream agents must use downloaded/local artifacts for novelty, field norms, writing style, terminology, table/figure conventions, and deletion/addition decisions: Yes",
            "- Shared PDF root: workspace/paper/pdf/{title}/",
            "- Shared TeX/source root: workspace/paper/tex/{title}/",
            "- Shared summary root: workspace/paper/summary/{title}/",
            "",
            "## Safety Rules Applied",
            "- No third-party code executed: Yes",
            "- No dependencies installed: Yes",
            "- No manuscript files modified: Yes",
            "",
            "## Output Paths",
            f"- Artifact CSV: {csv_path}",
            "- PDF Root: workspace/paper/pdf/",
            "- TeX Root: workspace/paper/tex/",
            "- Summary Root: workspace/paper/summary/",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--requirements", type=Path, default=Path("workspace/report/paper-reviewer/00_requirements.md"))
    parser.add_argument("--candidates", type=Path, default=Path("workspace/report/paper-reviewer/03_literature_candidates.csv"))
    parser.add_argument("--report-root", type=Path, default=Path("workspace/report/paper-reviewer"))
    parser.add_argument("--out-root", type=Path, default=None, help="Deprecated. Use --report-root.")
    args = parser.parse_args()

    config = read_requirements(args.requirements)
    rows = read_candidates(args.candidates)
    selected = select_rows(rows, config)
    outputs = process_rows(rows, selected, config)
    report_root = args.report_root if args.out_root is None else args.report_root
    write_outputs(outputs, report_root, config)
    print(f"Wrote artifact report: {report_root / '04_paper_artifacts.csv'}")
    print(f"Selected downloads: {len(selected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

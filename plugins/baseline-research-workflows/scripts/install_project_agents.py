#!/usr/bin/env python3
"""Install baseline-research workflow templates into a target repository.

The installer is conservative by default:
- missing files are copied;
- identical files are reported as unchanged;
- existing files with different content are skipped unless --force is used.
- obsolete files from older releases are left untouched unless --clean-obsolete is used.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ASSETS = PLUGIN_ROOT / "assets"

OBSOLETE_FILES = [
    ".codex/agents/baseline_orchestrator.toml",
    ".codex/agents/direction_integrity_reviewer.toml",
    ".codex/agents/direction_literature_scout_arxiv.toml",
    ".codex/agents/direction_literature_scout_pwc.toml",
    ".codex/agents/direction_literature_scout_venues.toml",
    ".codex/agents/direction_oss_verifier.toml",
    ".codex/agents/direction_report_writer.toml",
    ".codex/agents/direction_research_orchestrator.toml",
    ".codex/agents/direction_scope_locker.toml",
    ".codex/agents/experiment_designer.toml",
    ".codex/agents/integrity_reviewer.toml",
    ".codex/agents/literature_scout_arxiv.toml",
    ".codex/agents/literature_scout_pwc.toml",
    ".codex/agents/literature_scout_venues.toml",
    ".codex/agents/oss_verifier.toml",
    ".codex/agents/paper_auditor.toml",
    ".codex/agents/research_workflow_router.toml",
    ".codex/baseline-workflow-prompt.md",
    ".codex/direction-research-workflow-prompt.md",
    ".codex/research-router-prompt.md",
    "prompts/direction_integrity_reviewer.md",
    "prompts/direction_literature_scout.md",
    "prompts/direction_orchestrator.md",
    "prompts/direction_oss_verifier.md",
    "prompts/direction_report_writer.md",
    "prompts/direction_scope_locker.md",
    "prompts/experiment_designer.md",
    "prompts/integrity_reviewer.md",
    "prompts/literature_scout.md",
    "prompts/orchestrator.md",
    "prompts/oss_verifier.md",
    "prompts/paper_auditor.md",
]


def copy_tree_contents(src_dir: Path, dst_dir: Path, force: bool) -> tuple[int, int, int]:
    copied = unchanged = conflicts = 0
    for src in sorted(src_dir.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        dst = dst_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
            continue
        if filecmp.cmp(src, dst, shallow=False):
            unchanged += 1
            continue
        if force:
            shutil.copy2(src, dst)
            copied += 1
        else:
            print(f"CONFLICT skip: {dst} differs from plugin asset")
            conflicts += 1
    return copied, unchanged, conflicts


def clean_obsolete_files(repo: Path) -> int:
    removed = 0
    for rel in OBSOLETE_FILES:
        path = repo / rel
        if not path.exists() or not path.is_file():
            continue
        path.unlink()
        print(f"Removed obsolete: {path}")
        removed += 1
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        default=".",
        help="Target repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files that differ from plugin assets.",
    )
    parser.add_argument(
        "--clean-obsolete",
        action="store_true",
        help="Remove known files from older baseline-research workflow releases.",
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"Target repo does not exist: {repo}")

    agent_src = ASSETS / "agents"
    codex_prompt_src = ASSETS / "prompts" / "codex"
    project_prompt_src = ASSETS / "prompts" / "project"

    targets = [
        (agent_src, repo / ".codex" / "agents"),
        (codex_prompt_src, repo / ".codex"),
        (project_prompt_src, repo / "prompts"),
    ]

    removed = clean_obsolete_files(repo) if args.clean_obsolete else 0

    total = {"copied": 0, "unchanged": 0, "conflicts": 0}
    for src, dst in targets:
        copied, unchanged, conflicts = copy_tree_contents(src, dst, args.force)
        total["copied"] += copied
        total["unchanged"] += unchanged
        total["conflicts"] += conflicts

    print(f"Installed into: {repo}")
    print(f"Copied: {total['copied']}")
    print(f"Unchanged: {total['unchanged']}")
    print(f"Conflicts: {total['conflicts']}")
    print(f"Obsolete removed: {removed}")
    if total["conflicts"]:
        print("Re-run with --force only if you intentionally want to overwrite target files.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

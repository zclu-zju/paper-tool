#!/usr/bin/env python3
"""Install deep-paper-search workflow templates into a target repository."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ASSETS = PLUGIN_ROOT / "assets"


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Target repository root.")
    parser.add_argument("--force", action="store_true", help="Overwrite conflicting files.")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        raise SystemExit(f"Target repo does not exist: {repo}")

    targets = [
        (ASSETS / "agents", repo / ".codex" / "agents"),
        (ASSETS / "prompts" / "codex", repo / ".codex"),
        (ASSETS / "prompts" / "project", repo / "prompts"),
    ]

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
    if total["conflicts"]:
        print("Re-run with --force only if overwriting is intentional.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync plugin packages from source branches into the main branch."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGINS_DIR = ROOT / "plugins"


@dataclass(frozen=True)
class BranchPlugin:
    branch: str
    plugin_name: str


BRANCH_PLUGINS = [
    BranchPlugin("research", "paper-research"),
    BranchPlugin("reviewer", "paper-reviewer"),
    BranchPlugin("experiment", "paper-experiment"),
    BranchPlugin("paper-deep-research", "deep-paper-search"),
]

FORBIDDEN_PATHS = [
    "workspace/literature_research",
    "workspace/experiment_rewrite",
    "workspace/draft_paper_review",
    "workspace/pdf",
    "workspace/tex",
    "workspace/summary",
]


def run(cmd: list[str], cwd: Path | None = None, stdout=None) -> None:
    subprocess.run(cmd, cwd=cwd, stdout=stdout, check=True)


def fetch_branches() -> None:
    branches = ["main", *(item.branch for item in BRANCH_PLUGINS)]
    for branch in branches:
        try:
            run(
                [
                    "git",
                    "fetch",
                    "origin",
                    f"+refs/heads/{branch}:refs/remotes/origin/{branch}",
                ]
            )
        except subprocess.CalledProcessError:
            print(f"Warning: could not fetch origin/{branch}; falling back to local refs")


def branch_ref(branch: str) -> str:
    remote_ref = f"origin/{branch}"
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", remote_ref],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode == 0:
        return remote_ref
    return branch


def export_plugin(branch: str, plugin_name: str, destination: Path) -> None:
    with tempfile.TemporaryDirectory(prefix=f"{plugin_name}-archive-") as tmp:
        tmp_path = Path(tmp)
        archive = tmp_path / "plugin.tar"
        with archive.open("wb") as handle:
            run(
                [
                    "git",
                    "archive",
                    "--format=tar",
                    branch_ref(branch),
                    f"plugins/{plugin_name}",
                ],
                stdout=handle,
            )
        with tarfile.open(archive) as tar:
            tar.extractall(tmp_path)
        package = tmp_path / "plugins" / plugin_name
        if not package.exists():
            raise SystemExit(f"Branch {branch!r} does not contain plugins/{plugin_name}")
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(package, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    normalize_file_modes(destination)
    validate_contract(destination, plugin_name)


def normalize_file_modes(plugin_dir: Path) -> None:
    for path in plugin_dir.rglob("*"):
        if path.is_file():
            path.chmod(0o644)


def validate_contract(plugin_dir: Path, plugin_name: str) -> None:
    manifest = plugin_dir / ".codex-plugin" / "plugin.json"
    with manifest.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("name") != plugin_name:
        raise SystemExit(f"{manifest} name is {data.get('name')!r}, expected {plugin_name!r}")

    offenders: list[str] = []
    for path in plugin_dir.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".toml", ".json", ".py"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for token in FORBIDDEN_PATHS:
            if token in text:
                offenders.append(f"{path.relative_to(ROOT)} contains {token}")
    if offenders:
        raise SystemExit("Workspace contract violation:\n" + "\n".join(offenders[:80]))


def main() -> int:
    fetch_branches()
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    for item in BRANCH_PLUGINS:
        export_plugin(item.branch, item.plugin_name, PLUGINS_DIR / item.plugin_name)
        print(f"Synced {item.plugin_name} from branch {item.branch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

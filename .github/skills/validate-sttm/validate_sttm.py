"""Checks that STTM markdown documents describe a complete gold-table load."""

import argparse
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# (check name, level when it fails, pattern searched in the document text)
_CHECKS = [
    ("title", "FAIL", re.compile(r"\A\s*#\s+\S.*\bSTTM\b", re.IGNORECASE)),
    ("target_table", "FAIL", re.compile(r"\bgold\.\w+")),
    ("load_schedule", "FAIL", re.compile(r"\b\d{2}:\d{2} UTC\b")),
    ("source", "FAIL", re.compile(r"\b(loaded|refreshed)\b[^.]*\bfrom\b", re.IGNORECASE)),
    ("column_rules", "WARN", re.compile(r"\bThe column \w+")),
    ("reject_handling", "WARN", re.compile(r"\b(reject|rejected|quarantine)\w*", re.IGNORECASE)),
]


def _collect_files(target: Path) -> list[Path]:
    if not target.exists():
        raise FileNotFoundError(f"sttm path not found: {target}")
    files = sorted(target.rglob("*.md")) if target.is_dir() else [target]
    if not files:
        raise ValueError(f"sttm folder {target} contains no .md files")
    return files


def build_report(path: Path) -> list[tuple[str, str]]:
    """Return (check name, PASS/WARN/FAIL) for one STTM document."""
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"sttm document {path.name} is empty")
    logger.info("build_report: checking %s (%d characters)", path.name, len(text))
    results = [(name, "PASS" if pattern.search(text) else level) for name, level, pattern in _CHECKS]
    logger.info("build_report: %s -> %d checks", path.name, len(results))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate STTM markdown documents.")
    parser.add_argument("target", type=Path, help="an STTM file or a folder containing them")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    exit_code = 0
    for path in _collect_files(args.target):
        report = build_report(path)
        print(f"{path.name}: " + ", ".join(f"{name}={status}" for name, status in report))
        if any(status == "FAIL" for _, status in report):
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

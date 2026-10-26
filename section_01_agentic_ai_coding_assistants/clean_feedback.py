import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def clean_feedback_csv(path: str | Path) -> list[dict[str, str]]:
    """Load feedback from CSV, trim cell values, and drop fully blank rows."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"feedback file not found: {source}")

    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("feedback CSV is missing a header row")
        rows = list(reader)

    logger.info("clean_feedback_csv: %d rows in", len(rows))
    cleaned = []
    for row in rows:
        normalized = {
            key: (value or "").strip()
            for key, value in row.items()
            if key is not None
        }
        if any(normalized.values()):
            cleaned.append(normalized)

    logger.info("clean_feedback_csv: %d rows out", len(cleaned))
    return cleaned
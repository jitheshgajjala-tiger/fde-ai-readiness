import csv
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_REQUIRED_COLUMNS = {"ticket_id", "customer_id", "priority"}


def _normalize_priority(value: str) -> str:
    return value.strip().lower()


def clean_tickets(path: str | Path) -> list[dict[str, str]]:
    """Load support tickets from CSV, drop rows without a ticket_id and normalise priority."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"tickets file not found: {source}")
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = _REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"tickets is missing required columns: {sorted(missing)}")
        rows = list(reader)
    logger.info("clean_tickets: %d rows in", len(rows))
    cleaned = [{**row, "priority": _normalize_priority(row["priority"])} for row in rows if row["ticket_id"].strip()]
    logger.info("clean_tickets: %d rows out", len(cleaned))
    return cleaned

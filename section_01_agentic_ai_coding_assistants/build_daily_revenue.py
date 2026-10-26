import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"order_date", "order_total"}


def build_daily_revenue(orders: list[dict]) -> dict[str, float]:
    """Sum order_total per order_date."""
    logger.info("build_daily_revenue: %d rows in", len(orders))
    for position, order in enumerate(orders):
        missing = _REQUIRED_KEYS - order.keys()
        if missing:
            raise ValueError(f"orders row {position} is missing required keys: {sorted(missing)}")
    totals: dict[str, float] = defaultdict(float)
    for order in orders:
        totals[order["order_date"]] += float(order["order_total"])
    logger.info("build_daily_revenue: %d days out", len(totals))
    return dict(totals)

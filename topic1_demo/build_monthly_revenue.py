import logging
from collections import defaultdict
from datetime import date

logger = logging.getLogger(__name__)

_REQUIRED_KEYS = {"order_date", "order_total"}


def build_monthly_revenue(orders: list[dict]) -> dict[str, float]:
    """Sum order_total per calendar month using YYYY-MM keys."""
    logger.info("build_monthly_revenue: %d rows in", len(orders))
    for position, order in enumerate(orders):
        missing = _REQUIRED_KEYS - order.keys()
        if missing:
            raise ValueError(f"orders row {position} is missing required keys: {sorted(missing)}")

    totals: dict[str, float] = defaultdict(float)
    for position, order in enumerate(orders):
        try:
            month = date.fromisoformat(str(order["order_date"])).strftime("%Y-%m")
            amount = float(order["order_total"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"orders row {position} has an invalid order_date or order_total") from error
        totals[month] += amount

    logger.info("build_monthly_revenue: %d months out", len(totals))
    return dict(totals)
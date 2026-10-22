import json
import py_compile
import sys
from pathlib import Path

import pytest

PREP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PREP))
sys.path.insert(0, str(PREP / "notebooks"))

from build_eval_set import OUTPUT, build_eval_rows  # noqa: E402
from seed_data import COLUMN_COMMENTS, CUSTOMERS, ORDERS, PRODUCTS  # noqa: E402


def test_foreign_keys_resolve():
    customer_ids = {c[0] for c in CUSTOMERS}
    product_ids = {p[0] for p in PRODUCTS}
    assert all(o[1] in customer_ids and o[2] in product_ids for o in ORDERS)


def test_order_ids_are_unique():
    assert len({o[0] for o in ORDERS}) == len(ORDERS)


def test_dates_match_status():
    for order_id, _, _, _, _, _, ship, delivered, status in ORDERS:
        if status == "DELIVERED":
            assert ship and delivered, order_id
        elif status in {"CANCELLED", "PROCESSING"}:
            assert ship is None and delivered is None, order_id
        elif status == "SHIPPED":
            assert ship and delivered is None, order_id


def test_every_fact_orders_column_has_a_comment():
    assert len(COLUMN_COMMENTS["fact_orders"]) == 10


def test_eval_file_matches_seed_data():
    on_disk = [json.loads(line) for line in OUTPUT.read_text(encoding="utf-8").splitlines()]
    assert on_disk == build_eval_rows()


def test_eval_set_size_and_known_answers():
    rows = {r["question"]: r for r in build_eval_rows()}
    assert 10 <= len(rows) <= 15
    assert rows["How many orders are there in total?"]["expected_any"] == ["24"]
    assert rows["How many days late was order 1011?"]["expected_any"] == ["3"]
    late = rows["Which orders were delivered after their promised date?"]["expected_any"]
    assert sorted(late) == ["1002", "1005", "1007", "1011", "1016"]


def test_notebook_eval_data_matches():
    from eval_data import EVAL_ROWS

    assert EVAL_ROWS == build_eval_rows()


def test_documented_on_time_rates():
    from datetime import date

    delivered = [o for o in ORDERS if o[8] == "DELIVERED"]
    by_promise = sum(o[7] <= o[5] for o in delivered)
    by_warehouse_sla = sum((date.fromisoformat(o[6]) - date.fromisoformat(o[4])).days <= 2 for o in delivered)
    assert (len(delivered), round(100 * by_promise / len(delivered), 1)) == (17, 70.6)
    assert round(100 * by_warehouse_sla / len(delivered), 1) == 76.5


def test_seed_chunks_cover_all_doc_types():
    from seed_chunks import CHUNKS

    assert {c["doc_type"] for c in CHUNKS} == {"sttm", "drd", "policy"}
    assert len({c["chunk_id"] for c in CHUNKS}) == len(CHUNKS)


@pytest.mark.parametrize(
    "relative",
    [p.relative_to(PREP).as_posix() for p in sorted(PREP.rglob("*.py")) if "tests" not in p.parts and "__pycache__" not in p.parts],
)
def test_python_files_compile(relative):
    py_compile.compile(str(PREP / relative), doraise=True)

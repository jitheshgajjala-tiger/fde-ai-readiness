# Databricks notebook source
# Deterministic order-fulfilment data shared by the Genie, app and agent exercises.
# Pure Python on purpose: it is imported by local tests and run with %run in notebooks.

CUSTOMERS = [
    # customer_id, customer_name, region, segment
    (1, "Acme Corp", "North", "enterprise"),
    (2, "Bright Retail", "South", "smb"),
    (3, "Cedar Foods", "East", "mid-market"),
    (4, "Delta Logistics", "West", "enterprise"),
    (5, "Evergreen Co", "North", "smb"),
    (6, "Fjord Traders", "South", "mid-market"),
    (7, "Granite Works", "East", "smb"),
    (8, "Harbor Supplies", "West", "mid-market"),
]

PRODUCTS = [
    # product_id, product_name, category, unit_price
    (101, "Widget A", "hardware", 25.00),
    (102, "Widget B", "hardware", 40.00),
    (103, "Gadget C", "electronics", 120.00),
    (104, "Gadget D", "electronics", 200.00),
    (105, "Service Plan", "services", 60.00),
    (106, "Cable Pack", "accessories", 10.00),
]

ORDERS = [
    # order_id, customer_id, product_id, quantity, order_date, promised_date, ship_date, delivered_date, order_status
    (1001, 1, 101, 10, "2026-01-05", "2026-01-12", "2026-01-06", "2026-01-11", "DELIVERED"),
    (1002, 2, 103, 2, "2026-01-07", "2026-01-14", "2026-01-10", "2026-01-16", "DELIVERED"),
    (1003, 3, 105, 5, "2026-01-15", "2026-01-22", "2026-01-16", "2026-01-21", "DELIVERED"),
    (1004, 4, 104, 1, "2026-02-02", "2026-02-09", "2026-02-03", "2026-02-09", "DELIVERED"),
    (1005, 1, 102, 4, "2026-02-10", "2026-02-17", "2026-02-15", "2026-02-18", "DELIVERED"),
    (1006, 5, 106, 20, "2026-02-12", "2026-02-19", "2026-02-13", "2026-02-17", "DELIVERED"),
    (1007, 6, 103, 3, "2026-03-01", "2026-03-08", "2026-03-02", "2026-03-10", "DELIVERED"),
    (1008, 2, 101, 8, "2026-03-05", "2026-03-12", None, None, "CANCELLED"),
    (1009, 7, 102, 6, "2026-03-18", "2026-03-25", "2026-03-19", "2026-03-24", "DELIVERED"),
    (1010, 8, 105, 2, "2026-04-02", "2026-04-09", "2026-04-03", "2026-04-08", "DELIVERED"),
    (1011, 3, 104, 2, "2026-04-10", "2026-04-17", "2026-04-14", "2026-04-20", "DELIVERED"),
    (1012, 4, 101, 12, "2026-04-22", "2026-04-29", "2026-04-23", "2026-04-28", "DELIVERED"),
    (1013, 1, 103, 1, "2026-05-06", "2026-05-13", "2026-05-07", "2026-05-12", "DELIVERED"),
    (1014, 5, 105, 3, "2026-05-20", "2026-05-27", None, None, "CANCELLED"),
    (1015, 6, 106, 50, "2026-06-03", "2026-06-10", "2026-06-04", "2026-06-09", "DELIVERED"),
    (1016, 7, 104, 1, "2026-06-15", "2026-06-22", "2026-06-19", "2026-06-24", "DELIVERED"),
    (1017, 8, 102, 5, "2026-07-01", "2026-07-08", "2026-07-02", "2026-07-07", "DELIVERED"),
    (1018, 2, 104, 2, "2026-07-14", "2026-07-21", "2026-07-15", "2026-07-20", "DELIVERED"),
    (1019, 3, 101, 15, "2026-08-04", "2026-08-11", "2026-08-05", "2026-08-10", "DELIVERED"),
    (1020, 4, 103, 2, "2026-08-19", "2026-08-26", "2026-08-20", None, "SHIPPED"),
    (1021, 1, 105, 4, "2026-09-02", "2026-09-09", "2026-09-03", None, "SHIPPED"),
    (1022, 5, 102, 7, "2026-09-10", "2026-09-17", None, None, "PROCESSING"),
    (1023, 6, 101, 9, "2026-09-21", "2026-09-28", None, None, "PROCESSING"),
    (1024, 8, 106, 30, "2026-09-25", "2026-10-02", None, None, "PROCESSING"),
]

TABLE_COMMENTS = {
    "dim_customer": "One row per customer. Region is the sales region that owns the account.",
    "dim_product": "One row per product in the catalogue with its current list price.",
    "fact_orders": (
        "One row per customer order. Revenue is quantity * unit_price from dim_product. "
        "Cancelled orders are kept but never count as revenue."
    ),
}

COLUMN_COMMENTS = {
    "dim_customer": {
        "customer_id": "Unique customer key.",
        "customer_name": "Legal name of the customer.",
        "region": "Sales region: North, South, East or West.",
        "segment": "Commercial segment: enterprise, mid-market or smb.",
    },
    "dim_product": {
        "product_id": "Unique product key.",
        "product_name": "Display name of the product.",
        "category": "Product family: hardware, electronics, services or accessories.",
        "unit_price": "List price in USD for one unit.",
    },
    "fact_orders": {
        "order_id": "Unique order key.",
        "customer_id": "Customer who placed the order. Joins to dim_customer.customer_id.",
        "product_id": "Product ordered. Joins to dim_product.product_id.",
        "region": "Region of the customer at order time (copied from dim_customer).",
        "quantity": "Units ordered.",
        "order_date": "Date the order was placed.",
        "promised_date": "Delivery date promised to the customer at order time.",
        "ship_date": "Date the warehouse shipped the order. Null until shipped.",
        "delivered_date": "Date the customer received the order. Null until delivered.",
        "order_status": "One of PROCESSING, SHIPPED, DELIVERED, CANCELLED.",
    },
}

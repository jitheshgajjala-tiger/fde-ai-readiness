# Data Quality Rules Register

Rule DQ-1047 checks that order_id is unique within gold.orders and fails the load if duplicates are found.
Rule DQ-1074 checks that order_date is not in the future and raises a warning only.
Rule DQ-1407 checks that customer_key exists in gold.dim_customer and fails the load on orphan keys.
Rule DQ-1470 checks that order_total is never negative and quarantines the offending rows.
Rule DQ-4107 checks that sku exists in gold.dim_product and raises a warning for unknown products.
Rule DQ-4170 checks that discount_amount does not exceed the gross order value and quarantines the offending rows.

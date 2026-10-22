# Products STTM

The table gold.dim_product is loaded daily at 03:00 UTC from the product master system.
The column margin_pct is calculated as list_price minus unit_cost divided by list_price.
The column category_path concatenates category level one, level two and level three with a greater than sign.
Products with a null sku are rejected and logged to gold.product_rejects.
Discontinued products keep their row with product_status set to DISCONTINUED.

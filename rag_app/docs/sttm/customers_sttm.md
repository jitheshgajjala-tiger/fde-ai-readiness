# Customers STTM

The dimension table gold.dim_customer is refreshed weekly on Sunday at 04:00 UTC from silver.crm_customers.
The column email_hash is the SHA-256 hash of the lowercase trimmed email address and raw emails are never stored in gold.
The column customer_segment is derived from lifetime_value: PLATINUM above 10000, GOLD from 5000 to 10000, SILVER from 1000 to 5000, otherwise BRONZE.
Duplicate customers are merged using the highest confidence match on email_hash and phone_number.
Customers inactive for 24 months have is_active set to false but are never deleted.

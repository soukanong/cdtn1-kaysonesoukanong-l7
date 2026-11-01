-- View che số điện thoại (QT-15, NFR5): Marketing chỉ đọc qua view này.
-- Ví dụ 0901234567 -> 090****567
CREATE OR REPLACE VIEW core.view_customer_masked AS
SELECT customer_id,
       full_name,
       LEFT(phone, 3) || '****' || RIGHT(phone, 3) AS phone_masked,
       store_key,
       is_active,
       merged_into_id
FROM   core.customer_clean;

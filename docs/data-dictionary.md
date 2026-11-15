# Data Dictionary – L7 Customer Data Quality (track DA)

> Generated from `sql/001_schema_dwh.sql`, `sql/002_schema_stg_core.sql` and `sql/003_view_masked.sql`. Verified against the live database: yes (15/11/2026, commit `ac94772`).

Classification levels (as in the course material): **CÔNG KHAI** (public) · **NỘI BỘ** (internal) · **ĐỊNH DANH CÁ NHÂN** (personal identifiers: name, phone, email, address) · **NHẠY CẢM** (sensitive; no column of this system is in this level).

Total: 14 objects, 94 columns.

## dwh.dim_date

Calendar dimension, SCD type 0.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `date_key` | INT | NO | Surrogate date key in yyyymmdd form; −1 is the Unknown row | 8-digit date or −1 | CÔNG KHAI | None |
| `full_date` | DATE | YES | Calendar date of the run; NULL only in the Unknown row | any date | CÔNG KHAI | None |
| `month_no` | SMALLINT | YES | Month number | 1–12 | CÔNG KHAI | None |
| `quarter_no` | SMALLINT | YES | Quarter number | 1–4 | CÔNG KHAI | None |
| `year_no` | SMALLINT | YES | Year | four-digit year | CÔNG KHAI | None |

## dwh.dim_run

One row per pipeline run, SCD type 0.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `run_key` | BIGINT | NO | Surrogate key of the run (identity); −1 is the Unknown row | positive integer or −1 | NỘI BỘ | None |
| `started_at` | TIMESTAMP | YES | Run start time | timestamp | NỘI BỘ | None |
| `finished_at` | TIMESTAMP | YES | Run end time; NULL while the run is RUNNING | timestamp or NULL | NỘI BỘ | None |
| `source_file` | VARCHAR(100) | YES | Name of the source CSV file | file name | NỘI BỘ | File name only, no personal data |
| `source_row_count` | INT | YES | Number of rows read from the source | integer ≥ 0 | NỘI BỘ | None |
| `status` | VARCHAR(10) | YES | Run result | SUCCESS, FAILED or RUNNING (CHECK constraint) | NỘI BỘ | None |

## dwh.dim_dq_rule

Quality rule versions, SCD type 2 on threshold_pct.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `rule_key` | SMALLINT | NO | Surrogate key of the rule version (identity); −1 is the Unknown row | positive integer or −1 | NỘI BỘ | None |
| `rule_code` | VARCHAR(10) | YES | Business key of the rule | DQ01–DQ06, or UNKNOWN | NỘI BỘ | None |
| `rule_name` | VARCHAR(120) | YES | Human-readable rule statement | text | NỘI BỘ | None |
| `quality_dimension` | VARCHAR(20) | YES | Quality dimension measured | completeness, validity, uniqueness or consistency | NỘI BỘ | None |
| `column_name` | VARCHAR(40) | YES | Column or object the rule checks | column name | NỘI BỘ | None |
| `threshold_pct` | NUMERIC(5,2) | YES | Pass threshold in percent; a change adds a new row (SCD 2) | 0.00–100.00 | NỘI BỘ | None |
| `is_active` | BOOLEAN | YES | Whether the rule is in use (default TRUE) | TRUE or FALSE | NỘI BỘ | None |
| `valid_from` | DATE | YES | Date this version became effective | date | NỘI BỘ | None |
| `valid_to` | DATE | YES | Date this version ended; NULL for the current version | date or NULL | NỘI BỘ | None |
| `is_current` | BOOLEAN | YES | Current version flag (default TRUE); a unique index allows one current row per rule_code | TRUE or FALSE | NỘI BỘ | None |

## dwh.dim_store

Store dimension, SCD type 1. Only the Unknown row (−1) exists today because the source has no store column (TD-07).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `store_key` | INT | NO | Surrogate store key; −1 is the Unknown row | integer | NỘI BỘ | None |
| `store_code` | VARCHAR(20) | YES | Business store code | store code or UNKNOWN | NỘI BỘ | None |
| `store_name` | VARCHAR(100) | YES | Store name | text | NỘI BỘ | None |
| `city` | VARCHAR(50) | YES | City of the store | text or NULL | NỘI BỘ | None |

## dwh.fact_dq_result

Grain: one rule at one stage for one store in one run. UNIQUE (run_key, rule_key, stage, store_key).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `result_key` | BIGINT | NO | Surrogate key of the row (identity) | positive integer | NỘI BỘ | None |
| `date_key` | INT | NO | Foreign key to dim_date | existing date_key | NỘI BỘ | None |
| `run_key` | BIGINT | NO | Foreign key to dim_run | existing run_key | NỘI BỘ | None |
| `rule_key` | SMALLINT | NO | Foreign key to dim_dq_rule | existing rule_key | NỘI BỘ | None |
| `store_key` | INT | NO | Foreign key to dim_store | existing store_key | NỘI BỘ | None |
| `stage` | VARCHAR(5) | NO | Measurement stage | RAW or CLEAN (CHECK constraint) | NỘI BỘ | None |
| `total_records` | INT | YES | Records checked (additive across stores only for a fixed run, rule and stage) | integer ≥ 0 | NỘI BỘ | Aggregate count, no personal data |
| `failed_records` | INT | YES | Records violating the rule (additive across stores only for a fixed run, rule and stage) | integer ≥ 0 | NỘI BỘ | Aggregate count, no personal data |
| `pass_rate_pct` | NUMERIC(5,2) | YES | Pass rate in percent; not additive, recompute as 100 × (1 − Σfailed / Σtotal) | 0.00–100.00 | NỘI BỘ | Aggregate, no personal data |
| `is_threshold_met` | BOOLEAN | YES | Whether pass_rate_pct reaches the rule threshold | TRUE or FALSE | NỘI BỘ | None |

## dwh.fact_dq_issue

Grain: one violation of one rule by one raw record in one run. Keeps only the latest run (TD-10).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `issue_key` | BIGINT | NO | Surrogate key of the row (identity) | positive integer | NỘI BỘ | None |
| `date_key` | INT | NO | Foreign key to dim_date | existing date_key | NỘI BỘ | None |
| `run_key` | BIGINT | NO | Foreign key to dim_run | existing run_key | NỘI BỘ | None |
| `rule_key` | SMALLINT | NO | Foreign key to dim_dq_rule | existing rule_key | NỘI BỘ | None |
| `store_key` | INT | NO | Foreign key to dim_store | existing store_key | NỘI BỘ | None |
| `stg_id` | BIGINT | YES | Id of the raw staging record that violated the rule (degenerate dimension, no foreign key) | integer | NỘI BỘ | Identifier only; no personal data copied |
| `dup_group_id` | BIGINT | YES | Suspect duplicate group, when the violation relates to one | integer or NULL | NỘI BỘ | None |
| `issue_detail` | VARCHAR(255) | YES | Short description of the violation; by design does not contain a full phone number | text | NỘI BỘ | No full phone number by design |

## stg.stg_customer

Raw records exactly as read; reloaded every run.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `stg_id` | BIGINT | NO | Surrogate id of the raw record | integer | NỘI BỘ | Staging only; reloaded every run |
| `source_row_no` | INT | YES | Row number in the source file | integer ≥ 1 | NỘI BỘ | None |
| `record_id_raw` | VARCHAR(100) | YES | Record id as written in the source | text | NỘI BỘ | Staging only |
| `full_name_raw` | TEXT | YES | Customer name as in the source | text or empty | ĐỊNH DANH CÁ NHÂN | Plain text in staging; reloaded every run |
| `phone_raw` | TEXT | YES | Phone as in the source, any format | text or empty | ĐỊNH DANH CÁ NHÂN | Plain text in staging; reloaded every run |
| `email_raw` | TEXT | YES | Email as in the source | text or empty | ĐỊNH DANH CÁ NHÂN | Plain text in staging; reloaded every run |
| `address_raw` | TEXT | YES | Address as in the source | text or empty | ĐỊNH DANH CÁ NHÂN | Plain text in staging; reloaded every run |
| `created_at_raw` | TEXT | YES | Creation date as text (yyyy-mm-dd in the real file) | text or empty | NỘI BỘ | None |
| `run_key` | BIGINT | YES | Run that loaded this record | existing run_key | NỘI BỘ | None |

## stg.stg_customer_clean

Normalised and phone-de-duplicated profiles waiting for the upsert into core.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `source_row_no` | INT | NO | Source row number (primary key) | integer ≥ 1 | NỘI BỘ | Staging only |
| `full_name` | VARCHAR(120) | YES | Normalised customer name | text | ĐỊNH DANH CÁ NHÂN | Plain text in staging |
| `phone` | VARCHAR(20) | YES | Normalised phone | 10 digits starting with 0 | ĐỊNH DANH CÁ NHÂN | Plain text in staging |
| `email` | VARCHAR(120) | YES | Lower-cased valid email, NULL if invalid or empty | email or NULL | ĐỊNH DANH CÁ NHÂN | Plain text in staging |
| `address` | VARCHAR(255) | YES | Address text | text or NULL | ĐỊNH DANH CÁ NHÂN | Plain text in staging |
| `created_at` | TIMESTAMP | YES | Parsed creation date | timestamp or NULL | NỘI BỘ | None |

## stg.stg_duplicate

Suspect duplicate groups found in this run, referenced by phone.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `group_id` | BIGINT | YES | Group identifier (smallest source row number of the group) | integer | NỘI BỘ | None |
| `phone` | VARCHAR(20) | YES | Phone of a profile in the group | 10 digits starting with 0 | ĐỊNH DANH CÁ NHÂN | Plain text in staging |
| `match_rule` | VARCHAR(20) | YES | Rule that matched the group | EMAIL or NAME_ADDR | NỘI BỘ | None |

## core.customer_clean

Clean customer profiles; never physically deleted (QT-13).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `customer_id` | BIGINT | NO | Surrogate id of the profile (identity) | positive integer | NỘI BỘ | None |
| `full_name` | VARCHAR(120) | NO | Normalised customer name | non-empty text | ĐỊNH DANH CÁ NHÂN | Plain text; shown unmasked in view_customer_masked (known gap) |
| `phone` | VARCHAR(20) | NO | Normalised phone; business key, UNIQUE | matches ^0[0-9]{9}$ (CHECK) | ĐỊNH DANH CÁ NHÂN | Plain text in core; masked in view_customer_masked; never written to fact_dq_issue or reports |
| `email` | VARCHAR(120) | YES | Lower-cased valid email | email or NULL | ĐỊNH DANH CÁ NHÂN | Plain text; not exposed in view_customer_masked |
| `address` | VARCHAR(255) | YES | Address | text or NULL | ĐỊNH DANH CÁ NHÂN | Plain text; not exposed in view_customer_masked |
| `store_key` | INT | NO | Store of the profile (default −1 Unknown) | existing store_key | NỘI BỘ | None |
| `created_at` | TIMESTAMP | YES | Creation date from the source | timestamp or NULL | NỘI BỘ | None |
| `is_active` | BOOLEAN | NO | FALSE after the profile was merged into another (default TRUE) | TRUE or FALSE | NỘI BỘ | None |
| `merged_into_id` | BIGINT | YES | Primary profile this profile was merged into | existing customer_id or NULL | NỘI BỘ | None |

## core.reject_customer

Raw records that could not be normalised, with a reason.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `reject_id` | BIGINT | NO | Surrogate id (identity) | positive integer | NỘI BỘ | None |
| `stg_id` | BIGINT | NO | Raw record rejected (foreign key to stg.stg_customer) | existing stg_id | NỘI BỘ | None |
| `run_key` | BIGINT | NO | Run that rejected it | existing run_key | NỘI BỘ | None |
| `reason_code` | VARCHAR(30) | NO | Why the record was rejected | PHONE_MISSING, PHONE_INVALID or NAME_MISSING | NỘI BỘ | None |
| `reason_text` | VARCHAR(255) | YES | Readable explanation | text | NỘI BỘ | Must not contain a full phone number |

## core.duplicate_review

Suspect duplicate groups waiting for a manager decision (BR-L7-04).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `review_id` | BIGINT | NO | Surrogate id (identity) | positive integer | NỘI BỘ | None |
| `group_id` | BIGINT | NO | Group identifier | integer | NỘI BỘ | None |
| `customer_id` | BIGINT | NO | Profile in the group (foreign key to customer_clean) | existing customer_id | NỘI BỘ | None |
| `match_rule` | VARCHAR(20) | YES | Rule that matched | EMAIL or NAME_ADDR (CHECK) | NỘI BỘ | None |
| `status` | VARCHAR(10) | NO | Decision state (default PENDING) | PENDING, CONFIRMED or REJECTED (CHECK) | NỘI BỘ | None |
| `reviewed_by` | VARCHAR(50) | YES | Name of the simulated user who decided | text or NULL | NỘI BỘ | User name only |
| `reviewed_at` | TIMESTAMP | YES | Decision time | timestamp or NULL | NỘI BỘ | None |

## core.merge_log

History of merges (BR-L7-05).

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `merge_id` | BIGINT | NO | Surrogate id (identity) | positive integer | NỘI BỘ | None |
| `group_id` | BIGINT | YES | Suspect group that was merged | integer or NULL | NỘI BỘ | None |
| `primary_customer_id` | BIGINT | NO | Profile kept | existing customer_id | NỘI BỘ | None |
| `merged_customer_id` | BIGINT | NO | Profile marked inactive | existing customer_id | NỘI BỘ | None |
| `merged_by` | VARCHAR(50) | YES | Name of the simulated user who merged | text or NULL | NỘI BỘ | User name only |
| `merged_at` | TIMESTAMP | YES | Merge time | timestamp or NULL | NỘI BỘ | None |

## core.view_customer_masked

View read by the Marketing role (QT-15). Not a table; nullability follows core.customer_clean.

| Column | Type | Nullable | Meaning | Valid values | Classification | Security handling |
|---|---|---|---|---|---|---|
| `customer_id` | BIGINT | NO | Profile id | existing customer_id | NỘI BỘ | None |
| `full_name` | VARCHAR(120) | NO | Customer name | non-empty text | ĐỊNH DANH CÁ NHÂN | NOT masked in the view (known gap, see checklist item 4) |
| `phone_masked` | TEXT | NO | First 3 digits + **** + last 3 digits | for example 090****567 | NỘI BỘ | Masked by the view expression LEFT(phone,3) \|\| '****' \|\| RIGHT(phone,3) |
| `store_key` | INT | NO | Store of the profile | existing store_key | NỘI BỘ | None |
| `is_active` | BOOLEAN | NO | Active flag | TRUE or FALSE | NỘI BỘ | None |
| `merged_into_id` | BIGINT | YES | Primary profile after a merge | existing customer_id or NULL | NỘI BỘ | None |

## Analysis views and pseudonymisation (criterion D4)

What the view used by the Marketing role exposes today:

| View | Columns it exposes | Direct identifier exposed? | Action |
|---|---|---|---|
| `core.view_customer_masked` | `customer_id`, `full_name`, `phone_masked`, `store_key`, `is_active`, `merged_into_id` | `phone_masked`: no (first 3 and last 3 digits only). `full_name`: **yes, shown in full**. `email` and `address`: no (not in the view) | left as is, with the reason: prototype simulates roles at the app layer only; masking `full_name` would require HMAC pseudonymisation with a key from `.env`, which is out of scope for BT3. Recorded as "CHƯA LÀM" in `docs/checklist-bao-mat.md` item 4. |

The `dwh` schema contains no direct identifier. If `full_name` stays exposed, record it as "CHƯA LÀM" in `docs/checklist-bao-mat.md` (item 4); if you fix it, record the fix as a bug with its own commit in `docs/bug-log.md`.
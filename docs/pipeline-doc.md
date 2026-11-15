# Pipeline Documentation – L7 Customer Data Quality (track DA)

## 1. Phases
customers_raw.csv --> [Extract] --> stg.stg_customer (raw, as-is)
|
[Quality: RAW measurement DQ01-DQ06]
|
[Transform] normalise phone, name, email; reject; de-duplicate by phone;
| find suspect duplicates (never auto-merged)
[Quality: CLEAN measurement DQ01-DQ06] --> gate (DQ01-DQ04)
|
[Load] one transaction: stg -> core (upsert by phone) -> dwh facts

| Phase | Folder | What it does |
|---|---|---|
| Extract | `src/extract/read_source.py` | reads the CSV as-is; rejects the file with a clear message if a required column is missing |
| Transform | `src/transform/` | `rules.py` (phone, name, email, date), `clean_customers.py`, `dedupe.py`, `intake.py`, `merge_rules.py`; pure functions, no database access |
| Quality | `src/quality/checks.py` | six checks DQ01–DQ06 at RAW and CLEAN, each returning total, failed and pass rate |
| Load | `src/load/loader.py`, `customer_repo.py` | writes PostgreSQL in one transaction; user actions (create profile, confirm merge) |
| Orchestration | `src/pipeline.py` | runs the phases; exit code 0 success, 1 technical error, 2 stopped by a quality gate |

## 2. Sources

| Item | Value |
|---|---|
| Source | `customers_raw.csv` |
| Format | CSV, UTF-8, 6 columns: `record_id`, `ho_ten`, `so_dien_thoai`, `email`, `dia_chi`, `ngay_tao` (no `store_code`, see TD-07) |
| Size | 67,037 rows (real file, kept outside the repository); 400 rows in `data/mau/customers_raw_sample.csv` (in the repository) |
| Update frequency | monthly (from the BT1 data requirements) |
| Owner | course case study dataset "Mekong Mobile Smart CRM" provided by the lecturer |
| Access | read-only; the pipeline never writes back to the source |

## 3. Targets and grain

| Table | Grain (one row = …) | Business key | Surrogate key |
|---|---|---|---|
| `dwh.fact_dq_result` | the result of ONE quality rule at ONE stage (RAW or CLEAN) for ONE store in ONE run | (`run_key`, `rule_key`, `stage`, `store_key`) | `result_key` |
| `dwh.fact_dq_issue` | ONE violation of ONE rule by ONE raw record in ONE run | none (`stg_id` is a degenerate dimension) | `issue_key` |
| `dwh.dim_run` | one pipeline run | none | `run_key` |
| `dwh.dim_dq_rule` | one version of one quality rule (SCD type 2 on `threshold_pct`) | `rule_code` (one current row) | `rule_key` |
| `dwh.dim_store` | one store (only the Unknown row −1 today) | `store_code` | `store_key` |
| `dwh.dim_date` | one calendar date | `full_date` | `date_key` |
| `core.customer_clean` | one customer profile, unique by phone | `phone` | `customer_id` |
| `core.reject_customer` | one raw record rejected in the latest run | `stg_id` | `reject_id` |
| `core.duplicate_review` | one profile inside one suspect group | (`group_id`, `customer_id`) | `review_id` |
| `core.merge_log` | one merge event | none | `merge_id` |

## 4. Cleaning rules and rows affected

| Rule | Action | Real file (67,037 rows) | Sample file (400 rows) |
|---|---|---|---|
| Phone missing (BR-L7-02) | rejected with reason `PHONE_MISSING`, never loaded to `core` | 4,133 | 26 |
| Phone not 10 digits after normalisation (QT-02) | rejected with reason `PHONE_INVALID` | 0 | 17 |
| Name missing | rejected with reason `NAME_MISSING` | 0 | 6 |
| Same normalised phone as an earlier record (QT-01) | raw record attached to the first profile, no new profile | 11,625 | 28 (400 − 49 − 323) |
| Phone normalisation (strip non-digits, prefix 84 to 0) | value rewritten | not counted separately (RAW pass rate of DQ02 was 69.73%) | not counted |
| Name cleanup (trim, collapse spaces, capitalise, keep Vietnamese marks) | value rewritten | not counted separately (RAW pass rate of DQ04 was 97.99%) | not counted |
| Email lower-case; invalid email set to NULL | value rewritten | 0 invalid (DQ05 RAW pass rate 100%) | not counted |
| Suspect duplicates (BR-L7-04: same email, or same unaccented name and address, different phone) | recorded for review, never merged automatically | 2,624 groups, 5,438 profiles | 23 groups, 47 profiles |
| Clean profiles in `core.customer_clean` | result | 51,279 (4,133 + 11,625 + 51,279 = 67,037) | 323 (49 + 28 + 323 = 400) |

A record with several problems carries only one reason code, in this order: phone first, then name (TD-12).

### Quality measurement (latest run on the real file)

The "Dimension" column maps each rule to the three dimensions of the course (completeness, accuracy, consistency).

| Code | Dimension | Object | RAW % | CLEAN % | Threshold % | Conclusion |
|---|---|---|---:|---:|---:|---|
| DQ01 | Completeness | phone present | 93.83 | 100 | 100 | Met |
| DQ02 | Accuracy | phone format | 69.73 | 100 | 100 | Met |
| DQ03 | Consistency | phone unique | 90.23 | 100 | 100 | Met |
| DQ04 | Accuracy | name clean | 97.99 | 100 | 100 | Met |
| DQ05 | Accuracy | email format | 100 | 100 | 99 | Met |
| DQ06 | Consistency | no pending suspected duplicates | not measured | 89.40 | 95 | **Not met** |

Overall clean score: 98.23. Only DQ01–DQ04 block loading (`gate: true` in `configs/thresholds.yaml`).

**Coverage of the three dimensions (honest status).** Accuracy has three rules (DQ02, DQ04, DQ05). Consistency has two checks (DQ03 unique key, DQ06 pending duplicates); there is no referential-integrity check and no allowed-values check yet. Completeness is measured only for the phone (DQ01); email, address and creation date have no completeness measure or threshold of their own. These gaps are known limitations (verified 15/11/2026).

## 5. Schedule and backfill

- **Schedule:** the source is updated monthly, so the pipeline is run manually once a month: `docker compose run --rm app python -m src.pipeline`. There is no scheduler (Airflow is out of scope).
- **Running twice on the same day:** safe. Staging tables are reloaded and `core` is upserted by phone, so `core.customer_clean`, `core.reject_customer`, `core.duplicate_review` and `dwh.fact_dq_issue` keep the same row counts (verified: 323 / 49 / 47 / 468 on the sample after two runs). `dwh.dim_run` and `dwh.fact_dq_result` gain one run (+1 and +11 rows) because they keep history.
- **Backfill:** point `SOURCE_CSV` at the older file and run the pipeline. A backfill by date range is not supported.
- **What is kept:** `fact_dq_issue` and `reject_customer` keep only the latest run (TD-09, TD-10); `fact_dq_result` keeps every run for the trend chart.

## 6. Known limitations, business impact and data latency

| Limitation | Business impact |
|---|---|
| The source has no `store_code`, so every profile has `store_key = −1` (TD-07) | store-level reports and the per-store access rule (NFR7) cannot be demonstrated; all stores appear as one |
| DQ06 is 89.4% on the real file (5,438 of 51,279 profiles in 2,624 unresolved groups), below the 95% threshold | Marketing may still contact the same customer twice until a manager confirms merges; the check is reported but does not block loading (TD-11, TD-14) |
| Only phone and name are checked for completeness; no referential-integrity or allowed-values checks | missing email (about 45% in the source) or address would not be flagged by a rule |
| Roles are simulated in the dashboard, not enforced by database roles | the dashboard connects with the database owner account; see the security checklist |
| `core.view_customer_masked` hides the phone but shows `full_name` | a Marketing user can read customer names |
| No historical raw data: staging is reloaded each run | a past run cannot be reproduced from the database alone |

**Data latency:** the data is a monthly batch, so it can be up to one month old. The numbers on the dashboard are as of the last pipeline run, and the dashboard caches aggregates for up to 60 seconds. Processing the real file takes about 45–55 seconds locally and about 90 seconds on a fresh Docker database.


"""Truy vấn CHỈ ĐỌC cho dashboard. Số điện thoại cho Marketing đi qua view che số (QT-15)."""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def _df(engine: Engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


def runs(engine: Engine) -> pd.DataFrame:
    """Các đợt chạy SUCCESS, mới nhất trước."""
    return _df(engine, "SELECT run_key, started_at, finished_at, source_file, source_row_count "
                       "FROM dwh.dim_run WHERE status = 'SUCCESS' ORDER BY run_key DESC")


def measures(engine: Engine, run_key: int) -> pd.DataFrame:
    return _df(engine, """
        SELECT r.rule_code, f.stage, f.total_records, f.failed_records, f.pass_rate_pct,
               r.threshold_pct, f.is_threshold_met
        FROM dwh.fact_dq_result f JOIN dwh.dim_dq_rule r ON r.rule_key = f.rule_key
        WHERE f.run_key = :k ORDER BY r.rule_code, f.stage""", {"k": run_key})


def trend(engine: Engine, rule_code: str | None) -> pd.DataFrame:
    """Điểm sạch (trung bình các quy tắc ở CLEAN) hoặc tỉ lệ đạt một quy tắc, theo đợt chạy."""
    where, params = "WHERE f.stage = 'CLEAN' AND d.status = 'SUCCESS'", {}
    if rule_code:
        where += " AND r.rule_code = :c"
        params["c"] = rule_code
    return _df(engine, f"""
        SELECT d.run_key, d.started_at, ROUND(AVG(f.pass_rate_pct), 2) AS pass_rate_pct,
               ROUND(AVG(r.threshold_pct), 2) AS threshold_pct
        FROM dwh.fact_dq_result f
        JOIN dwh.dim_dq_rule r ON r.rule_key = f.rule_key
        JOIN dwh.dim_run d ON d.run_key = f.run_key
        {where} GROUP BY d.run_key, d.started_at ORDER BY d.run_key""", params)


def reject_summary(engine: Engine) -> pd.DataFrame:
    return _df(engine, "SELECT reason_code, MIN(reason_text) AS reason_text, COUNT(*) AS records "
                       "FROM core.reject_customer GROUP BY reason_code ORDER BY records DESC")


def pending_overview(engine: Engine) -> dict:
    row = _df(engine, "SELECT COUNT(DISTINCT group_id) AS groups, COUNT(*) AS records "
                      "FROM core.duplicate_review WHERE status = 'PENDING'").iloc[0]
    return {"groups": int(row["groups"]), "records": int(row["records"])}


def pending_groups(engine: Engine, masked: bool, limit: int = 200) -> pd.DataFrame:
    """Nhóm nghi trùng chờ xác nhận, nhóm mới nhất trước (FR7). masked=True: dùng view che số."""
    phone = "m.phone_masked" if masked else "c.phone"
    source = "core.view_customer_masked m ON m.customer_id = r.customer_id" if masked else \
             "core.customer_clean c ON c.customer_id = r.customer_id"
    alias = "m" if masked else "c"
    return _df(engine, f"""
        SELECT r.group_id, r.customer_id, {alias}.full_name, {phone} AS phone, r.match_rule
        FROM core.duplicate_review r JOIN {source}
        WHERE r.status = 'PENDING'
          AND r.group_id IN (SELECT DISTINCT group_id FROM core.duplicate_review
                             WHERE status = 'PENDING' ORDER BY group_id DESC LIMIT :lim)
        ORDER BY r.group_id DESC, r.customer_id""", {"lim": limit})


def merge_history(engine: Engine) -> pd.DataFrame:
    return _df(engine, """
        SELECT merged_at, merged_by, merged_customer_id AS secondary_id,
               primary_customer_id AS primary_id, group_id
        FROM core.merge_log ORDER BY merged_at DESC LIMIT 200""")

"""PHA 4 - LOAD: ghi vào PostgreSQL trong MỘT transaction. KHÔNG biến đổi dữ liệu.

Chạy lại được (NFR2): stg xóa và nạp lại; core upsert theo số điện thoại; duplicate_review
ON CONFLICT DO NOTHING (giữ trạng thái đã xác nhận); fact_dq_issue chỉ giữ đợt gần nhất.
Một đợt chạy mới thêm một dòng dim_run và các dòng fact_dq_result của nó (lịch sử xu hướng).
Hỏng giữa chừng -> rollback toàn bộ, không nạp dở (UC1 luồng ngoại lệ 8a).
"""
import datetime as dt
import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from src.errors import LoadError

log = logging.getLogger(__name__)
UNKNOWN_STORE = -1          # tệp nguồn không có store_code (xem docs/thay-doi-thiet-ke.md)


def sync_rules(conn: Connection, rules_cfg: dict, today: dt.date) -> dict[str, int]:
    """dim_dq_rule SCD loại 2 cho threshold_pct. Trả về {rule_code: rule_key hiện hành}."""
    keys: dict[str, int] = {}
    for code, cfg in rules_cfg.items():
        cur = conn.execute(text(
            "SELECT rule_key, threshold_pct FROM dwh.dim_dq_rule "
            "WHERE rule_code = :c AND is_current"), {"c": code}).first()
        new_threshold = float(cfg["threshold_pct"])
        if cur is not None and float(cur.threshold_pct) == new_threshold:
            keys[code] = cur.rule_key
            continue
        if cur is not None:                                   # đổi ngưỡng: đóng dòng cũ, giữ lịch sử
            conn.execute(text("UPDATE dwh.dim_dq_rule SET is_current = FALSE, valid_to = :d "
                              "WHERE rule_key = :k"), {"d": today, "k": cur.rule_key})
        keys[code] = conn.execute(text(
            "INSERT INTO dwh.dim_dq_rule (rule_code, rule_name, quality_dimension, column_name, "
            "threshold_pct, is_active, valid_from, valid_to, is_current) "
            "VALUES (:c, :n, :d, :col, :t, TRUE, :vf, NULL, TRUE) RETURNING rule_key"),
            {"c": code, "n": cfg["name"], "d": cfg["dimension"], "col": cfg["column"],
             "t": new_threshold, "vf": today}).scalar_one()
    return keys


def _ensure_date(conn: Connection, day: dt.date) -> int:
    key = int(day.strftime("%Y%m%d"))
    conn.execute(text(
        "INSERT INTO dwh.dim_date (date_key, full_date, month_no, quarter_no, year_no) "
        "VALUES (:k, :d, :m, :q, :y) ON CONFLICT DO NOTHING"),
        {"k": key, "d": day, "m": day.month, "q": (day.month - 1) // 3 + 1, "y": day.year})
    return key


def _insert_df(conn: Connection, df: pd.DataFrame, table: str, schema: str) -> None:
    if len(df):
        df.to_sql(table, conn, schema=schema, if_exists="append", index=False,
                  method="multi", chunksize=2000)


def load_run(engine: Engine, result, measures, issues: pd.DataFrame, rules_cfg: dict,
             source_file: str, started_at: dt.datetime) -> dict:
    """Nạp một đợt chạy. Trả về số liệu để đưa vào báo cáo."""
    raw = result.raw
    today = started_at.date()
    with engine.begin() as conn:
        rule_keys = sync_rules(conn, rules_cfg, today)
        date_key = _ensure_date(conn, today)
        run_key = conn.execute(text(
            "INSERT INTO dwh.dim_run (started_at, source_file, source_row_count, status) "
            "VALUES (:s, :f, :n, 'RUNNING') RETURNING run_key"),
            {"s": started_at, "f": source_file, "n": len(raw)}).scalar_one()

        # --- stg: xóa và nạp lại nguyên trạng ---
        conn.execute(text("TRUNCATE stg.stg_customer, stg.stg_customer_clean, stg.stg_duplicate, "
                          "core.reject_customer"))
        stg = pd.DataFrame({
            "stg_id": raw["source_row_no"], "source_row_no": raw["source_row_no"],
            "record_id_raw": raw["record_id"], "full_name_raw": raw["ho_ten"],
            "phone_raw": raw["so_dien_thoai"], "email_raw": raw["email"],
            "address_raw": raw["dia_chi"], "created_at_raw": raw["ngay_tao"], "run_key": run_key})
        _insert_df(conn, stg, "stg_customer", "stg")
        loaded = conn.execute(text("SELECT COUNT(*) FROM stg.stg_customer")).scalar_one()
        if loaded != len(raw):                                # UC1 3b
            raise LoadError(f"Số dòng nạp stg ({loaded}) khác số dòng của tệp ({len(raw)})")

        # --- bản ghi bị loại (NFR6: luôn có mã lý do và gắn với một đợt chạy) ---
        rej = result.rejects.rename(columns={"source_row_no": "stg_id"}).assign(run_key=run_key)
        _insert_df(conn, rej[["stg_id", "run_key", "reason_code", "reason_text"]],
                   "reject_customer", "core")

        # --- core: upsert hồ sơ sạch theo số điện thoại (QT-01) ---
        before = conn.execute(text("SELECT COUNT(*) FROM core.customer_clean")).scalar_one()
        clean_stg = result.clean[["source_row_no", "full_name", "phone", "email", "address", "created_at"]]
        clean_stg = clean_stg.astype({"created_at": "datetime64[us]"}).astype(object).where(clean_stg.notna(), None)
        _insert_df(conn, clean_stg, "stg_customer_clean", "stg")
        conn.execute(text(
            "INSERT INTO core.customer_clean (full_name, phone, email, address, store_key, created_at) "
            "SELECT full_name, phone, email, address, :s, created_at FROM stg.stg_customer_clean "
            "ORDER BY source_row_no "
            "ON CONFLICT (phone) DO UPDATE SET full_name = EXCLUDED.full_name, "
            "email = EXCLUDED.email, address = EXCLUDED.address, created_at = EXCLUDED.created_at "
            "WHERE (core.customer_clean.full_name, core.customer_clean.email, core.customer_clean.address, "
            "core.customer_clean.created_at) IS DISTINCT FROM "
            "(EXCLUDED.full_name, EXCLUDED.email, EXCLUDED.address, EXCLUDED.created_at)"),
            {"s": UNKNOWN_STORE})
        after = conn.execute(text("SELECT COUNT(*) FROM core.customer_clean")).scalar_one()
        new_customers = after - before

        # --- nhóm nghi trùng: giữ trạng thái đã xác nhận, bỏ nhóm PENDING không còn nghi trùng ---
        _insert_df(conn, result.suspects, "stg_duplicate", "stg")
        conn.execute(text(
            "INSERT INTO core.duplicate_review (group_id, customer_id, match_rule) "
            "SELECT d.group_id, c.customer_id, d.match_rule FROM stg.stg_duplicate d "
            "JOIN core.customer_clean c ON c.phone = d.phone "
            "ON CONFLICT (group_id, customer_id) DO NOTHING"))
        conn.execute(text(
            "DELETE FROM core.duplicate_review r WHERE r.status = 'PENDING' AND NOT EXISTS ("
            "SELECT 1 FROM stg.stg_duplicate d JOIN core.customer_clean c ON c.phone = d.phone "
            "WHERE d.group_id = r.group_id AND c.customer_id = r.customer_id)"))

        # --- kho dữ liệu: fact_dq_result và fact_dq_issue ---
        conn.execute(text(
            "INSERT INTO dwh.fact_dq_result (date_key, run_key, rule_key, store_key, stage, "
            "total_records, failed_records, pass_rate_pct, is_threshold_met) "
            "VALUES (:dk, :rk, :ruk, :sk, :st, :t, :f, :p, :ok)"),
            [{"dk": date_key, "rk": run_key, "ruk": rule_keys[m.rule_code], "sk": UNKNOWN_STORE,
              "st": m.stage, "t": m.total, "f": m.failed, "p": m.pass_rate_pct,
              "ok": m.is_threshold_met} for m in measures])
        conn.execute(text("DELETE FROM dwh.fact_dq_issue WHERE run_key <> :rk"), {"rk": run_key})
        if len(issues):
            fact = issues.assign(date_key=date_key, run_key=run_key, store_key=UNKNOWN_STORE,
                                 rule_key=issues["rule_code"].map(rule_keys))
            # dup_group_id để NULL (cột cho phép rỗng) nên không đưa vào câu INSERT
            _insert_df(conn, fact[["date_key", "run_key", "rule_key", "store_key", "stg_id",
                                   "issue_detail"]], "fact_dq_issue", "dwh")

        finished = dt.datetime.now()
        conn.execute(text("UPDATE dwh.dim_run SET finished_at = :f, status = 'SUCCESS' "
                          "WHERE run_key = :k"), {"f": finished, "k": run_key})
        counts = table_counts(conn)

    read_n, rejected_n = len(raw), len(result.rejects)
    valid_n = read_n - rejected_n
    return {"run_key": run_key, "read": read_n, "rejected": rejected_n,
            "new_customers": new_customers, "attached_to_existing": valid_n - new_customers,
            "table_counts": counts}


def table_counts(conn: Connection) -> dict[str, int]:
    names = ["stg.stg_customer", "core.customer_clean", "core.reject_customer",
             "core.duplicate_review", "core.merge_log", "dwh.dim_run",
             "dwh.fact_dq_result", "dwh.fact_dq_issue"]
    return {n: conn.execute(text(f"SELECT COUNT(*) FROM {n}")).scalar_one() for n in names}


def record_failed_run(engine: Engine, source_file: str, row_count: int, started_at: dt.datetime) -> None:
    """Ghi một dòng dim_run FAILED sau khi transaction chính đã rollback (best-effort)."""
    try:
        with engine.begin() as conn:
            conn.execute(text(
                "INSERT INTO dwh.dim_run (started_at, finished_at, source_file, source_row_count, status) "
                "VALUES (:s, :f, :n, :c, 'FAILED')"),
                {"s": started_at, "f": dt.datetime.now(), "n": source_file, "c": row_count})
    except Exception:                                         # noqa: BLE001
        log.warning("Không ghi được đợt chạy FAILED vào dim_run")

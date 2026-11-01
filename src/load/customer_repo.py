"""Truy cập dữ liệu cho thao tác của người dùng: tạo hồ sơ mới, gộp, báo không trùng.

Quy tắc nghiệp vụ nằm ở src/transform (intake.py, merge_rules.py); module này chỉ đọc ghi SQL.
"""
import datetime as dt

from sqlalchemy import text
from sqlalchemy.engine import Engine

from src.errors import InvalidInputError
from src.transform import merge_rules


def find_by_phone(engine: Engine, phone: str) -> int | None:
    with engine.connect() as conn:
        return conn.execute(text("SELECT customer_id FROM core.customer_clean WHERE phone = :p"),
                            {"p": phone}).scalar()


def insert_customer(engine: Engine, full_name: str, phone: str, email: str | None) -> int:
    with engine.begin() as conn:
        return conn.execute(text(
            "INSERT INTO core.customer_clean (full_name, phone, email, store_key, created_at) "
            "VALUES (:n, :p, :e, -1, :t) RETURNING customer_id"),
            {"n": full_name, "p": phone, "e": email, "t": dt.datetime.now()}).scalar_one()


def _lock_group(conn, group_id: int) -> list[dict]:
    rows = conn.execute(text(
        "SELECT r.customer_id, r.status, c.created_at, c.is_active, c.merged_into_id "
        "FROM core.duplicate_review r JOIN core.customer_clean c USING (customer_id) "
        "WHERE r.group_id = :g ORDER BY r.customer_id FOR UPDATE OF r, c"), {"g": group_id}).mappings().all()
    return [dict(r) for r in rows]


def confirm_merge(engine: Engine, group_id: int, role: str, user: str) -> dict:
    """UC5: giữ một hồ sơ chính, đánh dấu hồ sơ phụ ngừng sử dụng (QT-13), ghi lịch sử (BR-L7-05)."""
    merge_rules.require_store_manager(role)
    if not user or not user.strip():
        raise InvalidInputError("Cần nhập tên người thực hiện để ghi lịch sử gộp.", {"user": "Bắt buộc"})
    with engine.begin() as conn:
        members = _lock_group(conn, group_id)
        merge_rules.check_merge_allowed(members)
        primary = merge_rules.choose_primary(members)
        now = dt.datetime.now()
        secondaries = [m["customer_id"] for m in members if m["customer_id"] != primary["customer_id"]]
        for sid in secondaries:
            conn.execute(text("UPDATE core.customer_clean SET is_active = FALSE, merged_into_id = :p "
                              "WHERE customer_id = :s"), {"p": primary["customer_id"], "s": sid})
            conn.execute(text(
                "INSERT INTO core.merge_log (group_id, primary_customer_id, merged_customer_id, "
                "merged_by, merged_at) VALUES (:g, :p, :s, :u, :t)"),
                {"g": group_id, "p": primary["customer_id"], "s": sid, "u": user.strip(), "t": now})
        conn.execute(text("UPDATE core.duplicate_review SET status = 'CONFIRMED', reviewed_by = :u, "
                          "reviewed_at = :t WHERE group_id = :g"), {"u": user.strip(), "t": now, "g": group_id})
    return {"data": {"group_id": group_id, "primary_customer_id": primary["customer_id"],
                     "merged_customer_ids": secondaries}}


def reject_group(engine: Engine, group_id: int, role: str, user: str) -> dict:
    """UC5 4a: nhóm chuyển REJECTED, không xuất hiện lại ở các đợt chạy sau."""
    merge_rules.require_store_manager(role)
    with engine.begin() as conn:
        members = _lock_group(conn, group_id)
        merge_rules.check_merge_allowed(members)
        conn.execute(text("UPDATE core.duplicate_review SET status = 'REJECTED', reviewed_by = :u, "
                          "reviewed_at = :t WHERE group_id = :g"),
                     {"u": (user or "").strip() or "unknown", "t": dt.datetime.now(), "g": group_id})
    return {"data": {"group_id": group_id, "status": "REJECTED"}}

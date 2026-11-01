"""Quy tắc gộp hồ sơ (UC5, FR8, QT-13, BR-L7-01) - HÀM THUẦN, không đọc ghi CSDL."""
import pandas as pd

from src.errors import (InvalidInputError, MergeConflictError, NotFoundError,
                        PermissionDeniedError)

ROLE_STORE_MANAGER = "STORE_MANAGER"
ROLE_MARKETING = "MARKETING"


def require_store_manager(role: str) -> None:
    """Chỉ Quản lý cửa hàng được xác nhận gộp (SRS Mục 2)."""
    if role != ROLE_STORE_MANAGER:
        raise PermissionDeniedError(
            "Không thể thực hiện thao tác này. Chỉ Quản lý cửa hàng được xác nhận gộp hồ sơ. "
            "Hãy chuyển sang vai trò Quản lý cửa hàng.")


def choose_primary(members: list[dict]) -> dict:
    """Hồ sơ chính = created_at sớm nhất (UC5 bước 3). Hòa hoặc thiếu ngày: customer_id nhỏ hơn."""
    def key(m: dict):
        ts = m.get("created_at")
        missing = ts is None or bool(pd.isna(ts))
        return (missing, pd.Timestamp.max if missing else pd.Timestamp(ts), m["customer_id"])
    return min(members, key=key)


def check_merge_allowed(members: list[dict]) -> None:
    """Ném lỗi nếu nhóm không thể gộp (UC5 luồng ngoại lệ 5a)."""
    if not members:
        raise NotFoundError("Không tìm thấy nhóm nghi trùng này.")
    if len(members) < 2:
        raise InvalidInputError("Nhóm cần ít nhất hai hồ sơ để gộp.")
    if any(m["status"] != "PENDING" for m in members):
        raise MergeConflictError("Nhóm này đã được xử lý bởi thao tác khác. Hãy tải lại danh sách.")
    if any((not m["is_active"]) or m["merged_into_id"] is not None for m in members):
        raise MergeConflictError("Hồ sơ phụ đã được gộp bởi thao tác khác. Hãy tải lại danh sách.")

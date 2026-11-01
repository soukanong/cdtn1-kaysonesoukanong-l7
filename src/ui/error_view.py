"""Lớp trình bày: nơi DUY NHẤT quyết định hiển thị lỗi ra màn hình (Streamlit)."""
import logging

import streamlit as st

from src.errors import AppError

log = logging.getLogger(__name__)


def run_safely(action):
    """Chạy một thao tác trả về {"data": ...}. Trả về data, hoặc None nếu có lỗi.

    - AppError (lỗi người dùng): hiện câu người đọc, lỗi theo từng trường.
    - Lỗi khác (lỗi hệ thống): GHI LOG chi tiết, chỉ hiện câu chung chung. KHÔNG in chuỗi kết nối.
    """
    try:
        return action()["data"]
    except AppError as e:
        st.error(e.message)
        for field, msg in e.fields.items():
            st.caption(f"• {field}: {msg}")
    except Exception:                                   # noqa: BLE001
        log.exception("Lỗi hệ thống khi xử lý thao tác")
        st.error("Hệ thống đang gặp sự cố. Vui lòng thử lại.")
    return None

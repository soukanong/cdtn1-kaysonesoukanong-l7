"""Lỗi của hệ thống L7. Không biết gì về giao diện (Streamlit) hay HTTP.

Hai nhóm lỗi, xử lý khác nhau:
  - AppError: lỗi người dùng, ĐÃ LƯỜNG TRƯỚC, mang mã + câu người đọc + lỗi theo trường.
    Giao diện chỉ việc hiển thị.
  - SystemFault: lỗi hệ thống (mất kết nối, thiếu tệp nguồn...). Phải GHI LOG đầy đủ,
    người dùng chỉ thấy câu chung chung; không bao giờ lộ chuỗi kết nối.
Quy ước phản hồi: error (mã máy đọc) · message (câu người đọc) · fields (lỗi theo trường).
"""


class AppError(Exception):
    code = "LOI_HE_THONG"

    def __init__(self, message: str, fields: dict | None = None):
        super().__init__(message)
        self.message = message
        self.fields = fields or {}

    def to_dict(self) -> dict:
        body = {"error": self.code, "message": self.message}
        if self.fields:
            body["fields"] = self.fields
        return body


class InvalidInputError(AppError):       # dữ liệu nhập sai / thiếu (FR1, FR3)
    code = "DU_LIEU_KHONG_HOP_LE"


class PermissionDeniedError(AppError):   # vai trò không được phép (QT-15)
    code = "KHONG_DU_QUYEN"


class NotFoundError(AppError):
    code = "KHONG_TIM_THAY"


class PhoneExistsError(AppError):        # QT-01
    code = "SO_DIEN_THOAI_DA_TON_TAI"


class MergeConflictError(AppError):      # UC5, luồng ngoại lệ 5a
    code = "XUNG_DOT_GOP"


class SystemFault(Exception):
    """Lỗi kỹ thuật không lường trước: pipeline trả mã thoát 1."""


class SourceFileError(SystemFault):
    """Tệp nguồn không có hoặc thiếu cột bắt buộc (UC1 luồng ngoại lệ 3a)."""


class LoadError(SystemFault):
    """Nạp kho dữ liệu không khớp (UC1 luồng ngoại lệ 3b, 8a)."""

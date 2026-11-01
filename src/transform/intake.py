"""UC7 / FR1-FR3: kiểm tra khi tạo hồ sơ khách hàng mới. Dùng chung quy tắc với pipeline.

Hàm thuần: việc tra số điện thoại trong CSDL được truyền vào qua `find_by_phone`.
"""
from collections.abc import Callable

from src.errors import InvalidInputError, PhoneExistsError
from src.transform import rules


def validate_new_customer(full_name, phone_raw, email_raw=None,
                          find_by_phone: Callable[[str], int | None] | None = None) -> dict:
    fields: dict[str, str] = {}
    name = rules.normalize_name(full_name)
    phone, reason = rules.classify_phone(phone_raw)
    if name is None:
        fields["full_name"] = "Họ tên là bắt buộc."
    if reason == "PHONE_MISSING":
        fields["phone"] = "Số điện thoại là bắt buộc."
    elif reason == "PHONE_INVALID":
        fields["phone"] = "Số điện thoại phải đủ 10 chữ số và bắt đầu bằng 0."
    if not rules.is_empty(email_raw) and not rules.email_is_valid(email_raw):
        fields["email"] = "Email không đúng định dạng."
    if fields:
        raise InvalidInputError("Không thể tạo hồ sơ khách hàng. Hãy sửa các trường được nêu.", fields)

    existing_id = find_by_phone(phone) if find_by_phone else None
    if existing_id is not None:                                          # QT-01
        raise PhoneExistsError(
            f"Số điện thoại này đã có ở hồ sơ #{existing_id}. "
            "Hãy mở hồ sơ đó thay vì tạo mới.", {"phone": f"Đã có ở hồ sơ #{existing_id}"})
    return {"full_name": name, "phone": phone, "email": rules.normalize_email(email_raw)}

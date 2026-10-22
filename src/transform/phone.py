import re

import pandas as pd


def normalize_phone(raw):
    """Chuẩn hóa số điện thoại (QT-02). Trả về (số chuẩn, mã lý do)."""
    if pd.isna(raw) or str(raw).strip() == "":
        return None, "PHONE_MISSING"
    digits = re.sub(r"\D", "", str(raw))
    if digits.startswith("84"):
        digits = "0" + digits[2:]
    if re.fullmatch(r"0[0-9]{9}", digits):
        return digits, None
    return None, "PHONE_INVALID"

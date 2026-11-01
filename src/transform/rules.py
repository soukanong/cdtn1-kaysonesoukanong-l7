"""Quy tắc chuẩn hóa - HÀM THUẦN: không đọc ghi CSDL, không đọc tệp.

Mã quy tắc (QT-02...) ghi ngay trong chú thích để truy vết từ SRS tới mã nguồn.
"""
import re
import unicodedata

import pandas as pd

EMPTY_TOKENS = {"", "nan", "none", "nat", "<na>", "null"}
PHONE_RE = re.compile(r"^0[0-9]{9}$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")

REASON_TEXT = {
    "PHONE_MISSING": "Thiếu số điện thoại",
    "PHONE_INVALID": "Số điện thoại không đủ 10 chữ số hoặc không bắt đầu bằng 0 sau khi chuẩn hóa",
    "NAME_MISSING": "Thiếu họ tên",
}


def is_empty(value) -> bool:
    """True nếu giá trị rỗng: None, chuỗi trống, NaN/NaT/NA của pandas, hoặc chuỗi 'nan'.

    Cần hàm riêng vì pandas biểu diễn ô trống bằng NaN, mà `is None` không bắt được
    NaN: str(NaN) cho ra 'nan' và giá trị đó lọt vào kho dữ liệu.
    """
    if value is None:
        return True
    try:
        if bool(pd.isna(value)):
            return True
    except (TypeError, ValueError):
        pass                          # không phải giá trị vô hướng -> xét dạng chuỗi
    return str(value).strip().lower() in EMPTY_TOKENS


def normalize_phone(raw) -> str | None:
    """QT-02: trả về số 10 chữ số bắt đầu bằng 0, hoặc None nếu rỗng/không hợp lệ.

    Bỏ ký tự không phải chữ số, đổi tiền tố 84 (11 chữ số) thành 0.
    """
    if is_empty(raw):
        return None
    digits = re.sub(r"\D", "", str(raw))
    if digits.startswith("84") and len(digits) == 11:
        digits = "0" + digits[2:]
    return digits if PHONE_RE.fullmatch(digits) else None


def classify_phone(raw) -> tuple[str | None, str | None]:
    """Trả về (số_chuẩn, mã_lý_do). Mã lý do: PHONE_MISSING | PHONE_INVALID | None."""
    if is_empty(raw):
        return None, "PHONE_MISSING"
    phone = normalize_phone(raw)
    return (phone, None) if phone else (None, "PHONE_INVALID")


def normalize_name(raw) -> str | None:
    """FR3: bỏ khoảng trắng thừa, viết hoa chữ cái đầu mỗi từ, giữ dấu tiếng Việt."""
    if is_empty(raw):
        return None
    text = unicodedata.normalize("NFC", str(raw))
    return " ".join(word.capitalize() for word in text.split())


def is_clean_name(raw) -> bool:
    """DQ04: không rỗng, không khoảng trắng đầu/cuối hoặc liên tiếp."""
    if is_empty(raw):
        return False
    text = str(raw)
    return text == " ".join(text.split())


def strip_accents(text: str) -> str:
    """'Nguyễn Đức' -> 'Nguyen Duc'."""
    text = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def name_key(name: str | None) -> str | None:
    """Khóa so khớp họ tên không dấu đã chuẩn hóa (BR-L7-04)."""
    return None if is_empty(name) else strip_accents(str(name)).lower()


def address_key(raw) -> str | None:
    """Khóa so khớp địa chỉ đã chuẩn hóa: không dấu, chữ thường, bỏ dấu câu (BR-L7-04)."""
    if is_empty(raw):
        return None
    cleaned = re.sub(r"[^a-z0-9 ]", " ", strip_accents(str(raw)).lower())
    return " ".join(cleaned.split()) or None


def clean_address(raw) -> str | None:
    return " ".join(str(raw).split()) if not is_empty(raw) else None


def email_is_valid(raw) -> bool:
    return (not is_empty(raw)) and bool(EMAIL_RE.fullmatch(str(raw).strip()))


def normalize_email(raw) -> str | None:
    """Chữ thường. Sai định dạng -> None (và được ghi vi phạm DQ05). Thiếu: không tự điền."""
    return str(raw).strip().lower() if email_is_valid(raw) else None


def parse_dates(series: pd.Series) -> pd.Series:
    """Đọc cột ngày: ưu tiên dạng ISO yyyy-mm-dd, các giá trị còn lại thử dạng dd/mm/yyyy.

    Không gọi to_datetime với dayfirst=True cho chuỗi ISO, vì khi đó '2024-05-06' bị đọc nhầm thành ngày 5 tháng 6.
    """
    cleaned = series.where(~series.map(is_empty))
    result = pd.to_datetime(cleaned, format="%Y-%m-%d", errors="coerce")
    rest = cleaned[result.isna() & cleaned.notna()]
    if len(rest):
        result.loc[rest.index] = pd.to_datetime(rest, format="mixed", dayfirst=True, errors="coerce")
    return result

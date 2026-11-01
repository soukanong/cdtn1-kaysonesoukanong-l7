"""Kiểm thử quy tắc chuẩn hóa (hàm thuần, không cần CSDL hay tệp trên máy)."""
import pytest

from src.transform import rules


# ---------------- LOẠI 1: LUỒNG ĐÚNG ----------------
@pytest.mark.parametrize("raw", ["+84 901 234 567", "84901234567", "0901.234.567", "0901234567"])
def test_TR01_bon_dang_so_dien_thoai_ve_dang_chuan(raw):          # QT-02
    assert rules.normalize_phone(raw) == "0901234567"


def test_TR02_ho_ten_bo_khoang_trang_thua_va_viet_hoa_dau_tu():
    assert rules.normalize_name("  nGUYỄN   văn  an ") == "Nguyễn Văn An"
    assert rules.normalize_name("ĐẶNG THỊ LAN") == "Đặng Thị Lan"          # giữ dấu tiếng Việt


def test_TR03_email_chu_thuong_va_sai_dinh_dang_thanh_none():
    assert rules.normalize_email(" An@Example.COM ") == "an@example.com"
    assert rules.normalize_email("an.example.com") is None


def test_TR04_khoa_so_khop_ten_khong_dau():
    assert rules.name_key("Nguyễn Đức Anh") == "nguyen duc anh"
    assert rules.address_key("12 Lê Lợi, Q.1") == "12 le loi q 1"


# ---------------- LOẠI 2: GIÁ TRỊ BIÊN ----------------
@pytest.mark.parametrize("raw", ["090123456", "09012345678", "0084901234567", "1901234567"])
def test_TR05_bien_do_dai_va_dau_so_deu_khong_hop_le(raw):
    """9 chữ số, 11 chữ số, 13 chữ số, hoặc không bắt đầu bằng 0 -> PHONE_INVALID."""
    phone, reason = rules.classify_phone(raw)
    assert phone is None and reason == "PHONE_INVALID"


def test_TR06_dung_10_chu_so_la_hop_le_va_11_chu_so_tien_to_84_cung_hop_le():
    assert rules.classify_phone("0901234567") == ("0901234567", None)
    assert rules.classify_phone("84901234567") == ("0901234567", None)


# ---------------- LOẠI 3: DỮ LIỆU SAI ----------------
@pytest.mark.parametrize("raw", [None, "", "   ", float("nan"), "nan", "None"])
def test_TR07_gia_tri_rong_la_PHONE_MISSING_khong_phai_chuoi_nan(raw):
    assert rules.is_empty(raw) is True
    assert rules.classify_phone(raw) == (None, "PHONE_MISSING")


def test_TR08_chu_cai_trong_so_dien_thoai_khong_crash():
    assert rules.classify_phone("abc") == (None, "PHONE_INVALID")


# ---------------- NGÀY: ISO không bị đọc nhầm tháng/ngày ----------------
def test_TR09_ngay_iso_khong_bi_doc_nham_thang_ngay():
    """Giá trị biên: '2024-05-06' phải là 6/5/2024, không phải 5/6/2024 (lỗi khi dùng dayfirst=True cho ISO)."""
    import pandas as pd
    got = rules.parse_dates(pd.Series(["2024-05-06", "2024-12-01", "", "abc"]))
    assert got.iloc[0] == pd.Timestamp("2024-05-06") and got.iloc[1] == pd.Timestamp("2024-12-01")
    assert pd.isna(got.iloc[2]) and pd.isna(got.iloc[3])             # rỗng hoặc rác -> NaT, không crash


def test_TR10_ngay_dang_dd_mm_yyyy_van_doc_duoc():
    import pandas as pd
    got = rules.parse_dates(pd.Series(["06/05/2024", "13/01/2025"]))
    assert got.iloc[0] == pd.Timestamp("2024-05-06") and got.iloc[1] == pd.Timestamp("2025-01-13")

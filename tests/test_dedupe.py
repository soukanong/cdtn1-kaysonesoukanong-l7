"""BR-L7-04: tìm hồ sơ nghi trùng. Pipeline chỉ ĐỀ XUẤT, không tự gộp (BR-L7-01)."""
import pandas as pd

from src.transform import dedupe, rules


def clean_df(rows):
    df = pd.DataFrame(rows, columns=["phone", "email", "name", "addr"])
    return pd.DataFrame({
        "source_row_no": range(1, len(df) + 1), "phone": df["phone"], "email": df["email"],
        "name_key": df["name"].map(rules.name_key), "addr_key": df["addr"].map(rules.address_key)})


def test_DD01_trung_email_khac_hoa_thuong_la_nghi_trung():
    s = dedupe.find_suspects(clean_df([("0901111111", "a@x.com", "An", "1 A"),
                                       ("0902222222", "a@x.com", "Bình", "2 B")]))
    assert set(s["phone"]) == {"0901111111", "0902222222"} and set(s["match_rule"]) == {"EMAIL"}


def test_DD02_trung_ho_ten_khong_dau_va_dia_chi_la_nghi_trung():
    s = dedupe.find_suspects(clean_df([("0901111111", None, "Nguyễn Văn An", "12 Lê Lợi, Q.1"),
                                       ("0902222222", None, "NGUYEN VAN AN", "12 le loi q 1")]))
    assert len(s) == 2 and set(s["match_rule"]) == {"NAME_ADDR"}


def test_DD03_chi_trung_ho_ten_khong_trung_dia_chi_thi_khong_nghi_trung():
    s = dedupe.find_suspects(clean_df([("0901111111", None, "Nguyễn Văn An", "1 A"),
                                       ("0902222222", None, "Nguyễn Văn An", "2 B")]))
    assert s.empty


def test_DD04_email_rong_khong_duoc_coi_la_trung_nhau():
    s = dedupe.find_suspects(clean_df([("0901111111", None, "An", "1 A"),
                                       ("0902222222", None, "Bình", "2 B")]))
    assert s.empty


def test_DD05_ma_nhom_on_dinh_giua_cac_lan_chay_va_la_dong_nguon_nho_nhat():
    rows = [("0901111111", "a@x.com", "An", "1 A"), ("0902222222", "z@x.com", "Bình", "2 B"),
            ("0903333333", "a@x.com", "Cường", "3 C")]
    first, second = dedupe.find_suspects(clean_df(rows)), dedupe.find_suspects(clean_df(rows))
    assert first.equals(second) and set(first["group_id"]) == {1}

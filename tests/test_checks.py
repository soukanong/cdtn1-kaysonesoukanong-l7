"""Kiểm thử các phép đo chất lượng DQ01-DQ06 và việc pipeline từ chối dữ liệu sai."""
import pandas as pd
import pytest

from src import config
from src.quality import checks
from src.transform import clean_customers


def make_raw(rows: list[tuple]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["record_id", "ho_ten", "so_dien_thoai", "email", "dia_chi", "ngay_tao"])
    df.insert(0, "source_row_no", range(1, len(df) + 1))
    return df


RULES = config.load_rules()


# ---------------- LOẠI 1: LUỒNG ĐÚNG ----------------
def test_TC01_du_lieu_dung_thi_doc_du_so_dong_va_khong_bi_loai():
    raw = make_raw([("1", "An", "0901234567", "an@x.com", "1 A", "01/01/2024"),
                    ("2", "Bình", "0912345678", "", "2 B", "02/01/2024")])
    res = clean_customers.transform_customers(raw)
    assert len(res.rejects) == 0 and len(res.clean) == 2


def test_TC02_moi_ho_so_tho_deu_co_mat_o_mot_trong_ba_nhom():
    """NFR3: số hồ sơ đọc = hồ sơ mới + hồ sơ gắn vào hồ sơ có sẵn + bản ghi bị loại."""
    raw = make_raw([("1", "An", "0901234567", "", "1 A", ""),
                    ("2", "An B", "+84 901 234 567", "", "9 Z", ""),   # trùng số điện thoại -> gắn vào
                    ("3", "Cường", "", "", "3 C", ""),                  # bị loại
                    ("4", "Dũng", "0933333333", "", "4 D", "")])
    res = clean_customers.transform_customers(raw)
    assert len(raw) == len(res.clean) + res.attached_in_file + len(res.rejects)
    assert (len(res.clean), res.attached_in_file, len(res.rejects)) == (2, 1, 1)


# ---------------- LOẠI 2: GIÁ TRỊ BIÊN ----------------
def test_TC03_ti_le_dat_dung_bang_nguong_thi_van_dat():
    m = checks.Measure("DQ05", "CLEAN", total=100, failed=1, threshold_pct=99.0)   # đúng 99%
    assert m.pass_rate_pct == 99.0 and m.is_threshold_met is True


def test_TC04_ti_le_dat_duoi_nguong_mot_ho_so_thi_khong_dat():
    m = checks.Measure("DQ05", "CLEAN", total=100, failed=2, threshold_pct=99.0)   # 98%
    assert m.is_threshold_met is False


def test_TC05_khong_co_ho_so_nao_de_kiem_thi_ti_le_la_100_khong_chia_cho_0():
    assert checks.Measure("DQ05", "RAW", total=0, failed=0, threshold_pct=99.0).pass_rate_pct == 100.0


# ---------------- LOẠI 3: DỮ LIỆU SAI ----------------
def test_TC06_so_dien_thoai_rong_hoac_sai_vao_bang_reject_kem_ma_ly_do():
    raw = make_raw([("1", "An", "", "", "", ""),
                    ("2", "Bình", "12345", "", "", ""),
                    ("3", "", "0901234567", "", "", "")])
    res = clean_customers.transform_customers(raw)
    assert dict(zip(res.rejects["source_row_no"], res.rejects["reason_code"])) == {
        1: "PHONE_MISSING", 2: "PHONE_INVALID", 3: "NAME_MISSING"}
    assert res.rejects["reason_text"].notna().all()                 # NFR6: mọi dòng có lý do
    assert res.clean.empty


def test_TC07_do_chat_luong_ra_dung_so_do_o_ca_RAW_va_CLEAN():
    raw = make_raw([("1", "  an  ", "+84901234567", "BAD", "", ""),
                    ("2", "Bình", "", "b@x.com", "", "")])
    res = clean_customers.transform_customers(raw)
    by = {(m.rule_code, m.stage): m for m in checks.measure_all(res, RULES)}
    assert by[("DQ01", "RAW")].failed == 1                          # một dòng thiếu số điện thoại
    assert by[("DQ02", "RAW")].failed == 1                          # '+84...' chưa ở dạng chuẩn
    assert by[("DQ04", "RAW")].failed == 1                          # '  an  ' còn khoảng trắng thừa
    assert by[("DQ05", "RAW")].failed == 1                          # 'BAD' sai định dạng
    assert all(by[(c, "CLEAN")].failed == 0 for c in ("DQ01", "DQ02", "DQ03", "DQ04", "DQ05"))


def test_TC08_quy_tac_gate_khong_dat_o_CLEAN_thi_pipeline_phai_dung():
    bad = checks.Measure("DQ02", "CLEAN", total=10, failed=1, threshold_pct=100.0)
    ok_but_report_only = checks.Measure("DQ06", "CLEAN", total=10, failed=9, threshold_pct=95.0)
    stopped = checks.gate_failures([bad, ok_but_report_only], RULES)
    assert [m.rule_code for m in stopped] == ["DQ02"]               # DQ06 gate=false: chỉ báo cáo


def test_TC09_tep_nguon_thieu_cot_bi_tu_choi_voi_thong_bao_ro(tmp_path):
    from src.errors import SourceFileError
    from src.extract import read_source
    f = tmp_path / "x.csv"
    f.write_text("record_id,ho_ten\n1,An\n", encoding="utf-8")
    with pytest.raises(SourceFileError, match="thiếu cột bắt buộc"):
        read_source.read_customers(f)


def test_TC10_toan_bo_email_rong_van_do_duoc_khong_loi():
    """Biên: không có email nào để kiểm -> tổng 0, tỉ lệ đạt 100%, không ném lỗi kiểu dữ liệu."""
    raw = make_raw([("1", "An", "0901234567", "", "", ""), ("2", "Bình", "0912345678", "", "", "")])
    res = clean_customers.transform_customers(raw)
    m = {(x.rule_code, x.stage): x for x in checks.measure_all(res, RULES)}[("DQ05", "CLEAN")]
    assert (m.total, m.failed, m.pass_rate_pct) == (0, 0, 100.0)

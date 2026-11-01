"""UC7 (tạo hồ sơ mới có kiểm tra) và UC5 (quy tắc gộp). Dùng đối tượng giả, không cần CSDL."""
import pandas as pd
import pytest

from src.errors import (InvalidInputError, MergeConflictError, NotFoundError,
                        PermissionDeniedError, PhoneExistsError)
from src.transform import intake, merge_rules


def test_IM01_tao_ho_so_hop_le_tra_ve_du_lieu_da_chuan_hoa():
    out = intake.validate_new_customer("  nguyễn  an ", "+84 901 234 567", "AN@X.COM", find_by_phone=lambda p: None)
    assert out == {"full_name": "Nguyễn An", "phone": "0901234567", "email": "an@x.com"}


def test_IM02_thieu_ten_va_so_dien_thoai_bao_loi_theo_tung_truong():
    with pytest.raises(InvalidInputError) as e:
        intake.validate_new_customer("", "")
    assert e.value.code == "DU_LIEU_KHONG_HOP_LE" and set(e.value.fields) == {"full_name", "phone"}


def test_IM03_so_dien_thoai_9_chu_so_bi_tu_choi():
    with pytest.raises(InvalidInputError) as e:
        intake.validate_new_customer("An", "090123456")
    assert "10 chữ số" in e.value.fields["phone"]


def test_IM04_so_dien_thoai_da_ton_tai_khong_tao_moi_QT01():
    with pytest.raises(PhoneExistsError) as e:
        intake.validate_new_customer("An", "0901234567", find_by_phone=lambda p: 123)
    assert "#123" in e.value.message and e.value.to_dict()["error"] == "SO_DIEN_THOAI_DA_TON_TAI"


def member(cid, created, status="PENDING", active=True, merged=None):
    return {"customer_id": cid, "created_at": created, "status": status,
            "is_active": active, "merged_into_id": merged}


def test_IM05_ho_so_chinh_la_ho_so_tao_som_nhat_hoa_thi_ma_nho_hon():
    ms = [member(7, pd.Timestamp("2024-05-01")), member(3, pd.Timestamp("2023-01-01")),
          member(2, pd.Timestamp("2023-01-01"))]
    assert merge_rules.choose_primary(ms)["customer_id"] == 2


def test_IM06_ho_so_khong_co_ngay_tao_xep_sau_ho_so_co_ngay():
    assert merge_rules.choose_primary([member(1, None), member(9, pd.Timestamp("2024-01-01"))])["customer_id"] == 9


def test_IM07_marketing_khong_duoc_xac_nhan_gop():
    with pytest.raises(PermissionDeniedError):
        merge_rules.require_store_manager(merge_rules.ROLE_MARKETING)
    merge_rules.require_store_manager(merge_rules.ROLE_STORE_MANAGER)        # không ném lỗi


def test_IM08_ho_so_phu_da_bi_gop_boi_thao_tac_khac_thi_bao_xung_dot():
    with pytest.raises(MergeConflictError):
        merge_rules.check_merge_allowed([member(1, None), member(2, None, active=False, merged=1)])


def test_IM09_nhom_khong_ton_tai_hoac_da_xu_ly():
    with pytest.raises(NotFoundError):
        merge_rules.check_merge_allowed([])
    with pytest.raises(MergeConflictError):
        merge_rules.check_merge_allowed([member(1, None, status="CONFIRMED"), member(2, None, status="CONFIRMED")])

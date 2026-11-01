"""PHA 3 - QUALITY: đo sáu quy tắc DQ01-DQ06 ở hai giai đoạn RAW và CLEAN.

Nguyên tắc: mỗi hàm đo trả về MỘT SỐ ĐO (số kiểm, số đạt), không chỉ True/False, để biết
được MỨC ĐỘ và so sánh giữa các đợt chạy. Hàm thuần, không đọc ghi CSDL.
"""
from dataclasses import dataclass

import pandas as pd

from src.transform import rules


@dataclass
class Measure:
    rule_code: str
    stage: str            # RAW | CLEAN
    total: int            # số hồ sơ được kiểm
    failed: int           # số hồ sơ vi phạm
    threshold_pct: float

    @property
    def pass_rate_pct(self) -> float:
        return round(100.0 * (1 - self.failed / self.total), 2) if self.total else 100.0

    @property
    def is_threshold_met(self) -> bool:
        return self.pass_rate_pct >= self.threshold_pct

    def as_dict(self) -> dict:
        return {"rule_code": self.rule_code, "stage": self.stage, "total": self.total,
                "failed": self.failed, "pass_rate_pct": self.pass_rate_pct,
                "threshold_pct": self.threshold_pct, "is_threshold_met": self.is_threshold_met}


def _present(series: pd.Series) -> pd.Series:
    return ~series.map(rules.is_empty).astype(bool)


def _count_false(flags: pd.Series) -> int:
    """Đếm số giá trị False. Dùng vòng lặp thay cho ~flags vì Series rỗng sau .map có thể mất kiểu bool."""
    return sum(1 for f in flags if not f)


# ---------------------------------------------------------------- DQ01
def dq01_phone_present(phones: pd.Series, stage: str, threshold: float) -> Measure:
    """DQ01 completeness: tỉ lệ hồ sơ có số điện thoại."""
    return Measure("DQ01", stage, len(phones), int((~_present(phones)).sum()), threshold)


# ---------------------------------------------------------------- DQ02
def dq02_phone_format(phones: pd.Series, stage: str, threshold: float) -> Measure:
    """DQ02 validity: số điện thoại (khi có) khớp ^0[0-9]{9}$ NGUYÊN TRẠNG, chưa chuẩn hóa."""
    present = phones[_present(phones)].astype(str)
    ok = present.map(lambda p: bool(rules.PHONE_RE.fullmatch(p)))
    return Measure("DQ02", stage, len(present), _count_false(ok), threshold)


# ---------------------------------------------------------------- DQ03
def dq03_phone_unique(phones: pd.Series, stage: str, threshold: float) -> Measure:
    """DQ03 uniqueness: COUNT(*) = COUNT(DISTINCT phone). Số vi phạm = số bản ghi dư."""
    present = phones[_present(phones)].astype(str).str.strip()
    return Measure("DQ03", stage, len(present), len(present) - present.nunique(), threshold)


# ---------------------------------------------------------------- DQ04
def dq04_name_clean(names: pd.Series, stage: str, threshold: float) -> Measure:
    """DQ04 validity: họ tên không rỗng, không khoảng trắng đầu/cuối hoặc liên tiếp."""
    ok = names.map(rules.is_clean_name)
    return Measure("DQ04", stage, len(names), _count_false(ok), threshold)


# ---------------------------------------------------------------- DQ05
def dq05_email_format(emails: pd.Series, stage: str, threshold: float) -> Measure:
    """DQ05 validity: email khác rỗng thì đúng định dạng."""
    present = emails[_present(emails)]
    ok = present.map(rules.email_is_valid)
    return Measure("DQ05", stage, len(present), _count_false(ok), threshold)


# ---------------------------------------------------------------- DQ06
def dq06_pending_duplicates(total_clean: int, suspect_records: int, threshold: float) -> Measure:
    """DQ06 consistency (chỉ đo ở CLEAN): hồ sơ nằm trong nhóm nghi trùng chưa xử lý."""
    return Measure("DQ06", "CLEAN", total_clean, suspect_records, threshold)


def measure_all(result, rules_cfg: dict) -> list[Measure]:
    """Đo cả sáu quy tắc. `result` là TransformResult của pha transform."""
    t = {code: float(cfg["threshold_pct"]) for code, cfg in rules_cfg.items()}
    raw, clean = result.raw, result.clean
    return [
        dq01_phone_present(raw["so_dien_thoai"], "RAW", t["DQ01"]),
        dq02_phone_format(raw["so_dien_thoai"], "RAW", t["DQ02"]),
        dq03_phone_unique(raw["so_dien_thoai"], "RAW", t["DQ03"]),
        dq04_name_clean(raw["ho_ten"], "RAW", t["DQ04"]),
        dq05_email_format(raw["email"], "RAW", t["DQ05"]),
        dq01_phone_present(clean["phone"], "CLEAN", t["DQ01"]),
        dq02_phone_format(clean["phone"], "CLEAN", t["DQ02"]),
        dq03_phone_unique(clean["phone"], "CLEAN", t["DQ03"]),
        dq04_name_clean(clean["full_name"], "CLEAN", t["DQ04"]),
        dq05_email_format(clean["email"], "CLEAN", t["DQ05"]),
        dq06_pending_duplicates(len(clean), int(result.suspects["phone"].nunique()), t["DQ06"]),
    ]


def gate_failures(measures: list[Measure], rules_cfg: dict) -> list[Measure]:
    """Quy tắc có gate=true mà KHÔNG đạt ở giai đoạn CLEAN -> pipeline phải dừng, không nạp kho."""
    return [m for m in measures
            if m.stage == "CLEAN" and rules_cfg[m.rule_code].get("gate", False) and not m.is_threshold_met]


def clean_score(measures: list[Measure]) -> float:
    """Điểm sạch = trung bình tỉ lệ đạt các quy tắc ở giai đoạn CLEAN."""
    vals = [m.pass_rate_pct for m in measures if m.stage == "CLEAN"]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def collect_issues(raw: pd.DataFrame) -> pd.DataFrame:
    """Chi tiết vi phạm theo từng hồ sơ thô (cho fact_dq_issue). KHÔNG chứa số điện thoại đầy đủ."""
    parts = []

    def add(mask: pd.Series, code: str, detail: str) -> None:
        if mask.any():
            parts.append(pd.DataFrame({"stg_id": raw.loc[mask, "source_row_no"].values,
                                       "rule_code": code, "issue_detail": detail}))

    phone_present = _present(raw["so_dien_thoai"])
    add(~phone_present, "DQ01", "Thiếu số điện thoại")
    add(phone_present & ~raw["so_dien_thoai"].map(lambda p: bool(rules.PHONE_RE.fullmatch(str(p)))),
        "DQ02", "Số điện thoại chưa ở dạng chuẩn 10 chữ số bắt đầu bằng 0")
    stripped = raw["so_dien_thoai"].astype(str).str.strip()
    add(phone_present & stripped.duplicated(keep="first"), "DQ03",
        "Số điện thoại trùng với hồ sơ đứng trước trong tệp")
    add(~raw["ho_ten"].map(rules.is_clean_name), "DQ04",
        "Họ tên rỗng hoặc có khoảng trắng thừa")
    email_present = _present(raw["email"])
    add(email_present & ~raw["email"].map(rules.email_is_valid), "DQ05", "Email sai định dạng")
    if not parts:
        return pd.DataFrame(columns=["stg_id", "rule_code", "issue_detail"])
    return pd.concat(parts, ignore_index=True)

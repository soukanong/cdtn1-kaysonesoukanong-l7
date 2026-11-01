"""PHA 2 - TRANSFORM: làm sạch hồ sơ khách hàng. Không đọc ghi CSDL."""
from dataclasses import dataclass

import pandas as pd

from src.transform import dedupe, rules


@dataclass
class TransformResult:
    raw: pd.DataFrame        # hồ sơ thô kèm các cột chuẩn hóa (phone_std, name_std, ...)
    clean: pd.DataFrame      # hồ sơ sạch, số điện thoại duy nhất
    rejects: pd.DataFrame    # source_row_no, reason_code, reason_text
    suspects: pd.DataFrame   # group_id, phone, match_rule
    valid_rows: int          # số hồ sơ thô chuẩn hóa được (trước khi khử trùng theo số điện thoại)

    @property
    def attached_in_file(self) -> int:
        """Hồ sơ thô trùng số điện thoại với hồ sơ đứng trước trong cùng tệp (QT-01)."""
        return self.valid_rows - len(self.clean)


def transform_customers(raw: pd.DataFrame) -> TransformResult:
    df = raw.copy()
    classified = df["so_dien_thoai"].map(rules.classify_phone)
    df["phone_std"] = classified.map(lambda t: t[0])
    df["phone_reason"] = classified.map(lambda t: t[1])
    df["name_std"] = df["ho_ten"].map(rules.normalize_name)
    df["email_std"] = df["email"].map(rules.normalize_email)
    df["address_std"] = df["dia_chi"].map(rules.clean_address)
    df["name_key"] = df["name_std"].map(rules.name_key)
    df["addr_key"] = df["dia_chi"].map(rules.address_key)
    df["created_at_ts"] = rules.parse_dates(df["ngay_tao"])

    # Mỗi hồ sơ bị loại chỉ mang MỘT mã lý do (ưu tiên: số điện thoại trước, họ tên sau)
    reason = df["phone_reason"].where(df["phone_reason"].notna(),
                                      df["name_std"].map(lambda n: "NAME_MISSING" if rules.is_empty(n) else None))
    df["reject_reason"] = reason
    rejects = df.loc[reason.notna(), ["source_row_no"]].assign(reason_code=reason[reason.notna()])
    rejects["reason_text"] = rejects["reason_code"].map(rules.REASON_TEXT)

    valid = df[reason.isna()]
    # QT-01: số điện thoại duy nhất, giữ hồ sơ xuất hiện trước trong tệp
    clean = pd.DataFrame({
        "source_row_no": valid["source_row_no"], "full_name": valid["name_std"],
        "phone": valid["phone_std"], "email": valid["email_std"], "address": valid["address_std"],
        "created_at": valid["created_at_ts"], "name_key": valid["name_key"], "addr_key": valid["addr_key"],
    }).drop_duplicates(subset="phone", keep="first").reset_index(drop=True)

    suspects = dedupe.find_suspects(clean)
    return TransformResult(raw=df, clean=clean, rejects=rejects.reset_index(drop=True),
                           suspects=suspects, valid_rows=len(valid))

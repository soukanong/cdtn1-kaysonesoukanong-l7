"""PHA 1 - EXTRACT: đọc tệp nguồn nguyên trạng. KHÔNG biến đổi dữ liệu."""
import pathlib

import pandas as pd

from src.errors import SourceFileError

# Cột thật của customers_raw.csv (đã đối chiếu ở Sprint 1)
REQUIRED_COLUMNS = ["record_id", "ho_ten", "so_dien_thoai", "email", "dia_chi", "ngay_tao"]


def read_customers(path: pathlib.Path) -> pd.DataFrame:
    """Đọc mọi cột như chuỗi; ô trống giữ là chuỗi rỗng (không để pandas tự đổi thành NaN).

    Thêm cột source_row_no (số dòng trong tệp, tính từ 1) để truy ngược hồ sơ thô.
    """
    if not path.exists():
        raise SourceFileError(f"Không tìm thấy tệp nguồn: {path.name}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise SourceFileError(f"Tệp nguồn thiếu cột bắt buộc: {', '.join(missing)}")
    df = df[REQUIRED_COLUMNS].copy()
    df.insert(0, "source_row_no", range(1, len(df) + 1))
    return df

import pandas as pd


def read_source(path):
    """Đọc tệp nguồn nguyên trạng (mọi cột là văn bản)."""
    return pd.read_csv(path, dtype=str, encoding="utf-8")

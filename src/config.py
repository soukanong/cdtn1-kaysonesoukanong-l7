"""Đọc cấu hình từ biến môi trường (.env) và configs/thresholds.yaml.

Không có giá trị bí mật nào được ghi cứng trong mã nguồn.
"""
import os
import pathlib

import yaml
from dotenv import load_dotenv

from src.errors import SystemFault

ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _path(value: str) -> pathlib.Path:
    p = pathlib.Path(value)
    return p if p.is_absolute() else ROOT / p


def source_csv() -> pathlib.Path:
    """SOURCE_CSV nếu đặt; nếu không: dữ liệu thật nếu có, rồi tới dữ liệu mẫu."""
    explicit = os.environ.get("SOURCE_CSV", "").strip()
    if explicit:
        return _path(explicit)
    real = ROOT / "data" / "customers_raw.csv"
    return real if real.exists() else ROOT / "data" / "mau" / "customers_raw_sample.csv"


def db_url() -> str:
    url = os.environ.get("DWH_URL", "").strip()
    if not url:
        raise SystemFault("Thiếu biến môi trường DWH_URL (xem .env.example)")
    return url


def report_dir() -> pathlib.Path:
    return _path(os.environ.get("REPORT_DIR", "reports"))


def load_rules() -> dict:
    """Trả về {'DQ01': {name, dimension, column, threshold_pct, gate, reason}, ...}."""
    path = _path(os.environ.get("THRESHOLDS_FILE", "configs/thresholds.yaml"))
    if not path.exists():
        raise SystemFault(f"Không thấy tệp ngưỡng: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))["rules"]

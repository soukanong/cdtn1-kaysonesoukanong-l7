"""Kết nối cơ sở dữ liệu và dựng schema. KHÔNG chứa quy tắc nghiệp vụ."""
import pathlib

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src import config

SQL_DIR = pathlib.Path(__file__).resolve().parent.parent / "sql"


def get_engine() -> Engine:
           return create_engine(config.db_url(), pool_pre_ping=True, connect_args={"connect_timeout": 5})


def apply_schema(engine: Engine) -> None:
    """Chạy sql/*.sql theo thứ tự tên tệp. Các tệp đều idempotent nên chạy lại an toàn."""
    with engine.begin() as conn:
        for path in sorted(SQL_DIR.glob("*.sql")):
            for stmt in path.read_text(encoding="utf-8").split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))

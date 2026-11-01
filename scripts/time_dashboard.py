"""Đo thời gian chạy toàn bộ trang dashboard (NFR4: mỗi trang <= 3 giây).

  python scripts/time_dashboard.py

Chạy script dashboard/app.py 3 lần bằng bộ kiểm thử của Streamlit (AppTest), in thời gian từng lần.
Lần 1 là "khởi động nguội": gồm cả việc nạp thư viện (pandas, plotly, streamlit) và mở kết nối CSDL.
Lần 2 và 3 là trạng thái ổn định. Thời gian gồm truy vấn CSDL và dựng cả 3 khung,
KHÔNG gồm thời gian trình duyệt vẽ lên màn hình. Báo cáo CẢ HAI mức, không chỉ mức nhanh.
"""
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402

for i in range(1, 4):
    start = time.perf_counter()
    app = AppTest.from_file(str(ROOT / "dashboard" / "app.py"), default_timeout=60).run()
    label = "khởi động nguội" if i == 1 else "ổn định"
    print(f"lần {i} ({label}): {time.perf_counter() - start:.2f} giây | số lỗi: {len(app.exception)}")
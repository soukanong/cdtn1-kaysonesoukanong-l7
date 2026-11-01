# Quản lý chất lượng dữ liệu khách hàng – L7 (Smart CRM – Mekong Mobile)

- **Sinh viên:** KAYSONE Souk Anong · MSSV 237480201is05 · LHP 261_71ITGR40203_06
- **Track:** DA · **GVHD:** TS Nguyễn Trí Hải
- **Học phần:** Chuyên đề tốt nghiệp 1, HK1 năm học 2026 – 2027, Trường Đại học Văn Lang
- **Phiên bản nộp Bài tập 2:** tag `v0.2`

## 1. Hệ thống làm gì

Pipeline Python đọc tệp hồ sơ khách hàng thô `customers_raw.csv` (67.037 dòng), chuẩn hóa số điện thoại, họ tên và email, đưa hồ sơ không hợp lệ vào bảng reject kèm mã lý do, đo sáu quy tắc chất lượng DQ01–DQ06 ở hai giai đoạn RAW và CLEAN rồi nạp vào PostgreSQL (lớp `stg`, `core` và kho dữ liệu hình sao `dwh`). Hồ sơ nghi trùng chỉ được đề xuất, chỉ gộp sau khi Quản lý cửa hàng xác nhận trên dashboard Streamlit. Chạy lại nhiều lần không làm nhân đôi dữ liệu.

## 2. Yêu cầu môi trường

| Thành phần | Phiên bản |
|---|---|
| Python | 3.11 trở lên |
| PostgreSQL | 16 (dùng Docker hoặc cài sẵn) |
| Docker Desktop | Tùy chọn, chỉ để bật PostgreSQL bằng một lệnh |
| Thư viện Python | Khóa phiên bản (`==`) trong `requirements.txt` |

## 3. Các bước dựng và chạy (mỗi bước một lệnh)

Lệnh cho Windows PowerShell. Trên Linux hoặc macOS: bước 2 là `source .venv/bin/activate` và bước 4 là `cp .env.example .env`.

| Bước | Việc | Lệnh |
|---|---|---|
| 1 | Tạo môi trường ảo | `python -m venv .venv` |
| 2 | Kích hoạt | `.venv\Scripts\Activate.ps1` |
| 3 | Cài thư viện | `pip install -r requirements.txt` |
| 4 | Tạo tệp cấu hình | `Copy-Item .env.example .env` |
| 5 | Bật PostgreSQL | `docker compose up -d db` |
| 6 | Chạy pipeline | `python -m src.pipeline` |
| 7 | Chạy kiểm thử | `python -m pytest -q` |
| 8 | Mở dashboard (http://localhost:8501) | `streamlit run dashboard/app.py` |

Ghi chú:

- Bước 2 báo bị chặn script: chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` rồi kích hoạt lại.
- Bước 5 dùng cổng 5432. Nếu cổng này đã bị chiếm (ví dụ PostgreSQL cài sẵn trên máy), thêm dòng `DB_PORT=5433` vào `.env` và đổi cổng trong `DWH_URL` thành `5433`. Không dùng Docker thì cài PostgreSQL 16, tạo người dùng và cơ sở dữ liệu khớp với `DWH_URL`.
- Bước 6 tự tạo schema và bảng (các tệp `sql/*.sql` đều idempotent).
- Dữ liệu: nếu không có `data/customers_raw.csv` (không commit vì là dữ liệu khách hàng), pipeline tự dùng `data/mau/customers_raw_sample.csv` (400 dòng, dữ liệu giả). Muốn chạy tệp thật, đặt tệp vào `data/` hoặc đặt `SOURCE_CSV` trong `.env`.

## 4. Kiểm tra hệ thống đã chạy đúng

| Việc kiểm tra | Lệnh | Kết quả đúng |
|---|---|---|
| Pipeline chạy xong | `python -m src.pipeline` | Dòng `Kết luận: THANH_CONG (mã thoát 0)` và dòng `Đọc ... \| loại ... \| sạch ...` |
| Số liệu với dữ liệu mẫu | (cùng lệnh trên, không có tệp thật) | `Đọc 400 \| loại 49 \| sạch 323 \| nghi trùng 23 nhóm` |
| Chạy lại lần hai không nhân đôi | Chạy bước 6 lần nữa rồi đếm (lệnh bên dưới bảng) | `clean`, `reject`, `dup`, `issue` bằng lần 1; `runs` tăng thêm 1 |
| Chỉ đo, không cần cơ sở dữ liệu | `python -m src.pipeline --check-only` | `Kết luận: CHI_KIEM_KHONG_NAP`, không kết nối PostgreSQL |
| Kiểm thử đạt | `python -m pytest -q` | Dòng cuối dạng `... passed in ...s`, không có `failed` |
| Dữ liệu sai bị từ chối đúng cách | `python -m pytest -k "TC06 or TC09 or IM02" -v` | Các kiểm thử đạt: số điện thoại rỗng hoặc sai vào bảng reject; tệp thiếu cột bị từ chối; form báo lỗi theo từng trường |
| Dashboard không sập khi mất cơ sở dữ liệu | `docker compose stop db` rồi tải lại trang | Thông báo đỏ "Không đọc được dữ liệu..." và nút Thử lại, không hiện chuỗi kết nối; bật lại bằng `docker compose start db` |

Lệnh đếm số dòng (dùng cho dòng "Chạy lại lần hai"):

```powershell
docker compose exec db psql -U l7_user -d l7_dq -c "select (select count(*) from core.customer_clean) as clean, (select count(*) from core.reject_customer) as reject, (select count(*) from core.duplicate_review) as dup, (select count(*) from dwh.fact_dq_issue) as issue, (select count(*) from dwh.dim_run) as runs;"
```

Mã thoát của pipeline: `0` thành công · `1` lỗi kỹ thuật (thiếu tệp, thiếu cột, mất kết nối) · `2` dừng vì chất lượng đầu ra không đạt (DQ01–DQ04 ở CLEAN). Báo cáo luôn được ghi vào `reports/chat-luong-*.md` và `.json`, kể cả khi thất bại.

## 5. Dashboard

Ba khung theo wireframe BT1: (1) Tổng quan độ sạch, (2) Xu hướng theo thời gian, (3) Nghi trùng và gộp hồ sơ. Xử lý đủ ba trạng thái: đang tải, rỗng và lỗi kết nối. Vai trò chỉ mô phỏng ở thanh bên: Quản lý cửa hàng xem số điện thoại đầy đủ và được xác nhận gộp; Marketing chỉ xem số dạng che (`035****926`, đọc qua `core.view_customer_masked`) và bị từ chối khi bấm Xác nhận gộp.

## 6. Cấu trúc thư mục (khớp kiến trúc BT1)

```
src/extract/     Pha 1: đọc tệp nguồn nguyên trạng
src/transform/   Pha 2: quy tắc nghiệp vụ (QT-01, QT-02, BR-L7-04, gộp hồ sơ, tạo hồ sơ mới), hàm thuần
src/quality/     Pha 3: đo DQ01–DQ06 ở RAW và CLEAN
src/load/        Pha 4: ghi PostgreSQL (loader.py) và thao tác của người dùng (customer_repo.py)
src/report/      Truy vấn chỉ đọc cho dashboard
src/pipeline.py  Điều phối bốn pha
dashboard/       Streamlit, ba khung
sql/             DDL idempotent: kho dữ liệu dwh, stg + core, view che số điện thoại
configs/         Ngưỡng chất lượng (thresholds.yaml)
tests/           Kiểm thử pytest
scripts/         make_sample_data.py (tạo dữ liệu mẫu), time_dashboard.py (đo thời gian trang)
data/mau/        Dữ liệu mẫu nhỏ để chạy được ngay
docs/            Tài liệu BT1, thay-doi-thiet-ke.md, ai-disclosure.md, data-requirements.md
```

Chiều gọi chỉ đi xuống: dashboard → transform / load / report → PostgreSQL. `transform/` và `quality/` không đọc ghi cơ sở dữ liệu.

## 7. Biến môi trường

Xem `.env.example`. **Không commit `.env`** (đã nằm trong `.gitignore`).

| Biến | Ý nghĩa |
|---|---|
| `DWH_URL` | Chuỗi kết nối PostgreSQL |
| `SOURCE_CSV` | Tệp nguồn; bỏ trống thì dùng tệp thật nếu có, nếu không dùng dữ liệu mẫu |
| `THRESHOLDS_FILE`, `REPORT_DIR`, `LOG_LEVEL` | Tệp ngưỡng, thư mục báo cáo, mức log |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_PORT` | Dùng cho `docker-compose.yml` |

## 8. Kết quả đo NFR

Máy đo: AMD Ryzen 7 5700U (8 nhân, 16 luồng), RAM 7,4 GB, PostgreSQL 16 chạy trong Docker, tệp thật 67.037 dòng.

| NFR | Ngưỡng | Kết quả đo | Kết luận |
|---|---|---|---|
| NFR1 – pipeline xử lý toàn bộ tệp | < 5 phút | 101,5 giây (lần 1), 93,2 giây (lần 2) | Đạt |
| NFR2 – chạy lại hai lần, số dòng chênh lệch 0 | 0 dòng | `customer_clean` 51.279, `reject_customer` 4.133, `duplicate_review` 5.438, `fact_dq_issue` 30.666: không đổi giữa hai lần | Đạt |
| NFR4 – tải trang dashboard | ≤ 3 giây | Dùng bình thường: khoảng 1,32 giây trên trình duyệt, 0,21–0,26 giây phía máy chủ. Lần tải đầu sau khi bật máy chủ: 3,72 giây (nạp thư viện chiếm phần lớn) | Đạt khi dùng bình thường; lần đầu không đạt |

Cách đo: `python -m src.pipeline` hai lần liên tiếp rồi đếm bằng lệnh ở mục 4; `python scripts/time_dashboard.py` (lần 1 là khởi động nguội, lần 2 và 3 là ổn định) và đồng hồ bấm giờ khi tải lại trang.

Kết quả chất lượng trên tệp thật: bản ghi bị loại 4.133 (toàn bộ `PHONE_MISSING`), hồ sơ sạch 51.279, 2.624 nhóm nghi trùng, điểm sạch 98,23. DQ01–DQ05 đạt ở CLEAN; DQ06 (89,4%, ngưỡng 95%) không đạt vì chưa có xác nhận gộp.

## 9. Hạn chế đã biết

- Tệp nguồn thật không có cột cửa hàng nên chưa có bộ lọc theo cửa hàng và NFR7 chưa kiểm chứng được (TD-07).
- DQ06 không đạt ngưỡng cho đến khi Quản lý cửa hàng xác nhận gộp các nhóm nghi trùng (TD-14).
- Lần tải đầu tiên của dashboard sau khi bật máy chủ vượt 3 giây (mục 8).
- `docker-compose.yml` chỉ dựng PostgreSQL; pipeline và dashboard chạy bằng Python trên máy.

## 10. Tài liệu và trạng thái

| Bài tập | Nội dung | Trạng thái |
|---|---|---|
| BT1 | Phân tích và thiết kế: `docs/srs.md`, `docs/*.drawio`, `docs/export/` | Đã nộp |
| BT2 | Module cốt lõi chạy được (tag `v0.2`) | Nộp bản này |
| BT3 | Tích hợp và đóng gói | Chưa thực hiện |

- Thay đổi so với thiết kế BT1: [`docs/thay-doi-thiet-ke.md`](docs/thay-doi-thiet-ke.md)
- Đặc tả yêu cầu dữ liệu và số đo: [`docs/data-requirements.md`](docs/data-requirements.md)
- Khai báo sử dụng công cụ AI: [`docs/ai-disclosure.md`](docs/ai-disclosure.md)
- Kiến trúc đã hiện thực: `docs/architecture-thuc-te.png`

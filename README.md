# Quản lý chất lượng dữ liệu khách hàng – L7 (Smart CRM – Mekong Mobile)

- **Sinh viên:** KAYSONE Souk Anong · MSSV 237480201is05 · LHP 261_71ITGR40203_06
- **Track:** DA · **GVHD:** TS Nguyễn Trí Hải
- **Học phần:** Chuyên đề tốt nghiệp 1, HK1 năm học 2026 – 2027, Trường Đại học Văn Lang
- **Phiên bản nộp Bài tập 3:** tag `v1.0` (Bài tập 2: tag `v0.2`)

## 1. Hệ thống làm gì

Pipeline Python đọc tệp hồ sơ khách hàng thô `customers_raw.csv` (67.037 dòng), chuẩn hóa số điện thoại, họ tên và email, đưa hồ sơ không hợp lệ vào bảng reject kèm mã lý do, đo sáu quy tắc chất lượng DQ01–DQ06 ở hai giai đoạn RAW và CLEAN rồi nạp vào PostgreSQL (lớp `stg`, `core` và kho dữ liệu hình sao `dwh`). Hồ sơ nghi trùng chỉ được đề xuất, chỉ gộp sau khi Quản lý cửa hàng xác nhận trên dashboard Streamlit. Chạy lại nhiều lần không làm nhân đôi dữ liệu.

## 2. Yêu cầu môi trường

| Thành phần | Phiên bản |
|---|---|
| Docker (khuyến nghị) | Docker Desktop có Compose v2 (đã thử Docker Desktop 4.97.0, Engine 29.9.2); cổng 8501 và 5433 còn trống |
| Python | 3.11 trở lên (chỉ khi chạy không dùng Docker) |
| PostgreSQL | 16 (đã có trong Docker) |
| Thư viện Python | Khóa phiên bản (`==`) trong `requirements.txt` |

## 3. Chạy hệ thống bằng Docker (2 lệnh)

```
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
docker compose up -d --build
```

`docker compose ps` phải cho thấy `db` và `app` ở trạng thái **healthy**. Dashboard: <http://localhost:8501>. Khi khởi động, dịch vụ `app` chạy `python -m src.pipeline` rồi mở dashboard. Không có `data/customers_raw.csv` trong image nên pipeline dùng dữ liệu mẫu `data/mau/customers_raw_sample.csv` (400 dòng). Muốn bắt đầu lại từ cơ sở dữ liệu trống: `docker compose down -v` rồi chạy lại lệnh thứ hai. Cổng 5433 hoặc 8501 đã bị chiếm: đổi số bên trái ở các dòng `ports:` trong `docker-compose.yml`. Hướng dẫn đầy đủ: [`docs/deployment-guide.md`](docs/deployment-guide.md).

## 4. Chạy không dùng Docker (tùy chọn)

Lệnh cho Windows PowerShell. Trên Linux hoặc macOS: bước 2 là `source .venv/bin/activate` và bước 4 là `cp .env.example .env`.

| Bước | Việc | Lệnh |
|---|---|---|
| 1 | Tạo môi trường ảo | `python -m venv .venv` |
| 2 | Kích hoạt | `.venv\Scripts\Activate.ps1` |
| 3 | Cài thư viện | `pip install -r requirements.txt` |
| 4 | Tạo tệp cấu hình | `Copy-Item .env.example .env` |
| 5 | Bật PostgreSQL (chỉ dịch vụ `db`) | `docker compose up -d db` |
| 6 | Đặt cổng trong `.env` | sửa `DWH_URL` thành cổng `5433` (cổng Docker mở ra trên máy) |
| 7 | Chạy pipeline | `python -m src.pipeline` |
| 8 | Chạy kiểm thử | `python -m pytest -q` |
| 9 | Mở dashboard (http://localhost:8501) | `streamlit run dashboard/app.py` |

- Bước 2 báo bị chặn script: chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` rồi kích hoạt lại.
- Bước 7 tự tạo schema và bảng (các tệp `sql/*.sql` đều idempotent).
- Muốn chạy tệp thật: đặt `customers_raw.csv` vào `data/` hoặc đặt `SOURCE_CSV` trong `.env`.

## 5. Kiểm tra hệ thống đã chạy đúng

Lệnh dưới đây dùng Docker; chạy không dùng Docker thì bỏ phần `docker compose run --rm --no-deps app`.

| Việc kiểm tra | Lệnh | Kết quả đúng |
|---|---|---|
| Dịch vụ lên | `docker compose ps` | `db` và `app` healthy |
| Dashboard lên | `curl -s http://localhost:8501/_stcore/health` (PowerShell: `curl.exe`) | `ok` |
| Pipeline chạy xong | `docker compose logs app --tail 20` | Dòng `Kết luận: THANH_CONG (mã thoát 0)` và dòng `Đọc ... \| loại ... \| sạch ...` |
| Số liệu với dữ liệu mẫu | (cùng log trên) | `Đọc 400 \| loại 49 \| sạch 323 \| nghi trùng 23 nhóm` |
| Chạy lại không nhân đôi | `docker compose run --rm app python -m src.pipeline` rồi đếm (lệnh bên dưới bảng) | `clean`, `reject`, `dup`, `issue` bằng lần trước (323, 49, 47, 468); `runs` tăng thêm 1 |
| Chỉ đo, không cần cơ sở dữ liệu | `docker compose run --rm --no-deps app python -m src.pipeline --check-only` | `Kết luận: CHI_KIEM_KHONG_NAP`, không kết nối PostgreSQL |
| Kiểm thử đạt | `docker compose run --rm --no-deps app python -m pytest -q` | Dòng cuối dạng `45 passed in ...s`, không có `failed` |
| Dữ liệu sai bị từ chối đúng cách | `docker compose run --rm --no-deps app python -m pytest -k "TC06 or TC09 or IM02" -v` | Các kiểm thử đạt: số điện thoại rỗng hoặc sai vào bảng reject; tệp thiếu cột bị từ chối; form báo lỗi theo từng trường |
| Dashboard không sập khi mất cơ sở dữ liệu | `docker compose stop db` rồi tải lại trang | Thông báo đỏ "Không đọc được dữ liệu..." và nút Thử lại, không hiện chuỗi kết nối; bật lại bằng `docker compose start db` |

Lệnh đếm số dòng:

```powershell
docker compose exec db psql -U l7_user -d l7_dq -c "select (select count(*) from core.customer_clean) as clean, (select count(*) from core.reject_customer) as reject, (select count(*) from core.duplicate_review) as dup, (select count(*) from dwh.fact_dq_issue) as issue, (select count(*) from dwh.dim_run) as runs;"
```

Mã thoát của pipeline: `0` thành công · `1` lỗi kỹ thuật (thiếu tệp, thiếu cột, mất kết nối) · `2` dừng vì chất lượng đầu ra không đạt (DQ01–DQ04 ở CLEAN). Báo cáo luôn được ghi vào `reports/chat-luong-*.md` và `.json`, kể cả khi thất bại.

## 6. Dashboard

Ba khung theo wireframe BT1: (1) Tổng quan độ sạch, (2) Xu hướng theo thời gian, (3) Nghi trùng và gộp hồ sơ. Xử lý đủ ba trạng thái: đang tải, rỗng và lỗi kết nối. Vai trò chỉ mô phỏng ở thanh bên: Quản lý cửa hàng xem số điện thoại đầy đủ và được xác nhận gộp; Marketing chỉ xem số dạng che (`035****926`, đọc qua `core.view_customer_masked`) và bị từ chối khi bấm Xác nhận gộp.

## 7. Cấu trúc thư mục (khớp kiến trúc BT1)

```
Dockerfile, docker-compose.yml, .dockerignore   Đóng gói: dịch vụ db (PostgreSQL 16) và app
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
scripts/         make_sample_data.py (tạo dữ liệu mẫu)
data/mau/        Dữ liệu mẫu nhỏ để chạy được ngay
docs/            Tài liệu BT1, BT2, BT3 (xem mục 11)
```

Chiều gọi chỉ đi xuống: dashboard → transform / load / report → PostgreSQL. `transform/` và `quality/` không đọc ghi cơ sở dữ liệu. Hai ngoại lệ so với thiết kế được ghi ở TD-16.

## 8. Biến môi trường

Xem `.env.example`. **Không commit `.env`** (đã nằm trong `.gitignore`).

| Biến | Ý nghĩa |
|---|---|
| `DWH_URL` | Chuỗi kết nối PostgreSQL (trong Docker, máy chủ là `db`, cổng 5432; trên máy dùng cổng 5433) |
| `SOURCE_CSV` | Tệp nguồn; bỏ trống thì dùng tệp thật nếu có, nếu không dùng dữ liệu mẫu |
| `THRESHOLDS_FILE`, `REPORT_DIR`, `LOG_LEVEL` | Tệp ngưỡng, thư mục báo cáo, mức log |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Dùng cho `docker-compose.yml` |

## 9. Kết quả đo NFR

Máy đo: AMD Ryzen 7 5700U (8 nhân, 16 luồng), RAM 7,4 GB, PostgreSQL 16 chạy trong Docker, tệp thật 67.037 dòng.

| NFR | Ngưỡng | Kết quả đo | Kết luận |
|---|---|---|---|
| NFR1 – pipeline xử lý toàn bộ tệp | < 5 phút | 101,5 giây (lần 1) và 93,2 giây (lần 2); đo 31/10–01/11/2026 trên tệp thật 67.037 dòng | Đạt (mọi số đo đều dưới 5 phút) |
| NFR2 – chạy lại hai lần, số dòng chênh lệch 0 | 0 dòng | Tệp thật: `customer_clean` 51.279, `reject_customer` 4.133, `duplicate_review` 5.438, `fact_dq_issue` 30.666, không đổi giữa hai lần. Tệp mẫu trong Docker: 323 / 49 / 47 / 468, không đổi | Đạt |
| NFR4 – tải trang dashboard | ≤ 3 giây | Dùng bình thường: khoảng 1,32 giây trên trình duyệt, 0,21–0,26 giây phía máy chủ. Lần tải đầu sau khi bật máy chủ: 3,72 giây (nạp thư viện chiếm phần lớn) | Đạt khi dùng bình thường; lần đầu không đạt |

Kết quả chất lượng trên tệp thật: bản ghi bị loại 4.133 (toàn bộ `PHONE_MISSING`), hồ sơ sạch 51.279, 2.624 nhóm nghi trùng, điểm sạch 98,23. DQ01–DQ05 đạt ở CLEAN; DQ06 (89,4%, ngưỡng 95%) không đạt vì chưa có xác nhận gộp.

## 10. Hạn chế đã biết

- Tệp nguồn thật không có cột cửa hàng nên chưa có bộ lọc theo cửa hàng và NFR7 chưa kiểm chứng được (TD-07).
- DQ06 không đạt ngưỡng cho đến khi Quản lý cửa hàng xác nhận gộp các nhóm nghi trùng (TD-14).
- Lần tải đầu tiên của dashboard sau khi bật máy chủ vượt 3 giây (mục 9).
- Bộ đo chất lượng hiện có sáu phép đo DQ01–DQ06; chưa đo mức đầy đủ cho từng cột ngoài số điện thoại và họ tên, và chưa có phép kiểm toàn vẹn tham chiếu hoặc tập giá trị cho phép.
- Vai trò chỉ mô phỏng trên dashboard, không có đăng nhập thật; dashboard kết nối cơ sở dữ liệu bằng tài khoản chủ sở hữu (xem `docs/checklist-bao-mat.md`).

## 11. Tài liệu và trạng thái

| Bài tập | Nội dung | Trạng thái |
|---|---|---|
| BT1 | Phân tích và thiết kế: `docs/srs.md`, `docs/*.drawio`, `docs/export/` | Đã nộp |
| BT2 | Module cốt lõi chạy được (tag `v0.2`) | Đã nộp |
| BT3 | Kiểm thử, đóng gói Docker, tài liệu kỹ thuật (tag `v1.0`) | Nộp bản này |

**Tài liệu BT3 trong `docs/`:** `test-plan.md` · `test-report.md` · `bug-log.md` · `deployment-guide.md` · `checklist-bao-mat.md` · `pipeline-doc.md` · `data-dictionary.md` · `screenshots/` (ảnh chạy thật).

- Thay đổi so với thiết kế BT1: [`docs/thay-doi-thiet-ke.md`](docs/thay-doi-thiet-ke.md)
- Đặc tả yêu cầu dữ liệu và số đo: [`docs/data-requirements.md`](docs/data-requirements.md)
- Khai báo sử dụng công cụ AI: [`docs/ai-disclosure.md`](docs/ai-disclosure.md)
- Kiến trúc đã hiện thực: `docs/architecture-thuc-te.png`

# Bảng khai báo sử dụng công cụ AI

## Bài tập 2 – Hiện thực hoá module cốt lõi (L7, track DA)



| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
| --- | --- | --- | --- |
| Claude (Anthropic)  | Soạn bản nháp mã đọc nguồn, chuẩn hóa số điện thoại và tên, tìm nhóm nghi trùng, đo DQ01–DQ06 | `src/extract/read_source.py`, `src/transform/rules.py`, `clean_customers.py`, `dedupe.py`, `src/quality/checks.py` | Chạy `pytest` (45 test PASS); chạy trên tệp thật 67.037 dòng: loại 4.133, sạch 51.279, 2.624 nhóm nghi trùng, điểm sạch 98,23; tự tính lại 67.037 − 4.133 − 51.279 = 11.625 dòng trùng số điện thoại và đối chiếu với báo cáo |
| Claude (Anthropic) | Soạn bản nháp mã nạp PostgreSQL (upsert, SCD loại 2) và các câu SQL | `src/load/loader.py`, `src/load/customer_repo.py`, `src/db.py`, `sql/001…003` | Chạy pipeline hai lần trên PostgreSQL 16 trong Docker và đếm dòng `core.customer_clean`, `core.reject_customer`, `core.duplicate_review`, `dwh.fact_dq_issue`: số dòng bằng nhau giữa hai lần chạy; `select count(*)` trên `core.customer_clean` = 51.279 |
| Claude (Anthropic) | Hàm đọc ngày `parse_dates` (bản AI đầu tiên đọc sai) | `src/transform/rules.py` (`parse_dates`), `src/transform/clean_customers.py`, `src/load/loader.py` | Bản đầu dùng `dayfirst=True` nên đọc `2024-05-06` thành 5 tháng 6. Em đo tệp thật: 100% `ngay_tao` có dạng yyyy-mm-dd; trước khi sửa có 18.717 / 51.279 dòng (36,5%) ngày không khớp tệp nguồn; sau khi sửa và chạy lại pipeline, truy vấn so sánh cho 0 dòng lệch ở cả `stg` và `core`; `pytest` 45 PASS |
| Claude (Anthropic) | Soạn bản nháp dashboard Streamlit, ba trạng thái và che số điện thoại | `dashboard/app.py`, `src/ui/error_view.py`, `src/report/queries.py` | Mở trên trình duyệt và chụp đủ ba trạng thái (đang tải, rỗng với CSDL trống, lỗi khi dừng container `db`); vai trò Marketing bấm "Xác nhận gộp" bị từ chối và dữ liệu không đổi; số điện thoại hiển thị dạng che; đo thời gian tải trang bằng đồng hồ bấm giờ |
| Claude (Anthropic) | Soạn bản nháp bộ kiểm thử | `tests/test_rules.py`, `test_checks.py`, `test_dedupe.py`, `test_intake_merge.py`, `conftest.py` | Chạy `python -m pytest -q`: 45 PASS; đã đọc từng test và biết mỗi test kiểm tra điều gì, có ba loại: bình thường, biên, dữ liệu sai |


Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Họ tên: KAYSONE Souk Anong · MSSV: 237480201is05 · Ngày: 01/11/2026

---

## Bài tập 1 – Phân tích và Thiết kế (giữ nguyên bản đã nộp)

| Công cụ | Dùng vào việc gì | Áp dụng ở phần nào | Đã kiểm chứng thế nào |
| --- | --- | --- | --- |
| Claude (Anthropic) | Soạn bản nháp User Story, yêu cầu chức năng và phi chức năng, bảng truy vết, sắp xếp docs/srs.md, dựa trên nội dung và yêu cầu em cung cấp; hỗ trợ câu chữ tiếng Việt. | Mục 1 – SRS, docs/srs.md | Đối chiếu với case study (Bảng 9.1, Mục 8), đề bài BT1 và tài liệu tự học buổi 3; đọc lại tài liệu. |
| Claude (Anthropic) | Mục 4.2.1 và 4.2.2: em đưa ra ý chính; Claude soạn thành văn bản theo ý của em, bổ sung liên hệ NFR4, BR-L7-03, đánh đổi và hoàn thiện câu chữ. | Mục 4 (4.2.1, 4.2.2) | Đối chiếu với tài liệu tự học buổi 5 và đề bài BT1; em đã đọc lại và đối chiếu các tên bảng, cột với Mục 4. |
| Claude (Anthropic) | Soạn bản nháp mục 4.2.3–4.2.4, các câu lập luận kiến trúc và sơ đồ draw.io, dựa trên tiến độ và yêu cầu em cung cấp. | Mục 2, 3, 4 (4.2.3, 4.2.4), 5 | Em đã mở, kiểm tra và chỉnh một phần các file .drawio; kiểm tra thuật ngữ thống nhất. Phần lập luận thiết kế do AI soạn (đã khai báo), em rà soát và viết lại bằng lời của mình. |

Họ tên: KAYSONE Souk Anong · MSSV: 237480201is05 · Ngày: 10/10/2026

## Giai đoạn 3 (Bài tập 3, buổi 13–16)

| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
| --- | --- | --- | --- |
| Claude (Anthropic) | Soạn bản nháp Dockerfile, .dockerignore và docker-compose.yml (dịch vụ `db` và `app`, healthcheck, `app` chạy pipeline rồi mở dashboard) để đóng gói pipeline và dashboard | `Dockerfile`, `.dockerignore`, `docker-compose.yml` | Em build và chạy: `db` và `app` đều healthy, `curl` trả `ok`; chạy pytest trong container (45 passed); chạy lại pipeline và đếm 4 bảng: 323 / 49 / 47 / 468 không đổi; clone vào thư mục trống và làm đúng hai lệnh, hệ thống lên healthy. Em đã sửa: tên biến môi trường trong compose cho khớp `.env.example` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`); thêm `healthcheck` cho `db` với `pg_isready`; đặt `depends_on` có `condition: service_healthy`; đổi `DWH_URL` trong container thành host `db`, cổng 5432; đường dẫn dữ liệu mẫu đổi thành `data/mau/customers_raw_sample.csv` |
| Claude (Anthropic) | Hướng dẫn tạo `requirements.txt` bằng `pip freeze` | `requirements.txt` (commit `0e3aab5`) | Em cài vào venv mới rồi chạy pytest: 45 passed |
| Claude (Anthropic) | Soạn khung Test Plan, Test Report (12 test case), mẫu Bug Log, nhật ký thay đổi TD-16 đến TD-18 | `docs/test-plan.md`, `docs/test-report.md`, `docs/bug-log.md`, `docs/thay-doi-thiet-ke.md` | Em chạy lại từng test case bằng `pytest -v -k <mã>` và chụp ảnh `TC-nn.png` (12 ảnh); sửa ô "Kết quả thực tế" cho khớp `assert`; BUG-04, BUG-05 chỉ ghi khi đã có commit sửa riêng; ảnh `sec-*.png` chụp sau khi chạy lệnh checklist |
| Claude (Anthropic) | Soạn khung README, Deployment Guide, Checklist bảo mật, Pipeline doc, Data dictionary và bản nháp báo cáo PDF từ mã nguồn và kết quả em đã chạy | `README.md`, `docs/deployment-guide.md`, `docs/checklist-bao-mat.md`, `docs/pipeline-doc.md`, `docs/data-dictionary.md` | Em đối chiếu từng cột trong Data dictionary với `information_schema.columns` (94 cột, 14 đối tượng) — khớp; chạy 7 lệnh kiểm của Checklist ngày 15/11/2026 và điền kết quả; kiểm tra mọi con số trong Pipeline doc với báo cáo `reports/chat-luong-*.md` |
| — không dùng — (phần em tự làm) | Chọn phạm vi test và mức độ bug; tự chạy mọi test case, phép thử máy trắng và các lệnh kiểm tra bảo mật; chụp mọi ảnh; sửa lỗi BUG-04, BUG-05; thao tác Git (commit, push, tag v1.0). | `docs/test-report.md` (kết quả thực tế), `docs/checklist-bao-mat.md` (trạng thái), `docs/screenshots/` | Không áp dụng |

Tôi xác nhận đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp.

Họ tên: KAYSONE Souk Anong · MSSV: 237480201IS05 · Ngày: 15/11/2026
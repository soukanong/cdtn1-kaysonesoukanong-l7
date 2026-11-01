# Bảng khai báo sử dụng công cụ AI

## Bài tập 2 – Hiện thực hoá module cốt lõi (L7, track DA)



| Công cụ | Dùng vào việc gì | Áp dụng ở tệp / hàm nào | Em đã kiểm chứng thế nào |
| --- | --- | --- | --- |
| Claude (Anthropic)  | Soạn bản nháp mã đọc nguồn, chuẩn hóa số điện thoại và tên, tìm nhóm nghi trùng, đo DQ01–DQ06 | `src/extract/read_source.py`, `src/transform/rules.py`, `clean_customers.py`, `dedupe.py`, `src/quality/checks.py` | Chạy `pytest` (45 test PASS); chạy trên tệp thật 67.037 dòng: loại 4.133, sạch 51.279, 2.624 nhóm nghi trùng, điểm sạch 98,23; [XÁC NHẬN: tự tính lại 67.037 − 4.133 − 51.279 = 11.625 dòng trùng số điện thoại và đối chiếu với báo cáo] |
| Claude (Anthropic) | Soạn bản nháp mã nạp PostgreSQL (upsert, SCD loại 2) và các câu SQL | `src/load/loader.py`, `src/load/customer_repo.py`, `src/db.py`, `sql/001…003` | Chạy pipeline hai lần trên PostgreSQL 16 trong Docker và đếm dòng `core.customer_clean`, `core.reject_customer`, `core.duplicate_review`, `dwh.fact_dq_issue`: số dòng bằng nhau giữa hai lần chạy; `select count(*)` trên `core.customer_clean` = 51.279 |
| Claude (Anthropic) | Hàm đọc ngày `parse_dates` (bản AI đầu tiên đọc sai) | `src/transform/rules.py` (`parse_dates`), `src/transform/clean_customers.py`, `src/load/loader.py` | Bản đầu dùng `dayfirst=True` nên đọc `2024-05-06` thành 5 tháng 6. Em đo tệp thật: 100% `ngay_tao` có dạng yyyy-mm-dd; trước khi sửa có 18.717 / 51.279 dòng (36,5%) ngày không khớp tệp nguồn; sau khi sửa và chạy lại pipeline, truy vấn so sánh cho 0 dòng lệch ở cả `stg` và `core`; `pytest` 45 PASS |
| Claude (Anthropic) | Soạn bản nháp dashboard Streamlit, ba trạng thái và che số điện thoại | `dashboard/app.py`, `src/ui/error_view.py`, `src/report/queries.py` | Mở trên trình duyệt và chụp đủ ba trạng thái (đang tải, rỗng với CSDL trống, lỗi khi dừng container `db`); vai trò Marketing bấm "Xác nhận gộp" bị từ chối và dữ liệu không đổi; số điện thoại hiển thị dạng che; đo thời gian tải trang bằng đồng hồ bấm giờ |
| Claude (Anthropic) | Soạn bản nháp bộ kiểm thử | `tests/test_rules.py`, `test_checks.py`, `test_dedupe.py`, `test_intake_merge.py`, `conftest.py` | Chạy `python -m pytest -q`: 45 PASS; [XÁC NHẬN: đã đọc từng test và biết mỗi test kiểm tra điều gì, có ba loại: bình thường, biên, dữ liệu sai] |


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
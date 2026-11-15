# Test Plan – Luồng L7: Chất lượng dữ liệu khách hàng (track DA)

## 1. Phạm vi

**Kiểm:** chuẩn hóa số điện thoại (QT-02), không tạo hồ sơ trùng số điện thoại (QT-01), phát hiện hồ sơ nghi trùng (BR-L7-04), chọn hồ sơ chính khi gộp (UC5, FR8: hồ sơ tạo sớm nhất), chỉ Quản lý cửa hàng được xác nhận gộp (BR-L7-01 và quyền của Marketing ở SRS Mục 2), đọc tệp nguồn, đo chất lượng DQ01–DQ06 ở RAW và CLEAN, chạy lại pipeline không nhân đôi dữ liệu, dựng lại hệ thống từ thư mục trống. Số điện thoại hiển thị dạng che (QT-15) và việc không xóa vật lý hồ sơ (QT-13) được kiểm thủ công bằng ảnh chụp (MT-06 trong Test Report), không nằm trong 12 test case.

| Nhóm | Quy tắc hoặc yêu cầu | Test case |
|---|---|---|
| Chuẩn hóa số điện thoại | QT-02 (10 chữ số bắt đầu bằng 0; bốn dạng viết; 9 chữ số bị từ chối) | TC-01, TC-09 |
| Số lượng hồ sơ nhất quán | NFR3: đọc = mới + gắn vào + bị loại | TC-02 |
| Nghi trùng | BR-L7-04 (cùng email) | TC-03 |
| Chọn hồ sơ chính khi gộp | UC5, FR8 | TC-04 |
| Số điện thoại duy nhất | QT-01 | TC-05 |
| Ngưỡng chất lượng | DQ05, ngưỡng 99% ở hai phía | TC-06, TC-07 |
| Đọc tệp nguồn | tệp thiếu cột bị từ chối rõ ràng | TC-08 |
| Phân quyền gộp hồ sơ | BR-L7-01; SRS Mục 2 (Marketing không xác nhận gộp) | TC-10 |
| Số đo chất lượng | DQ01–DQ05 ở RAW và CLEAN | TC-11 |
| Chạy lại không nhân đôi | NFR2 | TC-12 |

**Chủ ý KHÔNG kiểm (kèm lý do):**
- Hiệu năng và tải: pipeline là tác vụ theo lô; NFR1 và NFR4 chỉ đo, không đặt tiêu chí PASS hoặc FAIL ở Test Report; kiểm tải thuộc Chuyên đề tốt nghiệp 2.
- Lọc dữ liệu theo cửa hàng (NFR7): tệp nguồn không có cột `store_code`, mọi hồ sơ có `store_key = −1` (TD-07), không có gì để kiểm.
- Đăng nhập thật: đã loại khỏi phạm vi từ BT1; vai trò chỉ mô phỏng trên dashboard.
- Kiểm thử giao diện tự động: giao diện chỉ có logic hiển thị, kiểm bằng ảnh chụp ba trạng thái (đang tải, rỗng, lỗi).
- Giới hạn của bộ đo chất lượng: hiện có sáu phép đo DQ01–DQ06; chưa đo completeness cho từng cột ngoài số điện thoại và họ tên, và chưa có phép kiểm toàn vẹn tham chiếu hoặc tập giá trị cho phép. Ghi nhận là hạn chế đã biết.

## 2. Loại test và số lượng

| Loại | Số lượng | Nội dung |
|---|---|---|
| Unit: hàm làm sạch và quy tắc nghiệp vụ | 45 test pytest (test_rules 21, test_checks 10, test_dedupe 5, test_intake_merge 9) | chuẩn hóa, đo DQ, tìm nghi trùng, nhập và gộp hồ sơ |
| Phép đo chất lượng trên dữ liệu | DQ01–DQ06 ở hai giai đoạn, kiểm bằng TC-11 và báo cáo `reports/chat-luong-*.md` | số đo RAW và CLEAN |
| Chạy lại pipeline (tích hợp, thủ công) | 2 lần, đếm 4 bảng | tái lập (NFR2) |

Kỹ thuật chọn dữ liệu: phân vùng tương đương (số điện thoại hợp lệ ở bốn dạng; không hợp lệ: rỗng, 9 chữ số, 11 chữ số không tiền tố 84) và giá trị biên (tỉ lệ đạt đúng bằng ngưỡng 99% và thấp hơn một hồ sơ).

Test Report chọn 12 test case, đủ năm loại: luồng đúng ×5 (TC-01 đến TC-05) · giá trị biên ×2 (TC-06, TC-07; hai phía của cùng ngưỡng 99%) · dữ liệu sai ×2 (TC-08, TC-09) · bảo mật hoặc chất lượng dữ liệu ×2 (TC-10, TC-11) · tái lập ×1 (TC-12).

## 3. Tiêu chí thành công (đặt trước khi chạy)

- 12 / 12 test case có kết quả thực tế cụ thể và ảnh chụp `docs/screenshots/TC-nn.png`; PASS chỉ khi mọi giá trị khớp mong đợi.
- Mỗi quy tắc nghiệp vụ đã hiện thực (QT-01, QT-02, BR-L7-01, BR-L7-04) có ít nhất 1 test; ngưỡng chất lượng có 2 test ở hai phía (TC-06, TC-07).
- 45 / 45 test PASS bằng một lệnh: `docker compose run --rm --no-deps app python -m pytest -q`, cả trên máy: `python -m pytest -q`.
- Chạy pipeline hai lần: số dòng `core.customer_clean`, `core.reject_customer`, `core.duplicate_review`, `dwh.fact_dq_issue` chênh lệch 0 (tệp mẫu: 323 / 49 / 47 / 468).
- Không còn bug Critical đang mở tại tag v1.0; bug Major còn lại có lý do và hướng xử lý.
- Hệ thống lên được từ thư mục trống bằng không quá 2 lệnh, hai dịch vụ `db` và `app` healthy.

**Làm sao biết đã kiểm đủ?** Mỗi quy tắc nghiệp vụ đã hiện thực có ít nhất một test luồng đúng; mỗi ngưỡng chất lượng có hai test ở hai phía; có hai test dữ liệu sai, hai test bảo mật hoặc chất lượng dữ liệu và một test tái lập. Phần cố ý không kiểm đã nêu ở mục 1, kèm lý do.

## 4. Môi trường và dữ liệu thử

- **Chạy ở đâu:** Windows với Docker Compose (`db` PostgreSQL 16 và `app`); phiên bản thư viện khóa bằng `==`.
- **Dữ liệu test tự động:** mỗi test tự dựng dữ liệu trong mã (DataFrame nhỏ, tệp tạm của pytest); không cần cơ sở dữ liệu, không dùng tệp có sẵn trên máy (test PASS trong container với `--no-deps`).
- **Dữ liệu chạy hệ thống:** `data/mau/customers_raw_sample.csv` (400 dòng) có trong repo; tệp thật 67.037 dòng không commit.
- **Dựng và dọn:** `docker compose down -v` xóa dữ liệu; `docker compose up -d --build` nạp lại từ tệp mẫu.
- **Lệnh chạy một test case:** `docker compose run --rm --no-deps app python -m pytest -v -k "<mã test>"`; chạy lại pipeline: `docker compose run --rm app python -m src.pipeline`.
# Test Plan – L7 Chất lượng dữ liệu khách hàng (track DA)

## 1. Mục tiêu và phạm vi

Kiểm thử hệ thống tích hợp ở mức cá nhân: pipeline làm sạch (extract → transform → quality → load), kho dữ liệu PostgreSQL và dashboard Streamlit.
Ngoài phạm vi: kiểm thử tải lớn, kiểm thử bảo mật xâm nhập, đăng nhập thật (đã loại trừ từ BT1).

## 2. Môi trường

Windows, Python 3.11 (venv), PostgreSQL 16 chạy trong Docker (`docker compose up -d db`), dữ liệu thật `customers_raw.csv` (67.037 dòng) và dữ liệu mẫu `data/mau/customers_raw_sample.csv`.

## 3. Cách chạy

| Việc | Lệnh |
|---|---|
| Toàn bộ test tự động (một lệnh, không cần cơ sở dữ liệu) | `python -m pytest -q` |
| Xem từng test case | `python -m pytest -v` |
| Chạy pipeline hai lần để kiểm tra tái lập | `python -m src.pipeline` (hai lần) rồi đếm bằng `select count(*)` |
| Kiểm thử thủ công dashboard | `streamlit run dashboard/app.py` |

## 4. Test case tự động (pytest)

### Loại 1 – Luồng đúng
| ID | Test case | Tệp |
|---|---|---|
| TR01 | Bốn dạng số điện thoại (+84…, 84…, 0901.234.567, 0901234567) đều ra 0901234567 | tests/test_rules.py |
| TR02 | Họ tên bỏ khoảng trắng thừa, viết hoa chữ cái đầu, giữ dấu tiếng Việt | tests/test_rules.py |
| TR03 | Email đổi chữ thường; email sai định dạng thành None | tests/test_rules.py |
| TR04 | Khóa so khớp họ tên và địa chỉ không dấu | tests/test_rules.py |
| TR10 | Ngày dạng dd/mm/yyyy vẫn đọc được | tests/test_rules.py |
| TC01 | Dữ liệu đúng thì nạp đủ số dòng, không bị loại | tests/test_checks.py |
| TC02 | Số dòng đọc = hồ sơ mới + gắn vào hồ sơ có sẵn + bản ghi bị loại (NFR3) | tests/test_checks.py |
| DD01, DD02 | Nghi trùng theo email; theo họ tên không dấu cùng địa chỉ | tests/test_dedupe.py |
| IM01 | Tạo hồ sơ hợp lệ trả về dữ liệu đã chuẩn hóa | tests/test_intake_merge.py |
| IM05, IM06 | Hồ sơ chính là hồ sơ tạo sớm nhất; hồ sơ không có ngày xếp sau | tests/test_intake_merge.py |

### Loại 2 – Giá trị biên
| ID | Test case | Tệp |
|---|---|---|
| TR05 | Số điện thoại 9, 11, 13 chữ số hoặc đầu số khác 0 đều không hợp lệ | tests/test_rules.py |
| TR06 | Đúng 10 chữ số hợp lệ; 11 chữ số tiền tố 84 cũng hợp lệ | tests/test_rules.py |
| TR09 | Ngày ISO `2024-05-06` đọc là 6/5/2024, không bị đảo tháng và ngày | tests/test_rules.py |
| TC03, TC04 | Tỉ lệ đạt đúng bằng ngưỡng thì đạt; thấp hơn một hồ sơ thì không đạt | tests/test_checks.py |
| TC05, TC10 | Không có hồ sơ nào để kiểm thì tỉ lệ 100%, không chia cho 0; toàn bộ email rỗng vẫn đo được | tests/test_checks.py |
| DD03, DD04 | Chỉ trùng họ tên thì không nghi trùng; email rỗng không coi là trùng nhau | tests/test_dedupe.py |

### Loại 3 – Dữ liệu sai
| ID | Test case | Tệp |
|---|---|---|
| TR07 | Giá trị rỗng, NaN, chuỗi "nan" là PHONE_MISSING, không thành chuỗi "nan" | tests/test_rules.py |
| TR08 | Chữ cái trong số điện thoại không làm hệ thống sập | tests/test_rules.py |
| TC06 | Số điện thoại rỗng hoặc sai vào bảng reject kèm mã lý do | tests/test_checks.py |
| TC09 | Tệp nguồn thiếu cột bị từ chối kèm thông báo rõ | tests/test_checks.py |
| IM02, IM03 | Form để trống báo lỗi theo từng trường; số điện thoại 9 chữ số bị từ chối | tests/test_intake_merge.py |
| IM04 | Số điện thoại đã tồn tại thì không tạo mới (QT-01) | tests/test_intake_merge.py |
| IM08, IM09 | Xung đột khi gộp; nhóm không tồn tại hoặc đã xử lý | tests/test_intake_merge.py |

### Loại 4 – Bảo mật và chất lượng dữ liệu
| ID | Test case | Tệp |
|---|---|---|
| IM07 | Marketing không được xác nhận gộp (QT-15) | tests/test_intake_merge.py |
| TC07 | Số đo chất lượng đúng ở cả RAW và CLEAN | tests/test_checks.py |
| TC08 | Quy tắc gate không đạt ở CLEAN thì pipeline phải dừng | tests/test_checks.py |

### Loại 5 – Tái lập
| ID | Test case | Tệp |
|---|---|---|
| DD05 | Mã nhóm nghi trùng ổn định giữa các lần chạy | tests/test_dedupe.py |

## 5. Test case thủ công (có ảnh chụp trong docs/screenshots/)

| ID | Loại | Các bước | Kết quả mong đợi | Ảnh |
|---|---|---|---|---|
| MT-01 | Dữ liệu sai | Mở Khung 3, để trống cả form, bấm Lưu | Thông báo đỏ và lỗi theo từng trường full_name, phone | 05 |
| MT-02 | Dữ liệu sai | Nhập số điện thoại đã có trong hệ thống, bấm Lưu | Báo đã có ở hồ sơ #…, không tạo hồ sơ mới (QT-01) | 06 |
| MT-03 | Bảo mật / lỗi | Tắt PostgreSQL, tải lại dashboard | Thông báo lỗi ngắn có nút Thử lại, không lộ chuỗi kết nối | 08 |
| MT-04 | Dữ liệu sai (trạng thái rỗng) | Dùng cơ sở dữ liệu chưa có dữ liệu | Hiện thông báo rỗng, không lỗi | 10, 11, 12 |
| MT-05 | Bảo mật | Chọn Marketing, bấm Xác nhận gộp | Từ chối, không gộp | 09 |
| MT-06 | Bảo mật | Chọn Marketing, xem danh sách nghi trùng | Số điện thoại dạng che (035****926) | 04 |
| MT-07 | Luồng đúng | Mở dashboard với dữ liệu thật | Khung 1, 2, 3 hiện đúng số liệu | 01, 02, 03 |
| MT-08 | Tái lập | Chạy pipeline hai lần rồi đếm số dòng các bảng | Số dòng customer_clean, reject_customer, duplicate_review, fact_dq_issue không đổi | `mt08-chay-lai-2-lan.png` |

## 6. Tiêu chí đạt

Toàn bộ test tự động PASS bằng một lệnh; mọi test thủ công cho kết quả đúng như mong đợi và có ảnh chụp; mỗi lỗi tìm thấy được ghi vào `docs/bug-log.md` với một commit sửa riêng.

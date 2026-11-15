# Test Report – Luồng L7 Chất lượng dữ liệu khách hàng

Kế hoạch: `docs/test-plan.md` · mã test: `tests/` · lỗi tìm được: `docs/bug-log.md`.
Lệnh chạy toàn bộ test tự động (một lệnh): `docker compose run --rm --no-deps app python -m pytest -q` hoặc trên máy: `python -m pytest -q`.
Toàn bộ: **45 passed** (container chạy 15/11/2026 lúc commit `ac94772`; 2.36s). Môi trường: Windows, Python 3.11.18 (container), PostgreSQL 16 trong Docker Compose.

**Cách chạy từng case.** Một lệnh cho mỗi case: `docker compose run --rm --no-deps app python -m pytest -v -k "<mã test>"`. Ảnh chụp terminal của lệnh đó là `docs/screenshots/TC-nn.png`. Ưu tiên: Cao = quy tắc MUST hoặc thuộc tính bảo mật hoặc dữ liệu · Trung bình = hành vi SHOULD hoặc chất lượng thông báo · Thấp = tiện ích.

## Mười hai test case

| Mã | Tiền điều kiện | Các bước | Dữ liệu thử | Kết quả mong đợi | Ưu tiên | Kết quả thực tế | P/F |
|---|---|---|---|---|---|---|---|
| TC-01 (QT-02) | Có `src/` và pytest; test tự dựng dữ liệu | 1. Chạy `python -m pytest -v -k TR01` | `+84 901 234 567`, `84901234567`, `0901.234.567`, `0901234567` | Cả bốn dạng chuẩn hóa thành `0901234567` | Cao | 4 tham số PASSED, mỗi dạng ra `0901234567`. Ảnh: `docs/screenshots/TC-01.png` | PASS |
| TC-02 (NFR3) | như trên | 1. Chạy `python -m pytest -v -k TC02` | 4 hồ sơ thô: một hồ sơ mới; một hồ sơ trùng số điện thoại (dạng `+84…`); một hồ sơ số điện thoại rỗng; một hồ sơ mới khác | Số dòng đọc = mới + gắn vào hồ sơ có sẵn + bị loại, tức 4 = 2 + 1 + 1 | Cao | `(mới, gắn, loại) = (2, 1, 1); 4 = 2 + 1 + 1; 1 passed`. Ảnh: `TC-02.png` | PASS |
| TC-03 (BR-L7-04) | như trên | 1. Chạy `python -m pytest -v -k DD01` | hai hồ sơ sạch số điện thoại khác nhau (`0901111111`, `0902222222`) cùng email `a@x.com` | Cả hai thành nghi trùng, `match_rule` = EMAIL | Cao | cả hai số điện thoại nằm trong nhóm, quy tắc EMAIL; 1 passed. Ảnh: `TC-03.png` | PASS |
| TC-04 (UC5, FR8) | như trên | 1. Chạy `python -m pytest -v -k IM05` | nhóm 3 hồ sơ: id 7 (01/05/2024), id 3 và id 2 (cùng 01/01/2023) | Hồ sơ chính là hồ sơ tạo sớm nhất; hòa thì mã nhỏ hơn: id 2 | Cao | `choose_primary` trả về `id 2` (hòa ngày 01/01/2023, chọn id nhỏ hơn); 1 passed. Ảnh: `TC-04.png` | PASS |
| TC-05 (QT-01) | như trên | 1. Chạy `python -m pytest -v -k IM04` | họ tên `An`, số điện thoại `0901234567`, hồ sơ có sẵn mã 123 | Lỗi `SO_DIEN_THOAI_DA_TON_TAI`, thông báo nêu `#123`, không tạo hồ sơ mới | Cao | `PhoneExistsError`, thông báo chứa `#123`; 1 passed. Ảnh: `TC-05.png` | PASS |
| TC-06 (biên, phía đạt) | như trên | 1. Chạy `python -m pytest -v -k TC03` | quy tắc DQ05 giai đoạn CLEAN: 100 hồ sơ, 1 vi phạm, ngưỡng 99% | Tỉ lệ đúng 99,0% thì vẫn đạt | Trung bình | tỉ lệ 99,0; đạt; 1 passed. Ảnh: `TC-06.png` | PASS |
| TC-07 (biên, phía không đạt) | như trên | 1. Chạy `python -m pytest -v -k TC04` | như TC-06 nhưng 2 vi phạm | Tỉ lệ 98% thấp hơn ngưỡng một hồ sơ thì không đạt | Trung bình | không đạt; 1 passed. Ảnh: `TC-07.png` | PASS |
| TC-08 (dữ liệu sai) | như trên; pytest tạo tệp tạm | 1. Chạy `python -m pytest -v -k TC09` | tệp CSV chỉ có hai cột `record_id,ho_ten` | Bị từ chối bằng `SourceFileError`, thông báo "thiếu cột bắt buộc", không sập | Cao | `SourceFileError` được raise, `match="thiếu cột bắt buộc"` khớp; không sập; 1 passed. Ảnh: `TC-08.png` | PASS |
| TC-09 (dữ liệu sai, QT-02) | như trên | 1. Chạy `python -m pytest -v -k IM03` | họ tên `An`, số điện thoại `090123456` (9 chữ số) | Bị từ chối, lỗi ở trường số điện thoại nêu "10 chữ số" | Cao | `InvalidInputError` được raise; `e.value.fields["phone"]` chứa "10 chữ số"; 1 passed. Ảnh: `TC-09.png` | PASS |
| TC-10 (bảo mật, BR-L7-01) | như trên | 1. Chạy `python -m pytest -v -k IM07` | vai trò Marketing, rồi vai trò Quản lý cửa hàng | Marketing bị từ chối xác nhận gộp; Quản lý cửa hàng được phép | Cao | Marketing → `PermissionDeniedError`; Quản lý cửa hàng → không lỗi; 1 passed. Ảnh: `TC-10.png` | PASS |
| TC-11 (chất lượng dữ liệu) | như trên | 1. Chạy `python -m pytest -v -k TC07` | 2 hồ sơ: `  an  ` / `+84901234567` / email `BAD`; `Bình` / số điện thoại rỗng / `b@x.com` | RAW: DQ01, DQ02, DQ04, DQ05 mỗi quy tắc 1 vi phạm; CLEAN: DQ01–DQ05 đều 0 | Cao | RAW — DQ01/DQ02/DQ04/DQ05 mỗi quy tắc `failed == 1`; CLEAN — DQ01–DQ05 đều `failed == 0`; 1 passed. Ảnh: `TC-11.png` | PASS |
| TC-12 (tái lập, NFR2) | `docker compose up -d --build` xong, `db` và `app` healthy; dữ liệu mẫu 400 dòng | 1. Đếm 4 bảng bằng `psql`. 2. Chạy `docker compose run --rm app python -m src.pipeline`. 3. Đếm lại 4 bảng | `data/mau/customers_raw_sample.csv` | Số dòng 4 bảng không đổi giữa hai lần đếm | Cao | cả hai lần: customer_clean 323, reject_customer 49, duplicate_review 47, fact_dq_issue 468; pipeline `THANH_CONG`. Ảnh: `TC-12.png` | PASS |

TC-02, TC-04, TC-08, TC-09, TC-10 và TC-11 đã được chạy lại và giá trị khớp với `assert` trong `tests/`: TC-02 → `(2, 1, 1)`; TC-04 → `id 2`; TC-08 → `SourceFileError` với `match="thiếu cột bắt buộc"`; TC-09 → `InvalidInputError` với `fields["phone"]` chứa `"10 chữ số"`; TC-10 → Marketing `PermissionDeniedError`, Quản lý cửa hàng không lỗi; TC-11 → RAW 4 vi phạm, CLEAN 0 vi phạm.

## Tổng kết

| | Lần 1 | Lần 2 (máy trắng) |
|---|---|---|
| Ngày và commit | 05/11/2026 · commit trước BT3 | 15/11/2026 · commit `ac94772` |
| Số case chạy | 12 | 12 |
| PASS / FAIL | 12 / 0 | 12 / 0 |
| Bug mở ra | không | BUG-04, BUG-05 |
| Cả bộ test, một lệnh | `python -m pytest -q` → 45 passed (05/11/2026) | `docker compose run --rm --no-deps app python -m pytest -q` → 45 passed (15/11/2026) |

Tiêu chí thành công (Test Plan mục 3): ĐẠT toàn bộ 6 tiêu chí — 12/12 test case có kết quả và ảnh; mỗi quy tắc có ≥1 test; 45/45 PASS; pipeline 2 lần chênh lệch 0; không còn bug Critical mở tại tag v1.0; hệ thống dựng từ thư mục trống bằng 2 lệnh, `db` và `app` healthy.

## Phân loại theo năm loại

| Loại | Test case |
|---|---|
| Luồng đúng | TC-01, TC-02, TC-03, TC-04, TC-05 |
| Giá trị biên | TC-06, TC-07 (hai phía của cùng một ngưỡng 99%) |
| Dữ liệu sai | TC-08, TC-09 |
| Bảo mật / chất lượng dữ liệu | TC-10, TC-11 |
| Tái lập | TC-12 |

## Kiểm thử thủ công bổ sung (ảnh trong `docs/screenshots/`)

| ID | Kết quả mong đợi | Kết quả thực tế | Ảnh |
|---|---|---|---|
| MT-01 | Báo lỗi đỏ, lỗi theo từng trường | PASS | `05-form-thieu-truong-bat-buoc.png` |
| MT-02 | Báo số điện thoại đã có ở hồ sơ #50546, không tạo mới | PASS | `06-form-so-dien-thoai-da-co.png` |
| MT-03 | Thông báo lỗi ngắn, không lộ chuỗi kết nối, có nút Thử lại | PASS (sau khi sửa BUG-01) | `08-loi-ket-noi-sau-khi-sua.png` |
| MT-04 | Hiện thông báo rỗng ở Khung 1, 2, 3 | PASS | `10-rong-khung1.png`, `11-rong-khung2.png`, `12-rong-khung3.png` |
| MT-05 | Marketing bấm Xác nhận gộp bị từ chối | PASS | `09-marketing-khong-du-quyen-gop.png` |
| MT-06 | Marketing chỉ thấy số điện thoại dạng che (QT-15) | PASS | `04-khung3-marketing-so-bi-che.png` |
| MT-07 | Ba khung hiện đúng số liệu thật | PASS (sau khi sửa BUG-03) | `01-khung1-tong-quan-do-sach.png`, `02-khung2-xu-huong-sau-khi-sua.png`, `03-khung3-quan-ly-so-day-du.png` |
| MT-08 | Chạy pipeline hai lần trên tệp thật, số dòng không đổi | PASS | `mt08-chay-lai-2-lan.png` (customer_clean 51.279, reject_customer 4.133, duplicate_review 5.438, fact_dq_issue 30.666; đo 05/11/2026) |

## Lỗi tìm thấy

Xem `docs/bug-log.md`. Mỗi bug ghi test case phát hiện; sau khi sửa, chạy lại test case đó và ghi kết quả vào dòng 7 của bug.
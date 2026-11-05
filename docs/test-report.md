# Test Report – L7 Chất lượng dữ liệu khách hàng

Ngày chạy: 05/11/2026 · Máy: AMD Ryzen 7 5700U (8 nhân), RAM 7,4 GB, Windows · Python 3.11.5 · PostgreSQL 16 (Docker)

> Em ghi kết quả đúng như quan sát trên máy em.

## 1. Tổng hợp

| Nhóm | Số test case | PASS | FAIL |
|---|---:|---:|---:|
| Tự động (`python -m pytest -v`) | 45 | 45 | 0 |
| Thủ công có ảnh chụp (MT-01 đến MT-08) | 8 | 8 | 0 |
| **Tổng** | 53 | 53 | 0 |

Lệnh chạy toàn bộ test tự động bằng một lệnh: `python -m pytest -q`, kết quả dòng cuối: `45 passed in 15.31s`.
Ảnh: `docs/screenshots/pytest-v-dau.png` và `docs/screenshots/pytest-v-cuoi.png` (em chụp màn hình `python -m pytest -v`, cả đầu và cuối danh sách).

## 2. Đủ 5 loại kiểm thử

| Loại | Test case (xem docs/test-plan.md) | Có |
|---|---|---|
| Luồng đúng | TR01–TR04, TR10, TC01, TC02, DD01, DD02, IM01, IM05, IM06, MT-07 | Có |
| Giá trị biên | TR05, TR06, TR09, TC03–TC05, TC10, DD03, DD04 | Có |
| Dữ liệu sai | TR07, TR08, TC06, TC09, IM02–IM04, IM08, IM09, MT-01, MT-02, MT-04 | Có |
| Bảo mật / chất lượng dữ liệu | IM07, TC07, TC08, MT-03, MT-05, MT-06 | Có |
| Tái lập | DD05, MT-08 | Có (DD05 tự động PASS; MT-08 PASS có ảnh chụp) |

## 3. Test thủ công (có ảnh trong docs/screenshots/)

| ID | Kết quả mong đợi | Kết quả thực tế | Ảnh |
|---|---|---|---|
| MT-01 | Báo lỗi đỏ, lỗi theo từng trường | PASS | `05-form-thieu-truong-bat-buoc.png` |
| MT-02 | Báo số điện thoại đã có ở hồ sơ #50546, không tạo mới | PASS | `06-form-so-dien-thoai-da-co.png` |
| MT-03 | Thông báo lỗi ngắn, không lộ chuỗi kết nối, có nút Thử lại | PASS (sau khi sửa BUG-01) | `08-loi-ket-noi-sau-khi-sua.png` |
| MT-04 | Hiện thông báo rỗng ở Khung 1, 2, 3 | PASS | `10-rong-khung1.png`, `11-rong-khung2.png`, `12-rong-khung3.png` |
| MT-05 | Marketing bấm Xác nhận gộp bị từ chối | PASS | `09-marketing-khong-du-quyen-gop.png` |
| MT-06 | Marketing chỉ thấy số điện thoại dạng che | PASS | `04-khung3-marketing-so-bi-che.png` |
| MT-07 | Ba khung hiện đúng số liệu thật | PASS | `01-khung1-tong-quan-do-sach.png`, `02-khung2-xu-huong-sau-khi-sua.png`, `03-khung3-quan-ly-so-day-du.png` |
| MT-08 | Chạy pipeline hai lần, số dòng không đổi | PASS | `mt08-chay-lai-2-lan.png` |

Số liệu MT-08 em đã đo ngày 05/11/2026 (hai lần chạy pipeline liên tiếp, đếm bằng `select count(*)`): customer_clean 51.279, reject_customer 4.133, duplicate_review 5.438, fact_dq_issue 30.666, không đổi giữa hai lần chạy. dim_run tăng từ 7 lên 8 và fact_dq_result tăng từ 66 lên 77 vì hai bảng này lưu lịch sử mỗi đợt chạy (đúng thiết kế). Lần chạy thứ hai mất 92,22 giây.

## 4. Lỗi tìm thấy

Xem `docs/bug-log.md` (BUG-01, BUG-02, BUG-03).
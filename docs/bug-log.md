# Bug Log

Mức độ: Cao (hệ thống treo hoặc sai kết quả), Trung bình (sai dữ liệu phụ), Thấp (hiển thị).
Ghi chú trung thực về commit: cả ba lỗi được phát hiện và sửa trong lúc phát triển, trước khi mã tương ứng được commit lần đầu, nên em KHÔNG có commit sửa riêng cho từng lỗi. Cột "Commit chứa mã sửa" trỏ tới commit đầu tiên có chứa đoạn mã đã sửa (commit tính năng, gộp nhiều thay đổi), không phải commit chỉ sửa một lỗi.

| Mã | Mức độ | Tóm tắt | Trạng thái | Commit chứa mã sửa |
|---|---|---|---|---|
| BUG-01 | Cao | Dashboard treo mãi ở "Đang truy vấn kho dữ liệu..." khi PostgreSQL tắt | Đã sửa | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/916fc94 (không có commit sửa riêng) |
| BUG-02 | Trung bình | Cột created_at bị đọc nhầm tháng và ngày với ngày dạng yyyy-mm-dd có ngày ≤ 12 | Đã sửa | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/9c76a6a (không có commit sửa riêng) |
| BUG-03 | Thấp | Khung 2: trục X hiện 1, 1.2, 1.4… thay vì nhãn đợt chạy; trục Y 0–105 làm hai đường gần như trùng | Đã sửa | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/7d48d15 (không có commit sửa riêng) |

## BUG-01 – Dashboard treo khi mất kết nối cơ sở dữ liệu
- **Cách tái hiện:** `docker compose stop db`, tải lại http://localhost:8501.
- **Hiện tượng:** màn hình đứng ở "Đang truy vấn kho dữ liệu..." không hiện thông báo lỗi (ảnh `07`, `14`).
- **Nguyên nhân:** engine SQLAlchemy không đặt thời gian chờ kết nối.
- **Cách sửa:** `connect_args={"connect_timeout": 5}` trong `src/db.py`.
- **Kiểm chứng sau khi sửa:** sau khoảng 5 giây hiện thông báo lỗi và nút Thử lại, không lộ chuỗi kết nối (ảnh `08`).

## BUG-02 – created_at đọc nhầm tháng và ngày
- **Cách tái hiện:** đọc cột `ngay_tao` dạng `2024-05-06` bằng `pd.to_datetime(..., format="mixed", dayfirst=True)`: kết quả 2024-06-05.
- **Phát hiện:** khi đo định dạng thật của `ngay_tao` trên `customers_raw.csv` (dạng yyyy-mm-dd), khác với dạng dd/mm/yyyy mà mã giả định.
- **Ảnh hưởng:** sai `created_at` của khoảng 40% hồ sơ, ảnh hưởng việc chọn hồ sơ chính khi gộp; không ảnh hưởng số đo chất lượng.
- **Cách sửa:** hàm `parse_dates` trong `src/transform/rules.py` đọc ISO trước; upsert cập nhật cả `created_at`; thêm test TR09, TR10.
- **Kiểm chứng sau khi sửa:** `python -m pytest tests/test_rules.py -v` (TR09, TR10), kết quả: [PASS/FAIL].

## BUG-03 – Biểu đồ xu hướng hiển thị sai trục
- **Hiện tượng:** trục X hiện số thập phân 1, 1.2, 1.4… (ảnh `13`).
- **Cách sửa:** `fig2.update_xaxes(type="category")` và thu hẹp khoảng trục Y trong `dashboard/app.py`.
- **Kiểm chứng sau khi sửa:** trục X hiện #1, #2 và thấy khoảng cách giữa đường dữ liệu và đường ngưỡng (ảnh `02`).

## Lỗi đã biết, chưa sửa
- Lần tải dashboard đầu tiên sau khi bật máy chủ mất 3,72 giây (> 3 giây của NFR4); nạp thư viện chiếm phần lớn (khoảng 5,2 giây ở một lần đo riêng).

## Cách tìm commit đã sửa từng lỗi
```
git log --oneline -S "connect_timeout" -- src/db.py
git log --oneline -S "parse_dates" -- src/transform/rules.py
git log --oneline -S "category" -- dashboard/app.py
```
Mỗi lệnh in ra mã commit đầu tiên đưa đoạn sửa vào. Nếu hai lỗi cùng nằm trong một commit lớn thì chưa đạt yêu cầu "mỗi lỗi một commit": xem hướng dẫn trong tin nhắn.

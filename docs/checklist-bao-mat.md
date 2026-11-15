# Checklist bảo mật – 7 mục (track DA)

Điền bằng cách CHẠY lệnh kiểm, không điền từ trí nhớ. Mỗi mục: **ĐÃ LÀM / CHƯA LÀM / KHÔNG ÁP DỤNG** kèm một dòng minh chứng (lệnh và kết quả, đường dẫn tệp hoặc ảnh). Ghi CHƯA LÀM trung thực không bị trừ điểm; ghi ĐÃ LÀM mà không có minh chứng thì bị trừ.

Ngày chạy: 15/11/2026 · commit: ac94772 · ảnh: `docs/screenshots/sec-1.png` … `sec-7.png` (ẩn secret và địa chỉ IP công khai).

| # | Mục | Trạng thái | Minh chứng (lệnh → kết quả) |
|---|---|---|---|
| 1 | Không có secret trong repo (kể cả lịch sử Git) | ĐÃ LÀM | `.env` nằm trong `.gitignore` và `.dockerignore`; `.env.example` chỉ có giá trị mẫu (`change_me`). Lệnh kiểm: `git log --all --oneline -- .env` → trống (không có commit nào chứa `.env`); `git check-ignore -v .env` → `.gitignore:2:.env`; `git log -p --all \| Select-String -Pattern "password\|secret\|api_key\|token" \| Select-Object -First 10` → chỉ thấy `POSTGRES_PASSWORD=change_me` (giá trị mẫu trong `.env.example`) và `DB_PASSWORD=` (giá trị rỗng). Ảnh `sec-1.png` |
| 2 | Dữ liệu vào được kiểm ở tầng ứng dụng | ĐÃ LÀM | TC-05 (số điện thoại đã có bị báo lỗi), TC-08 (tệp thiếu cột bị từ chối), TC-09 (số điện thoại 9 chữ số bị từ chối) đều PASS; ngoài ra DQ01–DQ04 là cổng chặn nạp: pipeline dừng với mã thoát 2 nếu không đạt (test `test_TC08_quy_tac_gate_khong_dat_o_CLEAN_thi_pipeline_phai_dung` PASSED). Đã thử nhập `'` và `;` vào trường họ tên và số điện thoại trên form: form báo lỗi và không ghi vào `core`; chuỗi 500 ký tự bị từ chối với thông báo độ dài. Ảnh `sec-2.png` |
| 3 | Kiểm soát truy cập theo vai trò | CHƯA LÀM | Mức ứng dụng: Marketing bấm "Xác nhận gộp" bị từ chối (TC-10 và MT-05). Mức cơ sở dữ liệu: `docker-compose.yml` cấu hình `DWH_URL` bằng `POSTGRES_USER` (tài khoản chủ sở hữu); không có ROLE hoặc GRANT trong PostgreSQL; vai trò chỉ mô phỏng trên dashboard (TD-13). |
| 4 | Dữ liệu nhạy cảm được che, băm hoặc mã hóa | CHƯA LÀM | `core.view_customer_masked` chỉ che số điện thoại (`093****196`); `full_name` vẫn hiện đầy đủ (kết quả query thấy `Trần Văn Trang`, `Vũ Quốc Trang`, `Đỗ Quốc Quân`); chưa có giả danh hóa HMAC và chưa có khóa `PSEUDO_KEY`. Kho `dwh` không chứa cột định danh cá nhân (`fact_dq_issue.issue_detail` không chứa số điện thoại đầy đủ). Lệnh kiểm: `docker compose exec db psql -U l7_user -d l7_dq -c "select * from core.view_customer_masked limit 3;"` → thấy 6 cột, `full_name` đầy đủ. Ảnh `sec-4.png` |
| 5 | Thông báo lỗi không lộ cấu trúc bên trong | ĐÃ LÀM (sau khi sửa BUG-07) | `docker compose stop db`, mở dashboard → chỉ thấy tên loại lỗi (`OperationalError`) và nút Thử lại, không có chuỗi kết nối. Đã tạo `.streamlit/config.toml` với `showErrorDetails = false` (BUG-07). Ảnh `sec-5.png` |
| 6 | Nhật ký không ghi secret hay dữ liệu cá nhân không cần thiết | ĐÃ LÀM | Bản tóm tắt của pipeline chỉ in số đếm (đọc, loại, sạch, nhóm nghi trùng, điểm sạch). Lệnh kiểm: `docker compose logs app \| Select-String -Pattern "\b0\d{9}\b"` → trống; `Select-String -Path reports\*.md -Pattern "\b0\d{9}\b"` → trống. Ảnh `sec-6.png` |
| 7 | Phụ thuộc ghim phiên bản và đã kiểm cảnh báo lỗ hổng | ĐÃ LÀM | `requirements.txt` khóa toàn bộ bằng `==` (commit `0e3aab5`), cài vào venv mới và `pytest` cho 45 passed. Lệnh kiểm: `pip install pip-audit` rồi `pip-audit -r requirements.txt` → `No known vulnerabilities found`. Ảnh `sec-7.png` |

## Ghi chú về dữ liệu mẫu trong repo

`data/mau/customers_raw_sample.csv` (400 dòng) nằm trong repo. Kết quả `Get-Content data\mau\customers_raw_sample.csv -TotalCount 5`: có 5 dòng, cột `record_id, ho_ten, so_dien_thoai, email, dia_chi, ngay_tao`; tên và số điện thoại có dạng giống dữ liệu thật (ví dụ `Trần Văn Trang`, `84933218196`). Dữ liệu mẫu là **dữ liệu thật đã được chọn ngẫu nhiên 400 dòng** — nếu đây là dữ liệu thật của khách hàng, cần thay bằng dữ liệu giả trước khi public repo; hiện repo ở chế độ private thì chấp nhận được. Trạng thái: CHƯA LÀM (nếu repo sẽ public).

## Ghi chú trung thực

Mục 3 và 4 chưa làm: dashboard còn ghi dữ liệu (tạo hồ sơ, xác nhận gộp) nên tài khoản hạn chế phải có quyền INSERT hoặc UPDATE trên một số bảng, không thể chỉ có SELECT; giả danh hóa HMAC chưa được thêm vào pipeline. Mục 1, 2, 5 (sau BUG-07), 6, 7 đã xác nhận bằng lệnh kiểm ngày 15/11/2026.

## Bug phát hiện khi chạy checklist

- **BUG-05** (Minor) — `find_suspects` so khớp email có phân biệt hoa thường, trái với BR-L7-04. Đã sửa trong commit `ac94772`.
- **BUG-07** (Major) — Thiếu `.streamlit/config.toml` với `showErrorDetails = false`; dashboard có thể hiện stack trace đầy đủ khi có lỗi. Đã sửa trong commit riêng `b42c3c0`; xem `docs/bug-log.md`.
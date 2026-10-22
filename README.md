# Quản lý chất lượng dữ liệu khách hàng – L7 (Smart CRM – Mekong Mobile)

- **Sinh viên:** KAYSONE Souk Anong – MSSV 237480201is05 – LHP 261_71ITGR40203_06
- **Track:** DA
- **Học phần:** Chuyên đề tốt nghiệp 1 – HK1, năm học 2026–2027 (Trường Đại học Văn Lang, Khoa Công nghệ Thông tin)
- **GVHD:** TS Nguyễn Trí Hải
- **Luồng nghiệp vụ:** L7 – Chất lượng dữ liệu khách hàng

## 1. Mục tiêu

Quản lý chất lượng dữ liệu khách hàng: hệ thống phát hiện hồ sơ trùng, thiếu và sai định dạng, chuẩn hóa số điện thoại và tên, gộp các hồ sơ được xác nhận trùng, và báo cáo mức độ sạch của dữ liệu theo thời gian.

Hệ thống phục vụ Quản lý cửa hàng (chạy làm sạch, xác nhận gộp hồ sơ) và Marketing (xem báo cáo, số điện thoại được che). Dữ liệu nguồn là tệp mẫu `customers_raw.csv` (khoảng 65.000 bản ghi) của case study Mekong Mobile.

## 2. Yêu cầu môi trường

- Python 3.11, pip
- Tạo môi trường ảo: `python -m venv .venv`, rồi kích hoạt: `.venv\Scripts\Activate.ps1`
- Cài thư viện: `pip install -r requirements.txt` (hiện có pandas 3.0.6, numpy 2.4.6)
- Tệp nguồn: `data/customers_raw.csv` (không commit vì chứa dữ liệu khách hàng)
- Dự kiến dùng thêm ở BT2: SQLAlchemy, PostgreSQL 16, Streamlit (chưa cài ở buổi 8)
- Biến môi trường: xem `.env.example` (không commit file `.env`)

## 3. Hướng dẫn chạy

1. Kích hoạt môi trường ảo (xem mục 2).
2. Đặt tệp `customers_raw.csv` vào thư mục `data/`.
3. Chạy từ thư mục gốc của repo: `python -m src.pipeline`
4. Kết quả in ra màn hình: số dòng, số cột, tỉ lệ ô trống, số dòng trước/sau và số dòng bị loại. Bảng reject lưu ở `reports/reject_customer.csv` (không commit).

## 4. Cấu trúc thư mục

```
cdtn1-kaysonesoukanong-l7/
├── README.md              ← tên đề tài, luồng, track, cách mở các file thiết kế
├── docs/                  ← toàn bộ tài liệu và sơ đồ của BT1
├── data/                  ← dữ liệu mẫu (không commit dữ liệu lớn)
├── src/                   ← mã nguồn (BT2)
├── tests/                 ← kiểm thử (BT2/BT3)
├── .env.example           ← tên biến môi trường, không chứa giá trị thật
└── .gitignore
```

## 5. Cách mở các file thiết kế

Các file `.drawio` là bản gốc. Mở bằng một trong hai cách:

- Truy cập https://app.diagrams.net, chọn **Open Existing Diagram** và chọn file `.drawio`.
- Trong VS Code, cài tiện ích **Draw.io Integration** rồi mở trực tiếp file `.drawio`.

Các file `.md` mở bằng VS Code (xem bản xem trước bằng `Ctrl+Shift+V`) hoặc ngay trên GitHub.

| File trong `docs/` | Nội dung | Mục trong PDF nộp |
|---|---|---|
| `srs.md` | Bản SRS rút gọn (gồm phụ lục Use Case) | Mục 1 (và Mục 2) |
| `usecase.drawio` | Use Case Diagram | Mục 2 |
| `architecture.drawio` | Sơ đồ kiến trúc 4 lớp | Mục 3 |
| `dataflow.drawio` | Sơ đồ luồng dữ liệu | Mục 4 |
| `erd.drawio` | Lược đồ hình sao của kho dữ liệu | Mục 4 |
| `wireframe.drawio` | Wireframe 3 màn hình | Mục 5 |
| `export/*.png` | Ảnh xuất để chèn vào PDF | – |
| `ai-declaration.md` | Bảng khai báo sử dụng công cụ AI | Phụ lục |
| `data-requirements.md` | Đặc tả yêu cầu dữ liệu (track DA) | Kèm BT1 |



## 6. Trạng thái hiện tại

**Bài tập 1 – Phân tích và Thiết kế**

- [x] Bản SRS rút gọn (`docs/srs.md`)
- [x] Use Case Diagram và đặc tả use case
- [x] Thiết kế kiến trúc và các câu lập luận
- [x] Mô hình dữ liệu (data flow, lược đồ hình sao) và đặc tả yêu cầu dữ liệu
- [x] Wireframe 3 màn hình
- [x] Bảng khai báo sử dụng công cụ AI


**Buổi 8 – Sprint 1 (module đầu tiên)**

- [x] Ghi quyết định điều chỉnh thiết kế theo phản hồi BT1 (`docs/thay-doi-thiet-ke.md`)
- [x] Cấu trúc `src/` theo sơ đồ kiến trúc (extract, transform, quality, load, pipeline.py)
- [x] Môi trường ảo và thư viện đã cài
- [x] Đọc tệp nguồn: 67.037 dòng, 6 cột; tỉ lệ ô trống: so_dien_thoai 6,17%, email 44,99%, dia_chi 8,98%, các cột còn lại 0%
- [x] Hàm chuẩn hóa số điện thoại; 4.133 dòng bị loại (PHONE_MISSING), 62.904 dòng hợp lệ
- [x] Ảnh kết quả chạy: `docs/ket-qua-chay.png`
- [ ] Chuẩn hóa họ tên, email chưa làm
- [ ] Tìm hồ sơ nghi trùng, đo RAW/CLEAN chưa làm
- [ ] Nạp PostgreSQL (`src/load`) và dashboard chưa làm
- [ ] Chưa có unit test
- Ghi chú: tệp thật không có cột `store_code` (chỉ có record_id, ho_ten, so_dien_thoai, email, dia_chi, ngay_tao), cần quyết định lại cho `dim_store` ở BT2
- Ghi chú: mạng chậm nên cài pandas bị timeout lần đầu, đã cài lại thành công

## 7. Khai báo sử dụng công cụ AI

Xem chi tiết tại [`docs/ai-declaration.md`](docs/ai-declaration.md).
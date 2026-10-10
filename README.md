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

- Python 3.11 trở lên
- Thư viện: pandas, SQLAlchemy, Streamlit
- PostgreSQL 16
- Biến môi trường: xem `.env.example` (không commit file `.env`)

## 3. Hướng dẫn chạy

Bài tập 1 chỉ gồm tài liệu và sơ đồ, chưa có mã nguồn. Hướng dẫn chạy (tối đa 4 bước) sẽ được cập nhật ở Bài tập 2, khi pipeline được hiện thực (dự kiến chạy bằng lệnh `make run`).

Dữ liệu nguồn dung lượng lớn không được commit; đặt tệp mẫu vào thư mục `data/` khi chạy.

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

## 7. Khai báo sử dụng công cụ AI

Xem chi tiết tại [`docs/ai-declaration.md`](docs/ai-declaration.md).
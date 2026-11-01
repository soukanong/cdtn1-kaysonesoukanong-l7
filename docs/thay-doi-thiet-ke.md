# Nhật ký thay đổi thiết kế

## Sau phản hồi Bài tập 1 (buổi 8, ngày 15/10/2026)

### TD-01 Bổ sung chú thích ký hiệu cho Use Case Diagram

- **Phản hồi của GV:** Use Case Diagram (Hình 2.1) chưa có chú thích ký hiệu (actor, use case, include, ranh giới).
- **Quyết định:** SỬA
- **Lý do:** sơ đồ phải đọc được độc lập mà không cần giải thích thêm.
- **Ảnh hưởng:** usecase.drawio và ảnh xuất usecase.png (thêm khung chú thích: actor, use case, include, ranh giới hệ thống).

### TD-02 Giữ nguyên 8 User Story

- **Phản hồi của GV:** có 8 User Story, đề yêu cầu 5–7.
- **Quyết định:** GIỮ NGUYÊN
- **Lý do:** tài liệu workshop buổi 4 yêu cầu ≥ 8 User Story; cả 8 story đều nối được tới FR và Use Case trong bảng truy vết, không có story thừa.
- **Ảnh hưởng:** không. SRS mục 1.3 và bảng truy vết giữ nguyên.

### TD-03 Rút gọn tài liệu nộp, giữ nội dung SCD và bản ghi Unknown

- **Phản hồi của GV:** tài liệu 24 trang, dài hơn nhiều so với 6–9 trang; các mục SCD, bản ghi Unknown chưa cần ở BT1.
- **Quyết định:** SỬA phần hình thức; GIỮ nội dung thiết kế.
- **Lý do:** PDF của BT2 sẽ giữ trong 6–9 trang. SCD loại 2 của dim_dq_rule và dòng −1 Unknown được dùng khi hiện thực bước load ở BT2, nên giữ trong thiết kế.
- **Ảnh hưởng:** độ dài PDF BT2; Mục 4 của thiết kế (erd.drawio, 4.2.2, 4.2.4) giữ nguyên.

### TD-04 Đặt tên file nộp theo MSSV

- **Phản hồi của GV:** tên file nên ghi đúng MSSV: BT1_237480201IS05_KaysoneSoukAnong.pdf.
- **Quyết định:** SỬA
- **Lý do:** để GV tìm và chấm đúng bài.
- **Ảnh hưởng:** tên file nộp BT2 (BT2_237480201IS05_KaysoneSoukAnong.pdf) và trang bìa.

### TD-05 Tự viết lại phần lập luận và đo thật NFR1, NFR4

- **Phản hồi của GV:** nên tự viết lại phần lập luận bằng lời của em như đã cam kết, và đo thật NFR1, NFR4 trên tệp 65.000 dòng.
- **Quyết định:** SỬA
- **Lý do:** lập luận thiết kế là phần được chấm; NFR chỉ có ý nghĩa khi có số đo thật.
- **Ảnh hưởng:** SRS mục 1.4, kiến trúc mục 3.2, mục 4.2 (viết lại bằng lời của em); README và báo cáo BT2 ghi kết quả đo NFR1 (xử lý 65.000 hồ sơ) và NFR4 (dashboard ≤ 3 giây); docs/ai-disclosure.md cập nhật cho BT2.
- **Kết quả đo (31/10 và 01/11/2026):** tệp thật có 67.037 dòng (không phải 65.000). Máy đo: AMD Ryzen 7 5700U (8 nhân, 16 luồng), RAM 7,4 GB, PostgreSQL 16 chạy trong Docker. NFR1 đạt: 101,5 giây (lần 1) và 93,2 giây (lần 2). NFR4: tải lại trang khoảng 1,32 giây trên trình duyệt (đo bằng đồng hồ bấm giờ) và 0,21–0,26 giây ở phía máy chủ (`scripts/time_dashboard.py`): đạt. Lần tải đầu tiên sau khi bật máy chủ mất 3,72 giây: không đạt; đo riêng cho thấy nạp thư viện chiếm khoảng 5,2 giây, truy vấn cơ sở dữ liệu chỉ 0,18 giây.

### TD-06 Cấu trúc thư mục src/ theo yêu cầu BT2 (track DA)

- **Phản hồi của GV:** không có (đối chiếu đề bài BT2 và tài liệu buổi 7).
- **Quyết định:** SỬA
- **Lý do:** BT2 yêu cầu ba pha extract / transform / load tách ở ba nơi và có thư mục quality.
- **Ảnh hưởng:** src/ gồm extract/, transform/, quality/, load/ và pipeline.py. Ánh xạ với kiến trúc BT1: Repository ↔ extract và load; Service ↔ transform và quality; Presentation ↔ dashboard/; Data store ↔ PostgreSQL. Sơ đồ kiến trúc đã hiện thực được vẽ ở docs/architecture-thuc-te.png; architecture.drawio của BT1 giữ nguyên làm bản thiết kế.

## Phát hiện khi hiện thực BT2

### TD-07 Tệp thật không có cột store_code

- **Phản hồi của GV:** không có (phát hiện khi đọc tệp thật ở Sprint 1).
- **Quyết định:** SỬA
- **Lý do:** customers_raw.csv chỉ có 6 cột (record_id, ho_ten, so_dien_thoai, email, dia_chi, ngay_tao), không cột nào xác định cửa hàng.
- **Ảnh hưởng:** mọi hồ sơ dùng store_key = −1 (Unknown, Mục 4.2.4 BT1); dim_store chỉ có dòng −1; bỏ bộ lọc cửa hàng ở Khung 1 và Khung 2; NFR7 (chỉ thấy dữ liệu của cửa hàng mình) không kiểm chứng được ở BT2.

### TD-08 Tên cột thật và số dòng thật của tệp nguồn

- **Phản hồi của GV:** không có (BT1 mục 4.3 hẹn đối chiếu tên cột ở BT2).
- **Quyết định:** SỬA
- **Lý do:** tên cột thật là ho_ten, so_dien_thoai, email, dia_chi, ngay_tao; tệp có 67.037 dòng thay vì khoảng 65.000.
- **Ảnh hưởng:** src/extract/read_source.py đọc theo tên cột thật; bảng đích vẫn dùng tên trong SRS (customer_clean, phone, full_name); docs/data-requirements.md điền tỉ lệ thiếu đã đo thay cho "chưa đo".

### TD-09 Thêm hai bảng trung gian ở lớp stg; reject_customer nạp lại mỗi đợt

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** nạp một lần bằng pandas rồi upsert bằng SQL trong một transaction nhanh hơn và dễ kiểm chứng hơn upsert từng dòng. reject_customer tham chiếu stg_customer nên được xóa và nạp lại cùng stg ở mỗi đợt.
- **Ảnh hưởng:** thêm stg.stg_customer_clean và stg.stg_duplicate (sql/002); reject_customer chỉ giữ kết quả của đợt chạy gần nhất; lược đồ hình sao không đổi.

### TD-10 fact_dq_issue chỉ giữ chi tiết của đợt chạy gần nhất

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** chạy lại hai lần phải cho số dòng bằng nhau (NFR2) và dung lượng chi tiết vi phạm không tăng vô hạn; fact_dq_result vẫn giữ lịch sử mọi đợt cho biểu đồ xu hướng.
- **Ảnh hưởng:** dwh.fact_dq_issue (các đợt cũ bị xóa khi chạy đợt mới); câu hỏi CH1 vẫn trả lời được từ fact_dq_result.

### TD-11 DQ06 chỉ đo ở CLEAN; chỉ DQ01–DQ04 chặn nạp

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** DQ01–DQ04 là bảo đảm của đầu ra (NFR3). DQ06 (hồ sơ nghi trùng chưa xử lý) phụ thuộc người xác nhận gộp nên không thể chặn việc nạp.
- **Ảnh hưởng:** configs/thresholds.yaml (gate: true cho DQ01–DQ04, false cho DQ05–DQ06), src/quality/checks.py, src/pipeline.py (mã thoát 2 khi quy tắc gate không đạt ở CLEAN).

### TD-12 Mỗi bản ghi bị loại chỉ mang một mã lý do

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** NFR3 yêu cầu mỗi hồ sơ đọc thuộc đúng một nhóm (mới / gắn vào hồ sơ có sẵn / bị loại). Hồ sơ vừa thiếu số điện thoại vừa thiếu họ tên chỉ ghi PHONE_MISSING (ưu tiên số điện thoại trước, họ tên sau).
- **Ảnh hưởng:** core.reject_customer, src/transform/clean_customers.py.

### TD-13 Vai trò chỉ mô phỏng; Quản lý cửa hàng xem số điện thoại đầy đủ, Marketing xem dạng che

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** BT1 đã loại trừ đăng nhập thật; vai trò chọn ở thanh bên dashboard và quy tắc "chỉ Quản lý cửa hàng được gộp" nằm ở transform/merge_rules.py. SRS Mục 2 cho Quản lý cửa hàng xem số đầy đủ (QT-15), còn wireframe BT1 vẽ dạng che cho mọi vai trò; hai chỗ trong BT1 không khớp nhau, em theo SRS.
- **Ảnh hưởng:** dashboard/app.py, src/report/queries.py (Marketing đọc qua core.view_customer_masked); không tạo ROLE/GRANT trong PostgreSQL nên NFR5 chỉ kiểm chứng ở mức ứng dụng và view.

### TD-14 Giữ nguyên ngưỡng DQ05 và DQ06 sau khi đo RAW

- **Phản hồi của GV:** không có (BR-L7-03: ngưỡng chỉ chốt sau khi đo RAW trên dữ liệu thật).
- **Quyết định:** GIỮ NGUYÊN
- **Lý do:** DQ05 đo được 100% ở RAW (36.880 email không sai định dạng nào) nên giữ 99%. DQ06 đo được 89,4% (5.438 trong 51.279 hồ sơ nằm trong 2.624 nhóm nghi trùng) nên không đạt ngưỡng 95%; ngưỡng này là mục tiêu sau khi Quản lý cửa hàng xác nhận gộp, hạ ngưỡng khi chưa có xác nhận sẽ làm chỉ số mất ý nghĩa. DQ06 không có số RAW để căn chỉnh vì chỉ đo ở CLEAN.
- **Ảnh hưởng:** configs/thresholds.yaml không đổi; pipeline vẫn thành công vì DQ06 có gate: false.

### TD-15 Bố cục Khung 3 và thêm ô Email vào form tạo hồ sơ

- **Phản hồi của GV:** không có.
- **Quyết định:** SỬA
- **Lý do:** có 2.624 nhóm nghi trùng nên một bảng chung quá dài; chọn một nhóm bằng danh sách thả xuống rồi xem các hồ sơ của nhóm đó. Ô Email cần để khớp quy tắc BR-L7-04 (nghi trùng theo email).
- **Ảnh hưởng:** wireframe Khung 3 (dashboard/app.py); không đổi dữ liệu hay quy tắc nghiệp vụ.

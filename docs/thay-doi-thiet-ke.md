# Nhật ký thay đổi thiết kế

## Sau phản hồi Bài tập 1 (buổi 8, ngày 15/10/2026)

### TD-01 Bổ sung chú thích ký hiệu cho Use Case Diagram
- Phản hồi của GV: Use Case Diagram (Hình 2.1) chưa có chú thích ký hiệu (actor, use case, include, ranh giới).
- Quyết định: SỬA
- Lý do: sơ đồ phải đọc được độc lập mà không cần giải thích thêm.
- Ảnh hưởng: usecase.drawio và ảnh xuất usecase.png (thêm khung chú thích: actor, use case, include, ranh giới hệ thống).

### TD-02 Giữ nguyên 8 User Story
- Phản hồi của GV: có 8 User Story, đề yêu cầu 5–7.
- Quyết định: GIỮ NGUYÊN
- Lý do: tài liệu workshop buổi 4 yêu cầu ≥ 8 User Story; cả 8 story đều nối được tới FR và Use Case trong bảng truy vết, không có story thừa.
- Ảnh hưởng: không. SRS mục 1.3 và bảng truy vết giữ nguyên.

### TD-03 Rút gọn tài liệu nộp, giữ nội dung SCD và bản ghi Unknown
- Phản hồi của GV: tài liệu 24 trang, dài hơn nhiều so với 6–9 trang; các mục SCD, bản ghi Unknown chưa cần ở BT1.
- Quyết định: SỬA phần hình thức; GIỮ nội dung thiết kế.
- Lý do: PDF của BT2 sẽ giữ trong 6–9 trang. SCD loại 2 của dim_dq_rule và dòng −1 Unknown được dùng khi hiện thực bước load ở BT2, nên giữ trong thiết kế.
- Ảnh hưởng: độ dài PDF BT2; Mục 4 của thiết kế (erd.drawio, 4.2.2, 4.2.4) giữ nguyên.

### TD-04 Đặt tên file nộp theo MSSV
- Phản hồi của GV: tên file nên ghi đúng MSSV: BT1_237480201IS05_KaysoneSoukAnong.pdf.
- Quyết định: SỬA
- Lý do: để GV tìm và chấm đúng bài.
- Ảnh hưởng: tên file nộp BT2 (BT2_237480201IS05_KaysoneSoukAnong.pdf) và trang bìa.

### TD-05 Tự viết lại phần lập luận và đo thật NFR1, NFR4
- Phản hồi của GV: nên tự viết lại phần lập luận bằng lời của em như đã cam kết, và đo thật NFR1, NFR4 trên tệp 65.000 dòng.
- Quyết định: SỬA
- Lý do: lập luận thiết kế là phần được chấm; NFR chỉ có ý nghĩa khi có số đo thật.
- Ảnh hưởng: SRS mục 1.4, kiến trúc mục 3.2, mục 4.2 (viết lại bằng lời của em); README và báo cáo BT2 ghi kết quả đo NFR1 (xử lý 65.000 hồ sơ) và NFR4 (dashboard ≤ 3 giây); docs/ai-disclosure.md cập nhật cho BT2.

### TD-06 Cấu trúc thư mục src/ theo yêu cầu BT2 (track DA)
- Phản hồi của GV: không có (đối chiếu đề bài BT2 và tài liệu buổi 7).
- Quyết định: SỬA
- Lý do: BT2 yêu cầu ba pha extract / transform / load tách ở ba nơi và có thư mục quality.
- Ảnh hưởng: src/ gồm extract/, transform/, quality/, load/ và pipeline.py. Ánh xạ với kiến trúc BT1: Repository ↔ extract và load; Service ↔ transform và quality; Presentation ↔ dashboard/; Data store ↔ PostgreSQL. architecture.drawio cập nhật cho khớp.

# Đặc tả yêu cầu dữ liệu – Luồng L7 Chất lượng dữ liệu khách hàng

Tài liệu này cập nhật Mục 4.3 của BT1 bằng số đo thật trên `customers_raw.csv` (BT2). Số đo ngày 31/10/2026 (lệnh đo nằm ở cuối tệp).

## 1. Câu hỏi phân tích

Mỗi câu hỏi nối về một User Story.

| Mã | Câu hỏi phân tích | US |
|---|---|---|
| CH1 | Tỉ lệ hồ sơ thiếu hoặc sai định dạng theo từng quy tắc của đợt chạy gần nhất là bao nhiêu? | US3 |
| CH2 | Sau làm sạch, mỗi quy tắc cải thiện bao nhiêu điểm phần trăm so với RAW? | US3, US4 |
| CH3 | Điểm sạch thay đổi thế nào qua các đợt chạy? | US4 |
| CH4 | Có bao nhiêu nhóm hồ sơ nghi trùng chưa xử lý và liên quan bao nhiêu hồ sơ? | US5 |
| CH5 | Bao nhiêu phần trăm hồ sơ thô chuẩn hóa được số điện thoại thành công? | US1, US2 |
| CH6 | Mỗi tháng có bao nhiêu lần gộp hồ sơ, do ai thực hiện? | US6, US7 |

Ghi chú: ở BT2 chưa có bộ lọc theo cửa hàng vì tệp thật không có cột cửa hàng (xem TD-07 trong `thay-doi-thiet-ke.md`), nên CH1 trả lời cho toàn bộ tệp.

## 2. Nguồn dữ liệu

- Tệp: `customers_raw.csv`, CSV UTF-8, cập nhật hằng tháng.
- Số dòng thật: **67.037** (BT1 ước tính khoảng 65.000, xem TD-08).
- Vấn đề đã biết (case study, Bảng 5.2 và V1): ước tính 18–22% hồ sơ trùng, số điện thoại có nhiều dạng, tên viết hoa thường lẫn lộn, có ô trống.
- Dữ liệu mẫu để dựng lại hệ thống: `data/mau/customers_raw_sample.csv` (400 dòng).

## 3. Từ điển dữ liệu nguồn

Tên cột là tên thật trong tệp (đã đối chiếu, xem TD-08). Tỉ lệ thiếu = số ô trống ÷ tổng số dòng, ô trống gồm chuỗi rỗng và giá trị như `nan`, `none`, `null`.

| Cột nguồn | Cột đích | Kiểu thực tế | Ý nghĩa | Giá trị hợp lệ | Tỉ lệ thiếu (đo) |
|---|---|---|---|---|---|
| record_id | — (chỉ lưu ở stg) | Văn bản | Mã bản ghi trong hệ thống nguồn | Không bắt buộc | 0,00% (0 / 67.037) |
| ho_ten | full_name | Văn bản | Họ tên khách | Không rỗng; có thể hoa thường lẫn lộn, có khoảng trắng thừa | 0,00% (0 / 67.037); 1.346 dòng vi phạm DQ04 đều do khoảng trắng hoặc dạng chữ chưa chuẩn |
| so_dien_thoai | phone | Văn bản | Số điện thoại | Sau chuẩn hóa: `^0[0-9]{9}$` | 6,17% (4.133 / 67.037) |
| email | email | Văn bản | Thư điện tử | Rỗng hoặc đúng định dạng | 44,99% (30.157 / 67.037) |
| dia_chi | address | Văn bản | Địa chỉ liên hệ | Văn bản tự do | 8,98% (6.023 / 67.037) |
| ngay_tao | created_at | Văn bản (ngày) | Thời điểm tạo hồ sơ | Ngày hợp lệ; dạng thật là yyyy-mm-dd (ví dụ 2024-05-26) | 0,00% (0 / 67.037) |
| (không có) | store_key | — | Cửa hàng nguồn của hồ sơ | Tệp thật không có cột này; mọi hồ sơ dùng store_key = −1 (Unknown) | Không áp dụng |

## 4. Quy tắc chất lượng có ngưỡng

Ngưỡng nằm trong `configs/thresholds.yaml`. Cột "Chặn nạp" nghĩa là nếu không đạt ở giai đoạn CLEAN thì pipeline dừng (mã thoát 2), xem TD-11. Ba chiều chất lượng của học phần là Completeness, Accuracy và Consistency; từ "tính hợp lệ" và "tính duy nhất" trong ngoặc là cách gọi trong mã nguồn (`src/quality/checks.py`).

| Mã | Chiều | Quy tắc | Ngưỡng đạt | Chặn nạp | Cách kiểm chứng |
|---|---|---|---|---|---|
| DQ01 | Completeness | Hồ sơ có số điện thoại | 100% | Có | Đếm phone rỗng |
| DQ02 | Accuracy (tính hợp lệ) | Số điện thoại khớp `^0[0-9]{9}$` | 100% | Có | Regex trên cột phone |
| DQ03 | Consistency (tính duy nhất) | `COUNT(*) = COUNT(DISTINCT phone)` trên các số điện thoại có giá trị; số vi phạm = số bản ghi dư (tổng trừ số giá trị khác nhau). Ở RAW so sánh chuỗi chưa chuẩn hóa (chỉ cắt khoảng trắng đầu và cuối); ở CLEAN so sánh số đã chuẩn hóa | 100% | Có | So sánh hai phép đếm trên cột phone |
| DQ04 | Accuracy (tính hợp lệ) | Họ tên không rỗng, không khoảng trắng đầu, cuối hoặc liên tiếp | 100% | Có | Kiểm tra trên full_name |
| DQ05 | Accuracy (tính hợp lệ) | Email khác rỗng thì đúng định dạng; email sai được đặt NULL và ghi vi phạm | 99% | Không | Regex trên email |
| DQ06 | Consistency | Hồ sơ nằm trong nhóm nghi trùng chưa xử lý không quá 5% hồ sơ sạch | 95% | Không | Tỉ lệ từ duplicate_review (PENDING), chỉ đo ở CLEAN |

## 5. Kết quả đo (đợt chạy ngày 31/10/2026, 67.037 dòng)

| Mã | RAW: tổng | RAW: vi phạm | RAW (%) | CLEAN: tổng | CLEAN: vi phạm | CLEAN (%) | Ngưỡng (%) | Đạt (CLEAN) |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| DQ01 | 67.037 | 4.133 | 93,83 | 51.279 | 0 | 100,00 | 100 | Đạt |
| DQ02 | 62.904 | 19.041 | 69,73 | 51.279 | 0 | 100,00 | 100 | Đạt |
| DQ03 | 62.904 | 6.146 | 90,23 | 51.279 | 0 | 100,00 | 100 | Đạt |
| DQ04 | 67.037 | 1.346 | 97,99 | 51.279 | 0 | 100,00 | 100 | Đạt |
| DQ05 | 36.880 | 0 | 100,00 | 28.214 | 0 | 100,00 | 99 | Đạt |
| DQ06 | không đo | không đo | — | 51.279 | 5.438 | 89,40 | 95 | **Không đạt** |

Điểm sạch (trung bình tỉ lệ đạt ở CLEAN): 98,23. Bản ghi bị loại: 4.133 (toàn bộ PHONE_MISSING). Nhóm nghi trùng: 2.624 nhóm, 5.438 hồ sơ. Ngưỡng DQ05 và DQ06 giữ nguyên theo TD-14.

Giải thích DQ03: ở RAW có 6.146 bản ghi dư vì chỉ so sánh chuỗi chưa chuẩn hóa. Sau khi chuẩn hóa số điện thoại, 11.625 bản ghi được gắn vào hồ sơ có sẵn (62.904 − 51.279); phần chênh 5.479 là các số trùng nhau nhưng viết khác dạng (ví dụ `+84…` và `0…`), chỉ lộ ra sau chuẩn hóa. Ở CLEAN số bản ghi dư là 0 vì bước khử trùng theo số điện thoại (QT-01) đã chạy trước phép đo.

## 6. Quy tắc biến đổi

- **Số điện thoại:** bỏ ký tự không phải chữ số, đổi tiền tố 84 thành 0, bắt buộc đúng 10 chữ số; không đạt thì vào bản ghi bị loại (PHONE_MISSING, PHONE_INVALID).
- **Họ tên:** cắt và gộp khoảng trắng, viết hoa chữ cái đầu mỗi từ, giữ dấu tiếng Việt; thiếu thì vào bản ghi bị loại (NAME_MISSING).
- **Email:** đổi sang chữ thường; sai định dạng thì đặt NULL và ghi vi phạm.
- **Giá trị thiếu:** không tự điền, chỉ ghi vi phạm.
- **Khử trùng:** theo số điện thoại đã chuẩn hóa (tự động, giữ hồ sơ đứng trước trong tệp) và theo BR-L7-04 (nghi trùng, chờ Quản lý cửa hàng xác nhận).

## 7. Cách đo tỉ lệ thiếu

Chạy ở thư mục gốc của repo (cần `data/customers_raw.csv`):

```
python -c "import pandas as pd; from src.transform.rules import is_empty; df=pd.read_csv('data/customers_raw.csv', dtype=str, keep_default_na=False, encoding='utf-8-sig'); print('tổng', len(df)); [print(c, int(df[c].map(is_empty).sum()), round(100*df[c].map(is_empty).mean(),2)) for c in df.columns]; print(df['ngay_tao'].head(3).tolist())"
```
# Bug Log

Mức độ theo ba câu hỏi: (1) người dùng còn làm được việc không; (2) dữ liệu có sai hoặc bị lộ không; (3) có cách làm tạm không.
**Critical** = hệ thống không dùng được, dữ liệu sai, hoặc có lỗ hổng bảo mật · **Major** = một chức năng quan trọng sai hoặc không dùng được nhưng có cách làm khác · **Minor** = ảnh hưởng trình bày, nghiệp vụ vẫn đúng.

## A. Bug của giai đoạn BT3 (mỗi bug một commit riêng)

| Mã | Mức độ | Tóm tắt | Phát hiện bởi | Commit |
|---|---|---|---|---|
| BUG-04 | Major | `requirements.txt` chưa khóa toàn bộ phiên bản bằng `==` | Nhận xét GV về BT2 (C6); phép thử máy trắng | [0e3aab5](https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/0e3aab5) (commit riêng) |
| BUG-05 | Minor | `find_suspects` so khớp email có phân biệt hoa thường, trái với BR-L7-04 | Đối chiếu test TC-03 với mã nguồn (dữ liệu thử dùng cùng một chuỗi `a@x.com` nên không kiểm được "không phân biệt hoa thường"); gọi thử hàm với `a@x.com` và `A@X.COM` cho kết quả rỗng | [ac94772](https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/ac94772) (commit riêng) |
| BUG-07 | Major | Thiếu `.streamlit/config.toml` với `showErrorDetails = false`; dashboard có thể hiện stack trace đầy đủ khi có lỗi | Checklist bảo mật mục 5 (`Test-Path .streamlit\config.toml` → False) | [hash-BUG-07] |

> Mức độ ở trên là đề xuất theo ba câu hỏi; em đọc lại từng lý do và đổi nếu thấy không đúng.

### BUG-04 · Major — `requirements.txt` chưa khóa toàn bộ phiên bản
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-04 · Major. Câu 1: hệ thống chạy được trên máy em nhưng người khác không dựng lại được đúng môi trường; câu 3: có cách tránh (cài tay đúng phiên bản) nên không phải Critical. |
| 2. Phát hiện bởi | Nhận xét của giảng viên về BT2, mục kiểm chứng C6; sau đó kiểm lại bằng phép thử máy trắng. |
| 3. Triệu chứng | Một số dòng trong `requirements.txt` không dùng `==`, nên hai lần cài ở hai thời điểm khác nhau có thể ra hai bộ thư viện khác nhau. |
| 4. Cách tái lập | `git log --all --oneline -- requirements.txt` cho thấy `requirements.txt` được tạo từ commit `2a55e91` và sửa ở `e32f247`; trước commit `0e3aab5`, các dòng trong tệp chưa được khóa bằng `==`. |
| 5. Nguyên nhân | Trong BT2 em cài trực tiếp các thư viện bằng `pip install` mà không ghi lại phiên bản, nên `requirements.txt` ban đầu chưa khóa `==`. Giảng viên nhận xét mục C6: cần khóa `==`. Em sinh lại toàn bộ bằng `pip freeze` để đảm bảo mọi dòng có `==`. |
| 6. Cách sửa | Sinh lại tệp bằng `pip freeze` từ môi trường đang chạy tốt, lưu bằng mã hóa ASCII; kiểm tra mọi dòng đều có `==`. |
| 7. Commit và xác nhận | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/0e3aab5 (commit riêng) · cài trong venv mới và `python -m pytest -q` → 45 passed · ảnh `docs/screenshots/BUG-04-fixed.png` |

### BUG-05 · Minor — `find_suspects` so khớp email có phân biệt hoa thường
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-05 · Minor. Câu 1: người dùng vẫn dùng được; câu 2: kết quả của pipeline không sai vì `clean_customers.py` chuẩn hóa email về chữ thường (`rules.normalize_email`) trước khi gọi `find_suspects`; câu 3: không cần cách làm tạm. Lỗi nằm ở chính hàm: nếu gọi hàm với email chưa chuẩn hóa thì bỏ sót nghi trùng. |
| 2. Phát hiện bởi | Khi đối chiếu TC-03 với mã test: tên test nói "khác hoa thường" nhưng dữ liệu thử dùng `a@x.com` ở cả hai hồ sơ nên không kiểm được điều đó. Gọi thử `find_suspects` với `a@x.com` và `A@X.COM` thì trả về bảng rỗng. |
| 3. Triệu chứng | Hai hồ sơ khác số điện thoại, email chỉ khác hoa thường, không được nhận là nghi trùng (kết quả rỗng), trái với BR-L7-04 và docstring của hàm. |
| 4. Cách tái lập | `python -c "from tests.test_dedupe import clean_df; from src.transform import dedupe; print(dedupe.find_suspects(clean_df([('0901111111','a@x.com','An','1 A'),('0902222222','A@X.COM','Binh','2 B')])))"` → `Empty DataFrame`. |
| 5. Nguyên nhân | `find_suspects` trong `src/transform/dedupe.py` nhóm hồ sơ bằng `groupby(["email"])` trên giá trị nguyên văn, không tự chuẩn hóa chữ hoa/thường; hàm chỉ đúng nhờ bước `normalize_email` ở nơi gọi, dù tài liệu hàm cam kết "không phân biệt hoa thường". Test DD01 cũ dùng cùng một chuỗi email nên không phát hiện. |
| 6. Cách sửa | Chuẩn hóa cột email (cắt khoảng trắng, chuyển chữ thường, rỗng thành None) ngay đầu `find_suspects`; sửa dữ liệu của `test_DD01` để hồ sơ thứ hai dùng `A@X.COM`. |
| 7. Commit và xác nhận | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/ac94772 (commit riêng) · `pytest -k DD01` FAILED trước khi sửa (`docs/screenshots/BUG-05-before.png`), PASSED sau khi sửa (`docs/screenshots/BUG-05-fixed.png`) · `pytest -q` → 45 passed. |

### BUG-07 · Major — Dashboard hiện stack trace đầy đủ khi có lỗi
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-07 · Major. Câu 1: người dùng vẫn dùng được; câu 2: **có thể lộ cấu trúc nội bộ** (đường dẫn tệp, tên hàm, chuỗi kết nối) qua stack trace; câu 3: có cách tránh (không để lỗi xảy ra) nhưng không bền → Major. |
| 2. Phát hiện bởi | Checklist bảo mật mục 5: `Test-Path .streamlit\config.toml` → `False`. |
| 3. Triệu chứng | Khi dashboard gặp lỗi (ví dụ mất kết nối DB), Streamlit hiển thị đầy đủ traceback, bao gồm đường dẫn và tên hàm. |
| 4. Cách tái lập | `docker compose stop db` → mở http://localhost:8501 → xem trang lỗi. |
| 5. Nguyên nhân | Không có tệp `.streamlit/config.toml` trong repo, nên Streamlit dùng giá trị mặc định `client.showErrorDetails = true`. |
| 6. Cách sửa | Tạo `.streamlit/config.toml` với `[client] showErrorDetails = false` (và `[browser] gatherUsageStats = false`); restart `app`. |
| 7. Commit và xác nhận | [hash-BUG-07] · sau khi restart, `docker compose stop db`, mở dashboard → chỉ thấy thông báo ngắn và nút Thử lại, không có stack trace (ảnh `sec-5.png`); `docker compose start db` khôi phục. |

## B. Lỗi đã biết, chưa sửa
- Lần tải dashboard đầu tiên sau khi bật máy chủ mất 3,72 giây (> 3 giây của NFR4). Thời gian chủ yếu là nạp thư viện (khoảng 5,2 giây ở một lần đo riêng); truy vấn cơ sở dữ liệu chỉ 0,18 giây. Mức Minor: không ảnh hưởng dữ liệu hay nghiệp vụ. Hướng xử lý: chấp nhận ở prototype; nếu làm tiếp thì tải sẵn thư viện hoặc giữ tiến trình máy chủ chạy sẵn.

## C. Phụ lục: lỗi phát hiện và sửa trong BT2 (không tính vào danh sách A)

BUG-01, BUG-02 và BUG-03 được phát hiện và sửa trong lúc phát triển BT2, trước khi mã tương ứng được commit lần đầu, nên em KHÔNG có commit sửa riêng cho từng lỗi. Cột commit trỏ tới commit tính năng đầu tiên chứa đoạn mã đã sửa (gộp nhiều thay đổi). Ghi lại để tham khảo và vì các tài liệu BT2 có nhắc tới chúng.

| Mã | Mức độ | Tóm tắt | Phát hiện bởi | Commit tính năng |
|---|---|---|---|---|
| BUG-01 | Major | Dashboard treo ở "Đang truy vấn kho dữ liệu..." khi PostgreSQL tắt | MT-03 | [916fc94](https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/916fc94) |
| BUG-02 | Critical | `created_at` bị đọc nhầm tháng và ngày (36,5% hồ sơ) | Đo định dạng nguồn; hồi quy TR09, TR10 | [9c76a6a](https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/9c76a6a) |
| BUG-03 | Minor | Khung 2: trục X hiện 1, 1.2, 1.4… thay vì nhãn đợt chạy | MT-07 | [7d48d15](https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/7d48d15) |

### BUG-01 · Major — Dashboard treo khi mất kết nối cơ sở dữ liệu
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-01 · Major. Câu 1: người dùng không biết hệ thống đang lỗi gì; câu 2: dữ liệu không sai, không lộ; câu 3: có cách làm tạm (bật lại PostgreSQL rồi tải lại trang) nên không phải Critical. |
| 2. Phát hiện bởi | MT-03 (thủ công): dừng PostgreSQL rồi tải dashboard; ảnh `07`, `14` ghi lại lỗi trước khi sửa. |
| 3. Triệu chứng | Sau `docker compose stop db`, trang đứng ở "Đang truy vấn kho dữ liệu..." mãi và không hiện thông báo lỗi. |
| 4. Cách tái lập | `docker compose stop db` → tải lại http://localhost:8501. |
| 5. Nguyên nhân | `create_engine` trong `src/db.py` không đặt thời gian chờ kết nối, nên lần kết nối tới máy chủ không phản hồi chờ theo mặc định của hệ điều hành thay vì báo lỗi sớm. |
| 6. Cách sửa | Thêm `connect_args={"connect_timeout": 5}` trong `src/db.py`. |
| 7. Commit và xác nhận | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/916fc94 (commit tính năng) · sau khoảng 5 giây hiện thông báo ngắn và nút Thử lại, không lộ chuỗi kết nối (ảnh `08`; MT-03 PASS). |

### BUG-02 · Critical — `created_at` bị đọc nhầm tháng và ngày
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-02 · Critical. Câu 2: dữ liệu sai ở 36,5% hồ sơ; câu 3: không có cách tránh trong ứng dụng. (Số đo chất lượng không bị ảnh hưởng, nhưng việc chọn hồ sơ chính khi gộp bị ảnh hưởng.) |
| 2. Phát hiện bởi | Đo định dạng thật của cột `ngay_tao` trên `customers_raw.csv`: 100% có dạng yyyy-mm-dd, trong khi mã giả định dd/mm/yyyy. Sau khi sửa có thêm test hồi quy TR09 và TR10. |
| 3. Triệu chứng | `2024-05-06` được đọc thành 2024-06-05. Trên tệp thật, 18.717 / 51.279 dòng (36,5%) có `created_at` không khớp tệp nguồn. |
| 4. Cách tái lập | `pd.to_datetime("2024-05-06", format="mixed", dayfirst=True)` → 2024-06-05. |
| 5. Nguyên nhân | `parse_dates` trong `src/transform/rules.py` đặt `dayfirst=True`, trong khi dữ liệu nguồn là ISO yyyy-mm-dd; với ngày ≤ 12, tháng và ngày bị hoán đổi. Bước upsert trước đây không cập nhật lại `created_at`, nên giá trị sai còn nằm lại trong `core`. |
| 6. Cách sửa | `parse_dates` đọc định dạng ISO trước; upsert cập nhật cả `created_at`; thêm test TR09 và TR10. |
| 7. Commit và xác nhận | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/9c76a6a (commit tính năng) · `python -m pytest tests/test_rules.py -v`: TR09, TR10 PASS · truy vấn so sánh `created_at` giữa `stg` và `core` cho 0 dòng lệch. |

### BUG-03 · Minor — Biểu đồ xu hướng hiển thị sai trục
| Dòng | Nội dung |
|---|---|
| 1. Mã và mức độ | BUG-03 · Minor. Chỉ ảnh hưởng trình bày: số liệu đúng, nghiệp vụ không đổi. |
| 2. Phát hiện bởi | MT-07 (thủ công): kiểm tra ba khung với số liệu thật; ảnh `13` ghi lại lỗi. |
| 3. Triệu chứng | Khung 2: trục X hiện số thập phân 1, 1.2, 1.4… thay vì nhãn đợt chạy; trục Y từ 0 đến 105 làm đường dữ liệu và đường ngưỡng gần như trùng nhau. |
| 4. Cách tái lập | Mở tab "Xu hướng theo thời gian" khi đã có từ hai đợt chạy trở lên. |
| 5. Nguyên nhân | Số thứ tự đợt chạy được truyền vào biểu đồ dưới dạng số, nên thư viện vẽ coi đó là trục số liên tục và tự chia nhỏ khoảng; khoảng trục Y để mặc định (0–105) nên hai đường bị nén sát nhau. |
| 6. Cách sửa | `fig2.update_xaxes(type="category")` và thu hẹp khoảng trục Y trong `dashboard/app.py`. |
| 7. Commit và xác nhận | https://github.com/soukanong/cdtn1-kaysonesoukanong-l7/commit/7d48d15 (commit tính năng) · trục X hiện #1, #2 và thấy khoảng cách giữa hai đường (ảnh `02`). |
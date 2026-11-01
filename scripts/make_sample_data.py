"""Tạo data/mau/customers_raw_sample.csv để người khác clone về là chạy được (README mục chạy).

  python scripts/make_sample_data.py                       # dữ liệu TỔNG HỢP có seed cố định
  python scripts/make_sample_data.py --from-real data/customers_raw.csv --n 400
                                                           # lấy mẫu ngẫu nhiên từ tệp thật (seed 42)

Dữ liệu tổng hợp có đủ tình huống: số điện thoại 4 dạng, ô trống, số sai độ dài, họ tên hoa thường lẫn
lộn và thừa khoảng trắng, email sai định dạng, trùng số điện thoại, nghi trùng theo email và theo họ tên+địa chỉ.
Số điện thoại và tên là GIẢ, không phải dữ liệu khách hàng thật.
"""
import argparse
import pathlib
import random

import pandas as pd

OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "mau" / "customers_raw_sample.csv"
COLUMNS = ["record_id", "ho_ten", "so_dien_thoai", "email", "dia_chi", "ngay_tao"]
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đặng", "Bùi", "Đỗ", "Ngô"]
DEM = ["Văn", "Thị", "Minh", "Quốc", "Hữu", "Ngọc", "Thanh", "Gia"]
TEN = ["An", "Bình", "Cường", "Dũng", "Hà", "Hùng", "Lan", "Linh", "Nam", "Phương", "Quân", "Trang"]
PHO = ["Lê Lợi", "Nguyễn Huệ", "Trần Hưng Đạo", "Hai Bà Trưng", "Điện Biên Phủ", "Cách Mạng Tháng 8"]


def fmt_phone(digits: str, rnd: random.Random) -> str:
    style = rnd.choice(["plain", "dot", "space", "intl", "intl84"])
    if style == "dot":
        return f"{digits[:4]}.{digits[4:7]}.{digits[7:]}"
    if style == "space":
        return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
    if style == "intl":
        return "+84" + digits[1:]
    if style == "intl84":
        return "84" + digits[1:]
    return digits


def synthetic(n: int = 400, seed: int = 42) -> pd.DataFrame:
    rnd = random.Random(seed)
    rows, pool = [], []
    for i in range(1, n + 1):
        name = f"{rnd.choice(HO)} {rnd.choice(DEM)} {rnd.choice(TEN)}"
        digits = "0" + rnd.choice("39") + "".join(rnd.choice("0123456789") for _ in range(8))
        email = f"user{i}@example.com" if rnd.random() < 0.55 else ""
        addr = f"{rnd.randint(1, 300)} {rnd.choice(PHO)}, Quận {rnd.randint(1, 12)}"
        date = f"{rnd.randint(1, 28):02d}/{rnd.randint(1, 12):02d}/{rnd.randint(2022, 2025)}"
        roll = rnd.random()
        if pool and roll < 0.08:                      # trùng số điện thoại với hồ sơ trước
            digits = rnd.choice(pool)["digits"]
        elif pool and roll < 0.14:                    # nghi trùng theo email
            src = rnd.choice(pool)
            if src["email"]:
                email = src["email"].upper()
        elif pool and roll < 0.20:                    # nghi trùng theo họ tên + địa chỉ
            src = rnd.choice(pool)
            name, addr = src["name"].upper(), src["addr"].lower()
        pool.append({"digits": digits, "email": email, "name": name, "addr": addr})
        phone = fmt_phone(digits, rnd)
        r = rnd.random()
        if r < 0.06:
            phone = ""
        elif r < 0.09:
            phone = digits[:9]                        # thiếu một chữ số
        if rnd.random() < 0.15:
            name = f"  {name.upper()}  "
        elif rnd.random() < 0.10:
            name = name.replace(" ", "   ")
        if email and rnd.random() < 0.06:
            email = email.replace("@", "")
        if rnd.random() < 0.01:
            name = ""
        rows.append([f"KH{i:05d}", name, phone, email, addr, date])
    return pd.DataFrame(rows, columns=COLUMNS)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-real", default=None, help="Lấy mẫu từ tệp thật thay vì tạo dữ liệu giả")
    ap.add_argument("--n", type=int, default=400)
    args = ap.parse_args()
    if args.from_real:
        df = pd.read_csv(args.from_real, dtype=str, keep_default_na=False, encoding="utf-8-sig")
        df = df.sample(n=min(args.n, len(df)), random_state=42).sort_index()
    else:
        df = synthetic(args.n)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8")
    print(f"Đã ghi {len(df)} dòng vào {OUT}")


if __name__ == "__main__":
    main()

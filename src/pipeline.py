import sys
from pathlib import Path

from src.extract.read_source import read_source
from src.quality.profile import print_profile
from src.transform.phone import normalize_phone

SOURCE = Path("data/customers_raw.csv")
REJECT_OUT = Path("reports/reject_customer.csv")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    df = read_source(SOURCE)
    print_profile(df)

    if "so_dien_thoai" not in df.columns:
        print("Không thấy cột 'so_dien_thoai'. Các cột thật:", list(df.columns))
        return

    result = df["so_dien_thoai"].apply(normalize_phone)
    df["phone_clean"] = result.str[0]
    df["reason_code"] = result.str[1]

    rejected = df[df["reason_code"].notna()]
    clean = df[df["reason_code"].isna()]

    REJECT_OUT.parent.mkdir(exist_ok=True)
    rejected.to_csv(REJECT_OUT, index=False, encoding="utf-8-sig")

    print("--- Báo cáo ---")
    print(f"Số dòng trước: {len(df)}")
    print(f"Số dòng sau (hồ sơ hợp lệ): {len(clean)}")
    print(f"Số dòng bị loại: {len(rejected)}")
    print(rejected["reason_code"].value_counts().to_string())


if __name__ == "__main__":
    main()

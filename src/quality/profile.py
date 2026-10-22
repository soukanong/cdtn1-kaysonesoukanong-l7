def blank_rate(df):
    """Tỉ lệ ô trống (%) của từng cột; ô chỉ có khoảng trắng cũng tính là trống."""
    blank = df.apply(lambda s: s.fillna("").str.strip().eq(""))
    return (blank.mean() * 100).round(2)


def print_profile(df):
    print(f"Số dòng: {len(df)}")
    print(f"Số cột: {df.shape[1]}")
    print("Tỉ lệ ô trống từng cột (%):")
    print(blank_rate(df).to_string())

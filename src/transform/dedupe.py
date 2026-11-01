"""BR-L7-04: tìm nhóm hồ sơ NGHI TRÙNG. Pipeline KHÔNG tự gộp (BR-L7-01).

Hai hồ sơ sạch (số điện thoại đã khác nhau) là nghi trùng khi:
  - trùng email (không rỗng, không phân biệt hoa thường), HOẶC
  - trùng đồng thời họ tên không dấu đã chuẩn hóa và địa chỉ đã chuẩn hóa.
Các cặp được nối bắc cầu thành nhóm (union-find).
"""
import pandas as pd


def find_suspects(clean: pd.DataFrame) -> pd.DataFrame:
    """Nhận hồ sơ sạch có cột source_row_no, phone, email, name_key, addr_key.

    Trả về DataFrame[group_id, phone, match_rule]. group_id = số dòng nguồn nhỏ nhất
    của nhóm, nên ỔN ĐỊNH giữa các lần chạy (cần cho việc chạy lại không nhân đôi).
    """
    columns = ["group_id", "phone", "match_rule"]
    if clean.empty:
        return pd.DataFrame(columns=columns)

    df = clean.reset_index(drop=True)
    parent = list(range(len(df)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    email_linked: set[int] = set()
    for keys, is_email in ((["email"], True), (["name_key", "addr_key"], False)):
        sub = df[df[keys].notna().all(axis=1)]
        for _, grp in sub.groupby(keys, sort=False):
            members = grp.index.tolist()
            if len(members) < 2:
                continue
            for other in members[1:]:
                union(members[0], other)
            if is_email:
                email_linked.update(members)

    roots = [find(i) for i in range(len(df))]
    df = df.assign(_root=roots)
    sizes = df.groupby("_root")["_root"].transform("size")
    df = df[sizes > 1]
    if df.empty:
        return pd.DataFrame(columns=columns)

    rows = []
    for _, grp in df.groupby("_root", sort=True):
        group_id = int(grp["source_row_no"].min())
        rule = "EMAIL" if any(i in email_linked for i in grp.index) else "NAME_ADDR"
        rows += [(group_id, p, rule) for p in grp["phone"]]
    return pd.DataFrame(rows, columns=columns)

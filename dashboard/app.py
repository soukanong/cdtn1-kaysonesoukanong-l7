"""Dashboard Streamlit - 3 khung theo wireframe BT1 (Mục 5).  Chạy: streamlit run dashboard/app.py

Xử lý đủ ba trạng thái: đang tải (spinner) · rỗng · lỗi kết nối. Thông báo lỗi KHÔNG in chuỗi kết nối.
Mọi số liệu lấy từ CSDL (src/report/queries.py), không ghi cứng. Vai trò chỉ MÔ PHỎNG (WON'T: đăng nhập thật).
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import db
from src.load import customer_repo
from src.report import queries
from src.transform import intake, merge_rules
from src.ui.error_view import run_safely

st.set_page_config(page_title="Chất lượng dữ liệu khách hàng - L7", layout="wide")
st.title("Chất lượng dữ liệu khách hàng (L7)")


@st.cache_resource
def engine():
    return db.get_engine()


role_label = st.sidebar.radio("Vai trò (mô phỏng)", ["Quản lý cửa hàng", "Marketing"])
role = merge_rules.ROLE_STORE_MANAGER if role_label == "Quản lý cửa hàng" else merge_rules.ROLE_MARKETING
user = st.sidebar.text_input("Tên người thực hiện", "quanly01")
CACHE_SECONDS = 60
st.sidebar.caption(f"Dữ liệu tổng hợp được lưu đệm tối đa {CACHE_SECONDS} giây.")


@st.cache_data(ttl=CACHE_SECONDS)
def load_overview():
    e = engine()
    return {"runs": queries.runs(e), "rejects": queries.reject_summary(e),
            "pending": queries.pending_overview(e)}


# ---------------- TRẠNG THÁI 1: đang tải · TRẠNG THÁI 3: lỗi ----------------
with st.spinner("Đang truy vấn kho dữ liệu..."):
    try:
        overview = load_overview()
    except Exception as exc:                                    # noqa: BLE001
        st.error("Không đọc được dữ liệu từ kho dữ liệu. Kiểm tra PostgreSQL đã chạy rồi thử lại.")
        st.caption(f"Chi tiết kỹ thuật: {type(exc).__name__}")   # chỉ tên loại lỗi
        if st.button("Thử lại"):
            st.cache_data.clear()
            st.rerun()
        st.stop()

runs_df: pd.DataFrame = overview["runs"]
tab1, tab2, tab3 = st.tabs(["1. Tổng quan độ sạch", "2. Xu hướng theo thời gian",
                            "3. Nghi trùng và gộp hồ sơ"])

# =========================== KHUNG 1 ===========================
with tab1:
    if runs_df.empty:                                           # TRẠNG THÁI 2: rỗng
        st.error("⚠ Chưa có kết quả cho đợt chạy này (đợt chạy chưa có dữ liệu hoặc FAILED). "
                 "Hãy chạy pipeline: python -m src.pipeline")
    else:
        run_key = st.selectbox("Đợt chạy", runs_df["run_key"].tolist(),
                               format_func=lambda k: f"#{k}")
        m = queries.measures(engine(), int(run_key))
        run_row = runs_df[runs_df["run_key"] == run_key].iloc[0]
        clean = m[m["stage"] == "CLEAN"]
        score = round(float(clean["pass_rate_pct"].mean()), 2) if not clean.empty else None
        raw_missing = m[(m["rule_code"] == "DQ01") & (m["stage"] == "RAW")]
        c1, c2, c3 = st.columns(3)
        c1.metric("Điểm sạch (CLEAN)", f"{score}" if score is not None else "-")
        c2.metric("Thiếu số điện thoại (RAW)",
                  int(raw_missing["failed_records"].iloc[0]) if not raw_missing.empty else 0)
        c3.metric("Nhóm nghi trùng chờ xử lý", overview["pending"]["groups"])

        st.subheader("Tỉ lệ đạt theo quy tắc: RAW so với CLEAN")
        fig = go.Figure()
        for stage, color in (("RAW", "#9aa0a6"), ("CLEAN", "#202124")):
            part = m[m["stage"] == stage]
            fig.add_bar(x=part["rule_code"], y=part["pass_rate_pct"], name=stage, marker_color=color)
        thr = m.drop_duplicates("rule_code")
        fig.add_scatter(x=thr["rule_code"], y=thr["threshold_pct"], mode="markers+lines", name="Ngưỡng",
                        line=dict(color="#d93025", dash="dot"))
        fig.update_layout(barmode="group", yaxis_title="Tỉ lệ đạt (%)", yaxis_range=[0, 105], height=380)
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Nguồn: dwh.fact_dq_result · đợt #{run_key} · tệp {run_row['source_file']} · "
                   f"chạy lúc {run_row['started_at']:%d/%m/%Y %H:%M}. "
                   f"Mốc so sánh: RAW (trước làm sạch) và ngưỡng của từng quy tắc.")

        st.subheader("Bản ghi bị loại")
        rej = overview["rejects"]
        if rej.empty:
            st.info("Không có bản ghi nào bị loại ở lần chạy này.")
        else:
            st.dataframe(rej[["reason_code", "records", "reason_text"]].rename(
                columns={"reason_code": "Mã lý do", "records": "Số hồ sơ", "reason_text": "Lý do"}),
                hide_index=True, width="stretch")

# =========================== KHUNG 2 ===========================
with tab2:
    if runs_df.empty:
        st.info("Chưa có đợt chạy nào để vẽ xu hướng.")
    else:
        pick = st.selectbox("Quy tắc", ["Tất cả (Điểm sạch)", "DQ01", "DQ02", "DQ03", "DQ04", "DQ05", "DQ06"])
        t = queries.trend(engine(), None if pick.startswith("Tất cả") else pick)
        if len(t) < 2:
            st.error("⚠ Mới có 1 đợt chạy, chưa đủ dữ liệu để vẽ xu hướng. Hãy chạy pipeline thêm một lần.")
        if not t.empty:
            fig2 = go.Figure()
            fig2.add_scatter(x=[f"#{k}" for k in t["run_key"]], y=t["pass_rate_pct"], mode="lines+markers",
                             name="Tỉ lệ đạt (CLEAN)")
            fig2.add_scatter(x=[f"#{k}" for k in t["run_key"]], y=t["threshold_pct"], mode="lines",
                             name="Ngưỡng", line=dict(color="#d93025", dash="dot"))
            low = float(min(t["pass_rate_pct"].astype(float).min(), t["threshold_pct"].astype(float).min()))
            fig2.update_layout(yaxis_title="%", yaxis_range=[max(0.0, low - 5), 101], height=380,
                               xaxis_title="Đợt chạy")
            fig2.update_xaxes(type="category")                       # nhãn #1, #2... không bị hiểu là số
            st.plotly_chart(fig2, width="stretch")
            st.caption("Nguồn: dwh.fact_dq_result, dwh.dim_dq_rule, dwh.dim_run · giai đoạn CLEAN. "
                       f"Dữ liệu mới nhất: đợt #{int(t['run_key'].max())}.")

# =========================== KHUNG 3 ===========================
with tab3:
    st.subheader("Tạo hồ sơ khách hàng mới (UC7)")
    with st.container(border=True):
        name = st.text_input("Họ tên *")
        phone = st.text_input("Số điện thoại *")
        email = st.text_input("Email")
        if st.button("Lưu"):
            def create():
                data = intake.validate_new_customer(
                    name, phone, email, find_by_phone=lambda p: customer_repo.find_by_phone(engine(), p))
                new_id = customer_repo.insert_customer(engine(), **data)
                return {"data": new_id}
            new_id = run_safely(create)
            if new_id:
                st.success(f"Đã tạo hồ sơ #{new_id}.")

    st.subheader("Hồ sơ nghi trùng (UC4, UC5)")
    if role == merge_rules.ROLE_MARKETING:
        st.caption("Số điện thoại hiển thị dạng che (đọc qua view_customer_masked).")
    groups = queries.pending_groups(engine(), masked=(role == merge_rules.ROLE_MARKETING))
    if groups.empty:
        st.caption("Không có hồ sơ nghi trùng")                    # trạng thái rỗng
    else:
        gid = st.selectbox("Nhóm", groups["group_id"].unique().tolist(), format_func=lambda g: f"Nhóm {g}")
        view = groups[groups["group_id"] == gid].rename(columns={
            "customer_id": "Mã hồ sơ", "full_name": "Họ tên", "phone": "Số điện thoại", "match_rule": "Khớp theo"})
        st.dataframe(view.drop(columns=["group_id"]), hide_index=True, width="stretch")
        b1, b2 = st.columns(2)
        if b1.button("Xác nhận gộp"):
            res = run_safely(lambda: customer_repo.confirm_merge(engine(), int(gid), role, user))
            if res:
                st.success(f"Đã gộp: hồ sơ chính #{res['primary_customer_id']}.")
                st.cache_data.clear()
        if b2.button("Không trùng"):
            res = run_safely(lambda: customer_repo.reject_group(engine(), int(gid), role, user))
            if res:
                st.success("Đã đánh dấu không trùng.")
                st.cache_data.clear()

    st.subheader("Lịch sử gộp (UC6)")
    hist = queries.merge_history(engine())
    if hist.empty:
        st.info("Chưa có lần gộp nào.")
    else:
        st.dataframe(hist.rename(columns={"merged_at": "Thời điểm", "merged_by": "Người gộp",
                                          "secondary_id": "Hồ sơ phụ", "primary_id": "Hồ sơ chính",
                                          "group_id": "Nhóm"}), hide_index=True, width="stretch")
    st.caption("Nguồn: core.customer_clean (qua view che số cho Marketing), core.duplicate_review, core.merge_log.")
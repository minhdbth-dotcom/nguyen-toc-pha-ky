import json
import os
import pandas as pd
import streamlit as st

# --- CẤU HÌNH TRANG VÀ GIAO DIỆN SÁCH A4 ĐỨNG ---
st.set_page_config(
    page_title="NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI",
    page_icon="📖",
    layout="wide",
)

st.markdown(
    """
    <style>
        @media print {
            body { background-color: white; }
            .book-page {
                width: 210mm;
                min-height: 297mm;
                padding: 20mm;
                margin: 10mm auto;
                border: 1px solid #d3d3d3;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                page-break-after: always;
                font-family: 'Times New Roman', Times, serif;
                color: #000;
            }
            .no-print { display: none; }
        }
        
        .book-page {
            width: 100%;
            max-width: 800px;
            min-height: 1100px;
            padding: 40px;
            margin: 20px auto;
            background: #fffdf9;
            border: 1px solid #dcd6cd;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-radius: 8px;
            font-family: 'Times New Roman', Times, serif;
            color: #2c2c2c;
        }
        
        .cover-title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            color: #b71c1c;
            text-transform: uppercase;
            margin-top: 50px;
            margin-bottom: 10px;
        }
        
        .cover-subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
            margin-bottom: 30px;
        }
        
        .member-card {
            background: #ffffff;
            border-left: 4px solid #b71c1c;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- QUẢN LÝ DỮ LIỆU JSON ---
DATA_FILE = "giapha_data.json"


def get_default_data():
    return [
        {
            "id": "1",
            "fullName": "Nguyễn Văn Tộc Tổ Khảo",
            "generation": "Tiên Tổ Khảo",
            "chi": "Gốc",
            "birthYear": "Đang cập nhật",
            "deathAnniversary": "Đang cập nhật",
            "location": "Từ đường dòng họ",
            "profession": "Tiên tổ",
            "spouse": "Nguyễn Thị Tổ Khảo",
            "father": "",
            "thuTu": None,
            "notes": "Bậc tiền hiền khai sáng dòng họ.",
            "imageUrl": "",
        }
    ]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return get_default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = "Khách"
if "username" not in st.session_state:
    st.session_state.username = ""

# --- THANH BÊN (SIDEBAR) & PHÂN QUYỀN ---
st.sidebar.title("🔐 Hệ Thống Phân Quyền")
if not st.session_state.logged_in:
    with st.sidebar.form("login_form"):
        st.subheader("Đăng Nhập Quản Trị")
        u_role = st.selectbox(
            "Vai trò:", ["Quản trị viên (Admin)", "Trưởng/Đầu Chi"]
        )
        u_pass = st.text_input("Mật khẩu bảo mật:", type="password")
        login_btn = st.form_submit_button("Đăng Nhập")
        if login_btn:
            if u_pass == "admin123" or u_pass == "chi123":
                st.session_state.logged_in = True
                st.session_state.role = u_role
                st.session_state.username = (
                    "Admin Tộc" if "Admin" in u_role else "Đầu Chi"
                )
                st.success("Đăng nhập thành công!")
                st.rerun()
            else:
                st.error("Sai mật khẩu! Vui lòng thử lại.")
else:
    st.sidebar.success(f"Đang đăng nhập với tư cách:\n**{st.session_state.username}**")
    if st.sidebar.button("Đăng Xuất"):
        st.session_state.logged_in = False
        st.session_state.role = "Khách"
        st.session_state.username = ""
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Hướng dẫn:** Sử dụng các thẻ (Tab) phía màn hình chính để tra cứu phả đồ, in sách, thêm mới hoặc xuất/nhập dữ liệu dòng họ."
)

# --- TIÊU ĐỀ CHÍNH ---
st.markdown(
    "<h1 style='text-align: center; color: #b71c1c;'>NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-style: italic; color: #666;'>Ghi chép nguồn cội, kết nối tương lai - 5 Chi đồng lòng gìn giữ gia phong</p>",
    unsafe_allow_html=True,
)

raw_data = load_data()
df = pd.DataFrame(raw_data)
df["_original_index"] = range(len(df))

# --- KHỞI TẠO CÁC TABS ---
tab_trang_chu, tab_cay_pha_he, tab_tra_cuu, tab_chi_tiet, tab_in_phu, tab_xuat, tab_nhap, tab_quan_tri = st.tabs(
    [
        "🏠 Trang Chủ",
        "🌳 Cây Phả Hệ",
        "🔍 Tra Cứu",
        "📋 Sổ Tay Chi Tiết",
        "📖 In Cuốn Gia Phả",
        "💾 Xuất Dữ Liệu",
        "📥 Nhập Dữ Liệu",
        "⚙️ Quản Trị & Thêm Mới",
    ]
)


def get_gen_number(gen_str):
    if not isinstance(gen_str, str):
        return 999
    if "Tiên Tổ" in gen_str:
        return 0
    import re

    nums = re.findall(r"\d+", gen_str)
    return int(nums[0]) if nums else 999


# ================= TAB 1: TRANG CHỦ =================
with tab_trang_chu:
    st.markdown(
        f'<div class="book-page"><div class="cover-title">NGUYỄN TỘC PHẢ KÝ</div><div class="cover-subtitle">GIA PHẢ TOÀN TỘC 5 CHI</div><hr><p style="text-align: justify; line-height: 1.6;">Chào mừng con cháu nội ngoại toàn tộc đến với Không gian lưu trữ Phả ký số của dòng họ Nguyễn.</p><p style="text-align: center; margin-top: 50px;"><b>Tổng số thành viên trong phả ký hiện tại:</b> <span style="color: #b71c1c; font-size: 24px;">{len(df)}</span></p></div>',
        unsafe_allow_html=True,
    )


# ================= TAB 2: CÂY PHẢ HỆ =================
with tab_cay_pha_he:
    st.subheader("🌳 Sơ Đồ Cây Phả Hệ Toàn Tộc 5 Chi")
    selected_chi_filter = st.selectbox(
        "Lọc hiển thị theo Chi:",
        ["Tất cả các Chi", "Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"],
    )

    filtered_df = df
    if selected_chi_filter != "Tất cả các Chi":
        filtered_df = df[df["chi"] == selected_chi_filter]

    sorted_gens = sorted(
        filtered_df["generation"].dropna().unique(), key=get_gen_number
    )

    for gen in sorted_gens:
        st.markdown(
            f"<h3 style='color: #b71c1c; border-bottom: 2px solid #b71c1c; padding-bottom: 5px;'>📌 {gen.upper()}</h3>",
            unsafe_allow_html=True,
        )
        gen_members = filtered_df[filtered_df["generation"] == gen]


        def sort_key(row):
            t = row.get("thuTu")
            if pd.isna(t) or t == "" or t is None:
                return 9999
            try:
                return int(t)
            except:
                return 9999


        gen_members_sorted = sorted(
            gen_members.to_dict("records"),
            key=lambda x: (sort_key(x), x.get("_original_index", 0)),
        )

        cols = st.columns(3)
        for idx, member in enumerate(gen_members_sorted):
            col = cols[idx % 3]
            with col:
                name = member.get("fullName", "Chưa rõ")
                chi = member.get("chi", "Chưa rõ")
                thutu_val = member.get("thuTu")
                thutu_str = (
                    f"Con thứ {int(thutu_val)}"
                    if pd.notna(thutu_val)
                    and str(thutu_val).strip() != ""
                    and str(thutu_val) != "None"
                    else "Thứ tự: Chưa rõ"
                )
                spouse = member.get("spouse", "Chưa rõ")
                father = member.get("father", "Chưa rõ")

                st.markdown(
                    f"""
                <div class="member-card">
                    <b>{name}</b><br>
                    <span style="font-size: 12px; color: #555;">🏷️ Chi: {chi} | {thutu_str}</span><br>
                    <span style="font-size: 12px; color: #555;">👨 Phụ thân: {father if father else 'Chưa rõ'}</span><br>
                    <span style="font-size: 12px; color: #555;">👥 Phối: {spouse if spouse else 'Chưa rõ'}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )


# ================= TAB 3: TRA CỨU =================
with tab_tra_cuu:
    st.subheader("🔍 Tra Cứu Thông Tin Thành Viên")
    search_keyword = st.text_input(
        "Nhập tên, đời, năm sinh hoặc nội dung cần tìm kiếm:"
    )

    if search_keyword:
        mask = df.apply(
            lambda row: row.astype(str)
            .str.contains(search_keyword, case=False, na=False)
            .any(),
            axis=1,
        )
        search_results = df[mask]
        st.write(
            f"Tìm thấy **{len(search_results)}** kết quả phù hợp với từ khóa '{search_keyword}':"
        )

        for _, row in search_results.iterrows():
            thutu_val = row.get("thuTu")
            thutu_str = (
                f"Con thứ {int(thutu_val)}"
                if pd.notna(thutu_val)
                and str(thutu_val).strip() != ""
                and str(thutu_val) != "None"
                else "Thứ tự: Chưa rõ"
            )
            st.markdown(
                f"""
            <div style="background: white; padding: 12px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #ddd;">
                <h4 style="margin: 0; color: #b71c1c;">{row.get('fullName', 'Chưa rõ')}</h4>
                <p style="margin: 5px 0 0 0; font-size: 13px;">
                    <b>Đời:</b> {row.get('generation', '')} | <b>Chi:</b> {row.get('chi', '')} | <b>{thutu_str}</b><br>
                    <b>Phụ thân:</b> {row.get('father', 'Chưa rõ')} | <b>Vợ/Chồng:</b> {row.get('spouse', 'Chưa rõ')}<br>
                    <b>Ghi chú/Tiểu sử:</b> {row.get('notes', 'Không có')}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )


# ================= TAB 4: SỔ TAY CHI TIẾT =================
with tab_chi_tiet:
    st.subheader("📋 Sổ Tay Chi Tiết Thành Viên Dòng Họ")

    if not df.empty and "generation" in df.columns:
        gen_list = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        selected_gen_detail = st.selectbox(
            "Chọn Đời để xem sổ tay chi tiết:", gen_list, key="gen_detail_box"
        )

        gen_df = df[df["generation"] == selected_gen_detail]


        def sort_key_detail(row):
            t = row.get("thuTu")
            if pd.isna(t) or t == "" or t is None:
                return 9999
            try:
                return int(t)
            except:
                return 9999


        gen_records = sorted(
            gen_df.to_dict("records"),
            key=lambda x: (sort_key_detail(x), x.get("_original_index", 0)),
        )

        for member in gen_records:
            name = member.get("fullName", "Chưa rõ")
            chi = member.get("chi", "Chưa rõ")
            thutu_val = member.get("thuTu")
            thutu_html = (
                f'<span style="font-size: 13px; color: #d32f2f; font-weight: normal;">(Con thứ {int(thutu_val)})</span>'
                if pd.notna(thutu_val)
                and str(thutu_val).strip() != ""
                and str(thutu_val) != "None"
                else '<span style="font-size: 13px; color: #777; font-weight: normal;">(Thứ tự: Chưa rõ)</span>'
            )
            spouse = member.get("spouse", "Chưa rõ")
            spouse_text = (
                f"Phối: <b>{spouse}</b>"
                if spouse and spouse != "Chưa rõ"
                else "Phối: <i>Chưa rõ</i>"
            )
            father = member.get("father", "Chưa rõ")
            father_text = father if father else "Chưa rõ"
            notes = member.get("notes", "")
            notes_html = (
                f'<div style="margin-top: 8px; font-size: 13px; font-style: italic; color: #444;">📜 Tiểu sử/Ghi chú: {notes}</div>'
                if notes and notes != "nan"
                else ""
            )

            img_url = member.get("imageUrl", "")
            img_html = (
                f'<img src="{img_url}" style="width: 80px; height: 100px; object-fit: cover; border-radius: 4px; border: 1px solid #ccc;">'
                if img_url
                else '<div style="width: 80px; height: 100px; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #777; border-radius: 4px; border: 1px solid #ccc;">Chưa có ảnh</div>'
            )

            st.markdown(
                f"""
            <div style="background: white; border: 1px solid #dcd6cd; border-radius: 6px; padding: 15px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="width: 100px; vertical-align: top;">
                            {img_html}
                        </td>
                        <td style="vertical-align: top; padding-left: 15px;">
                            <div style="font-size: 16px; font-weight: bold; color: #b71c1c;">{name} {thutu_html}</div>
                            <div style="font-size: 13px; color: #333; margin-top: 3px;">🏷️ Chi: <b>{chi}</b></div>
                            <div style="font-size: 13px; color: #333; margin-top: 3px;">👥 {spouse_text}</div>
                            <div style="font-size: 13px; color: #555; margin-top: 3px;">👨 Phụ thân: {father_text}</div>
                        </td>
                    </tr>
                </table>
                {notes_html}
            </div>
            """,
                unsafe_allow_html=True,
            )


# ================= TAB 5: IN CUỐN GIA PHẢ =================
with tab_in_phu:
    st.subheader("📖 In Cuốn Gia Phả Toàn Tộc (Định Dạng Sách A4 Đứng)")
    if st.button("🖨 Mở Giao Diện In Sách"):
        st.markdown(
            "<script>window.print();</script>", unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="book-page">
            <h1 style="text-align: center; color: #b71c1c; margin-top: 100px;">NGUYỄN TỘC PHẢ KÝ</h1>
            <h3 style="text-align: center; color: #555; margin-bottom: 150px;">GIA PHẢ TOÀN TỘC 5 CHI</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )

    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        for gen in sorted_gens:
            gen_members = df[df["generation"] == gen]


            def sort_key_print(row):
                t = row.get("thuTu")
                if pd.isna(t) or t == "" or t is None:
                    return 9999
                try:
                    return int(t)
                except:
                    return 9999


            gen_members_sorted = sorted(
                gen_members.to_dict("records"),
                key=lambda x: (sort_key_print(x), x.get("_original_index", 0)),
            )

            page_content = f"<h2 style='text-align: center; color: #795548;'>CHI TIẾT: {gen.upper()}</h2><hr style='border: 1px solid #795548; margin-bottom: 20px;'>"

            for member in gen_members_sorted:
                name = member.get("fullName", "Chưa rõ")
                chi = member.get("chi", "Chưa rõ")
                thutu_val = member.get("thuTu")
                thutu_str = (
                    f"Con thứ: {int(thutu_val)}"
                    if pd.notna(thutu_val)
                    and str(thutu_val).strip() != ""
                    and str(thutu_val) != "None"
                    else "Thứ tự: Chưa rõ"
                )
                spouse = member.get("spouse", "Chưa rõ")
                father = member.get("father", "Chưa rõ")
                notes = member.get("notes", "Chưa có thông tin tiểu sử.")

                page_content += f"""
                <div style="margin-bottom: 20px; border-bottom: 1px dashed #ccc; padding-bottom: 12px;">
                    <p style="margin: 4px 0;"><b>Họ và tên:</b> <span style="font-size: 16px; color: #b71c1c; font-weight: bold;">{name}</span> ({thutu_str})</p>
                    <p style="margin: 4px 0;"><b>Thuộc Chi:</b> {chi} | <b>Đời thứ:</b> {gen}</p>
                    <p style="margin: 4px 0;"><b>Phụ thân:</b> {father if father else 'Chưa rõ'} | <b>Phối (Vợ/Chồng):</b> {spouse if spouse else 'Chưa rõ'}</p>
                    <p style="margin: 4px 0;"><b>Tiểu sử / Ghi chú:</b> {notes if pd.notna(notes) and notes != '' else 'Chưa cập nhật'}</p>
                </div>
                """

            st.markdown(
                f'<div class="book-page">{page_content}</div>',
                unsafe_allow_html=True,
            )


# ================= TAB 6: XUẤT DỮ LIỆU =================
with tab_xuat:
    st.subheader("💾 Xuất Dữ Liệu Gia Phả")
    if not df.empty:
        json_str = df.drop(columns=["_original_index"], errors="ignore").to_json(
            force_ascii=False, orient="records", indent=4
        )
        st.download_button(
            label="📥 Tải xuống file dữ liệu (JSON)",
            data=json_str,
            file_name="GiaPha_DongHoNguyen.json",
            mime="application/json",
        )

        try:
            from io import BytesIO

            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.drop(columns=["_original_index"], errors="ignore").to_excel(
                    writer, index=False, sheet_name="GiaPha"
                )
            excel_data = output.getvalue()
            st.download_button(
                label="📊 Tải xuống file Excel",
                data=excel_data,
                file_name="GiaPha_DongHoNguyen.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception:
            st.info(
                "💡 Định dạng Excel đang tạm ẩn do chưa cài đặt thư viện `openpyxl`. Bạn vẫn có thể tải xuống file JSON hoàn toàn bình thường."
            )


# ================= TAB 7: NHẬP DỮ LIỆU =================
with tab_nhap:
    st.subheader("📥 Nhập Dữ Liệu Gia Phả Từ File")
    uploaded_file = st.file_uploader(
        "Chọn file dữ liệu (JSON hoặc XLSX)", type=["json", "xlsx"]
    )
    if uploaded_file is not None:
        if st.button("⚡ Xác nhận nhập và cập nhật dữ liệu"):
            try:
                if uploaded_file.name.endswith(".json"):
                    imported_data = json.load(uploaded_file)
                elif uploaded_file.name.endswith(".xlsx"):
                    imported_df = pd.read_excel(uploaded_file)
                    imported_data = imported_df.to_dict(orient="records")

                if isinstance(imported_data, list) and len(imported_data) > 0:
                    save_data(imported_data)
                    st.success(
                        "🎉 Nhập dữ liệu thành công! Hãy tải lại trang để hiển thị thông tin mới."
                    )
                    st.rerun()
                else:
                    st.error("File dữ liệu không hợp lệ hoặc rỗng!")
            except Exception as e:
                st.error(f"Lỗi khi đọc file: {e}")


# ================= TAB 8: QUẢN TRỊ (THÊM MỚI) =================
with tab_quan_tri:
    st.subheader("⚙️ Thêm Mới Thành Viên Vào Dòng Họ")

    if not st.session_state.logged_in:
        st.warning(
            "🔒 Bạn cần đăng nhập với tài khoản **Quản trị viên** hoặc **Đầu Chi** ở cột bên trái để thực hiện thêm mới thành viên."
        )
    else:
        with st.form("add_member_form"):
            new_name = st.text_input("Họ và tên thành viên mới (*):")

            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                danh_sach_doi = ["Tiên Tổ Khảo"] + [
                    f"Đời thứ {i}" for i in range(1, 21)
                ]
                new_gen = st.selectbox("Đời thứ:", danh_sach_doi)
            with col_a2:
                chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
                new_chi = st.selectbox("Thuộc Chi:", chi_options)
            with col_a3:
                has_thutu = st.checkbox(
                    "Đã rõ thứ tự sinh?",
                    value=False,
                    help="Bỏ chọn nếu chưa rõ con thứ mấy",
                )
                new_thutu = st.number_input(
                    "Thứ tự ra đời (Con thứ):",
                    min_value=1,
                    max_value=50,
                    value=1,
                    disabled=not has_thutu,
                )

            danh_sach_cha = ["-- Không có / Chưa rõ --"]
            mapping_h = {}
            for _, r in df.iterrows():
                fname = str(r.get("fullName", "")).strip()
                fgen = str(r.get("generation", "")).strip()
                fchi = str(r.get("chi", "")).strip()
                if fname:
                    display_str = f"{fname} ({fgen} - {fchi})"
                    danh_sach_cha.append(display_str)
                    mapping_h[display_str] = fname

            new_father_select = st.selectbox("Chọn Phụ thân (Cha):", danh_sach_cha)
            new_spouse = st.text_input("Vợ/Chồng (Phối):")
            new_notes = st.text_area("Tiểu sử / Ghi chú / Nơi an táng:")
            new_image_url = st.text_input(
                "Đường dẫn ảnh chân dung (URL hình ảnh - Không bắt buộc):"
            )

            submitted = st.form_submit_button("➕ Thêm Thành Viên Mới")

            if submitted:
                if not new_name.strip():
                    st.error("Vui lòng nhập họ và tên thành viên!")
                else:
                    final_father_name = (
                        ""
                        if new_father_select == "-- Không có / Chưa rõ --"
                        else mapping_h.get(new_father_select, "")
                    )
                    import time

                    new_id = str(int(time.time()))
                    final_thutu = int(new_thutu) if has_thutu else None

                    new_record = {
                        "id": new_id,
                        "fullName": new_name.strip(),
                        "generation": new_gen,
                        "chi": new_chi,
                        "birthYear": "",
                        "deathAnniversary": "",
                        "location": "",
                        "profession": "",
                        "spouse": new_spouse.strip(),
                        "father": final_father_name,
                        "thuTu": final_thutu,
                        "notes": new_notes.strip(),
                        "imageUrl": new_image_url.strip(),
                    }

                    current_data = load_data()
                    if isinstance(current_data, list):
                        current_data.append(new_record)
                    else:
                        current_data = [new_record]

                    save_data(current_data)
                    st.success(
                        f"🎉 Đã thêm thành công thành viên: **{new_name}** vào phả ký!"
                    )
                    st.rerun()

import json
import os
import re
import pandas as pd
import streamlit as st

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI", page_icon="🌳", layout="wide"
)

# --- CSS TÙY CHỈNH GIAO DIỆN & KHUNG SÁCH IN A4 CHUẨN XÁC ---
st.markdown(
    """
    <style>
        .header-container {
            background: linear-gradient(135deg, #795548 0%, #4e342e 100%);
            padding: 25px 30px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-title {
            font-size: 32px;
            font-weight: bold;
            margin: 0;
            letter-spacing: 1px;
        }
        .header-subtitle {
            font-size: 15px;
            color: #d7ccc8;
            margin-top: 5px;
        }
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        .gen-badge {
            background-color: #ffecb3;
            color: #e65100;
            padding: 6px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 15px;
            display: inline-block;
            border: 2px solid #ffb300;
            margin: 15px 0 10px 0;
        }
        .intro-container {
            background-color: #fffdf9;
            border: 1px solid #e0d0c0;
            padding: 40px;
            border-radius: 10px;
            margin-top: 25px;
            line-height: 1.8;
            font-family: "Times New Roman", serif;
            font-size: 16px;
            color: #2c2c2c;
            text-align: justify;
        }
        /* ĐỊNH DẠNG TRANG SÁCH A4 CHUẨN */
        .book-page {
            background-color: #ffffff;
            border: 3px double #795548;
            padding: 50px 60px;
            margin: 30px auto;
            max-width: 800px;
            min-height: 1050px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-family: "Times New Roman", serif;
            font-size: 16px;
            color: #222222;
            text-align: justify;
            line-height: 1.8;
            box-sizing: border-box;
            page-break-after: always;
            position: relative;
        }
        @media print {
            body { background: white; margin: 0; }
            .stSidebar, .stTabs, .header-container, button, header, footer { display: none !important; }
            .book-page { 
                border: 3px double #795548 !important; 
                padding: 40px 50px !important; 
                margin: 0 !important; 
                width: 100% !important; 
                max-width: 100% !important; 
                min-height: 100vh !important;
                box-shadow: none !important; 
                page-break-after: always;
                page-break-inside: avoid;
            }
        }
    </style>
""",
    unsafe_allow_html=True,
)


# --- HÀM HỖ TRỢ XỬ LÝ DỮ LIỆU & SẮP XẾP CHUẨN XÁC ---
def get_gen_number(gen_str):
    if not isinstance(gen_str, str):
        return 999
    s_lower = gen_str.lower()
    if "tiên tổ" in s_lower or "gốc" in s_lower or "thủy tổ" in s_lower:
        return 0
    match = re.search(r"\d+", gen_str)
    return int(match.group()) if match else 999


def normalize_generation(gen_str):
    if not isinstance(gen_str, str):
        return str(gen_str)
    s_lower = gen_str.lower()
    if "tiên tổ" in s_lower or "gốc" in s_lower:
        return "Tiên Tổ Khảo"
    num = get_gen_number(gen_str)
    if num != 999 and num > 0:
        return f"Đời thứ {num}"
    return gen_str.strip()


def normalize_chi(chi_str):
    if not isinstance(chi_str, str):
        return "Khác"
    s = chi_str.strip()
    mapping = {
        "Chi I": "Chi 1",
        "Chi II": "Chi 2",
        "Chi III": "Chi 3",
        "Chi IV": "Chi 4",
        "Chi V": "Chi 5",
        "Chi 1": "Chi 1",
        "Chi 2": "Chi 2",
        "Chi 3": "Chi 3",
        "Chi 4": "Chi 4",
        "Chi 5": "Chi 5",
        "Gốc": "Gốc",
    }
    return mapping.get(s, s)


@st.cache_data
def load_data():
    filename = "GiaPha_DongHoNguyen.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_data(data):
    with open("GiaPha_DongHoNguyen.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.cache_data.clear()


raw_data = load_data()

if isinstance(raw_data, list) and len(raw_data) > 0:
    df = pd.DataFrame(raw_data)
elif isinstance(raw_data, dict):
    possible_keys = [k for k, v in raw_data.items() if isinstance(v, list)]
    if possible_keys:
        df = pd.DataFrame(raw_data[possible_keys[0]])
    else:
        df = pd.DataFrame([raw_data])
else:
    df = pd.DataFrame(
        columns=[
            "id",
            "fullName",
            "generation",
            "chi",
            "birthYear",
            "deathAnniversary",
            "location",
            "profession",
            "spouse",
            "father",
            "notes",
            "imageUrl",
        ]
    )

if not df.empty:
    if "hoTen" in df.columns and "fullName" not in df.columns:
        df["fullName"] = df["hoTen"]
    if "doi" in df.columns and "generation" not in df.columns:
        df["generation"] = df["doi"]

    if "generation" in df.columns:
        df["generation"] = df["generation"].apply(normalize_generation)
    if "chi" in df.columns:
        df["chi"] = df["chi"].apply(normalize_chi)
    if "father" not in df.columns:
        df["father"] = ""
    if "imageUrl" not in df.columns:
        df["imageUrl"] = ""

    if "id" not in df.columns:
        df["id"] = [str(i + 1000) for i in range(len(df))]

    if "_original_index" not in df.columns:
        df["_original_index"] = range(len(df))

# --- THANH ĐĂNG NHẬP & PHÂN QUYỀN (SIDEBAR) ---
st.sidebar.markdown("## 🔐 Cổng Đăng Nhập Phân Quyền")

ACCOUNTS = {
    "admin": {"pass": "admin123", "role": "Admin", "chi": "Tất cả"},
    "chi1": {"pass": "chi123", "role": "Đầu Chi", "chi": "Chi 1"},
    "chi2": {"pass": "chi123", "role": "Đầu Chi", "chi": "Chi 2"},
    "chi3": {"pass": "chi123", "role": "Đầu Chi", "chi": "Chi 3"},
    "chi4": {"pass": "chi123", "role": "Đầu Chi", "chi": "Chi 4"},
    "chi5": {"pass": "chi123", "role": "Đầu Chi", "chi": "Chi 5"},
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "Khách"
    st.session_state.chi = "Không"

if not st.session_state.logged_in:
    with st.sidebar.form("login_form"):
        username_input = st.text_input("Tên đăng nhập:")
        password_input = st.text_input("Mật khẩu:", type="password")
        submit_login = st.form_submit_button("Đăng Nhập")

        if submit_login:
            if (
                username_input in ACCOUNTS
                and ACCOUNTS[username_input]["pass"] == password_input
            ):
                st.session_state.logged_in = True
                st.session_state.username = username_input
                st.session_state.role = ACCOUNTS[username_input]["role"]
                st.session_state.chi = ACCOUNTS[username_input]["chi"]
                st.success(f"Đăng nhập thành công với quyền: {st.session_state.role}!")
                st.rerun()
            else:
                st.error("Sai tên đăng nhập hoặc mật khẩu!")
else:
    st.sidebar.success(
        f"👤 Đang đăng nhập: **{st.session_state.username}**"
        f" ({st.session_state.role} - {st.session_state.chi})"
    )
    if st.sidebar.button("Đăng Xuất"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = "Khách"
        st.session_state.chi = "Không"
        st.rerun()

st.sidebar.markdown("---")

# --- HEADER ỨNG DỤNG ---
st.markdown(
    """
    <div class="header-container">
        <div class="header-title">NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI</div>
        <div class="header-subtitle">Thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- MENU ĐIỀU HƯỚNG ---
tabs = st.tabs([
    "🏠 Tổng Quan",
    "📋 Danh Sách & Quản Trị Trực Tiếp",
    "🌳 Cây Phả Hệ (Dạng Đứng)",
    "🌳 Cây Phả Hệ (Hàng Ngang Chi Tiết)",
    "📖 In Cuốn Gia Phả",
    "💾 Xuất Dữ Liệu",
    "📥 Nhập Dữ Liệu",
    "⚙️ Quản Trị (Thêm Mới)",
])

tab_tong_quan = tabs[0]
tab_danh_sach = tabs[1]
tab_so_do_doi = tabs[2]
tab_so_do_cot = tabs[3]
tab_in_phu = tabs[4]
tab_xuat = tabs[5]
tab_nhap = tabs[6]
tab_quan_tri = tabs[7]


# --- HÀM HIỂN THỊ NỘI DUNG LỜI TỰA ---
def render_loi_tua():
    st.markdown(
        "<h2 style='color: #795548; text-align: center; margin-top: 0;'>📜 NGUYỄN TỘC PHẢ KÝ</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Họ hàng và gia đình có phả ký cũng giống như đất nước có sử sách. Các cụ ngày xưa đã nói:"
    )
    st.markdown(
        """
    <div style="text-align: center; font-weight: bold; margin: 10px 0;">
        Nhân do hồ tổ<br>
        Mộc do hồ bản<br>
        Thủy do hồ nguyên.
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("**Đại ý như sau:**")
    st.markdown(
        "- Người phải có tổ\n- Cây phải có gốc\n- Nước phải có nguồn\n- Người phải có hàng xóm láng giềng...."
    )
    st.markdown("Hoặc cũng có câu thơ như sau:")
    st.markdown(
        """
    <div style="text-align: center; font-style: italic; margin: 10px 0;">
        Cây có gốc mới nở cành sinh ngọn<br>
        Nước có nguồn mới bể rộng sông sâu<br>
        Người ta có nguồn gốc từ đâu<br>
        Có tổ tiên trước rồi sau có mình.
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "Như vậy việc biên soạn, sao chép lại quá trình hình thành và phát triển của họ NGUYỄN ở thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa là một việc rất cần thiết và quan trọng. Để tỏ lòng thành kính tưởng nhớ tới công ơn của các bậc tổ tiên dòng họ Nguyễn, những người đã có công sinh thành và phát triển dòng họ."
    )
    st.markdown(
        "Kể từ khi cố Thủy tổ từ bản tộc Tiên Tổ ở Hải Dương Tỉnh, Nam Sách Phủ, Tuyên Minh huyện, An Đô Hạ xã. Ban đầu đi di cư vào tại bản tỉnh Hà Trung phủ, Hoàng Hóa huyện, Dương Sơn xã, Đại Yên thôn. Sinh cơ lập nghiệp (Thiết tương triệu cơ) Nghĩa là làm nghề thợ rèn. Sau đó chuyển lên Hội Hiền Thôn, Phúc Trạch xã, vào thời cố Chính Hòa (1680 – 1704). Tính đến nay đã gần 300 năm. Đã có 15 đời nối tiếp, hình thành 5 chi, có trên 100 hộ, là một trong những họ đông nhất của làng."
    )
    st.markdown(
        "Do thời cuộc nhất là sau cách mạng tháng tám năm 1945 đến nay có nhiều hộ, nhiều cá nhân trong dòng họ đã thoát ly đi xây dựng vùng kinh tế mới, đi công tác, học tập và chiến đấu ở nhiều vùng trên mọi miền đất nước. Các thế hệ có những anh dũng hy sinh cho sự nghiệp giải phóng dân tộc và bảo vệ Tổ quốc, nhất là thời kỳ đế quốc phong kiến ông cha ta đã tham gia các phong trào, Hội Ái Nghĩa, Hội Tương Tế, hướng nghiệp, Thanh niên Cách Mạng Đồng Chí Hội....."
    )
    st.markdown(
        "Có nhiều gia đình được Nhà nước tặng Bằng Khen Gia đình có công với nước. Bảng Vàng Danh Dự. Gia đình vẻ vang, có nhiều cá nhân được tặng huân huy chương và các phần thưởng cao quý khác."
    )
    st.markdown(
        "Càng nghiên cứu tìm hiểu về cội nguồn gốc tích tôn thống Nguyễn tộc, thân thế và sự nghiệp của ông cha ta chúng ta càng tự hào về quá khứ và hiện tại như bức đại tự ở nhà thờ đã nêu:"
    )
    st.markdown(
        "<div style='text-align: center; font-weight: bold; color: #b71c1c; margin: 10px 0;'>KÍNH NHƯ TẠI</div>",
        unsafe_allow_html=True,
    )
    st.markdown("Và hai câu đối:")
    st.markdown(
        """
    <div style="text-align: center; font-style: italic; margin: 8px 0;">
        Cương thường chi trậu ngất trung thiên<br>
        Bản thế vi niên tử tôn sinh.
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("Hoặc hai câu đối ở cột cạnh bức bình phong ở sân cũng ghi")
    st.markdown(
        """
    <div style="text-align: center; font-style: italic; margin: 8px 0;">
        Nhân nghĩa căn cơ tùy vĩnh thế<br>
        Cương thường đề trậu ngất trung thiên
    </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align: center; font-weight: bold; margin: 10px 0;'>Thật vậy<br>Tổ tông công đức bao trùm hậu thế<br>Con cháu muôn đời không sao quên được</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Vì thế theo nguyện vọng chung xây dựng và giữ vững tôn thống NGUYỄN TỘC là trách nhiệm và nghĩa vụ của mỗi thành viên trong dòng họ. Do đó ngày 25-02-1990 tức là ngày Xuân Kỵ ngày 01 tháng 02 năm Canh Ngọ các ông đầu chi và các cụ cao tuổi trong họ đã họp tại nhà ông Nguyễn Văn Chơn (nhà thờ của họ) dưới sự chủ trì của ông Nguyễn Văn Hiếu trưởng họ, đã họp bàn nhiều việc trong đó có việc viết gia phả và thành lập ban soạn dịch, tìm hiểu để viết lại gia phả, y sao lại bản chính của các cụ để lại là quan trọng. Phải nói đây là cuộc họp có nhiều ý nghĩa của cả họ."
    )
    st.markdown(
        "Ngày 11-03-1990 tức ngày 15 tháng 02 năm Canh Ngọ ban viết gia phả gồm có các ông sau: <b>Nguyễn Văn Hiếu, Nguyễn Văn Nghĩa, Nguyễn Hoàng Biền, Nguyễn Văn Yên, Nguyễn Công Thăng</b>. và lên kế hoạch tiến hành dịch và viết phấn đấu đến Đông chí phải hoàn thành tập NGUYỄN TỘC PHẢ KÝ.",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Tập NGUYỄN TỘC PHẢ KÝ này được viết căn cứ vào các tư liệu sau đây: Dịch từ chữ Hán cuốn phả ký của cố Nguyễn Hoàng Cừ sao chép trước lúc đi thi nhưng chỉ được đến đời thứ tám và các quyển viết tay bằng chữ Quốc ngữ của ông NGỌC MƠN (cố Vợi), NGỌC HIỆP, các ông trưởng chi một VĂN HIẾU, TRƯỜNG AN, và các ông cao tuổi trong họ cung cấp đồng thời có sự giúp đỡ của các ông ĐOÀN ĐỈNH, ÔNG TÂM, CỤ GIÁO CHINH, ÔNG PHÓ ĐIỀN Nam Giang và tra khảo các gia phả khác của các dòng họ có liên quan, đến tận các gia đình trong dòng họ để ghi chép lại."
    )
    st.markdown(
        "Do những hạn chế trong việc sưu tầm, biên soạn cũng như sự hiểu biết nên việc biên soạn chắc chắn không tránh khỏi những thiếu sót, rất mong được sự đóng góp và bổ sung ý kiến của các Cụ, Ông, Bà, con cháu trong và ngoài dòng họ để các lần tái bản sau được đầy đủ rõ ràng hơn. Mãi tới Đông chí năm 2013 (Quý Tỵ) con cháu mới sao chép, biên soạn lại được tập NGUYỄN TỘC PHẢ KÝ này với đầy đủ ý nghĩa và hy vọng nó sẽ tiếp thêm sức mạnh cho dòng họ Nguyễn để có những thắng lợi mới, góp phần vào sự phát triển của dòng họ cũng như góp phần cho sự phát triển của cả dân tộc."
    )
    st.markdown(
        "Trong quá trình sao viết lại không sao tránh khỏi những thiếu sót chúng tôi rất mong có sự đóng góp xây dựng chung để tập NGUYỄN TỘC PHẢ KÝ này hoàn thiện hơn."
    )
    st.markdown("Một lần nữa xin chân thành cám ơn sự đóng góp chung của các quý vị gần xa!")
    st.markdown(
        """
    <div style="text-align: right; margin-top: 20px;">
        <b>Ngày 22 tháng 12 năm 2013</b><br>
        <b>Đông Chí 20 tháng 11 năm Quý Tỵ</b>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ================= TAB 1: TỔNG QUAN =================
with tab_tong_quan:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""<div class="metric-card">
                  <p style="color: gray; margin: 0;">Tổng số thành viên toàn tộc</p>
                  <h2 style="color: #795548; margin: 5px 0;">{len(df)}</h2>
              </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        gen_count = (
            df["generation"].nunique()
            if not df.empty and "generation" in df.columns
            else 0
        )
        st.markdown(
            f"""<div class="metric-card">
                  <p style="color: gray; margin: 0;">Số đời đã quy tập</p>
                  <h2 style="color: #2e7d32; margin: 5px 0;">{gen_count}</h2>
              </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """<div class="metric-card">
                  <p style="color: gray; margin: 0;">Trạng thái dữ liệu</p>
                  <h4 style="color: #1976d2; margin: 8px 0;">Đã lưu tự động (Local)</h4>
              </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="intro-container">', unsafe_allow_html=True)
    render_loi_tua()
    st.markdown("</div>", unsafe_allow_html=True)

# ================= TAB 2: DANH SÁCH & QUẢN TRỊ TRỰC TIẾP =================
with tab_danh_sach:
    st.subheader("📋 Danh Sách Thành Viên & Quản Trị Hình Ảnh/Thông Tin")
    if not df.empty:
        danh_sach_thanh_vien_chi_tiet = ["-- Không có / Chưa rõ --"]
        mapping_display_to_real = {}

        df_temp = df.copy()
        df_temp["_gen_num"] = df_temp["generation"].apply(get_gen_number)
        df_temp = df_temp.sort_values(by=["_gen_num", "_original_index"])
        for _, r in df_temp.iterrows():
            fname = str(r.get("fullName", "")).strip()
            fgen = str(r.get("generation", "")).strip()
            fchi = str(r.get("chi", "")).strip()
            if fname:
                display_str = f"{fname} ({fgen} - {fchi})"
                danh_sach_thanh_vien_chi_tiet.append(display_str)
                mapping_display_to_real[display_str] = fname

        df_sorted = df.copy()
        df_sorted["_gen_num"] = df_sorted["generation"].apply(get_gen_number)
        df_sorted = df_sorted.sort_values(by=["_gen_num", "_original_index"]).drop(
            columns=["_gen_num"]
        )

        search_key = st.text_input("🔍 Tìm kiếm theo tên thành viên:", key="search_list_v4")
        filtered_df = df_sorted.copy()
        if search_key and "fullName" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["fullName"].str.contains(search_key, case=False, na=False)
            ]

        if "editing_id" not in st.session_state:
            st.session_state.editing_id = None

        for _, row in filtered_df.iterrows():
            m_id = str(row.get("id", ""))
            name = row.get("fullName", "Chưa rõ")
            gen = row.get("generation", "")
            chi = row.get("chi", "")
            father = (
                row.get("father", "")
                if pd.notna(row.get("father")) and row.get("father") != ""
                else "Chưa rõ"
            )
            spouse = (
                row.get("spouse", "")
                if pd.notna(row.get("spouse")) and row.get("spouse") != ""
                else "Chưa rõ"
            )

            col_i1, col_i2, col_i3 = st.columns([1, 4, 2])
            with col_i1:
                img_url = str(row.get("imageUrl", "")).strip()
                if img_url.startswith(("http://", "https://", "data:image/")):
                    try:
                        st.image(img_url, width=70)
                    except Exception:
                        st.markdown("👤 *Lỗi tải ảnh*")
                else:
                    st.markdown("👤 *Chưa có ảnh*")
            with col_i2:
                st.markdown(f"**👤 {name}** (`{gen}` - **{chi}**)")
                st.caption(f"Cha: {father} | Phối: {spouse}")
            with col_i3:
                if st.session_state.logged_in:
                    if st.button("✏️ Sửa / Cập Nhật Ảnh", key=f"edit_{m_id}"):
                        st.session_state.editing_id = m_id
                        st.rerun()
                else:
                    st.caption("🔒 Cần đăng nhập")

            if st.session_state.editing_id == m_id:
                with st.form(key=f"form_inline_{m_id}"):
                    st.markdown(f"#### ✏️ Cập nhật chi tiết & Ảnh cho: **{name}**")
                    e_name = st.text_input("Họ và tên:", value=name)
                    danh_sach_doi = ["Tiên Tổ Khảo"] + [
                        f"Đời thứ {i}" for i in range(1, 21)
                    ]
                    e_idx = (
                        danh_sach_doi.index(gen) if gen in danh_sach_doi else 0
                    )
                    e_gen = st.selectbox("Đời thứ:", danh_sach_doi, index=e_idx)
                    chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
                    c_idx = (
                        chi_options.index(chi) if chi in chi_options else 5
                    )
                    e_chi = st.selectbox("Thuộc Chi:", chi_options, index=c_idx)

                    current_father = str(father if father != "Chưa rõ" else "")
                    f_idx = 0
                    for idx, item in enumerate(danh_sach_thanh_vien_chi_tiet):
                        if item.startswith(current_father + " ("):
                            f_idx = idx
                            break
                    e_father_select = st.selectbox(
                        "Chọn Cha:", danh_sach_thanh_vien_chi_tiet, index=f_idx
                    )
                    e_spouse = st.text_input(
                        "Vợ/Chồng (Phối):",
                        value=str(spouse if spouse != "Chưa rõ" else ""),
                    )
                    e_image = st.text_input(
                        "Đường dẫn hình ảnh (URL ảnh chân dung/di ảnh):",
                        value=str(row.get("imageUrl", "")),
                    )
                    e_notes = st.text_area(
                        "Tiểu sử / Nơi an táng / Ghi chú thêm:",
                        value=str(
                            row.get("notes", "")
                            if pd.notna(row.get("notes"))
                            else ""
                        ),
                    )

                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        sub_save = st.form_submit_button("💾 Lưu Thay Đổi")
                    with f_col2:
                        sub_cancel = st.form_submit_button("❌ Hủy Bỏ")

                    if sub_save:
                        final_father = (
                            ""
                            if e_father_select == "-- Không có / Chưa rõ --"
                            else mapping_display_to_real.get(e_father_select, "")
                        )
                        df.loc[df["id"] == m_id, "fullName"] = e_name.strip()
                        df.loc[df["id"] == m_id, "generation"] = e_gen
                        df.loc[df["id"] == m_id, "chi"] = e_chi
                        df.loc[df["id"] == m_id, "father"] = final_father
                        df.loc[df["id"] == m_id, "spouse"] = e_spouse.strip()
                        df.loc[df["id"] == m_id, "imageUrl"] = e_image.strip()
                        df.loc[df["id"] == m_id, "notes"] = e_notes.strip()
                        save_data(
                            df.drop(
                                columns=["_original_index"], errors="ignore"
                            ).to_dict(orient="records")
                        )
                        st.session_state.editing_id = None
                        st.success(
                            f"Cập nhật thành công thành viên: {e_name}!"
                        )
                        st.rerun()
                    if sub_cancel:
                        st.session_state.editing_id = None
                        st.rerun()
            st.markdown(
                "<hr style='margin: 5px 0 15px 0; border-top: 1px solid #eee;'>",
                unsafe_allow_html=True,
            )

# ================= TAB 3: CÂY PHẢ HỆ (DẠNG ĐỨNG) =================
with tab_so_do_doi:
    st.subheader("🌳 Cây Phả Hệ Trực Quan - Dạng Đứng")
    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        for gen in sorted_gens:
            st.markdown(f"### 📌 {gen}")
            gen_members = df[df["generation"] == gen].sort_values(
                by="_original_index"
            )
            fathers = gen_members["father"].dropna().unique()
            for f in fathers:
                father_display = (
                    f if f and str(f).strip() != "" else "Tiên Tổ / Chưa rõ phụ thân"
                )
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;<b>└─ Phụ thân: {father_display}</b>",
                    unsafe_allow_html=True,
                )
                children = gen_members[gen_members["father"] == f]
                for _, row in children.iterrows():
                    name = row.get("fullName", "Chưa rõ")
                    chi = row.get("chi", "Chưa rõ")
                    spouse = row.get("spouse", "Chưa rõ")
                    st.markdown(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• <b>{name}</b> &nbsp;|&nbsp; <span style='color: #666; font-size: 13px;'>Chi: {chi} | Phối: {spouse}</span>",
                        unsafe_allow_html=True,
                    )
            st.markdown("---")

# ================= TAB 4: CÂY PHẢ HỆ (HÀNG NGANG CHI TIẾT) =================
with tab_so_do_cot:
    st.markdown(
        "<div style='text-align: center;'><h2 style='color: #2e7d32;'>🌳 SƠ ĐỒ CÂY PHẢ HỆ HÀNG NGANG CHI TIẾT</h2></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #555;'>Mỗi thẻ thành viên được hiển thị rộng rãi, tích hợp hình ảnh chân dung, thông tin phối ngẫu, phần mộ và tiểu sử trọn vẹn.</p>",
        unsafe_allow_html=True,
    )

    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        for gen in sorted_gens:
            is_root_gen = get_gen_number(gen) == 0
            badge_label = "TIÊN TỔ KHẢO" if is_root_gen else gen.upper()
            st.markdown(
                f"<div style='text-align: center;'><span class='gen-badge'>{badge_label}</span></div>",
                unsafe_allow_html=True,
            )

            gen_members = df[df["generation"] == gen].sort_values(
                by="_original_index"
            )
            if not gen_members.empty:
                members_list = gen_members.to_dict(orient="records")
                for i in range(0, len(members_list), 2):
                    batch = members_list[i : i + 2]
                    cols = st.columns(len(batch))
                    for col_idx, row in enumerate(batch):
                        with cols[col_idx]:
                            name = row.get("fullName", "Chưa rõ")
                            chi = row.get("chi", "Gốc")
                            spouse_text = (
                                f"Phối: {row.get('spouse')}"
                                if pd.notna(row.get("spouse"))
                                and str(row.get("spouse")).strip() != ""
                                else "Phối: Chưa rõ"
                            )
                            father_text = (
                                str(row.get("father"))
                                if pd.notna(row.get("father"))
                                and str(row.get("father")).strip() != ""
                                else "Chưa cập nhật"
                            )
                            img_url = str(row.get("imageUrl", "")).strip()
                            notes = (
                                str(row.get("notes", ""))
                                if pd.notna(row.get("notes"))
                                else ""
                            )

                            card_style = (
                                "background: #fff8e1; border: 2px solid #f57c00;"
                                if is_root_gen
                                else "background: #ffffff; border: 2px solid #ffa726;"
                            )
                            
                            if img_url.startswith(("http://", "https://", "data:image/")):
                                img_html = f"<img src='{img_url}' style='width: 90px; height: 110px; object-fit: cover; border-radius: 6px; border: 1px solid #ccc;'>"
                            else:
                                img_html = "<div style='width: 90px; height: 110px; background: #f0f0f0; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #888; border: 1px dashed #ccc;'>Chưa có ảnh</div>"

                            notes_html = (
                                f"<div style='font-size: 12px; color: #333; margin-top: 6px; font-style: italic; border-top: 1px dashed #e0e0e0; padding-top: 4px;'>📝 {notes}</div>"
                                if notes.strip() != ""
                                else ""
                            )

                            st.markdown(
                                f"""
                                <div style="{card_style} padding: 15px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin-bottom: 15px;">
                                    <table style="width: 100%; border: none;">
                                        <tr>
                                            <td style="width: 100px; vertical-align: middle; text-align: center; border: none; padding: 0;">
                                                {img_html}
                                            </td>
                                            <td style="vertical-align: top; padding-left: 12px; border: none;">
                                                <div style="font-weight: bold; color: #b71c1c; font-size: 17px; margin-bottom: 3px;">{name}</div>
                                                <div style="font-size: 13px; color: #e65100; font-weight: bold; margin-bottom: 3px;">Chi: {chi}</div>
                                                <div style="font-size: 12px; color: #444; margin-bottom: 3px;">💍 {spouse_text}</div>
                                                <div style="font-size: 11px; background-color: #fff3e0; color: #d84315; padding: 3px 6px; border-radius: 4px; border: 1px dashed #ffa726; display: inline-block; margin-top: 2px;">⬆ Cha: {father_text}</div>
                                            </td>
                                        </tr>
                                    </table>
                                    {notes_html}
                                </div>
                            """,
                                unsafe_allow_html=True,
                            )
                st.markdown(
                    "<div style='text-align: center; margin: 15px 0;'>⬇</div>",
                    unsafe_allow_html=True,
                )

# ================= TAB 5: IN CUỐN GIA PHẢ =================
with tab_in_phu:
    st.subheader(
        "📖 Bản In Sách Gia Phả Dòng Họ (Định dạng Trang Sách A4 Trang Trọng)"
    )
    st.info(
        "💡 Bác nhấn **Ctrl + P** (hoặc **Cmd + P** trên Mac) để in thành tệp sách A4 hoàn chỉnh."
    )

    # Trang Bìa Sách A4 Cân Đối
    st.markdown(
        """
        <div class="book-page" style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
            <div style="font-size: 24px; font-weight: bold; color: #795548; margin-bottom: 20px; letter-spacing: 2px;">ĐẠI TỘC GIA PHẢ</div>
            <div style="font-size: 40px; font-weight: bold; color: #4e342e; text-transform: uppercase; margin-bottom: 20px; line-height: 1.2;">NGUYỄN TỘC PHẢ KÝ</div>
            <div style="font-size: 22px; font-weight: bold; color: #5d4037; margin-bottom: 40px;">TOÀN TỘC 5 CHI</div>
            <hr style="width: 40%; margin: 20px auto; border-top: 2px solid #795548;">
            <div style="font-size: 16px; color: #444; margin-top: 60px; line-height: 2;">
                <b>Địa chỉ dòng họ:</b> Thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa<br>
                <b>Nguyên quán Thủy tổ:</b> Hải Dương tỉnh, Nam Sách phủ, Tuyên Minh huyện, An Đô Hạ xã<br>
                <i style="margin-top: 30px; display: block; font-size: 17px; color: #795548;">Lưu truyền đời đời cho con cháu muôn phương</i>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Trang Lời Tựa Trong Sách
    st.markdown('<div class="book-page">', unsafe_allow_html=True)
    render_loi_tua()
    st.markdown("</div>", unsafe_allow_html=True)

    # Các Trang Nội Dung Phả Hệ Theo Đời Trong Sách In
    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        for gen in sorted_gens:
            gen_members = df[df["generation"] == gen].sort_values(
                by="_original_index"
            )
            members_html = ""
            for _, r in gen_members.iterrows():
                name = r.get("fullName", "Chưa rõ")
                chi = r.get("chi", "Gốc")
                father = r.get("father", "Chưa rõ")
                spouse = r.get("spouse", "Chưa rõ")
                notes = r.get("notes", "")

                father_str = (
                    f" | Cha: {father}"
                    if father and str(father).strip() != ""
                    else ""
                )
                spouse_str = (
                    f" | Phối: {spouse}"
                    if spouse and str(spouse).strip() != ""
                    else ""
                )
                notes_str = (
                    f"<br><span style='font-size: 14px; font-style: italic; color: #555;'>Tiểu sử / Phần mộ: {notes}</span>"
                    if notes and str(notes).strip() != ""
                    else ""
                )

                members_html += f"<li style='margin-bottom: 14px;'><b>{name}</b> <span style='color: #b71c1c; font-size: 14px;'>[{chi}]</span>{father_str}{spouse_str}{notes_str}</li>"

            st.markdown(
                f"""
                <div class="book-page">
                    <div style="text-align: center; border-bottom: 2px solid #795548; padding-bottom: 15px; margin-bottom: 30px;">
                        <h2 style="color: #795548; margin: 0; text-transform: uppercase;">{gen}</h2>
                        <p style="font-size: 14px; color: #666; margin: 5px 0 0 0;">(Ghi chép các bậc tiền nhân và hậu duệ)</p>
                    </div>
                    <ul style="line-height: 1.9; font-size: 16px; padding-left: 20px;">
                        {members_html}
                    </ul>
                </div>
            """,
                unsafe_allow_html=True,
            )

# ================= TAB 6: XUẤT DỮ LIỆU =================
with tab_xuat:
    st.subheader("💾 Xuất Dữ Liệu Gia Phả (Backup)")
    if not df.empty:
        json_str = df.drop(columns=["_original_index"], errors="ignore").to_json(
            orient="records", force_ascii=False
        )
        st.download_button(
            label="📥 Tải xuống tệp JSON gia phả",
            data=json_str.encode("utf-8"),
            file_name="GiaPha_DongHoNguyen.json",
            mime="application/json",
        )

# ================= TAB 7: NHẬP DỮ LIỆU =================
with tab_nhap:
    st.subheader("📥 Nhập Dữ Liệu Gia Phả Mới")
    uploaded_file = st.file_uploader("Chọn tệp JSON gia phả:", type=["json"])
    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)
            if isinstance(imported_data, list):
                save_data(imported_data)
                st.success("Nhập dữ liệu thành công! Hãy tải lại trang.")
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi: {e}")

# ================= TAB 8: QUẢN TRỊ (THÊM MỚI) =================
with tab_quan_tri:
    st.subheader("⚙️ Thêm Thành Viên Mới Vào Dòng Họ")
    if st.session_state.logged_in:
        with st.form("add_member_form"):
            new_name = st.text_input("Họ và tên thành viên mới:")
            danh_sach_doi = ["Tiên Tổ Khảo"] + [
                f"Đời thứ {i}" for i in range(1, 21)
            ]
            new_gen = st.selectbox("Đời thứ:", danh_sach_doi)
            chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
            new_chi = st.selectbox("Thuộc Chi:", chi_options)

            danh_sach_cha = ["-- Không có / Chưa rõ --"]
            if not df.empty:
                for _, r in df.iterrows():
                    danh_sach_cha.append(
                        f"{r.get('fullName', '')} ({r.get('generation', '')} - {r.get('chi', '')})"
                    )

            new_father_select = st.selectbox(
                "Chọn Phụ Thân (Cha):", danh_sach_cha
            )
            new_spouse = st.text_input("Vợ/Chồng (Phối):")
            new_image = st.text_input(
                "Đường dẫn hình ảnh (URL ảnh chân dung/di ảnh):"
            )
            new_notes = st.text_area("Tiểu sử / Nơi an táng / Ghi chú thêm:")
            submit_add = st.form_submit_button("➕ Thêm Thành Viên")

            if submit_add:
                if not new_name.strip():
                    st.error("Vui lòng nhập họ và tên thành viên!")
                else:
                    final_new_father = (
                        ""
                        if new_father_select == "-- Không có / Chưa rõ --"
                        else new_father_select.split(" (")[0]
                    )
                    new_member = {
                        "id": str(int(pd.Timestamp.now().timestamp())),
                        "fullName": new_name.strip(),
                        "generation": new_gen,
                        "chi": new_chi,
                        "birthYear": "",
                        "deathAnniversary": "",
                        "location": "",
                        "profession": "",
                        "spouse": new_spouse.strip(),
                        "father": final_new_father,
                        "notes": new_notes.strip(),
                        "imageUrl": new_image.strip(),
                    }
                    current_list = (
                        df.drop(
                            columns=["_original_index"], errors="ignore"
                        ).to_dict(orient="records")
                        if not df.empty
                        else []
                    )
                    current_list.append(new_member)
                    save_data(current_list)
                    st.success(
                        f"Đã thêm thành công thành viên: {new_name}!"
                    )
                    st.rerun()
    else:
        st.warning(
            "🔒 Vui lòng đăng nhập ở thanh bên trái để thêm thành viên mới."
        )

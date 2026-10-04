import json
import os
import re
import pandas as pd
import streamlit as st

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI", page_icon="🌳", layout="wide"
)

# --- CSS TÙY CHỈNH GIAO DIỆN & KHUNG SÁCH IN A4 ---
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
            padding: 30px;
            border-radius: 10px;
            margin-top: 25px;
            line-height: 1.8;
            font-family: serif;
            color: #2c2c2c;
        }
        .han-nom-box {
            background-color: #f5f5f5;
            border-left: 4px solid #795548;
            padding: 15px;
            margin: 15px 0;
            font-style: italic;
        }

        /* --- GIAO DIỆN KHUNG TRANG SÁCH A4 CHO BẢN IN --- */
        .book-page {
            background-color: #ffffff;
            border: 3px double #795548;
            padding: 50px 60px;
            margin: 20px auto;
            max-width: 850px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-family: "Times New Roman", serif;
            color: #222222;
            line-height: 1.7;
        }
        .book-cover {
            text-align: center;
            padding: 60px 20px;
            border: 5px double #4e342e;
            background: #fffdf9;
        }
        .book-title {
            font-size: 28px;
            font-weight: bold;
            color: #795548;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        .book-subtitle {
            font-size: 18px;
            font-weight: bold;
            color: #5d4037;
            margin-bottom: 30px;
        }
        .chapter-title {
            font-size: 22px;
            font-weight: bold;
            color: #4e342e;
            text-align: center;
            margin: 30px 0 20px 0;
            text-transform: uppercase;
            border-bottom: 2px solid #d7ccc8;
            padding-bottom: 8px;
        }
        .member-print-box {
            border-bottom: 1px dashed #d7ccc8;
            padding: 15px 0;
            margin-bottom: 10px;
        }
        
        @media print {
            body { background: white; }
            .stSidebar, .stTabs, .header-container, button { display: none !important; }
            .book-page { border: none; padding: 0; box-shadow: none; margin: 0; width: 100%; max-width: 100%; }
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
    # Tự động quét tìm file JSON thực tế trên kho chứa
    possible_files = ["GiaPha_DongHoNguyen(5).json", "GiaPha_DongHoNguyen.json", "data.json"]
    for filename in possible_files:
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return []


def save_data(data):
    filename = "GiaPha_DongHoNguyen(5).json"
    with open(filename, "w", encoding="utf-8") as f:
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
    "🌳 Cây Phả Hệ (Hàng Ngang)",
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

    # --- NỘI DUNG LỜI TỰA & PHẢ KÝ ---
    st.markdown(
        """
<div class="intro-container">

<h2 style="color: #795548; text-align: center; margin-bottom: 25px;">📜 LỜI TỰA & LỊCH SỬ DÒNG HỌ NGUYỄN TỘC</h2>

Họ hàng và gia đình có phả ký cũng giống như đất nước có sử sách. Các cụ ngày xưa đã nói:
* **Nhân do hồ tổ**
* **Mộc do hồ bản**
* **Thủy do hồ nguyên**

**Đại ý như sau:**
* Người phải có tổ
* Cây phải có gốc
* Nước phải có nguồn

Hoặc cũng có câu thơ như sau:
> *Cây có gốc mới nở cành sinh ngọn*  
> *Nước có nguồn mới bể rộng sông sâu*  
> *Người ta có nguồn gốc từ đâu*  
> *Có tổ tiên trước rồi sau có mình.*

Như vậy việc biên soạn, sao chép lại quá trình hình thành và phát triển của họ **NGUYỄN** ở thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa là một việc rất cần thiết và quan trọng. Để tỏ lòng thành kính tưởng nhớ tới công ơn của các bậc tổ tiên dòng họ Nguyễn, những người đã có công sinh thành và phát triển dòng họ.

Kể từ khi cố Thủy tổ từ bản tộc Tiên Tổ ở Hải Dương Tỉnh, Nam Sách phủ, Tuyên Minh huyện, An Đô Hạ xã. Ban đầu di cư vào tại bản tỉnh Hà Trung phủ, Hoàng Hóa huyện, Dương Sơn xã, Đại Yên thôn. Sinh cơ lập nghiệp (Thiết tương triệu cơ) nghĩa là làm nghề thợ rèn. Sau đó chuyển lên Hội Hiền thôn, Phúc Trạch xã, vào thời cố Cảnh Hưng / Chính Hòa (1680 – 1704). Tính đến nay đã gần 300 năm, đã có 15 đời nối tiếp, hình thành 5 chi, có trên 100 hộ, là một trong những họ đông nhất của làng.

Do thời cuộc nhất là sau Cách mạng Tháng Tám năm 1945 đến nay có nhiều hộ, nhiều cá nhân trong dòng họ đã thoát ly đi xây dựng vùng kinh tế mới, đi công tác, học tập và chiến đấu ở nhiều vùng trên mọi miền đất nước. Các thế hệ có những anh dũng hy sinh cho sự nghiệp giải phóng dân tộc và bảo vệ Tổ quốc, nhất là thời kỳ đế quốc phong kiến ông cha ta đã tham gia các phong trào, Hội Ái Nghĩa, Hội Tương Tế, hướng nghiệp, Thanh niên Cách Mạng Đồng Chí Hội...

Có nhiều gia đình được Nhà nước tặng Bằng Khen Gia đình có công với nước, Bảng Vàng Danh Dự, Gia đình vẻ vang, có nhiều cá nhân được tặng huân huy chương và các phần thưởng cao quý khác.

Càng nghiên cứu tìm hiểu về cuội nguồn gốc tích tôn thống Nguyễn tộc, thân thế và sự nghiệp của ông cha ta chúng ta càng tự hào về quá khứ và hiện tại như bức đại tự ở nhà thờ đã nêu: **KÍNH NHƯ TẠI**

Và hai câu đối:
> *Cương thường chi trậu ngất trung thiên*  
> *Bản thế vi niên tử tôn sinh.*

Hoặc hai câu đối ở cột cạnh bức bình phong ở sân cũng ghi:
> *Nhân nghĩa căn cơ tùy vĩnh thế*  
> *Cương thường để trậu ngất trung thiên*

<p style="text-align: center; font-weight: bold; color: #795548; font-size: 17px; margin: 20px 0;">
Thật vậy:<br>
Tổ tông công đức bao trùm hậu thế<br>
Con cháu muôn đời không sao quên được
</p>

Vì thế theo nguyện vọng chung xây dựng và giữ vững tôn thống NGUYỄN TỘC là trách nhiệm và nghĩa vụ của mỗi thành viên trong dòng họ. Do đó ngày 25-02-1990 tức là ngày Xuân Kỵ ngày 01 tháng 02 năm Canh Ngọ các ông đầu chi và các cụ cao tuổi trong họ đã họp tại nhà ông Nguyễn Văn Chơn (nhà thờ của họ) dưới sự chủ trì của ông Nguyễn Văn Hiếu trưởng họ, đã họp bàn nhiều việc trong đó có việc viết gia phả và thành lập ban soạn dịch, tìm hiểu để viết lại gia phả, y sao lại bản chính của các cụ để lại là quan trọng. Phải nói đây là cuộc họp có nhiều ý nghĩa của cả họ.

Ngày 11-03-1990 tức ngày 15 tháng 02 năm Canh Ngọ ban viết gia phả gồm có các ông sau: **Nguyễn Văn Hiếu, Nguyễn Văn Nghĩa, Nguyễn Hoàng Biền, Nguyễn Văn Yên, Nguyễn Công Thăng** và lên kế hoạch tiến hành dịch và viết phấn đấu đến Đông chí phải hoàn thành tập **NGUYỄN TỘC PHẢ KÝ**.

Tập NGUYỄN TỘC PHẢ KÝ này được viết căn cứ vào các tư liệu sau đây:  
Dịch từ chữ Hán cuốn phả ký của cố Nguyễn Hoàng Cừ sao chép trước lúc đi thi nhưng chỉ được đến đời thứ tám và các quyển viết tay bằng chữ quốc ngữ của ông Ngọc Mơn (cố Vợi), Ngọc Hiệp, các ông trưởng chi một Văn Hiếu, Trường An, và các ông cao tuổi trong họ cung cấp đồng thời có sự giúp đỡ của các ông Đoàn Đỉnh, ông Tâm, cụ Giáo Chinh, ông Phó Điền Nam Giang và tra khảo các gia phả khác của các dòng họ có liên quan, đến tận các gia đình trong dòng họ để ghi chép lại.

Do những hạn chế trong việc sưu tầm, biên soạn cũng như sự hiểu biết nên việc biên soạn chắc chắn không tránh khỏi những thiếu sót, rất mong được sự đóng góp và bổ sung ý kiến của các Cụ, Ông, Bà, con cháu trong và ngoài dòng họ để các lần tái bản sau được đầy đủ rõ ràng hơn. Mãi tới Đông chí năm 2013 (Quý Tỵ) con cháu mới sao chép, biên soạn lại được tập NGUYỄN TỘC PHẢ KÝ này với đầy đủ ý nghĩa và hy vọng nó sẽ tiếp thêm sức mạnh cho dòng họ Nguyễn để có những thắng lợi mới, góp phần vào sự phát triển của dòng họ cũng như góp phần cho sự phát triển của cả dân tộc.

<p style="text-align: right; font-style: italic;">Ngày 22 tháng 12 năm 2013<br>Đông Chí 20 tháng 11 năm Quý Tỵ</p>

---

<h4 style="color: #795548; text-align: center;">BẢN GỐC HÁN NÔM & NGUYÊN QUÁN THỦY TỔ</h4>
<p><b>Công Vẫy (Cố Phê)</b> — Từ đời Thành Thái tháng 2 năm Nhâm Thìn 1882 (Ông Nguyễn Hoàng Cừ y sao trước lúc đi thi).</p>

<div class="han-nom-box">
<b>Nguyên văn âm Hán:</b><br>
Phù mộc chi thiên kha vạn diệp / Bản ư căn<br>
Thủy chi thiên lưu vạn phái / Thủy ư nguyên<br>
Ngô nhân chi sinh khởi vô sở tự tại / Cung duy thân gia / Tiên tổ giáng sinh...<br>
<i>(Đại ý dịch nghĩa: Ôi! Cây có ngàn cành ngàn lá, gốc có rễ; Nước có ngàn dòng chảy, nước có nguồn; Người ta sinh ra cũng có nguồn gốc...)</i>
</div>

**Nguyên quán Thủy tổ:**  
Hải Dương tỉnh, Nam Sách phủ, Tuyên Minh huyện, An Đô Hạ xã.  
**Húy:** Công Tình | **Tự:** Trung Lương | **Tỷ Húy:** Thị Thịnh | **Hiệu:** Từ Tai

**Hai ông bà sinh hạ được 2 người con trai:**
1. **Trưởng húy:** Công Dinh | **Tự:** Trung Ý (Kiêm bản tộc từ đường phụng tự vi thủy tổ)
2. **Thứ húy:** Văn Tự (vô tự) | **Tự:** Trung Cương

<p style="text-align: center; font-size: 13px; color: #666; margin-top: 20px;">
<i>HOÀNG TRIỀU THÀNH THÁI TỨ NIÊN — THÁNG 2 NĂM NHÂM THÌN 1882<br>LAI TÔN THI SINH HÚY BÁI TỰ (Y sao bản chính)</i>
</p>

</div>
    """,
    unsafe_allow_html=True,
)

# ================= TAB 2: DANH SÁCH & QUẢN TRỊ TRỰC TIẾP =================
with tab_danh_sach:
    st.subheader(
        "📋 Danh Sách Thành Viên (Sắp Xếp Chuẩn Theo Đời & Thứ Tự Anh Em Trước Sau)"
    )
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
        df_sorted = df_sorted.sort_values(
            by=["_gen_num", "_original_index"]
        ).drop(columns=["_gen_num"])

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            search_key = st.text_input(
                "🔍 Tìm kiếm theo tên thành viên:", key="search_list_v3"
            )
        with col_s2:
            chi_list = (
                ["Tất cả"] + sorted(df["chi"].dropna().unique().tolist())
                if "chi" in df.columns
                else ["Tất cả"]
            )
            filter_chi = st.selectbox(
                "📂 Lọc theo Chi:", chi_list, key="filter_chi_v3"
            )

        filtered_df = df_sorted.copy()
        if search_key and "fullName" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["fullName"].str.contains(search_key, case=False, na=False)
            ]
        if filter_chi != "Tất cả" and "chi" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["chi"] == filter_chi]

        if "editing_id" not in st.session_state:
            st.session_state.editing_id = None

        if not filtered_df.empty:
            header_cols = st.columns([2.5, 1.5, 1.2, 2, 2])
            header_cols[0].markdown("**Họ và Tên**")
            header_cols[1].markdown("**Đời**")
            header_cols[2].markdown("**Chi**")
            header_cols[3].markdown("**Cha & Phối**")
            header_cols[4].markdown("**Thao Tác (Admin / Đầu Chi)**")
            st.markdown("---")

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

                row_cols = st.columns([2.5, 1.5, 1.2, 2, 2])
                with row_cols[0]:
                    st.markdown(f"**👤 {name}**")
                with row_cols[1]:
                    st.markdown(f"`{gen}`")
                with row_cols[2]:
                    st.markdown(f"**{chi}**")
                with row_cols[3]:
                    st.caption(f"Cha: {father}<br>Phối: {spouse}", unsafe_allow_html=True)
                with row_cols[4]:
                    if st.session_state.logged_in:
                        btn_c1, btn_c2 = st.columns(2)
                        with btn_c1:
                            if st.button("✏️ Sửa", key=f"edit_{m_id}"):
                                st.session_state.editing_id = m_id
                                st.rerun()
                        with btn_c2:
                            if st.button("🗑 Xóa", key=f"del_{m_id}", type="primary"):
                                if (
                                    st.session_state.role == "Admin"
                                    or st.session_state.chi == chi
                                ):
                                    df = df[df["id"] != m_id]
                                    save_data(df.drop(columns=["_original_index"], errors="ignore").to_dict(orient="records"))
                                    st.success(f"Đã xóa thành công: {name}!")
                                    st.rerun()
                                else:
                                    st.error("Bạn chỉ có quyền xóa thành viên thuộc Chi của mình!")
                    else:
                        st.caption("🔒 Cần đăng nhập")

                if st.session_state.editing_id == m_id:
                    with st.form(key=f"form_inline_{m_id}"):
                        st.markdown(f"#### ✏️ Đang chỉnh sửa thông tin: **{name}**")
                        e_name = st.text_input("Họ và tên:", value=name)
                        
                        danh_sach_doi = ["Tiên Tổ Khảo"] + [
                            f"Đời thứ {i}" for i in range(1, 21)
                        ]
                        e_idx = (
                            danh_sach_doi.index(gen)
                            if gen in danh_sach_doi
                            else 0
                        )
                        e_gen = st.selectbox("Đời thứ:", danh_sach_doi, index=e_idx)
                        
                        chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
                        c_idx = (
                            chi_options.index(chi)
                            if chi in chi_options
                            else 5
                        )
                        e_chi = st.selectbox("Thuộc Chi:", chi_options, index=c_idx)
                        
                        current_father = str(father if father != "Chưa rõ" else "")
                        f_idx = 0
                        for idx, item in enumerate(danh_sach_thanh_vien_chi_tiet):
                            if item.startswith(current_father + " ("):
                                f_idx = idx
                                break
                        
                        e_father_select = st.selectbox(
                            "Chọn Cha (Phụ thân từ danh sách dòng họ - có kèm Đời/Chi):",
                            danh_sach_thanh_vien_chi_tiet,
                            index=f_idx
                        )

                        e_spouse = st.text_input(
                            "Vợ/Chồng (Phối):",
                            value=str(spouse if spouse != "Chưa rõ" else ""),
                        )
                        e_notes = st.text_area(
                            "Ghi chú thêm:",
                            value=str(row.get("notes", "") if pd.notna(row.get("notes")) else ""),
                        )

                        f_col1, f_col2 = st.columns(2)
                        with f_col1:
                            sub_save = st.form_submit_button("💾 Lưu Thay Đổi")
                        with f_col2:
                            sub_cancel = st.form_submit_button("❌ Hủy Bỏ")

                        if sub_save:
                            if e_father_select == "-- Không có / Chưa rõ --":
                                final_father = ""
                            else:
                                final_father = mapping_display_to_real.get(e_father_select, "")
                            
                            df.loc[df["id"] == m_id, "fullName"] = e_name.strip()
                            df.loc[df["id"] == m_id, "generation"] = e_gen
                            df.loc[df["id"] == m_id, "chi"] = e_chi
                            df.loc[df["id"] == m_id, "father"] = final_father
                            df.loc[df["id"] == m_id, "spouse"] = e_spouse.strip()
                            df.loc[df["id"] == m_id, "notes"] = e_notes.strip()

                            df_save = df.drop(columns=["_original_index"], errors="ignore")
                            save_data(df_save.to_dict(orient="records"))
                            st.session_state.editing_id = None
                            st.success(f"Cập nhật thành công thành viên: {e_name}!")
                            st.rerun()

                        if sub_cancel:
                            st.session_state.editing_id = None
                            st.rerun()

                st.markdown("<hr style='margin: 5px 0 15px 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)
        else:
            st.info("Không tìm thấy thành viên phù hợp với điều kiện tìm kiếm.")
    else:
        st.info("Chưa có dữ liệu thành viên trong hệ thống.")

# ================= TAB 3: CÂY PHẢ HỆ (DẠNG ĐỨNG) =================
with tab_so_do_doi:
    st.subheader("🌳 Cây Phả Hệ Trực Quan - Dạng Đứng (Theo Đời & Phân Cấp Cha Con)")
    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(df["generation"].dropna().unique(), key=get_gen_number)

        for gen in sorted_gens:
            st.markdown(f"### 📌 {gen}")
            gen_members = df[df["generation"] == gen].sort_values(by="_original_index")
            
            # Phân nhóm theo Cha
            fathers = gen_members["father"].dropna().unique()
            for f in fathers:
                father_display = f if f and str(f).strip() != "" else "Tiên Tổ / Chưa rõ phụ thân"
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<b>└─ Phụ thân: {father_display}</b>", unsafe_allow_html=True)
                
                children = gen_members[gen_members["father"] == f]
                for _, row in children.iterrows():
                    name = row.get("fullName", "Chưa rõ tên")
                    chi = row.get("chi", "Chưa rõ chi")
                    spouse = (
                        row.get("spouse", "")
                        if pd.notna(row.get("spouse")) and str(row.get("spouse")).strip() != ""
                        else "Chưa rõ"
                    )
                    st.markdown(
                        f"""
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;• <b>{name}</b> &nbsp;|&nbsp; <span style="color: #666; font-size: 13px;">Chi: {chi} | Phối: {spouse}</span>
                        """,
                        unsafe_allow_html=True,
                    )
            st.markdown("---")

# ================= TAB 4: CÂY PHẢ HỆ (DẠNG HÀNG NGANG) =================
with tab_so_do_cot:
    st.markdown(
        "<div style='text-align: center;'><h2 style='color: #2e7d32;'>🌳 SƠ ĐỒ CÂY PHẢ HỆ THEO HÀNG NGANG (CÓ TÊN CHA)</h2></div>",
        unsafe_allow_html=True,
    )

    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(df["generation"].dropna().unique(), key=get_gen_number)

        for gen in sorted_gens:
            is_root_gen = get_gen_number(gen) == 0

            badge_label = "TIÊN TỔ KHẢO" if is_root_gen else gen.upper()
            st.markdown(
                f"<div style='text-align: center;'><span class='gen-badge'>{badge_label}</span></div>",
                unsafe_allow_html=True,
            )

            gen_members = df[df["generation"] == gen].sort_values(by="_original_index")
            if not gen_members.empty:
                members_list = gen_members.to_dict(orient="records")
                num_items = len(members_list)

                items_per_row = 4
                for i in range(0, num_items, items_per_row):
                    batch = members_list[i : i + items_per_row]
                    cols = st.columns(len(batch))

                    for col_idx, row in enumerate(batch):
                        with cols[col_idx]:
                            name = row.get("fullName", "Chưa rõ")
                            chi = row.get("chi", "Gốc")

                            spouse_val = row.get("spouse", "")
                            spouse_text = (
                                f"Phối: {spouse_val}"
                                if pd.notna(spouse_val)
                                and str(spouse_val).strip() != ""
                                else "Phối: Chưa rõ"
                            )

                            father_val = row.get("father", "")
                            father_text = (
                                str(father_val)
                                if pd.notna(father_val)
                                and str(father_val).strip() != ""
                                else "Chưa cập nhật"
                            )

                            card_style = (
                                "background: #fff8e1; border: 2px solid #f57c00;"
                                if is_root_gen
                                else "background: #ffffff; border: 2px solid #ffa726;"
                            )

                            st.markdown(
                                f"""
                                <div style="{card_style} padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.08); margin-bottom: 10px; min-height: 140px;">
                                    <div style="font-weight: bold; color: #b71c1c; font-size: 16px; margin-bottom: 4px;">{name}</div>
                                    <div style="font-size: 13px; color: #e65100; font-weight: bold; margin-bottom: 4px;">{chi}</div>
                                    <div style="font-size: 12px; color: #555; margin-bottom: 6px;">{spouse_text}</div>
                                    <div style="font-size: 11px; background-color: #fff3e0; color: #d84315; padding: 4px 6px; border-radius: 6px; border: 1px dashed #ffa726; display: inline-block;">⬆ Cha: {father_text}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                st.markdown('<div class="arrow-down">⬇</div>', unsafe_allow_html=True)

# ================= TAB 5: IN CUỐN GIA PHẢ (PHÂN CẤP CHA CON TRONG SÁCH IN) =================
with tab_in_phu:
    st.subheader("📖 Bản In Sách Gia Phả Dòng Họ (Định dạng Trang Sách A4 Trang Trọng)")
    st.info("💡 Bác có thể xem trước bố cục trang sách bên dưới. Khi muốn in thành file PDF, hãy nhấn tổ hợp phím **Ctrl + P** (hoặc **Cmd + P** trên Mac), chọn khổ giấy **A4** và bật **Đồ họa nền (Background graphics)**.")

    if not df.empty:
        # Bìa sách
        st.markdown(
            """
            <div class="book-page">
                <div class="book-cover">
                    <div style="font-size: 20px; font-weight: bold; color: #795548; margin-bottom: 15px;">ĐẠI TỘC GIA PHẢ</div>
                    <div class="book-title">NGUYỄN TỘC PHẢ KÝ</div>
                    <div class="book-subtitle">TOÀN TỘC 5 CHI</div>
                    <div style="font-size: 14px; color: #555; margin-top: 40px; line-height: 1.6;">
                        <b>Địa chỉ dòng họ:</b> Thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa<br>
                        <b>Nguyên quán Thủy tổ:</b> Hải Dương tỉnh, Nam Sách phủ, Tuyên Minh huyện, An Đô Hạ xã
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        sorted_gens = sorted(df["generation"].dropna().unique(), key=get_gen_number)
        for gen in sorted_gens:
            is_root = get_gen_number(gen) == 0
            chapter_name = "PHẦN MỞ ĐẦU: TIÊN TỔ KHẢO" if is_root else f"CHƯƠNG: {gen.upper()}"
            
            gen_members = df[df["generation"] == gen].sort_values(by="_original_index")
            
            members_html = ""
            for _, row in gen_members.iterrows():
                m_name = row.get("fullName", "Chưa rõ")
                m_chi = row.get("chi", "Gốc")
                m_spouse = row.get("spouse", "")
                m_father = row.get("father", "")
                m_notes = row.get("notes", "")

                spouse_str = f"<b>Phối:</b> {m_spouse}" if pd.notna(m_spouse) and str(m_spouse).strip() != "" else ""
                father_str = f"<b>Phụ thân:</b> {m_father}" if pd.notna(m_father) and str(m_father).strip() != "" else ""
                notes_str = f"<br><i>Ghi chú: {m_notes}</i>" if pd.notna(m_notes) and str(m_notes).strip() != "" else ""

                meta_parts = [p for p in [f"<b>Thuộc Chi:</b> {m_chi}", father_str, spouse_str] if p]
                meta_combined = " &nbsp;|&nbsp; ".join(meta_parts)

                members_html += f"""
                <div class="member-print-box">
                    <div style="font-size: 17px; font-weight: bold; color: #4e342e; margin-bottom: 4px;">• {m_name}</div>
                    <div style="font-size: 14px; color: #444; margin-bottom: 2px;">{meta_combined}</div>
                    <div style="font-size: 13px; color: #555;">{notes_str}</div>
                </div>
                """

            st.markdown(
                f"""
                <div class="book-page">
                    <div class="chapter-title">{chapter_name}</div>
                    <p style="text-align: center; font-style: italic; color: #666; margin-bottom: 30px;">
                        Danh sách các bậc tiền bối và hậu duệ thuộc đời {gen} trong dòng họ Nguyễn tộc.
                    </p>
                    {members_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

# ================= TAB 6: XUẤT DỮ LIỆU =================
with tab_xuat:
    st.subheader("💾 Xuất Dữ Liệu Phả Hệ (JSON)")
    st.markdown("Bạn có thể tải xuống toàn bộ dữ liệu dòng họ hiện tại để sao lưu dự phòng.")

    if not df.empty:
        export_data = df.drop(columns=["_original_index"], errors="ignore").to_dict(orient="records")
        json_str = json.dumps(export_data, ensure_ascii=False, indent=4)
        
        st.download_button(
            label="📥 Tải xuống tệp JSON Gia Phả",
            data=json_str,
            file_name="GiaPha_DongHoNguyen.json",
            mime="application/json",
        )
    else:
        st.info("Không có dữ liệu để xuất.")

# ================= TAB 7: NHẬP DỮ LIỆU =================
with tab_nhap:
    st.subheader("📥 Nhập Dữ Liệu Phả Hệ Mới")
    st.markdown("Tải lên tệp JSON chứa dữ liệu gia phả để cập nhật hệ thống trực tuyến.")

    uploaded_file = st.file_uploader("Chọn tệp JSON gia phả:", type=["json"])
    if uploaded_file is not None:
        try:
            imported_data = json.load(uploaded_file)
            if isinstance(imported_data, list):
                if st.button("⚡ Xác nhận ghi đè dữ liệu mới"):
                    save_data(imported_data)
                    st.success("Đã nhập và cập nhật dữ liệu thành công! Hãy tải lại trang.")
                    st.rerun()
            else:
                st.error("Cấu trúc tệp JSON không hợp lệ (phải là một danh sách các thành viên).")
        except Exception as e:
            st.error(f"Lỗi khi đọc tệp: {e}")

# ================= TAB 8: QUẢN TRỊ (THÊM MỚI THÀNH VIÊN) =================
with tab_quan_tri:
    st.subheader("⚙️ Thêm Thành Viên Mới Vào Dòng Họ")

    if not st.session_state.logged_in:
        st.warning("⚠️ Bạn cần đăng nhập ở thanh bên trái (Sidebar) với quyền **Admin** hoặc **Đầu Chi** để thêm thành viên mới.")
    else:
        st.info(f"Đang thao tác với tư cách: **{st.session_state.username}** ({st.session_state.role} - Chi: {st.session_state.chi})")

        danh_sach_thanh_vien_chi_tiet_add = ["-- Không có / Chưa rõ --"]
        mapping_display_to_real_add = {}
        if not df.empty:
            df_temp_add = df.copy()
            df_temp_add["_gen_num"] = df_temp_add["generation"].apply(get_gen_number)
            df_temp_add = df_temp_add.sort_values(by=["_gen_num", "_original_index"])
            for _, r in df_temp_add.iterrows():
                fname = str(r.get("fullName", "")).strip()
                fgen = str(r.get("generation", "")).strip()
                fchi = str(r.get("chi", "")).strip()
                if fname:
                    disp = f"{fname} ({fgen} - {fchi})"
                    danh_sach_thanh_vien_chi_tiet_add.append(disp)
                    mapping_display_to_real_add[disp] = fname

        with st.form("add_member_form"):
            new_name = st.text_input("Họ và tên thành viên mới *:")
            
            danh_sach_doi = ["Tiên Tổ Khảo"] + [f"Đời thứ {i}" for i in range(1, 21)]
            new_gen = st.selectbox("Đời thứ:", danh_sach_doi, index=1)
            
            if st.session_state.role == "Admin":
                chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
                new_chi = st.selectbox("Thuộc Chi:", chi_options)
            else:
                new_chi = st.session_state.chi
                st.text(f"Thuộc Chi (Theo quyền quản trị): {new_chi}")

            new_father_select = st.selectbox(
                "Chọn Phụ thân (Cha) từ danh sách dòng họ:",
                danh_sach_thanh_vien_chi_tiet_add
            )
            
            new_spouse = st.text_input("Vợ/Chồng (Phối):")
            new_notes = st.text_area("Ghi chú / Tiểu sử / Thành tích:")

            submit_add = st.form_submit_button("➕ Thêm Thành Viên Mới")

            if submit_add:
                if not new_name.strip():
                    st.error("Vui lòng nhập họ tên thành viên!")
                else:
                    final_father_add = ""
                    if new_father_select != "-- Không có / Chưa rõ --":
                        final_father_add = mapping_display_to_real_add.get(new_father_select, "")

                    new_id = str(int(df["id"].astype(int).max() + 1) if not df.empty and "id" in df.columns and df["id"].astype(str).str.isdigit().any() else 1001)

                    new_row = {
                        "id": new_id,
                        "fullName": new_name.strip(),
                        "generation": new_gen,
                        "chi": new_chi,
                        "father": final_father_add,
                        "spouse": new_spouse.strip(),
                        "notes": new_notes.strip(),
                    }

                    if isinstance(raw_data, list):
                        raw_data.append(new_row)
                    else:
                        raw_data = [new_row]

                    save_data(raw_data)
                    st.success(f"Đã thêm thành công thành viên: **{new_name.strip()}** vào hệ thống!")
                    st.rerun()

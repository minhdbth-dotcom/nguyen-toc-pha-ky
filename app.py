import base64
import json
import os
import re
import pandas as pd
import streamlit as st

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="NGUYỄN TỘC PHẢ KÝ - TOÀN TỘC 5 CHI", page_icon="🌳", layout="wide"
)

# --- CSS TÙY CHỈNH GIAO DIỆN & KHUNG SÁCH IN A4 ĐỨNG ---
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
        
        /* ĐỊNH DẠNG TRANG SÁCH A4 ĐỨNG */
        .book-page {
            background-color: #ffffff;
            border: 2px solid #795548;
            padding: 35px 45px;
            margin: 20px auto;
            max-width: 750px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            font-family: "Times New Roman", serif;
            font-size: 15px;
            color: #222222;
            text-align: justify;
            line-height: 1.5;
            box-sizing: border-box;
            page-break-after: always;
            break-after: page;
        }

        @media print {
            @page {
                size: A4 portrait;
                margin: 15mm;
            }
            body { 
                background: white; 
                margin: 0; 
                -webkit-print-color-adjust: exact;
            }
            .stSidebar, .stTabs, .header-container, button, header, footer, .stInfo { 
                display: none !important; 
            }
            .book-page { 
                border: 2px solid #795548 !important; 
                padding: 20px 30px !important; 
                margin: 0 !important; 
                width: 100% !important; 
                max-width: 100% !important; 
                box-shadow: none !important; 
                page-break-after: always !important;
                break-after: page !important;
            }
            div.element-container, div.stMarkdown {
                margin: 0 !important;
                padding: 0 !important;
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


def load_data():
    filename = "GiaPha_DongHoNguyen.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception:
            pass

    default_data = [
        {
            "id": "1",
            "fullName": "Nguyễn Văn Thủy Tổ",
            "generation": "Tiên Tổ Khảo",
            "chi": "Gốc",
            "birthYear": "",
            "deathAnniversary": "",
            "location": "Hội Hiền, Tây Hồ, Thọ Xuân, Thanh Hóa",
            "profession": "",
            "spouse": "Bà chính thất",
            "father": "",
            "notes": "Thủy tổ di cư về lập ấp tại thôn Hội Hiền thời cố Chính Hòa.",
            "imageUrl": "",
        }
    ]
    return default_data


def save_data(data):
    filename = "GiaPha_DongHoNguyen.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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
        df["id"] = [str(k + 1000) for k in range(len(df))]

    if "_original_index" not in df.columns:
        df["_original_index"] = range(len(df))


# --- HÀM NỘI DUNG TỔNG QUAN ---
def get_loi_tua_html():
    parts = [
        '<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: justify;">',
        '<h3 style="color: #b30000; font-weight: bold; margin-bottom: 15px; text-align: left;">Lời nói đầu</h3>',
        '<p>Họ hàng và gia đình có phả ký cũng giống như đất nước có sử sách. Các cụ ngày xưa đã nói:</p>',
        '<ul style="margin-left: 20px;">',
        '<li><em>Nhân do hổ tổ</em></li>',
        '<li><em>Mộc do hổ bản</em></li>',
        '<li><em>Thủy do hổ nguyên.</em></li>',
        '</ul>',
        '<p><b>Đại ý như sau:</b></p>',
        '<ul style="margin-left: 20px;">',
        '<li>Người phải có tổ.</li>',
        '<li>Cây phải có gốc.</li>',
        '<li>Nước phải có nguồn.</li>',
        '<li>Người phải có hàng xóm láng giềng....</li>',
        '</ul>',
        '<p>Hoặc cũng có câu thơ như sau:</p>',
        '<div style="text-align: center; font-style: italic; margin: 15px 0;">'
        'Cây có gốc mới nở cành xanh ngọn,<br>'
        'Nước có nguồn mới bể rộng sông sâu,<br>'
        'Người ta có nguồn gốc từ đâu,<br>'
        'Có tổ tiên trước rồi sau có mình.'
        '</div>',
        '<p>Như vậy việc biên soạn, sao chép lại quá trình hình thành và phát triển của họ <b>NGUYỄN</b> ở thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa là một việc rất cần thiết và quan trọng. Để tỏ lòng thành kính tưởng nhớ tới công ơn của các bậc tổ tiên dòng họ Nguyễn, những người đã có công sinh thành và phát triển dòng họ.</p>',
        '<p>Kể từ khi cố Thủy tổ từ bản tộc Tiên Tổ ở Hải Dương Tỉnh, Nam Sách Phủ, Tuyên Minh huyện, An Đô Hạ xã. Ban đầu di cư vào tại bản tỉnh Hà Trung phủ, Hoàng Hóa huyện, Dương Sơn xã, Đại Yên thôn. Sinh cơ lập nghiệp (Thiết tương triệu cơ) nghĩa là làm nghề thợ rèn. Sau đó chuyển lên Hội Hiền thôn, Phúc Trạch xã, vào thời cổ Chính Hòa (1680 - 1704). Tính đến nay đã gần 300 năm. Đã có hơn 15 đời nối tiếp, hình thành 5 chi, có trên 100 hộ, là một trong những họ đông nhất của làng.</p>',
        '<p>Do thời cuộc nhất là sau Cách mạng Tháng Tám năm 1945 đến nay có nhiều hộ, nhiều cá nhân trong dòng họ đã thoát ly đi xây dựng vùng kinh tế mới, đi công tác, học tập và chiến đấu ở nhiều vùng trên mọi miền đất nước. Các thế hệ có những anh dũng hy sinh cho sự nghiệp giải phóng dân tộc và bảo vệ Tổ quốc, nhất là thời kỳ đế quốc phong kiến ông cha ta đã tham gia các phong trào, Hội Ái Nghĩa, Hội Tương Tế, hướng nghiệp, Thanh niên Cách Mạng Đồng Chí Hội.....</p>',
        '<p>Có nhiều gia đình được Nhà nước tặng Bằng Khen Gia đình có công với nước. Bảng Vàng Danh Dự. Gia đình vẻ vang, có nhiều cá nhân được tặng huân huy chương và các phần thưởng cao quý khác.</p>',
        '<p>Càng nghiên cứu tìm hiểu về cội nguồn gốc tích tôn thống Nguyễn tộc, thân thế và sự nghiệp của ông cha ta chúng ta càng tự hào về quá khứ và hiện tại như bức đại tự ở nhà thờ đã nêu.</p>',
        '<p style="text-align: center; font-weight: bold; margin-top: 20px;">KÍNH NHƯ TẠI</p>',
        '<p>Và hai câu đối:</p>',
        '<div style="text-align: center; font-style: italic; margin: 15px 0;">'
        'Cương thường chi trậu ngất trung thiên<br>'
        'Bản thế vi niên tử tôn sinh.'
        '</div>',
        '<p>Hoặc hai câu đối ở cột cạnh bức bình phong ở sân cũng ghi:</p>',
        '<div style="text-align: center; font-style: italic; margin: 15px 0;">'
        'Nhân nghĩa căn cơ tùy vĩnh thế<br>'
        'Cương thường để trậu ngất trung thiên'
        '</div>',
        '<p><b>Thật vậy:</b></p>',
        '<div style="text-align: center; font-style: italic; margin: 15px 0;">'
        'Tổ tông công đức bao trùm hậu thế<br>'
        'Con cháu muôn đời không sao quên được'
        '</div>',
        '<p>Vì thế theo nguyện vọng chung xây dựng và giữ vững tôn thống NGUYỄN TỘC là trách nhiệm và nghĩa vụ của mỗi thành viên trong dòng họ. Do đó ngày 25-02-1990 tức là ngày Xuân Kỵ ngày 01 tháng 02 năm Canh Ngọ các ông đầu chi và các cụ cao tuổi trong họ đã họp tại nhà ông Nguyễn Văn Chơn (nhà thờ của họ) dưới sự chủ trì của ông Nguyễn Văn Hiếu trưởng họ, đã họp bàn nhiều việc trong đó có việc viết gia phả và thành lập ban soạn dịch, tìm hiểu để viết lại gia phả, y sao lại bản chính của các cụ để lại là quan trọng. Phải nói đây là cuộc họp có nhiều ý nghĩa của cả họ.</p>',
        '<p>Ngày 11-03-1990 tức ngày 15 tháng 02 năm Canh Ngọ ban viết gia phả gồm có các ông sau:</p>',
        '<p><b>Nguyễn Văn Hiếu, Nguyễn Văn Nghĩa, Nguyễn Hoàng Biền, Nguyễn Văn Yên, Nguyễn Công Thăng.</b> Và lên kế hoạch tiến hành dịch và viết phấn đấu đến Đông chí phải hoàn thành tập NGUYỄN TỘC PHẢ KÝ.</p>',
        '<p>Tập NGUYỄN TỘC PHẢ KÝ này được viết căn cứ vào các tư liệu sau đây:</p>',
        '<p>Dịch từ chữ Hán cuốn phả ký của cố Nguyễn Hoàng Cừ sao chép trước lúc đi thi nhưng chỉ được đến đời thứ tám và các quyển viết tay bằng chữ quốc ngữ của ông NGỌC MƠN (cố Vợi), NGỌC HIỆP, các ông trưởng chi một VĂN HIẾU, TRƯỜNG AN, và các ông cao tuổi trong họ cung cấp đồng thời có sự giúp đỡ của các ông ĐOÀN ĐỈNH, ÔNG TÂM, CỤ GIÁO CHINH, ÔNG PHÓ ĐIỀN Nam Giang và tra khảo các gia phả khác của các dòng họ có liên quan, đến tận các gia đình trong dòng họ để ghi chép lại.</p>',
        '<p>Do những hạn chế trong việc sưu tầm, biên soạn cũng như sự hiểu biết nên việc biên soạn chắc chắn không tránh khỏi những thiếu sót, rất mong được sự đóng góp và bổ sung ý kiến của các Cụ, Ông, Bà, con cháu trong và ngoài dòng họ để các lần tái bản sau được đầy đủ rõ ràng hơn. Mãi tới Đông chí năm 2013 (Quý Tỵ) con cháu mới sao chép, biên soạn lại được tập NGUYỄN TỘC PHẢ KÝ này với đầy đủ ý nghĩa và hy vọng nó sẽ tiếp thêm sức mạnh cho dòng họ Nguyễn để có những thắng lợi mới, góp phần vào sự phát triển của dòng họ cũng như góp phần cho sự phát triển của cả dân tộc.</p>',
        '<p>Trong quá trình sao viết lại không sao tránh khỏi những thiếu sót chúng tôi rất mong có sự đóng góp xây dựng chung để tập NGUYỄN TỘC PHẢ KÝ này hoàn thiện hơn.</p>',
        '<p>Một lần nữa xin chân thành cảm ơn sự đóng góp chung của các quý vị gần xa!</p>',
        '<p style="text-align: right; font-style: italic; margin-top: 25px;">Ngày 22 tháng 12 năm 2013<br>Đông Chí 20 tháng 11 năm Quý Tỵ</p>',
        '</div>'
    ]
    return ''.join(parts)# --- THANH ĐĂNG NHẬP & PHÂN QUYỀN (SIDEBAR) ---
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
    "📝 Bảng Thêm/Xóa Nhanh (Excel Grid)",
    "🌳 Cây Phả Hệ (Dạng Đứng)",
    "🌳 Cây Phả Hệ (Hàng Ngang Chi Tiết)",
    "📖 In Cuốn Gia Phả",
    "💾 Xuất Dữ Liệu",
    "📥 Nhập Dữ Liệu",
    "⚙️ Quản Trị (Thêm Mới)",
])

tab_tong_quan = tabs[0]
tab_danh_sach = tabs[1]
tab_excel_grid = tabs[2]
tab_so_do_doi = tabs[3]
tab_so_do_cot = tabs[4]
tab_in_phu = tabs[5]
tab_xuat = tabs[6]
tab_nhap = tabs[7]
tab_quan_tri = tabs[8]


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

  # Hiển thị nội dung lời tựa tổng quan chuẩn HTML
  st.markdown(get_loi_tua_html(), unsafe_allow_html=True)
# ================= TAB 2: DANH SÁCH & QUẢN TRỊ TRỰC TIẾP =================
with tab_danh_sach:
    st.subheader(
        "📋 Danh Sách Thành Viên & Quản Trị (Hỗ trợ thêm, sửa ảnh, thông tin hoặc xóa thành viên)"
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

        search_key = st.text_input(
            "🔍 Tìm kiếm theo tên thành viên:", key="search_list_v4"
        )
        filtered_df = df_sorted.copy()
        if search_key and "fullName" in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df["fullName"].str.contains(search_key, case=False, na=False)
            ]

        if "editing_id" not in st.session_state:
            st.session_state.editing_id = None
        if "inserting_under_id" not in st.session_state:
            st.session_state.inserting_under_id = None

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

            col_i1, col_i2, col_i3 = st.columns([1, 4, 3])
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
                    c_btn1, c_btn2, c_btn3 = st.columns(3)
                    with c_btn1:
                        if st.button("➕ Thêm", key=f"insert_{m_id}", help="Thêm thành viên mới liên quan"):
                            st.session_state.inserting_under_id = m_id
                            st.session_state.editing_id = None
                            st.rerun()
                    with c_btn2:
                        if st.button("✏ Sửa", key=f"edit_{m_id}"):
                            st.session_state.editing_id = m_id
                            st.session_state.inserting_under_id = None
                            st.rerun()
                    with c_btn3:
                        if st.button("🗑️ Xóa", key=f"del_{m_id}"):
                            new_df_list = (
                                df[df["id"] != m_id]
                                .drop(columns=["_original_index"], errors="ignore")
                                .to_dict(orient="records")
                            )
                            save_data(new_df_list)
                            st.success(f"Đã xóa thành viên: {name}")
                            st.rerun()
                else:
                    st.caption("🔒 Cần đăng nhập")

            if st.session_state.inserting_under_id == m_id:
                with st.form(key=f"form_insert_{m_id}"):
                    st.markdown(f"#### ➕ Thêm thành viên mới (Có cha/mẹ là: **{name}**) hoặc cùng nhánh")
                    ins_name = st.text_input("Họ và tên thành viên mới:", key=f"ins_name_{m_id}")

                    ins_col1, ins_col2 = st.columns(2)
                    with ins_col1:
                        danh_sach_doi = ["Tiên Tổ Khảo"] + [
                            f"Đời thứ {i}" for i in range(1, 21)
                        ]
                        ins_idx = danh_sach_doi.index(gen) if gen in danh_sach_doi else 0
                        ins_gen = st.selectbox("Đời thứ:", danh_sach_doi, index=ins_idx, key=f"ins_gen_{m_id}")
                    with ins_col2:
                        chi_options = ["Chi 1", "Chi 2", "Chi 3", "Chi 4", "Chi 5", "Gốc"]
                        c_idx = chi_options.index(chi) if chi in chi_options else 5
                        ins_chi = st.selectbox("Thuộc Chi:", chi_options, index=c_idx, key=f"ins_chi_{m_id}")

                    f_default_idx = 0
                    for idx, item in enumerate(danh_sach_thanh_vien_chi_tiet):
                        if item.startswith(name + " ("):
                            f_default_idx = idx
                            break
                    ins_father_select = st.selectbox(
                        "Chọn Phụ Thân (Cha):", danh_sach_thanh_vien_chi_tiet, index=f_default_idx, key=f"ins_father_{m_id}"
                    )
                    ins_spouse = st.text_input("Vợ/Chồng (Phối):", key=f"ins_spouse_{m_id}")

                    st.markdown("**📷 Chọn ảnh chân dung:**")
                    uploaded_ins_img = st.file_uploader(
                        "Tải ảnh lên (JPEG, PNG)",
                        type=["jpg", "jpeg", "png"],
                        key=f"ins_upl_{m_id}",
                    )

                    ins_notes = st.text_area("Tiểu sử / Ghi chú:", key=f"ins_notes_{m_id}")

                    if_col1, if_col2 = st.columns(2)
                    with if_col1:
                        sub_ins_save = st.form_submit_button("💾 Xác Nhận Thêm")
                    with if_col2:
                        sub_ins_cancel = st.form_submit_button("❌ Hủy Bỏ")

                    if sub_ins_save:
                        if not ins_name.strip():
                            st.error("Vui lòng nhập họ và tên thành viên mới!")
                        else:
                            final_ins_father = (
                                ""
                                if ins_father_select == "-- Không có / Chưa rõ --"
                                else mapping_display_to_real.get(ins_father_select, "")
                            )
                            final_ins_img_url = ""
                            if uploaded_ins_img is not None:
                                bytes_data = uploaded_ins_img.getvalue()
                                b64_str = base64.b64encode(bytes_data).decode("utf-8")
                                final_ins_img_url = f"data:image/jpeg;base64,{b64_str}"

                            new_sub_member = {
                                "id": str(int(pd.Timestamp.now().timestamp())),
                                "fullName": ins_name.strip(),
                                "generation": ins_gen,
                                "chi": ins_chi,
                                "birthYear": "",
                                "deathAnniversary": "",
                                "location": "",
                                "profession": "",
                                "spouse": ins_spouse.strip(),
                                "father": final_ins_father,
                                "notes": ins_notes.strip(),
                                "imageUrl": final_ins_img_url,
                            }
                            current_list = (
                                df.drop(columns=["_original_index"], errors="ignore")
                                .to_dict(orient="records")
                                if not df.empty
                                else []
                            )
                            current_list.append(new_sub_member)
                            save_data(current_list)
                            st.session_state.inserting_under_id = None
                            st.success(f"Đã thêm thành công thành viên: {ins_name}!")
                            st.rerun()

                    if sub_ins_cancel:
                        st.session_state.inserting_under_id = None
                        st.rerun()

            if st.session_state.editing_id == m_id:
                with st.form(key=f"form_inline_{m_id}"):
                    st.markdown(f"#### ✏️ Cập nhật chi tiết cho: **{name}**")
                    e_name = st.text_input("Họ và tên:", value=name)

                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        danh_sach_doi = ["Tiên Tổ Khảo"] + [
                            f"Đời thứ {i}" for i in range(1, 21)
                        ]
                        e_idx = (
                            danh_sach_doi.index(gen) if gen in danh_sach_doi else 0
                        )
                        e_gen = st.selectbox(
                            "Đời thứ:", danh_sach_doi, index=e_idx
                        )
                    with e_col2:
                        chi_options = [
                            "Chi 1",
                            "Chi 2",
                            "Chi 3",
                            "Chi 4",
                            "Chi 5",
                            "Gốc",
                        ]
                        c_idx = (
                            chi_options.index(chi) if chi in chi_options else 5
                        )
                        e_chi = st.selectbox(
                            "Thuộc Chi:", chi_options, index=c_idx
                        )

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

                    st.markdown(
                        "**📷 Chọn ảnh chân dung từ thư viện điện thoại / máy tính:**"
                    )
                    uploaded_edit_img = st.file_uploader(
                        "Tải ảnh lên (JPEG, PNG)",
                        type=["jpg", "jpeg", "png"],
                        key=f"upl_{m_id}",
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
                        final_img_url = row.get("imageUrl", "")
                        if uploaded_edit_img is not None:
                            bytes_data = uploaded_edit_img.getvalue()
                            b64_str = base64.b64encode(bytes_data).decode("utf-8")
                            final_img_url = f"data:image/jpeg;base64,{b64_str}"

                        df.loc[df["id"] == m_id, "fullName"] = e_name.strip()
                        df.loc[df["id"] == m_id, "generation"] = e_gen
                        df.loc[df["id"] == m_id, "chi"] = e_chi
                        df.loc[df["id"] == m_id, "father"] = final_father
                        df.loc[df["id"] == m_id, "spouse"] = e_spouse.strip()
                        df.loc[df["id"] == m_id, "imageUrl"] = final_img_url
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

# ================= TAB 3: BẢNG THÊM/XÓA NHANH (EXCEL GRID) =================
with tab_excel_grid:
    st.subheader("📝 Bảng Thêm, Xóa và Chỉnh Sửa Hàng Loạt (Excel Grid)")
    st.info(
        "💡 Bác có thể bấm vào dấu **`+`** ở dưới bảng để **thêm dòng mới**, tích chọn cột để **xóa dòng**, hoặc sửa trực tiếp nội dung các ô rồi bấm nút **Lưu Lại** phía dưới."
    )

    if st.session_state.logged_in:
        editable_df = df.drop(
            columns=["_original_index", "imageUrl"], errors="ignore"
        ).copy()

        edited_df = st.data_editor(
            editable_df,
            num_rows="dynamic",
            key="grid_editor",
            use_container_width=True,
        )

        if st.button("💾 Lưu Thay Đổi Từ Bảng Lưới"):
            try:
                old_img_map = (
                    df.set_index("id")["imageUrl"].to_dict()
                    if "id" in df.columns
                    else {}
                )
                new_records = []
                for idx, row in edited_df.iterrows():
                    r_dict = row.to_dict()
                    m_id = str(r_dict.get("id", ""))
                    if not m_id or m_id == "nan" or m_id.strip() == "":
                        m_id = str(int(pd.Timestamp.now().timestamp()) + idx)
                    r_dict["id"] = m_id
                    r_dict["imageUrl"] = old_img_map.get(m_id, "")
                    new_records.append(r_dict)

                save_data(new_records)
                st.success(
                    "Đã lưu thành công các thay đổi từ bảng lưới! Hãy tải lại trang."
                )
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi khi lưu dữ liệu: {e}")
    else:
        st.warning(
            "🔒 Vui lòng đăng nhập ở thanh bên trái để sử dụng tính năng chỉnh sửa bảng lưới."
        )

# ============================== TAB 4: CÂY PHẢ HỆ (DẠNG ĐỨNG) ==============================
import re

# Định nghĩa hàm xử lý lấy số đời nằm ở bên ngoài để dùng chung cho cả 2 tab con
def xl_get_gen(x):
    nums = re.findall(r'\d+', str(x))
    return int(nums[0]) if nums else 0

with tab_so_do_doi:
    # Tách thành 2 tab con bên trong
    sub_tab1, sub_tab2 = st.tabs(["📜 Danh Sách Các Đời", "🌳 Sơ Đồ Khối Đồ Họa"])

    # ==================== TAB 1: DANH SÁCH CÁC ĐỜI (Giao diện truyền thống) ====================
    with sub_tab1:
        st.markdown("### 📋 Danh Sách Thành Viên Phân Chia Theo Thế Hệ")
        
        if not df.empty and "generation" in df.columns:
            danh_sach_doi = sorted(df["generation"].dropna().unique(), key=lambda x: xl_get_gen(x))
            
            for doi in danh_sach_doi:
                st.markdown(f"#### 📌 {doi}")
                df_doi = df[df["generation"] == doi]
                for _, row in df_doi.iterrows():
                    name = row.get("fullName", "")
                    chi = row.get("chi", "")
                    phu_than = row.get("father", "")
                    phoi_nguau = row.get("spouse", "")
                    
                    info_parts = []
                    if phu_than:
                        info_parts.append(f"Phụ thân: {phu_than}")
                    if chi:
                        info_parts.append(f"Chi: {chi}")
                    if phoi_nguau and str(phoi_nguau).strip() != "":
                        info_parts.append(f"Phối: {phoi_nguau}")
                        
                    info_str = " | ".join(info_parts)
                    st.markdown(f"• **{name}** {f'({info_str})' if info_str else ''}")
                st.markdown("---")
        else:
            st.info("Chưa có dữ liệu thành viên để hiển thị danh sách.")

   # ===============================================
# TAB 2: SƠ ĐỒ KHỐI CÂY PHẢ HỆ (Sắp xếp theo thứ tự các đời)
# ===============================================
with tab_so_do_doi:
    st.markdown("### 🗺️ Sơ Đồ Khối Cây Phả Hệ Trực Quan (Phân Theo Thế Hệ)")

    # Hộp lựa chọn 6 nhóm theo yêu cầu
    nhom_chon = st.selectbox(
        "📁 Chọn nhóm / nhánh phả hệ để hiển thị:",
        [
            "📜 Nhóm gốc (Từ đời 1 đến hết đời 8)",
            "🌿 Chi 1",
            "🌿 Chi 2",
            "🌿 Chi 3",
            "🌿 Chi 4",
            "🌿 Chi 5"
        ],
        key="select_6_nhom_pha_he_doi_tab2_ordered_v2"
    )

    # Lọc dữ liệu theo nhánh được chọn
    df_hien_thi = df.copy()
    if "Nhóm gốc" in nhom_chon:
        if "generation" in df_hien_thi.columns:
            df_hien_thi = df_hien_thi[df_hien_thi["generation"].apply(xl_get_gen) <= 8]
    else:
        chi_match = re.search(r'\d+', nhom_chon)
        if chi_match and "chi" in df_hien_thi.columns:
            so_chi = chi_match.group(0)
            df_hien_thi = df_hien_thi[df_hien_thi["chi"].astype(str).str.contains(so_chi)]

    # Xử lý sắp xếp chuẩn theo số thứ tự của Đời (generation)
    rows_html = ""
    if not df_hien_thi.empty and "generation" in df_hien_thi.columns:
        def get_gen_number(val):
            match = re.search(r'\d+', str(val))
            return int(match.group()) if match else 99
            
        df_hien_thi["_gen_sort_val"] = df_hien_thi["generation"].apply(get_gen_number)
        df_hien_thi = df_hien_thi.sort_values(by=["_gen_sort_val"], kind="stable")
        
        unique_gens = df_hien_thi[["generation", "_gen_sort_val"]].drop_duplicates().sort_values("_gen_sort_val")
        
        for _, gen_row in unique_gens.iterrows():
            gen_name = gen_row["generation"]
            group = df_hien_thi[df_hien_thi["generation"] == gen_name]
            
            rows_html += f"""
            <div class="generation-row">
                <div class="generation-title">📜 {gen_name}</div>
                <div class="nodes-grid">
            """
            for idx, row in group.iterrows():
                name = str(row.get("fullName", "Chưa rõ")).strip()
                chi = str(row.get("chi", ""))
                father = str(row.get("father", "")).strip()
                
                chi_str = f" - Chi {chi}" if chi else ""
                father_str = f"<div class='node-father'>Phụ thân: {father}</div>" if father else ""

                rows_html += f"""
                    <div class="node">
                        <div class="node-name">{name}</div>
                        <div class="node-gen">{gen_name}{chi_str}</div>
                        {father_str}
                    </div>
                """
            rows_html += """
                </div>
            </div>
            """
    else:
        rows_html = "<p style='text-align: center; font-style: italic;'>Không có dữ liệu thành viên trong nhánh này.</p>"

    # Khung giao diện HTML/CSS tổng thể
    tree_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                background-color: #fdfbf7;
                background-image: radial-gradient(#d5c3aa 0.75px, transparent 0.75px);
                background-size: 15px 15px;
                font-family: 'Times New Roman', serif;
                color: #3e2723;
                margin: 0;
                padding: 20px;
            }}
            .tree-container {{
                border: 4px double #795548;
                border-radius: 8px;
                padding: 25px;
                background: #fdfbf7;
                box-shadow: inset 0 0 15px rgba(121, 85, 72, 0.1);
            }}
            h3.title {{
                text-align: center;
                color: #5d4037;
                margin-bottom: 25px;
                border-bottom: 2px solid #8d6e63;
                padding-bottom: 10px;
            }}
            .generation-row {{
                margin-bottom: 25px;
                border-bottom: 1px dashed #d7ccc8;
                padding-bottom: 15px;
            }}
            .generation-title {{
                font-weight: bold;
                font-size: 16px;
                color: #5d4037;
                margin-bottom: 10px;
                background: #efebe9;
                padding: 5px 12px;
                border-radius: 4px;
                display: inline-block;
                border-left: 4px solid #795548;
            }}
            .nodes-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
            }}
            .node {{
                border: 2px solid #a1887f;
                padding: 10px 14px;
                background: #fff8e1;
                color: #4e342e;
                border-radius: 6px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
                width: 210px;
                text-align: center;
            }}
            .node-name {{
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 4px;
            }}
            .node-gen {{
                font-size: 11px;
                color: #6d4c41;
                background: #efebe9;
                padding: 2px 6px;
                border-radius: 4px;
                display: inline-block;
            }}
            .node-father {{
                font-size: 10px;
                font-style: italic;
                color: #795548;
                margin-top: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="tree-container">
            <h3 class="title">SƠ ĐỒ PHẢ HỆ - {nhom_chon.upper()}</h3>
            {rows_html}
        </div>
    </body>
    </html>
    """

    # Render giao diện mượt mà trên Streamlit
    import streamlit.components.v1 as components
    components.html(tree_html, height=750, scrolling=True)
    st.caption("💡 **Mẹo sử dụng:** Các thành viên được tự động sắp xếp chuẩn theo số thứ tự thế hệ từ nhỏ đến lớn (Đời 1, Đời 2,...) giúp quan sát dòng họ mạch lạc và chính xác.")# ================= TAB 5: CÂY PHẢ HỆ (HÀNG NGANG CHI TIẾT) =================
with tab_so_do_cot:
    st.markdown(
        "<div style='text-align: center;'><h2 style='color: #2e7d32;'>🌳 SƠ ĐỒ CÂY PHẢ HỆ HÀNG NGANG CHI TIẾT</h2></div>",
        unsafe_allow_html=True,
    )
    if not df.empty and "generation" in df.columns:
        sorted_gens = sorted(
            df["generation"].dropna().unique(), key=get_gen_number
        )
        for gen in sorted_gens:
            is_root_gen = gen == "Tiên Tổ Khảo"
            badge_label = "TIÊN TỔ KHẢO" if is_root_gen else gen.upper()
            st.markdown(
                f"<div style='text-align: center;'><span class='gen-badge'>{badge_label}</span></div>",
                unsafe_allow_html=True,
            )

            gen_members = df[df["generation"] == gen].sort_values(
                by=["_original_index"]
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

                            if img_url.startswith(
                                ("http://", "https://", "data:image/")
                            ):
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

# ==================== TAB 6: IN CUỐN GIA PHẢ ===================
    with tab_in_phu:
        st.subheader("📖 Bản In Sách Gia Phả Dòng Họ (Khổ Đứng A4 - Chuẩn Trang Trọng)")
        st.info("💡 Bác nhấn **Ctrl + P** (hoặc **Cmd + P** trên Mac), trong cài đặt máy in chọn khổ giấy **Portrait (Đứng)** để in các trang sách.")

        # CSS chung cho toàn bộ các trang in gia phả mang phong cách giấy cổ và khung kép
        st.markdown("""
<style>
.giay-co-kinh {
    background-color: #fcf9f2;
    background-image: radial-gradient(#e5dbc9 0.8px, transparent 0.8px), radial-gradient(#e5dbc9 0.8px, #fcf9f2 0.8px);
    background-size: 30px 30px;
    background-position: 0 0, 15px 15px;
    border: 4px double #795548 !important;
    border-radius: 4px;
    padding: 50px 40px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    max-width: 850px;
    margin: 0 auto 30px auto;
    box-sizing: border-box;
}
.trang-bia {
    min-height: 82vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

        # 1. TRANG BÌA
        cover_html = """
<div class="giay-co-kinh trang-bia">
    <div style="font-size: 22px; font-weight: bold; color: #795548; font-family: 'Times New Roman', serif; margin-bottom: 20px; letter-spacing: 2px;">ĐẠI TỘC GIA PHẢ</div>
    <div style="font-size: 38px; font-weight: bold; color: #4e342e; font-family: 'Times New Roman', serif; text-transform: uppercase; margin-bottom: 20px; line-height: 1.2;">NGUYỄN TỘC PHẢ KÝ</div>
    <div style="font-size: 20px; font-weight: bold; color: #5d4037; font-family: 'Times New Roman', serif; margin-bottom: 35px;">TOÀN TỘC 5 CHI</div>
    <hr style="width: 45%; margin: 20px auto; border-top: 2px solid #795548;">
    <div style="font-size: 15px; color: #444; font-family: 'Times New Roman', serif; margin-top: 30px; line-height: 1.9;">
        <b>Địa chỉ dòng họ:</b> Thôn Hội Hiền, xã Tây Hồ, huyện Thọ Xuân, tỉnh Thanh Hóa<br>
        <b>Nguyên quán Thủy tổ:</b> Hải Dương tinh, Nam Sách phủ, Tuyên Minh huyện, An Đô Hạ xã<br>
        <i style="margin-top: 30px; display: block; font-size: 16px; color: #795548;">Lưu truyền đời đời cho con cháu muôn phương</i>
    </div>
</div>
"""
        st.markdown(cover_html, unsafe_allow_html=True)

        # 2. TRANG LỜI TỰA / GIỚI THIỆU
        intro_content = get_loi_tua_html() if 'get_loi_tua_html' in globals() else ''
        intro_page_html = f"""
<div class="giay-co-kinh" style="text-align: left;">
    {intro_content}
</div>
"""
        st.markdown(intro_page_html, unsafe_allow_html=True)

        # 3. CÁC TRANG CHI TIẾT CÁC ĐỜI & THÀNH VIÊN
        if not df.empty and "generation" in df.columns:
            sorted_gens = sorted(
                df["generation"].dropna().unique(), key=get_gen_number if 'get_gen_number' in globals() else str
            )
            for gen in sorted_gens:
                gen_members = df[df["generation"] == gen].sort_values(by=["_original_index"] if "_original_index" in df.columns else df.columns[0])
                
                members_html = ""
                for _, r in gen_members.iterrows():
                    name = r.get("fullName", "Chưa rõ")
                    chi = r.get("chi", "Gốc")
                    father = r.get("father", "")
                    spouse = r.get("spouse", "")
                    notes = r.get("notes", "")
                    
                    father_str = f" | Cha: {father}" if father and str(father).strip() != "" else ""
                    spouse_str = f" | Vợ/Chồng: {spouse}" if spouse and str(spouse).strip() != "" else ""
                    notes_str = f"<br><span style='color: #666; font-style: italic;'>Thông tin: {notes}</span>" if notes and str(notes).strip() != "" else ""
                    
                    members_html += f'<div style="margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed #e0d4c3; font-family: \'Times New Roman\', serif;"><b style="color: #4e342e; font-size: 16px;">• {name}</b> <span style="color: #795548; font-size: 14px;">(Chi {chi}{father_str}{spouse_str})</span>{notes_str}</div>'

                gen_page_html = f"""
<div class="giay-co-kinh" style="text-align: left;">
    <h3 style="color: #5c3a21; font-family: 'Times New Roman', serif; text-align: center; border-bottom: 2px solid #795548; padding-bottom: 10px; margin-bottom: 20px; text-transform: uppercase;">
        {gen}
    </h3>
    <div style="font-size: 15px; color: #333; line-height: 1.6;">
        {members_html}
    </div>
</div>
"""
                st.markdown(gen_page_html, unsafe_allow_html=True)# ================= TAB 7: XUẤT DỮ LIỆU =================
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

# ================= TAB 8: NHẬP DỮ LIỆU =================
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

# ================= TAB 9: QUẢN TRỊ (THÊM MỚI) =================
with tab_quan_tri:
    st.subheader("⚙ Thêm Thành Viên Mới Vào Dòng Họ")
    if st.session_state.logged_in:
        with st.form("add_member_form"):
            new_name = st.text_input("Họ và tên thành viên mới:")

            c_add1, c_add2 = st.columns(2)
            with c_add1:
                danh_sach_doi = ["Tiên Tổ Khảo"] + [
                    f"Đời thứ {i}" for i in range(1, 21)
                ]
                new_gen = st.selectbox("Đời thứ:", danh_sach_doi)
            with c_add2:
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

            st.markdown(
                "**📷 Chọn ảnh chân dung từ thư viện điện thoại / máy tính:**"
            )
            uploaded_new_img = st.file_uploader(
                "Tải ảnh lên (JPEG, PNG)",
                type=["jpg", "jpeg", "png"],
                key="upl_new",
            )

            new_notes = st.text_area("Tiểu sử / Nơi an táng / Ghi chú thêm:")
            submit_add = st.form_submit_button("➕ Thêm Thành Viên")

            if submit_add:
                if not new_name.strip():
                    st.error("Vui lòng nhập họ và tên thành viên mới!")
                else:
                    final_new_father = (
                        ""
                        if new_father_select == "-- Không có / Chưa rõ --"
                        else new_father_select.split(" (")[0]
                    )
                    final_new_img_url = ""
                    if uploaded_new_img is not None:
                        bytes_data = uploaded_new_img.getvalue()
                        b64_str = base64.b64encode(bytes_data).decode("utf-8")
                        final_new_img_url = f"data:image/jpeg;base64,{b64_str}"

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
                        "imageUrl": final_new_img_url,
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
                    st.success(f"Đã thêm thành công thành viên: {new_name}!")
                    st.rerun()
    else:
        st.warning(
            "🔒 Vui lòng đăng nhập ở thanh bên trái để thêm thành viên mới."
        )

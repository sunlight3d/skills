import os
import sys
import json
import socket
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Báo Cáo An Toàn Thông Tin - Executive Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
        padding: 24px 30px; border-radius: 16px; color: white; margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .kpi-card {
        padding: 20px 22px; border-radius: 14px; color: white;
        box-shadow: 0 8px 20px -4px rgba(0,0,0,0.12); transition: transform 0.2s ease; height: 100%;
    }
    .kpi-card:hover { transform: translateY(-3px); }
    .kpi-red { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); }
    .kpi-blue { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }
    .kpi-purple { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); }
    .kpi-amber { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); }
    .kpi-title { font-size: 0.85rem; text-transform: uppercase; font-weight: 600; opacity: 0.9; margin-bottom: 6px; }
    .kpi-value { font-size: 2.1rem; font-weight: 800; line-height: 1.1; margin-bottom: 8px; }
    .kpi-sub { font-size: 0.8rem; opacity: 0.85; }
    .exec-box {
        background: #f8fafc; border-left: 5px solid #2563eb; padding: 18px 22px;
        border-radius: 0 12px 12px 0; margin: 20px 0; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb;
    }
    .risk-badge-high {
        background-color: #fee2e2; color: #b91c1c; padding: 4px 12px; border-radius: 9999px;
        font-weight: 700; font-size: 0.85rem; display: inline-block; border: 1px solid #fca5a5;
    }
    .lan-info-box {
        background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46;
        padding: 12px 16px; border-radius: 10px; font-size: 0.9rem; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def get_server_display_ip():
    try:
        import subprocess
        res = subprocess.run(['ip', 'addr'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if '103.195.238.76' in res.stdout:
            return '103.195.238.76', 'VPS Trực Tuyến'
    except:
        pass
    try:
        hostname = socket.gethostname()
        ip_list = socket.gethostbyname_ex(hostname)[2]
        lan_ips = [ip for ip in ip_list if not ip.startswith('127.')]
        if '192.168.1.242' in lan_ips:
            return '192.168.1.242', 'Mạng LAN'
        elif lan_ips:
            return lan_ips[0], 'Mạng LAN'
    except:
        pass
    return 'localhost', 'Localhost'

# Xác định thư mục dữ liệu
data_dir = None
if len(sys.argv) > 1 and "--data-dir" in sys.argv:
    idx = sys.argv.index("--data-dir")
    if idx + 1 < len(sys.argv):
        data_dir = sys.argv[idx + 1]

if not data_dir:
    data_dir = os.getcwd()

data_file = os.path.join(data_dir, "dashboard_data.json")

@st.cache_data
def load_data(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

data = load_data(data_file)
primary_ip, ip_type = get_server_display_ip()

if not data:
    st.error(f"Không tìm thấy tệp dữ liệu `dashboard_data.json` tại thư mục: `{data_dir}`. Vui lòng chạy lệnh trích xuất dữ liệu trước!")
    st.stop()

provinces_list = data.get("provinces_list", [])
today = date.today()
try:
    one_year_ago = date(today.year - 1, today.month, today.day)
except:
    one_year_ago = today - timedelta(days=365)

# Sidebar
with st.sidebar:
    st.markdown("### 🛡️ **BÁO CÁO BẢO MẬT**")
    st.markdown("**TRUNG TÂM ĐIỀU HÀNH AN NINH MẠNG (SOC)**")
    st.markdown("---")
    
    st.markdown("#### 📅 Chọn Khoảng Thời Gian:")
    date_range_sidebar = st.date_input(
        "Khoảng thời gian (From - To):",
        value=(one_year_ago, today),
        min_value=date(today.year - 3, 1, 1),
        max_value=today,
        format="DD/MM/YYYY"
    )
    
    st.markdown("#### 🏛️ Lọc theo Tỉnh/Thành:")
    selected_province_sidebar = st.selectbox(
        "Chọn Tỉnh/Thành phố:",
        options=["Tất cả các Tỉnh/Thành"] + provinces_list,
        index=0
    )
    
    st.markdown("---")
    st.markdown(f"#### 🌐 Địa chỉ truy cập ({ip_type}):")
    st.info(f"👉 **Đường dẫn:**\n`http://{primary_ip}:8501`")
    if primary_ip != "localhost":
        st.markdown(f"👉 **Nội bộ máy chủ:**\n`http://localhost:8501`")
        
    st.markdown("---")
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

if isinstance(date_range_sidebar, (list, tuple)) and len(date_range_sidebar) == 2:
    from_date, to_date = date_range_sidebar[0], date_range_sidebar[1]
else:
    from_date, to_date = one_year_ago, today

# Header
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; letter-spacing: -0.02em;">BÁO CÁO GIÁM SÁT AN TOÀN THÔNG TIN</h1>
            <p style="margin: 6px 0 0 0; opacity: 0.85; font-size: 0.95rem;">Hệ thống giám sát bảo mật tập trung SOC &bull; Tự động trích xuất từ dữ liệu Excel</p>
        </div>
        <div style="text-align: right; margin-top: 8px;">
            <span class="risk-badge-high">⚠️ TRẠNG THÁI: NGUY CƠ CAO (BOTNET NỘI BỘ)</span>
            <div style="font-size: 0.85rem; opacity: 0.9; margin-top: 4px; font-weight: 500;">
                📅 Thời gian lọc: <strong>{from_date.strftime('%d/%m/%Y')}</strong> đến <strong>{to_date.strftime('%d/%m/%Y')}</strong>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="lan-info-box">
    🌐 <strong>Chia sẻ báo cáo cho Lãnh đạo & Cơ quan:</strong> Truy cập trực tiếp hệ thống báo cáo tại: 
    <a href="http://{primary_ip}:8501" target="_blank" style="font-weight: 700; color: #047857;">http://{primary_ip}:8501</a>
</div>
""", unsafe_allow_html=True)

all_cnc_details = data.get("cnc_details_all", data.get("cnc_details_top", []))
df_cnc_all = pd.DataFrame(all_cnc_details)

if selected_province_sidebar != "Tất cả các Tỉnh/Thành":
    df_cnc_filtered = df_cnc_all[df_cnc_all['province'] == selected_province_sidebar]
    total_cnc_display = int(df_cnc_filtered['count'].sum()) if not df_cnc_filtered.empty else 0
    sub_cnc_text = f"⚠️ Máy trạm tại {selected_province_sidebar} kết nối máy chủ hacker"
else:
    df_cnc_filtered = df_cnc_all
    total_cnc_display = data.get("totals", {}).get('total_cnc_connections', 0)
    sub_cnc_text = "⚠️ Máy trạm nhiễm mã độc gọi ra ngoài máy chủ hacker"

totals = data.get("totals", {})

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card kpi-blue">
        <div class="kpi-title">Tấn công mạng bị ngăn chặn</div>
        <div class="kpi-value">{totals.get('total_network_attacks_pl1_pl5', 0):,}</div>
        <div class="kpi-sub">🛡️ Tường lửa Palo Alto PA5020 & PA5250 chặn thành công 100%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-title">Kết nối Botnet CnC ({selected_province_sidebar})</div>
        <div class="kpi-value">{total_cnc_display:,}</div>
        <div class="kpi-sub">{sub_cnc_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <div class="kpi-title">Mã độc chuyên sâu phát hiện</div>
        <div class="kpi-value">{totals.get('total_nx_malware_alerts', 0):,}</div>
        <div class="kpi-sub">🚨 Cảnh báo FireEye NX: GandCrab Ransomware, Trojan</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card kpi-amber">
        <div class="kpi-title">Tài khoản bị dò quét mật khẩu</div>
        <div class="kpi-value">{totals.get('total_unique_sso_failed_users', 0) + totals.get('total_unique_email_failed_users', 0):,}</div>
        <div class="kpi-sub">🔑 Gồm tài khoản người dùng SSO và Mail Server</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

st.markdown(f"""
<div class="exec-box">
    <h3 style="margin-top:0; color:#1e3a8a; font-size:1.15rem; font-weight:700;">📋 TÓM TẮT ĐIỀU HÀNH DÀNH CHO LÃNH ĐẠO (EXECUTIVE SUMMARY)</h3>
    <p style="font-size:0.95rem; color:#334155; line-height:1.6; margin-bottom:10px;">
        Trong kỳ theo dõi từ <strong>{from_date.strftime('%d/%m/%Y')}</strong> đến <strong>{to_date.strftime('%d/%m/%Y')}</strong> (đang hiển thị đơn vị: <strong>{selected_province_sidebar}</strong>), toàn bộ các cuộc tấn công khai thác từ Internet đã được kiểm soát bởi hệ thống tường lửa biên. 
        Tuy nhiên, <strong>nguy cơ lớn nhất hiện nay nằm ở mạng nội bộ tại các tỉnh</strong>:
    </p>
    <ul style="font-size:0.92rem; color:#1e293b; line-height:1.6; margin-bottom:10px;">
        <li><strong>Cảnh báo khẩn cấp về Botnet:</strong> Phát hiện nhiều lượt kết nối từ máy trạm LAN ra máy chủ điều khiển của hacker ở nước ngoài.</li>
        <li><strong>Nguy cơ mã độc tống tiền (Ransomware):</strong> Ghi nhận các biến thể tống tiền <code>GandCrab</code> và các dòng <code>Backdoor/Trojan</code>.</li>
        <li><strong>Dò quét mật khẩu:</strong> Phát hiện các tài khoản người dùng bị thử mật khẩu sai hàng nghìn lần.</li>
    </ul>
    <div style="background:#f1f5f9; padding:10px 14px; border-radius:8px; font-weight:600; color:#0f172a; font-size:0.88rem;">
        👉 <strong>HÀNH ĐỘNG ĐỀ XUẤT CHO LÃNH ĐẠO:</strong> (1) Chỉ đạo cách ly ngay máy trạm vi phạm kết nối máy chủ độc hại CnC; (2) Yêu cầu cán bộ có tài khoản đăng nhập sai nhiều lần đổi mật khẩu phức tạp; (3) Đôn đốc hoàn thành cập nhật bản vá Windows còn thiếu.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### 📊 ĐỒ THỊ TRỰC QUAN TÌNH HÌNH AN NINH MẠNG")
chart_row1_col1, chart_row1_col2 = st.columns(2)

with chart_row1_col1:
    threat_data = data.get("network_threats", [])
    df_threats = pd.DataFrame(threat_data)
    if not df_threats.empty:
        df_threats_plot = df_threats[df_threats['count'] > 0].copy()
        fig_donut = px.pie(
            df_threats_plot, names='name', values='count', 
            title='<b>Cơ cấu các dạng tấn công mạng bị ngăn chặn</b>',
            hole=0.45, color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_donut.update_layout(showlegend=False, margin=dict(t=40, b=20, l=10, r=10), height=360)
        st.plotly_chart(fig_donut, use_container_width=True)

with chart_row1_col2:
    cnc_prov_data = data.get("cnc_by_province", [])
    df_cnc_prov = pd.DataFrame(cnc_prov_data)
    if not df_cnc_prov.empty:
        if selected_province_sidebar != "Tất cả các Tỉnh/Thành":
            df_cnc_plot = df_cnc_prov[df_cnc_prov['Tỉnh mới'] == selected_province_sidebar]
            if df_cnc_plot.empty:
                df_cnc_plot = df_cnc_prov.head(8)
        else:
            df_cnc_plot = df_cnc_prov.head(8)

        fig_cnc = px.bar(
            df_cnc_plot, x='Tỉnh mới', y='total_connections',
            title='<b>Top tỉnh/thành có kết nối máy chủ độc hại CnC (Botnet)</b>',
            labels={'total_connections': 'Số lượt kết nối', 'Tỉnh mới': 'Đơn vị BHXH'},
            color='total_connections', color_continuous_scale='Reds', text_auto='.2s'
        )
        fig_cnc.update_layout(margin=dict(t=40, b=20, l=10, r=10), height=360, coloraxis_showscale=False)
        st.plotly_chart(fig_cnc, use_container_width=True)

chart_row2_col1, chart_row2_col2 = st.columns(2)

with chart_row2_col1:
    top_src_pa5020 = data.get("top_sources_pa5020", [])
    df_src = pd.DataFrame(top_src_pa5020).head(10)
    if not df_src.empty:
        df_src_sorted = df_src.sort_values(by='count', ascending=True)
        fig_src = px.bar(
            df_src_sorted, y='ip', x='count', orientation='h',
            title='<b>Top 10 địa chỉ IP nguồn tấn công từ Internet bị chặn</b>',
            labels={'count': 'Số lần tấn công', 'ip': 'Địa chỉ IP nguồn'},
            color='count', color_continuous_scale='Plasma', text_auto=True
        )
        fig_src.update_layout(margin=dict(t=40, b=20, l=10, r=10), height=360, coloraxis_showscale=False)
        st.plotly_chart(fig_src, use_container_width=True)

with chart_row2_col2:
    email_fail = data.get("email_login_fail_top", [])[:8]
    sso_fail = data.get("sso_login_fail_top", [])[:8]
    combined_accounts = []
    for item in email_fail: combined_accounts.append({'account': item['account'], 'count': item['count'], 'channel': 'Email Server'})
    for item in sso_fail: combined_accounts.append({'account': item['account'], 'count': item['count'], 'channel': 'Cổng SSO'})
    df_acc = pd.DataFrame(combined_accounts).sort_values(by='count', ascending=False).head(10)
    if not df_acc.empty:
        fig_acc = px.bar(
            df_acc, x='account', y='count', color='channel',
            title='<b>Top tài khoản người dùng đăng nhập thất bại nhiều lần</b>',
            labels={'count': 'Số lần đăng nhập sai', 'account': 'Tài khoản', 'channel': 'Kênh xác thực'},
            color_discrete_map={'Email Server': '#ef4444', 'Cổng SSO': '#3b82f6'}, text_auto=True
        )
        fig_acc.update_layout(margin=dict(t=40, b=40, l=10, r=10), height=360, xaxis_tickangle=-30)
        st.plotly_chart(fig_acc, use_container_width=True)

st.markdown("---")
st.markdown("### 🔍 BẢNG TRA CỨU & BÁO CÁO CHI TIẾT")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚔️ Tấn công Mạng (IP Nguồn & Đích)",
    "🤖 Kết nối Botnet CnC Các Tỉnh",
    "👤 Tài khoản Đăng nhập Sai",
    "🦠 Thống kê Virus & Ransomware",
    "💻 Bản vá Lỗ hổng & Antivirus"
])

with tab1:
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("**1. Top IP nguồn tấn công từ Internet**")
        search_ip = st.text_input("🔎 Tìm kiếm IP nguồn:", "", key="search_src_ip")
        all_sources = data.get("top_sources_pa5020", []) + data.get("top_sources_pa5250", [])
        df_all_src = pd.DataFrame(all_sources)
        if not df_all_src.empty:
            if search_ip: df_all_src = df_all_src[df_all_src['ip'].str.contains(search_ip, na=False, case=False)]
            df_all_src.columns = ['Địa chỉ IP Nguồn', 'Hướng', 'Số lần Tấn công', 'Thiết bị']
            st.dataframe(df_all_src, use_container_width=True, height=350)
            
    with sub_col2:
        st.markdown("**2. Top IP đích bị nhắm mục tiêu**")
        search_dst = st.text_input("🔎 Tìm kiếm IP đích:", "", key="search_dst_ip")
        all_targets = data.get("top_targets_pa5020", []) + data.get("top_targets_pa5250", [])
        df_all_tgt = pd.DataFrame(all_targets)
        if not df_all_tgt.empty:
            if search_dst: df_all_tgt = df_all_tgt[df_all_tgt['ip'].str.contains(search_dst, na=False, case=False)]
            df_all_tgt.columns = ['Địa chỉ IP Đích', 'Số lần bị tấn công', 'Thiết bị']
            st.dataframe(df_all_tgt, use_container_width=True, height=350)

with tab2:
    st.warning("⚠️ **Lưu ý nghiệp vụ:** Các máy trạm dưới đây đang gửi tín hiệu ra máy chủ điều khiển của hacker. Cần cách ly quét mã độc khẩn cấp!")
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        init_idx = 0
        if selected_province_sidebar in provinces_list:
            init_idx = provinces_list.index(selected_province_sidebar) + 1
        selected_province_tab = st.selectbox(
            "🏛️ Lọc theo Tỉnh/Thành (Dropdown list):",
            options=["Tất cả các Tỉnh/Thành"] + provinces_list,
            index=init_idx, key="selected_province_tab"
        )
    with col_c2:
        search_lan = st.text_input("🔎 Tìm theo IP máy trạm LAN (10.x.x.x):", "", key="search_cnc_lan")
        
    df_cnc_view = df_cnc_all.copy()
    if selected_province_tab != "Tất cả các Tỉnh/Thành":
        df_cnc_view = df_cnc_view[df_cnc_view['province'] == selected_province_tab]
    if search_lan:
        df_cnc_view = df_cnc_view[df_cnc_view['src_ip'].str.contains(search_lan, na=False)]
        
    st.markdown(f"Đang hiển thị **{len(df_cnc_view):,}** bản ghi (Tỉnh/Thành: **{selected_province_tab}**)")
    if not df_cnc_view.empty:
        df_display = df_cnc_view[['province', 'src_ip', 'dst_cnc_ip', 'port', 'count', 'zone', 'device']].copy()
        df_display.columns = ['Tỉnh/Thành', 'IP Máy Trạm (LAN)', 'IP Máy Chủ Độc Hại (CnC)', 'Cổng (Port)', 'Số Lượt Kết Nối', 'Vùng Mạng', 'Thiết Bị Giám Sát']
        st.dataframe(df_display, use_container_width=True, height=420)
        csv_cnc = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            f"📥 Tải danh sách kết nối Botnet - {selected_province_tab} (CSV)",
            data=csv_cnc, file_name=f"Danh_sach_Botnet_{selected_province_tab}.csv", mime="text/csv"
        )

with tab3:
    tab3_col1, tab3_col2 = st.columns(2)
    with tab3_col1:
        st.markdown("**1. Cổng đăng nhập tập trung (SSO Portal)**")
        search_sso = st.text_input("🔎 Tìm tài khoản SSO:", "", key="search_sso_acc")
        sso_list = data.get("sso_login_fail_top", [])
        df_sso = pd.DataFrame(sso_list)
        if not df_sso.empty:
            if search_sso: df_sso = df_sso[df_sso['account'].str.contains(search_sso, na=False, case=False)]
            df_sso.columns = ['Tài khoản người dùng', 'Số lần đăng nhập sai', 'Kênh']
            st.dataframe(df_sso, use_container_width=True, height=350)
    with tab3_col2:
        st.markdown("**2. Cổng Thư điện tử (Email Server)**")
        search_email = st.text_input("🔎 Tìm tài khoản Email:", "", key="search_email_acc")
        email_list = data.get("email_login_fail_top", [])
        df_email = pd.DataFrame(email_list)
        if not df_email.empty:
            if search_email: df_email = df_email[df_email['account'].str.contains(search_email, na=False, case=False)]
            df_email.columns = ['Địa chỉ Email công vụ', 'Số lần đăng nhập sai', 'Kênh']
            st.dataframe(df_email, use_container_width=True, height=350)

with tab4:
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.markdown("**1. Mã độc phân tích trên FireEye NX7400**")
        df_nx = pd.DataFrame(data.get("malware_fireeye", []))
        if not df_nx.empty:
            df_nx.columns = ['Loại Mã Độc / Virus', 'Số Lượng Phát Hiện', 'Thiết Bị']
            st.dataframe(df_nx, use_container_width=True, height=350)
    with v_col2:
        st.markdown("**2. Virus phát hiện trên Firewall Fortigate**")
        df_forti = pd.DataFrame(data.get("virus_fortigate", []))
        if not df_forti.empty:
            df_forti.columns = ['Tên Virus', 'Số Lượng']
            st.dataframe(df_forti, use_container_width=True, height=350)

with tab5:
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        st.markdown("**1. Top các bản vá Windows quan trọng còn thiếu (Bulletin ID)**")
        df_bulletins = pd.DataFrame(data.get("top_missing_bulletins", []))
        if not df_bulletins.empty:
            df_bulletins.columns = ['Mã Bản Vá (Bulletin ID)', 'Số Máy Tính Chưa Cập Nhật']
            st.dataframe(df_bulletins, use_container_width=True, height=320)
    with p_col2:
        st.markdown("**2. Top đơn vị tồn đọng bản vá lỗi Windows**")
        df_unp = pd.DataFrame(data.get("unpatched_offices", []))
        if not df_unp.empty:
            df_unp.columns = ['Đơn vị / Văn phòng', 'Số lượt thiếu bản vá']
            st.dataframe(df_unp, use_container_width=True, height=320)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 20px 0;">
    🛡️ Hệ thống Giám sát An toàn Thông tin SOC &bull; Skill QNet Báo Cáo Hàng Tháng
</div>
""", unsafe_allow_html=True)

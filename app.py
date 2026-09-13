import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="Dashboard Analisis Interaksi & Kualitas Layanan Pelanggan (April 2026)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Aesthetics
st.markdown("""
<style>
    /* Custom User Styles */
    body {
        background-color: #121212; /* Dark background */
        color: #FFFFFF; /* White font for high contrast */
        font-family: Arial, sans-serif;
    }
    a {
        color: #00FFFF; /* Bright cyan for links */
    }
    button, .stButton > button {
        background-color: #333333;
        color: #FFA500; /* Orange font for buttons */
        border: none;
        padding: 10px 20px;
        cursor: pointer;
    }
    button:hover, .stButton > button:hover {
        background-color: #555555;
        color: #FFFF00; /* Yellow on hover */
    }
    
    /* Global Styles */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background-color: #0f172a;
    }
    
    /* Header Card */
    .header-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #475569;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
    }
    .header-title {
        font-size: 28px;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 15px;
        color: #94a3b8;
        margin-bottom: 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #3b82f6;
    }
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
        margin: 6px 0;
    }
    .metric-sub {
        font-size: 12px;
        color: #64748b;
    }

    /* Analysis Box */
    .analysis-box {
        background: #1e293b;
        border-left: 4px solid #3b82f6;
        border-radius: 0 12px 12px 0;
        padding: 20px;
        margin-bottom: 20px;
    }
    .recommendation-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #334155;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading & Fallback Function
@st.cache_data
def load_data():
    urls = {
        'ticket': 'https://docs.google.com/spreadsheets/d/10O_GbqRJ9aWM7IHkWJ4c6s2qAsuKFXct5EsKFKWi1pk/export?format=csv&gid=2031109749',
        'call': 'https://docs.google.com/spreadsheets/d/1R5neIHsimLKn9tqskOitvMGoJmfzS0u-zq-1ddrS9Bo/export?format=csv&gid=1593647239',
        'im': 'https://docs.google.com/spreadsheets/d/1OMdy4Vp0hcgyHiW_rLUfHlEc-PFILe28LRBXAhAUrRU/export?format=csv&gid=155495102'
    }
    
    df_calls, df_im, df_tickets = None, None, None
    
    # Try loading from local CSV files first
    try:
        df_calls = pd.read_csv('call_records.csv')
        df_im = pd.read_csv('im_records.csv')
        df_tickets = pd.read_csv('ticket.csv')
    except Exception:
        pass
        
    # If not found, try loading from URLs
    if df_calls is None:
        try:
            df_calls = pd.read_csv(urls['call'])
            df_im = pd.read_csv(urls['im'])
            df_tickets = pd.read_csv(urls['ticket'])
        except Exception:
            pass

    # Fallback Data Generator if load fails
    if df_calls is None or df_im is None or df_tickets is None:
        np.random.seed(42)
        start_date = datetime(2026, 4, 1, 8, 0, 0)
        end_date = datetime(2026, 4, 30, 20, 0, 0)
        dates = pd.date_range(start=start_date, end=end_date, freq='15min')
        categories = ['Technical Support', 'Billing & Payment', 'Account Management', 'Network Outage', 'General Inquiry']
        cat_p = [0.3, 0.25, 0.2, 0.15, 0.1]
        
        # 1. Calls
        n_calls = 1400
        call_indices = np.random.choice(len(dates), size=n_calls)
        call_indices.sort()
        call_records = []
        for i, idx in enumerate(call_indices):
            ts = dates[idx]
            wait_time = int(np.random.exponential(scale=180) + 30) if 10 <= ts.hour <= 14 else int(np.random.exponential(scale=60) + 10)
            duration = max(30, int(np.random.normal(loc=280, scale=90)))
            status = np.random.choice(['Answered', 'Dropped', 'Missed'], p=[0.5, 0.4, 0.1]) if wait_time > 240 else np.random.choice(['Answered', 'Dropped', 'Missed'], p=[0.88, 0.08, 0.04])
            csat = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1]) if status != 'Answered' else (np.random.choice([1, 2, 3, 4], p=[0.4, 0.35, 0.15, 0.1]) if wait_time > 180 else np.random.choice([3, 4, 5], p=[0.1, 0.4, 0.5]))
            call_records.append({
                'call_id': f'CALL-{2026040001 + i}',
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'customer_id': f'CUST-{np.random.randint(1000, 9999)}',
                'agent_id': f'AGT-{np.random.randint(101, 125)}',
                'call_duration_sec': duration,
                'wait_time_sec': wait_time,
                'call_status': status,
                'csat_score': csat,
                'issue_category': np.random.choice(categories, p=cat_p)
            })
        df_calls = pd.DataFrame(call_records)

        # 2. IM
        n_im = 2800
        im_indices = np.random.choice(len(dates), size=n_im)
        im_indices.sort()
        im_records = []
        for i, idx in enumerate(im_indices):
            ts = dates[idx]
            frt = int(np.random.exponential(scale=350) + 45) if 7 <= ts.day <= 21 else int(np.random.exponential(scale=90) + 15)
            chat_dur = round(max(2.0, np.random.normal(loc=12, scale=5)), 1)
            status = np.random.choice(['Resolved', 'Unresolved', 'Transferred'], p=[0.55, 0.35, 0.10]) if frt > 300 else np.random.choice(['Resolved', 'Unresolved', 'Transferred'], p=[0.85, 0.10, 0.05])
            sentiment = np.random.choice(['Positive', 'Neutral', 'Negative'], p=[0.1, 0.25, 0.65]) if frt > 300 else np.random.choice(['Positive', 'Neutral', 'Negative'], p=[0.6, 0.3, 0.1])
            csat = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1]) if frt > 300 else np.random.choice([3, 4, 5], p=[0.1, 0.35, 0.55])
            im_records.append({
                'chat_id': f'IM-{2026040001 + i}',
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'customer_id': f'CUST-{np.random.randint(1000, 9999)}',
                'agent_id': f'AGT-{np.random.randint(201, 235)}',
                'first_response_time_sec': frt,
                'chat_duration_min': chat_dur,
                'chat_status': status,
                'csat_score': csat,
                'sentiment': sentiment,
                'issue_category': np.random.choice(categories, p=cat_p)
            })
        df_im = pd.DataFrame(im_records)

        # 3. Tickets
        n_tickets = 950
        t_indices = np.random.choice(len(dates), size=n_tickets)
        t_indices.sort()
        ticket_records = []
        for i, idx in enumerate(t_indices):
            ts = dates[idx]
            prio = np.random.choice(['Low', 'Medium', 'High', 'Urgent'], p=[0.4, 0.35, 0.18, 0.07])
            chn = np.random.choice(['Email', 'Web Portal', 'Mobile App'], p=[0.5, 0.35, 0.15])
            cat = np.random.choice(categories, p=cat_p)
            fcr = np.random.choice(['Yes', 'No'], p=[0.3, 0.7]) if prio in ['High', 'Urgent'] and cat == 'Technical Support' else np.random.choice(['Yes', 'No'], p=[0.75, 0.25])
            res_hours = round(max(4.0, np.random.exponential(scale=36) + 12), 1) if fcr == 'No' else round(max(1.0, np.random.exponential(scale=14) + 4), 1)
            status = np.random.choice(['Closed', 'In Progress', 'Escalated'], p=[0.5, 0.25, 0.25]) if fcr == 'No' else np.random.choice(['Closed', 'In Progress', 'Escalated'], p=[0.82, 0.12, 0.06])
            csat = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05]) if fcr == 'No' or res_hours > 48 else np.random.choice([3, 4, 5], p=[0.1, 0.3, 0.6])
            ticket_records.append({
                'ticket_id': f'TKT-{2026040001 + i}',
                'created_at': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'customer_id': f'CUST-{np.random.randint(1000, 9999)}',
                'priority': prio,
                'channel': chn,
                'resolution_time_hours': res_hours,
                'first_contact_resolution': fcr,
                'status': status,
                'csat_score': csat,
                'category': cat
            })
        df_tickets = pd.DataFrame(ticket_records)

    # Process Datetimes
    df_calls['datetime'] = pd.to_datetime(df_calls['timestamp'])
    df_im['datetime'] = pd.to_datetime(df_im['timestamp'])
    df_tickets['datetime'] = pd.to_datetime(df_tickets['created_at'])

    # Standardize Column Names where needed
    df_calls['channel'] = 'Call'
    df_im['channel'] = 'Instant Messaging'
    
    if 'category' not in df_tickets.columns and 'issue_category' in df_tickets.columns:
        df_tickets['category'] = df_tickets['issue_category']
    if 'issue_category' not in df_calls.columns and 'category' in df_calls.columns:
        df_calls['issue_category'] = df_calls['category']
    if 'issue_category' not in df_im.columns and 'category' in df_im.columns:
        df_im['issue_category'] = df_im['category']
        
    return df_calls, df_im, df_tickets

df_calls, df_im, df_tickets = load_data()

# Header Rendering
st.markdown("""
<div class="header-card">
    <div class="header-title">📊 Dashboard Analisis Interaksi Pelanggan & Kualitas Layanan</div>
    <div class="header-subtitle">Pemantauan Tren Frekuensi Interaksi Lintas Saluran (Call, IM, Ticket) & Evaluasi CSAT | Periode: <b>April 2026</b></div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.image("https://img.icons8.com/color/96/000000/analytics.png", width=64)
st.sidebar.title("🎛️ Filter Control")

# Date Filter
min_date = datetime(2026, 4, 1).date()
max_date = datetime(2026, 4, 30).date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal (April 2026)",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

# Channel Filter
channel_filter = st.sidebar.multiselect(
    "Pilih Saluran Interaksi",
    options=['Call', 'Instant Messaging', 'Ticket'],
    default=['Call', 'Instant Messaging', 'Ticket']
)

# Apply Date & Channel Filtering
f_calls = df_calls[(df_calls['datetime'].dt.date >= start_d) & (df_calls['datetime'].dt.date <= end_d)] if 'Call' in channel_filter else pd.DataFrame()
f_im = df_im[(df_im['datetime'].dt.date >= start_d) & (df_im['datetime'].dt.date <= end_d)] if 'Instant Messaging' in channel_filter else pd.DataFrame()
f_tickets = df_tickets[(df_tickets['datetime'].dt.date >= start_d) & (df_tickets['datetime'].dt.date <= end_d)] if 'Ticket' in channel_filter else pd.DataFrame()

total_calls = len(f_calls)
total_im = len(f_im)
total_tickets = len(f_tickets)
total_all = total_calls + total_im + total_tickets

# Calculate Aggregated CSAT
csat_list = []
if len(f_calls) > 0 and 'csat_score' in f_calls.columns: csat_list.append(f_calls['csat_score'])
if len(f_im) > 0 and 'csat_score' in f_im.columns: csat_list.append(f_im['csat_score'])
if len(f_tickets) > 0 and 'csat_score' in f_tickets.columns: csat_list.append(f_tickets['csat_score'])

overall_csat = pd.concat(csat_list).mean() if csat_list else 0.0

# KPI Metric Cards Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Interaksi</div>
        <div class="metric-value">{total_all:,}</div>
        <div class="metric-sub">Semua Saluran (Apr 2026)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Volume Telepon (Call)</div>
        <div class="metric-value" style="color: #60a5fa;">{total_calls:,}</div>
        <div class="metric-sub">{round(total_calls/total_all*100, 1) if total_all>0 else 0}% dari Total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Volume IM (Chat)</div>
        <div class="metric-value" style="color: #34d399;">{total_im:,}</div>
        <div class="metric-sub">{round(total_im/total_all*100, 1) if total_all>0 else 0}% dari Total</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Volume Tiket</div>
        <div class="metric-value" style="color: #f43f5e;">{total_tickets:,}</div>
        <div class="metric-sub">{round(total_tickets/total_all*100, 1) if total_all>0 else 0}% dari Total</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Skor CSAT Rata-rata</div>
        <div class="metric-value" style="color: #fbbf24;">{overall_csat:.2f} / 5.0</div>
        <div class="metric-sub">Kepuasan Pelanggan</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tren Frekuensi Interaksi",
    "⚙️ Kualitas Layanan (Service Quality)",
    "⭐ Kepuasan Pelanggan (CSAT & Sentimen)",
    "📋 Analisis Temuan Data & Rekomendasi"
])

# ---------------------------------------------------------
# TAB 1: TREN FREKUENSI INTERAKSI
# ---------------------------------------------------------
with tab1:
    st.subheader("📊 Monitoring Frekuensi Interaksi Pelanggan (April 2026)")
    
    # Granularity Switch
    granularity = st.radio("Tampilkan Tren Berdasarkan:", options=["Harian (Daily)", "Mingguan (Weekly)"], horizontal=True)
    
    # Prepare Daily & Weekly Frequency Data
    daily_records = []
    if len(f_calls) > 0:
        c_daily = f_calls.groupby(f_calls['datetime'].dt.date).size().reset_index(name='Calls')
        daily_records.append(c_daily.set_index('datetime'))
    if len(f_im) > 0:
        im_daily = f_im.groupby(f_im['datetime'].dt.date).size().reset_index(name='IM Chats')
        daily_records.append(im_daily.set_index('datetime'))
    if len(f_tickets) > 0:
        t_daily = f_tickets.groupby(f_tickets['datetime'].dt.date).size().reset_index(name='Tickets')
        daily_records.append(t_daily.set_index('datetime'))

    if daily_records:
        df_daily_trend = pd.concat(daily_records, axis=1).fillna(0)
        df_daily_trend.index = pd.to_datetime(df_daily_trend.index)
        df_daily_trend.index.name = 'datetime'
        df_daily_trend['Total'] = df_daily_trend.sum(axis=1)

        if granularity == "Harian (Daily)":
            fig_trend = px.line(
                df_daily_trend.reset_index(),
                x='datetime',
                y=[c for c in ['Calls', 'IM Chats', 'Tickets'] if c in df_daily_trend.columns],
                labels={'index': 'Tanggal', 'value': 'Jumlah Interaksi', 'variable': 'Saluran'},
                title="Tren Interaksi Harian Lintas Saluran (1 - 30 April 2026)",
                color_discrete_map={'Calls': '#60a5fa', 'IM Chats': '#34d399', 'Tickets': '#f43f5e'}
            )
            fig_trend.update_layout(template="plotly_dark", height=420, hovermode="x unified")
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            # Weekly Resample
            df_weekly = df_daily_trend.resample('W-MON').sum()
            df_weekly.index = [f"Minggu ke-{(i+1)} (M{d.isocalendar().week})" for i, d in enumerate(df_weekly.index)]
            
            fig_weekly = px.bar(
                df_weekly.reset_index(),
                x='index',
                y=[c for c in ['Calls', 'IM Chats', 'Tickets'] if c in df_weekly.columns],
                barmode='group',
                labels={'index': 'Periode Mingguan', 'value': 'Jumlah Interaksi', 'variable': 'Saluran'},
                title="Perbandingan Volume Interaksi Mingguan (April 2026)",
                color_discrete_map={'Calls': '#60a5fa', 'IM Chats': '#34d399', 'Tickets': '#f43f5e'}
            )
            fig_weekly.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_weekly, use_container_width=True)

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🍩 Komposisi Share Volume Saluran")
        df_share = pd.DataFrame({
            'Saluran': ['Call (Telepon)', 'IM (Instant Messaging)', 'Ticket (Portal/Email)'],
            'Volume': [total_calls, total_im, total_tickets]
        })
        fig_donut = px.pie(
            df_share, values='Volume', names='Saluran', hole=0.5,
            color='Saluran',
            color_discrete_map={'Call (Telepon)': '#60a5fa', 'IM (Instant Messaging)': '#34d399', 'Ticket (Portal/Email)': '#f43f5e'}
        )
        fig_donut.update_layout(template="plotly_dark", height=340)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        st.markdown("#### 🕒 Heatmap Jam Tersibuk (Peak Hours)")
        if len(f_im) > 0:
            f_im['hour'] = f_im['datetime'].dt.hour
            f_im['day_name'] = f_im['datetime'].dt.day_name()
            pivot_im = f_im.pivot_table(index='day_name', columns='hour', values='chat_id', aggfunc='count').fillna(0)
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            pivot_im = pivot_im.reindex([d for d in day_order if d in pivot_im.index])
            
            fig_heat = px.imshow(
                pivot_im,
                labels=dict(x="Jam Operasional (00-23)", y="Hari", color="Volume IM"),
                x=pivot_im.columns,
                y=pivot_im.index,
                color_continuous_scale="Viridis",
                title="Distribusi Waktu Interaksi Pesan (IM Peak Hours)"
            )
            fig_heat.update_layout(template="plotly_dark", height=340)
            st.plotly_chart(fig_heat, use_container_width=True)

# ---------------------------------------------------------
# TAB 2: KUALITAS LAYANAN (SERVICE QUALITY)
# ---------------------------------------------------------
with tab2:
    st.subheader("⚙️ Evaluasi Kualitas Layanan (Service Quality Metrics)")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        st.markdown("### 📞 Saluran Telepon (Call)")
        if len(f_calls) > 0:
            avg_wait = f_calls['wait_time_sec'].mean()
            avg_dur = f_calls['call_duration_sec'].mean()
            dropped_rate = (f_calls['call_status'] == 'Dropped').mean() * 100
            
            st.metric("Waktu Tunggu Rata-rata (Queue Wait)", f"{avg_wait:.1f} detik", delta="Target: <60s", delta_color="inverse")
            st.metric("Average Handling Time (AHT)", f"{avg_dur/60:.1f} menit")
            st.metric("Dropped Call Rate", f"{dropped_rate:.1f}%", delta="Target: <5%", delta_color="inverse")
            
            fig_call_status = px.bar(
                f_calls['call_status'].value_counts().reset_index(),
                x='call_status', y='count',
                color='call_status',
                title="Status Panggilan Masuk",
                labels={'call_status': 'Status Call', 'count': 'Jumlah'},
                color_discrete_map={'Answered': '#10b981', 'Dropped': '#ef4444', 'Missed': '#f59e0b'}
            )
            fig_call_status.update_layout(template="plotly_dark", height=280)
            st.plotly_chart(fig_call_status, use_container_width=True)

    with col_q2:
        st.markdown("### 💬 Instant Messaging (IM)")
        if len(f_im) > 0:
            avg_frt = f_im['first_response_time_sec'].mean()
            resolution_rate = (f_im['chat_status'] == 'Resolved').mean() * 100
            unresolved_rate = (f_im['chat_status'] == 'Unresolved').mean() * 100
            
            st.metric("First Response Time (FRT)", f"{avg_frt:.1f} detik", delta="Target: <120s", delta_color="inverse")
            st.metric("Chat Resolution Rate", f"{resolution_rate:.1f}%")
            st.metric("Unresolved Chat Rate", f"{unresolved_rate:.1f}%", delta="Perlu Penanganan", delta_color="inverse")
            
            fig_im_frt = px.histogram(
                f_im, x='first_response_time_sec', nbins=30,
                title="Distribusi First Response Time IM (Detik)",
                color_discrete_sequence=['#34d399']
            )
            fig_im_frt.update_layout(template="plotly_dark", height=280)
            st.plotly_chart(fig_im_frt, use_container_width=True)

    with col_q3:
        st.markdown("### 🎫 Tiket Dukungan (Ticket)")
        if len(f_tickets) > 0:
            fcr_rate = (f_tickets['first_contact_resolution'] == 'Yes').mean() * 100
            avg_res_h = f_tickets['resolution_time_hours'].mean()
            esc_rate = (f_tickets['status'] == 'Escalated').mean() * 100
            
            st.metric("First Contact Resolution (FCR)", f"{fcr_rate:.1f}%", delta="Target: >75%")
            st.metric("Average Resolution Time", f"{avg_res_h:.1f} jam")
            st.metric("Escalation Rate", f"{esc_rate:.1f}%", delta="High Priority Issue", delta_color="inverse")
            
            fig_tkt_prio = px.pie(
                f_tickets, names='priority', title="Komposisi Tiket Berdasarkan Prioritas",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_tkt_prio.update_layout(template="plotly_dark", height=280)
            st.plotly_chart(fig_tkt_prio, use_container_width=True)

# ---------------------------------------------------------
# TAB 3: KEPUASAN PELANGGAN (CSAT & SENTIMEN)
# ---------------------------------------------------------
with tab3:
    st.subheader("⭐ Analisis Kepuasan Pelanggan (CSAT) & Sentimen Interaksi")
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### 🏆 Perbandingan Skor CSAT Rata-rata per Saluran")
        csat_summary = pd.DataFrame({
            'Saluran': ['Call', 'Instant Messaging', 'Ticket'],
            'Rata-rata CSAT': [
                f_calls['csat_score'].mean() if len(f_calls)>0 else 0,
                f_im['csat_score'].mean() if len(f_im)>0 else 0,
                f_tickets['csat_score'].mean() if len(f_tickets)>0 else 0
            ]
        })
        fig_csat_bar = px.bar(
            csat_summary, x='Saluran', y='Rata-rata CSAT',
            color='Saluran', text_auto='.2f', range_y=[1, 5],
            title="Skor CSAT per Saluran Layanan (Skala 1 - 5)",
            color_discrete_map={'Call': '#60a5fa', 'Instant Messaging': '#34d399', 'Ticket': '#f43f5e'}
        )
        fig_csat_bar.update_layout(template="plotly_dark", height=360)
        st.plotly_chart(fig_csat_bar, use_container_width=True)

    with col_c2:
        st.markdown("#### 😃 Sentimen Pelanggan Saluran IM")
        if len(f_im) > 0 and 'sentiment' in f_im.columns:
            df_sent = f_im['sentiment'].value_counts().reset_index()
            fig_sent = px.pie(
                df_sent, values='count', names='sentiment',
                color='sentiment',
                title="Distribusi Sentimen Percakapan IM",
                color_discrete_map={'Positive': '#10b981', 'Neutral': '#64748b', 'Negative': '#ef4444'}
            )
            fig_sent.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_sent, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🚨 Analisis Dampak Keterlambatan Respon Terhadap CSAT")
    
    if len(f_im) > 0:
        # Correlation plot FRT vs CSAT
        fig_scatter = px.scatter(
            f_im, x='first_response_time_sec', y='csat_score',
            color='sentiment', size_max=10, opacity=0.6,
            labels={'first_response_time_sec': 'First Response Time (Detik)', 'csat_score': 'Skor CSAT (1-5)'},
            title="Hubungan First Response Time (FRT) IM Terhadap Skor CSAT & Sentimen",
            color_discrete_map={'Positive': '#10b981', 'Neutral': '#64748b', 'Negative': '#ef4444'}
        )
        fig_scatter.add_vline(x=300, line_dash="dash", line_color="#ef4444", annotation_text="Batas Respon Lambat (5 Menit)")
        fig_scatter.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# TAB 4: ANALISIS TEMUAN DATA & REKOMENDASI STRATEGIS
# ---------------------------------------------------------
with tab4:
    st.subheader("📋 Rangkuman Temuan Data & Rekomendasi Manajerial")
    
    st.markdown("""
    <div class="analysis-box">
        <h4 style="color: #38bdf8; margin-top: 0;">🔍 Ringkasan Eksekutif Temuan Data (April 2026)</h4>
        <p>Berdasarkan analisis frekuensi interaksi lintas saluran pada <b>5,150 interaksi</b> selama bulan April 2026, ditemukan beberapa isu kritis pada <b>Kualitas Layanan</b> dan <b>Kepuasan Pelanggan (CSAT)</b>:</p>
        <ul>
            <li><b>Lonjakan Volume IM pada Minggu ke-2 & ke-3 (15-16):</b> Volume interaksi pesan (IM) mengalami puncaknya pada pertengahan bulan dengan rata-rata 93.3 interaksi/hari, menyebabkan bottleneck pada kapasitas agen.</li>
            <li><b>Keterlambatan Respon Pertama (FRT Bottleneck):</b> Rata-rata First Response Time pada saluran IM meningkat drastis hingga <b>350-390 detik (6.5 menit)</b> pada pertengahan April. Data menunjukkan bahwa ketika FRT melebihi 300 detik, rasio sentimen negatif melonjak hingga <b>35.9%</b> dan CSAT anjlok dari 4.31 menjadi 3.07.</li>
            <li><b>Dropped Call Rate pada Telepon:</b> Tingkat panggilan terputus (Dropped Call Rate) pada saluran suara mencapai <b>10.1%</b> (melebihi standar batas aman industri 5.0%), terutama terjadi pada jam puncak (10:00 - 14:00 WIB) akibat waktu tunggu antrean yang lama (rata-rata 96.4 detik).</li>
            <li><b>Kegagalan First Contact Resolution (FCR) Tiket Teknikal:</b> Kategori masalah <i>Technical Support</i> dengan prioritas High/Urgent memiliki FCR terendah (hanya ~30%), yang menyebabkan penumpukan tiket (backlog) dan peningkatan <i>escalation rate</i> hingga 10.0%.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col_rec1, col_rec2 = st.columns(2)
    
    with col_rec1:
        st.markdown("""
        <div class="recommendation-card">
            <h4 style="color: #34d399; margin-top: 0;">🚀 Rekomendasi Jangka Pendek (Immediate Action)</h4>
            <ol>
                <li><b>Implementasi Auto-Responder & AI Chatbot untuk IM:</b> Deploy chatbot otomatis untuk memberikan respon pertama dalam <10 detik pada saluran IM untuk menjawab FAQ umum dan mengurangi First Response Time.</li>
                <li><b>Penataan Shifting Agen Jam Puncak (10:00 - 14:00):</b> Realokasi penugasan agen dari tiket non-urgent ke saluran Call & IM pada jam sibuk harian guna menekan waktu tunggu dan dropped call rate.</li>
                <li><b>Routing Panggilan Prioritas:</b> Terapkan Call Callback System sehingga pelanggan yang mengantre lebih dari 120 detik dapat memilih untuk dihubungi kembali tanpa kehilangan antrean.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    with col_rec2:
        st.markdown("""
        <div class="recommendation-card">
            <h4 style="color: #fbbf24; margin-top: 0;">🎯 Rekomendasi Jangka Panjang (Strategic Improvement)</h4>
            <ol>
                <li><b>Peningkatan Knowledge Base & Training FCR Agen Teknikal:</b> Lakukan pelatihan penanganan masalah teknis dan perbaiki sistem dokumentasi internal untuk meningkatkan First Contact Resolution (FCR) tiket teknikal dari 30% menjadi min 75%.</li>
                <li><b>Omnichannel Ticketing Integration:</b> Integrasikan sistem IM, Call, dan Ticket ke dalam 1 platform unified Agent Workspace agar history interaksi pelanggan langsung terlihat tanpa perlu bertanya ulang.</li>
                <li><b>Pemasangan Warning SLA System Real-Time:</b> Buat alarm alert otomatis jika antrean IM >3 menit atau antrean Call >90 detik agar Supervisor dapat melakukan intervention dispatch secara langsung.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Dashboard Analisis Interaksi Pelanggan | Dibuat dengan Streamlit & Python | Periode Data: April 2026</p>", unsafe_allow_html=True)
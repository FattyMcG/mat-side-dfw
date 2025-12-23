import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# 2. Updated CSS for White Title/Filters and High Contrast Cards
st.markdown("""
    <style>
    /* Force App Title and Filter Labels to WHITE */
    h1, [data-testid="stMarkdownContainer"] p, label {
        color: #FFFFFF !important;
    }

    /* 1. Day Selection Bar Styling (Grey bar with Black Text) */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 2px !important;
        background-color: #e0e0e0 !important; 
        border-radius: 8px;
        padding: 4px;
    }
    
    /* Day Labels inside the bar (Black text) */
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background-color: transparent !important;
        color: #000000 !important; /* Force Black text for names like Tu, TR, etc */
        font-size: 0.85rem !important;
        font-weight: bold !important;
        padding: 8px 0px !important;
    }

    /* Selected Day - White background */
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #ffffff !important;
        border-radius: 6px !important;
    }

    /* 2. Card Styling (White cards with Black text) */
    .mat-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 2px solid #000000;
    }
    
    .gym-title { 
        color: #000000 !important; 
        font-size: 1.4rem; 
        font-weight: 900; 
    }
    
    .time-badge { 
        color: #d32f2f !important; 
        font-weight: 800; 
        font-size: 1.1rem;
    }

    .location-text {
        color: #000000 !important;
        font-weight: 500;
    }

    .style-text {
        color: #000000 !important;
        font-weight: 800;
        font-size: 0.9rem;
        text-transform: uppercase;
        margin-top: 8px;
    }

    /* 3. Dropdown Box styling */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def load_data():
    try:
        mats = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
        schools = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
        mats = mats.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        schools = schools.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        df = pd.merge(mats, schools[['School', 'Website']], on='School', how='left')
        df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. Day Order & Custom Label Logic
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

# Custom abbreviation mapping
def get_day_label(day_name, is_today):
    if is_today: return "Tdy"
    mapping = {
        "Monday": "M",
        "Tuesday": "Tu",
        "Wednesday": "W",
        "Thursday": "TR",
        "Friday": "F",
        "Saturday": "Sa",
        "Sunday": "Su"
    }
    return mapping.get(day_name, day_name[:1])

day_labels = {day: get_day_label(day, day == days_full[today_idx]) for day in ordered_days}

st.title("DFW Mat Side")

# 5. Day Selector
selected_day_label = st.radio(
    "Select Day",
    options=ordered_days,
    format_func=lambda x: day_labels[x],
    label_visibility="collapsed"
)

# 6. Style Filter
sel_style = st.selectbox("Filter Style", ["All", "Gi", "No Gi", "Both"])

# Filtering
filtered = df[df['Day'].str.contains(selected_day_label, na=False, case=False)].sort_values('sort_time')
if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()

# 7. Card Display
if not filtered.empty:
    for i, row in filtered.iterrows():
        st.markdown(f"""
            <div class="mat-card">
                <div class="gym-title">{row['School']}</div>
                <div class="time-badge">🕒 {row['Start Time']}</div>
                <div class="location-text">📍 {row['City']}</div>
                <div class="style-text">STYLE: {row['Gi or Nogi']}</div>
                {f'<div style="margin-top:10px; font-size:0.85rem; color:#444; border-top:1px solid #eee; padding-top:5px;">{row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
            </div>
        """, unsafe_allow_html=True)
        
        b1, b2 =

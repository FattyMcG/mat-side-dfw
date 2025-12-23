import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# 2. CSS to Kill the Gaps and Force a Single Row
st.markdown("""
    <style>
    /* 1. Eliminate main container margins */
    .main .block-container { 
        padding: 1rem 0.5rem !important; 
    }
    
    /* 2. Style the Radio buttons as a unified horizontal bar */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 0px !important; /* This physically removes the gaps */
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 2px;
    }
    
    /* 3. Make each radio option look like a button */
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background-color: transparent;
        border-radius: 6px;
        padding: 6px 0px !important;
        margin: 0px !important;
        font-size: 0.75rem !important;
        font-weight: 600;
        border: none !important;
    }
    
    /* 4. Hide the radio circle icon */
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 0.75rem !important;
    }
    div[data-testid="stStyle"] { display: none; }
    
    /* Style for when an item is selected */
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #ffffff !important;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
    }

    /* Card Styling */
    .mat-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eee;
    }
    .gym-title { font-size: 1.3rem; font-weight: 800; margin-bottom: 2px; }
    .time-badge { color: #d32f2f; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Prep
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

# 4. Day Rotation Logic
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

# Map names for the display
day_map = {day: (day[:3] if day != days_full[today_idx] else "Tdy") for day in ordered_days}

st.title("🥋 DFW Mat Side")

# 5. The Segmented Control (The 7-Day Bar)
selected_day_label = st.radio(
    "Choose Day",
    options=ordered_days,
    format_func=lambda x: day_map[x],
    label_visibility="collapsed"
)

# 6. Filters & Cards
sel_style = st.selectbox("🥋 Style", ["All", "Gi", "No Gi", "Both"])
filtered = df[df['Day'].str.contains(selected_day_label, na=False, case=False)].sort_values('sort_time')

if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()

if not filtered.empty:
    for i, row in filtered.iterrows():
        st.markdown(f"""
            <div class="mat-card">
                <div class="gym-title">{row['School']}</div>
                <div class="time-badge">🕒 {row['Start Time']}</div>
                <div style="color: #666; font-size: 0.9rem;">📍 {row['City']}</div>
                <div style="background:#f0f2f6; display:inline-block; padding:2px 8px; border-radius:10px; font-size:0.7rem; margin-top:5px;">{row['Gi or Nogi']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        b1, b2 = st.columns(2)
        with b1:
            q = f"{row['School']} {row['Address']}".replace(" ", "+")
            st.link_button("📍 Maps", f"https://www.google.com/maps/search/?api=1&query={q}")
        with b2:
            if pd.notna(row['Website']) and str(row['Website']) != 'nan':
                st.link_button("🌐 Web", row['Website'])
            else:
                st.button("None", disabled=True, key=f"nw_{i}")

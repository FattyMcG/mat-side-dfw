import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# Tightened CSS for "All-on-one-screen" Day Bar
st.markdown("""
    <style>
    /* 1. Remove padding from main container for more width */
    .main .block-container { 
        padding-top: 1rem; 
        padding-left: 0.5rem; 
        padding-right: 0.5rem; 
    }
    
    /* 2. Force columns to be narrow and side-by-side */
    [data-testid="stHorizontalBlock"] {
        gap: 4px !important; /* Minimal gap between buttons */
        display: flex;
        flex-wrap: nowrap !important;
        overflow-x: auto;
    }
    
    [data-testid="column"] {
        width: auto !important;
        flex: 1 1 0% !important;
        min-width: 45px !important; /* Narrow enough for 7 days */
    }

    /* 3. Style the buttons to be compact */
    div.stButton > button {
        padding: 4px 2px !important;
        font-size: 0.75rem !important;
        width: 100% !important;
        border-radius: 6px;
    }

    .mat-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eee;
    }
    .gym-title { color: #1f1f1f; font-size: 1.2rem; font-weight: 800; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading (Cached)
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

# 3. Dynamic Day Order
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = ordered_days[0]

# 4. The 7-Day Button Row
st.title("🥋 DFW Mat Side")

cols = st.columns(7)
for i, day in enumerate(ordered_days):
    # Short labels to save space: "Tdy", "Mon", "Tue"...
    label = "Tdy" if i == 0 else day[:3]
    btn_type = "primary" if st.session_state.selected_day == day else "secondary"
    
    if cols[i].button(label, key=f"d_{day}", type=btn_type):
        st.session_state.selected_day = day
        st.rerun()

# 5. Filter & Cards
sel_style = st.selectbox("🥋 Filter Style", ["All", "Gi", "No Gi", "Both"])
query_day = st.session_state.selected_day
filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')

if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.markdown(f"### {query_day} Schedule")

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
                st.button("No Web", disabled=True, key=f"nw_{i}")
else:
    st.info("No mats today!")

import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# Mobile-First CSS with Horizontal Scroll
st.markdown("""
    <style>
    /* Force buttons into a scrolling row */
    div[data-testid="column"] {
        min-width: 85px !important;
        flex: 0 0 auto !important;
    }
    [data-testid="stHorizontalBlock"] {
        overflow-x: auto;
        flex-wrap: nowrap !important;
        display: flex;
        gap: 10px;
        padding-bottom: 10px;
        scrollbar-width: none; /* Firefox */
    }
    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none; /* Safari/Chrome */
    }
    
    .mat-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eee;
    }
    .gym-title { color: #1f1f1f; font-size: 1.4rem; font-weight: 800; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1.1rem; }
    .style-tag {
        display: inline-block;
        background-color: #f0f2f6;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    /* Full width buttons inside cards */
    .stButton button { width: 100%; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading
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
    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

df = load_data()

st.title("🥋 DFW Mat Side")

# 3. Dynamic Day Shifting Logic
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = ordered_days[0]

# 4. Horizontal Scrolling Buttons
st.write("### Choose Day")
# We create 7 columns to hold the 7 buttons in one swipable row
cols = st.columns(7)

for i, day in enumerate(ordered_days):
    label = "Today" if i == 0 else day[:3]
    # Highlight the selected day
    btn_type = "primary" if st.session_state.selected_day == day else "secondary"
    
    if cols[i].button(label, key=f"day_btn_{day}", type=btn_type):
        st.session_state.selected_day = day
        st.rerun()

# 5. Style Dropdown
st.write("")
sel_style = st.selectbox("🥋 Style", ["All", "Gi", "No Gi", "Both"])

# 6. Filter & Display
query_day = st.session_state.selected_day
filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')

if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()
st.subheader(f"{query_day} Mats")

if not filtered.empty:
    for i, row in filtered.iterrows():
        st.markdown(f"""
            <div class="mat-card">
                <div class="gym-title">{row['School']}</div>
                <div class="time-badge">🕒 {row['Start Time']}</div>
                <div style="color: #666;">📍 {row['City']}</div>
                <span class="style-tag">{row['Gi or Nogi']}</span>
                {f'<div style="margin-top:10px; font-size:0.9rem; color:#444; font-style: italic;">{row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
            </div>
        """, unsafe_allow_html=True)
        
        b1, b2 = st.columns(2)
        with b1:
            map_q = f"{row['School']} {row['Address']} {row['City']}".replace(" ", "+")
            st.link_button("📍 Directions", f"https://www.google.com/maps/search/?api=1&query={map_q}")
        with b2:
            if pd.notna(row['Website']) and str(row['Website']) != 'nan':
                st.link_button("🌐 Website", row['Website'])
            else:
                st.button("No Web", disabled=True, key=f"no_web_{i}")
        st.write("") 
else:
    st.info(f"No mats found for {query_day}.")

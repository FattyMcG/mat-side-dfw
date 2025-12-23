import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# Custom CSS for absolute control over spacing
st.markdown("""
    <style>
    /* 1. Tighten the main container */
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }
    
    /* 2. Create a custom Flexbox row for the buttons */
    .day-container {
        display: flex;
        justify-content: space-between;
        gap: 2px !important; /* This is the actual space between boxes */
        width: 100%;
        margin-bottom: 20px;
    }
    
    /* 3. Style Streamlit buttons to be narrow enough for 7-wide */
    div.stButton > button {
        width: 100% !important;
        padding: 4px 0px !important;
        font-size: 0.7rem !important;
        border-radius: 4px !important;
        min-width: 0px !important;
    }

    /* 4. Card Styling */
    .mat-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #eee;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .gym-title { color: #1f1f1f; font-size: 1.3rem; font-weight: 800; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1rem; }
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
    except:
        return pd.DataFrame()

df = load_data()

# 3. Dynamic Day Shifting
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

if 'selected_day' not in st.session_state:
    st.session_state.selected_day = ordered_days[0]

# 4. The 7-Day Button Row (Using fixed columns to force side-by-side)
st.title("🥋 DFW Mat Side")
st.write("### Select Day")

# forcing 7 columns with 0.1 gap ratio
cols = st.columns(7, gap="small")

for i, day in enumerate(ordered_days):
    # Shortest possible labels
    label = "Tdy" if i == 0 else day[:1] # Just 'M', 'T', 'W' etc or day[:3]
    if i != 0:
        label = day[:3]
        
    btn_type = "primary" if st.session_state.selected_day == day else "secondary"
    
    if cols[i].button(label, key=f"d_{day}", type=btn_type):
        st.session_state.selected_day = day
        st.rerun()

# 5. Filter & Display
sel_style = st.selectbox("🥋 Style Filter", ["All", "Gi", "No Gi", "Both"])
query_day = st.session_state.selected_day
filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')

if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.markdown(f"---")

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
else:
    st.info("No mats today!")

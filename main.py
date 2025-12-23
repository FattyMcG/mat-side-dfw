import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# 2. CSS Overhaul
st.markdown("""
    <style>
    /* Force App Title and Selectbox Label to WHITE */
    h1, [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
    }

    /* 1. Day Selection Bar (Grey bar with Black Text) */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 2px !important;
        background-color: #e0e0e0 !important; 
        border-radius: 8px;
        padding: 4px;
    }
    
    /* Ensure Day Labels are strictly BLACK */
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background-color: transparent !important;
    }
    
    /* Targeting the text specifically for high contrast */
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
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
        margin-bottom: 5px;
    }

    .style-text {
        color: #000000 !important;
        font-weight: 800;
        font-size: 0.95rem;
        text-transform: uppercase;
        margin-top: 8px;
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

# 4. Custom Label Logic
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]

def get_day_label(day_name, is_today):
    if is_today: return "Tdy"
    mapping = {"Monday": "M", "Tuesday": "Tu", "Wednesday": "W", "Thursday": "TR", "Friday": "F", "Saturday": "Sa", "Sunday": "Su"}
    return mapping.get(day_name, day_name[:1])

day_labels = {day: get_day_label(day, day == days_full[today_idx]) for day in ordered_days}

st.title("DFW Mat Side")

# 5. Day Selector (Radio Bar)
selected_day_label = st.radio(
    "Select Day",
    options=ordered_days,
    format_func=lambda x: day_labels[x],
    label_visibility="collapsed"
)

# 6. Style Filter with Emoji
sel_style = st.selectbox("🥋 Filter Style", ["All", "Gi", "No Gi", "Both"])

# Filtering logic
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
                <div class="style-text">🥋 STYLE: {row['Gi or Nogi']}</div>
                {f'<div style="margin-top:10px; font-size:0.85rem; color:#444; border-top:1px solid #eee; padding-top:5px;">{row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
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
    st.info(f"No mats found for {selected_day_label}.")

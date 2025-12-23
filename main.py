import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# 2. CSS (Exact high-contrast style preserved)
st.markdown("""
    <style>
    h1, [data-testid="stWidgetLabel"] p { color: #FFFFFF !important; }
    div[data-testid="stRadio"] > div {
        display: flex !important; flex-direction: row !important;
        justify-content: space-between !important; gap: 0px !important; 
        background-color: #e0e0e0 !important; border-radius: 8px; padding: 4px;
    }
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important; font-size: 0.9rem !important; font-weight: 900 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #ffffff !important; border-radius: 6px !important;
    }
    .mat-card {
        background-color: #ffffff; border-radius: 12px; padding: 16px;
        margin-bottom: 12px; border: 2px solid #000000;
    }
    .gym-title { color: #000000 !important; font-size: 1.4rem; font-weight: 900; line-height: 1.2; }
    .time-badge { color: #d32f2f !important; font-weight: 800; font-size: 1.1rem; margin: 5px 0px; }
    .location-text { color: #000000 !important; font-weight: 600; margin-bottom: 5px; }
    .style-text { color: #000000 !important; font-weight: 900; font-size: 0.95rem; text-transform: uppercase; margin-top: 8px; }
    
    .stButton button {
        padding: 2px 5px !important;
        font-size: 0.65rem !important;
        border: 1px solid #000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Enhanced Data Loading (The "Bulletproof Merge")
@st.cache_data
def load_data():
    try:
        mats = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
        schools = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
        
        # Clean column names (strip spaces from "Phone ", etc)
        mats.columns = mats.columns.str.strip()
        schools.columns = schools.columns.str.strip()
        
        # Create a "Match Key" (lowercase, no spaces) to link both sheets
        mats['match_key'] = mats['School'].astype(str).str.lower().str.strip()
        schools['match_key'] = schools['School'].astype(str).str.lower().str.strip()
        
        # Filter Schools sheet to only necessary columns for merging
        # Using match_key instead of original School name to avoid errors
        schools_clean = schools[['match_key', 'Website', 'Phone', 'Email']].drop_duplicates('match_key')
        
        # Merge using the cleaned keys
        df = pd.merge(mats, schools_clean, on='match_key', how='left')
        
        # Convert Start Time to sortable format
        df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
        return df
    except Exception as e:
        st.error(f"Merge Error: {e}")
        return pd.DataFrame()

df = load_data()

# 4. Navigation & Logic (Unchanged)
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]
day_labels = {day: ("Tdy" if i == 0 else day[0]) for i, day in enumerate(ordered_days)}

st.title("DFW Mat Side")
selected_day_label = st.radio("Day", options=ordered_days, format_func=lambda x: day_labels[x], label_visibility="collapsed")
sel_style = st.selectbox("🥋 Filter Style", ["All", "Gi", "No Gi", "Both"])

filtered = df[df['Day'].str.contains(selected_day_label, na=False, case=False)].sort_values('sort_time')
if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()

# 5. Display Cards
if not filtered.empty:
    for i, row in filtered.iterrows():
        st.markdown(f"""
            <div class="mat-card">
                <div class="gym-title">{row['School']}</div>
                <div class="time-badge">🕒 {row['Start Time']}</div>
                <div class="location-text">📍 {row['City']}</div>
                <div class="style-text">🥋 STYLE: {row.get('Gi or Nogi', 'N/A')}</div>
            </div>
        """, unsafe_allow_html=True)
        
        b1, b2, b3, b4 = st.columns(4)
        
        with b1:
            # Maps
            addr = row.get('Address', '')
            q = f"{row['School']} {addr}".replace(" ", "+")
            st.link_button("📍 Maps", f"https://www.google.com/maps/search/?api=1&query={q}")
        
        with b2:
            # Website
            if pd.notna(row.get('Website')) and str(row['Website']).strip() != "":
                st.link_button("🌐 Web", row['Website'])
            else:
                st.button("None", disabled=True, key=f"w_{i}")

        with b3:
            # Phone
            if pd.notna(row.get('Phone')) and str(row['Phone']).strip() != "":
                st.link_button("📞 Call", f"tel:{row['Phone']}")
            else:
                st.button("N/A", disabled=True, key=f"p_{i}")

        with b4:
            # Email
            if pd.notna(row.get('Email')) and str(row['Email']).strip() != "":
                st.link_button("✉️ Mail", f"mailto:{row['Email']}")
            else:
                st.button("N/A", disabled=True, key=f"e_{i}")
else:
    st.info(f"No mats found for {selected_day_label}.")

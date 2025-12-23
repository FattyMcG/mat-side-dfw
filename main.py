import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# Mobile-First CSS
st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    .mat-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 0px;
        border: 1px solid #eee;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .gym-title { color: #1f1f1f; font-size: 1.4rem; font-weight: 800; margin-bottom: 2px; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1.1rem; margin-bottom: 4px; }
    .style-tag {
        display: inline-block;
        background-color: #e8f0fe;
        color: #1967d2;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 5px;
    }
    /* Buttons spacing for mobile */
    .stButton button { width: 100%; border-radius: 8px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading
@st.cache_data
def load_data():
    try:
        mats = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
        schools = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
        
        # Clean data
        mats = mats.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        schools = schools.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Merge
        df = pd.merge(mats, schools[['School', 'Website']], on='School', how='left')
        df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
        return df
    except Exception as e:
        st.error(f"Error loading CSV files: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.title("🥋 DFW Mat Side")

    # 3. Mobile Navigation
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    curr_day = datetime.now().strftime("%A")

    c1, c2 = st.columns(2)
    with c1:
        sel_day = st.selectbox("📅 Day", ["Today"] + days)
    with c2:
        sel_style = st.selectbox("🥋 Style", ["All", "Gi", "No Gi", "Both"])

    query_day = curr_day if sel_day == "Today" else sel_day
    
    # 4. Filter
    filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')
    if sel_style != "All":
        filtered = filtered[filtered['Gi or Nogi'] == sel_style]

    st.divider()

    # 5. Display Cards
    if not filtered.empty:
        for i, row in filtered.iterrows():
            # The Card UI
            st.markdown(f"""
                <div class="mat-card">
                    <div class="gym-title">{row['School']}</div>
                    <div class="time-badge">🕒 {row['Start Time']}</div>
                    <div style="color: #666;">📍 {row['City']}</div>
                    <span class="style-tag">{row['Gi or Nogi']}</span>
                    {f'<div style="margin-top:10px; font-size:0.9rem; color:#444; font-style: italic;">Note: {row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
                </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons
            b1, b2 = st.columns(2)
            with b1:
                map_q = f"{row['School']} {row['Address']} {row['City']}".replace(" ", "+")
                st.link_button("📍 Directions", f"https://www.google.com/maps/search/?api=1&query={map_q}")
            with b2:
                if pd.notna(row['Website']) and str(row['Website']) != 'nan':
                    st.link_button("🌐 Website", row['Website'])
                else:
                    # Added a unique key here using the index 'i' to prevent the Duplicate ID error
                    st.button("No Website", disabled=True, key=f"no_web_{i}")
            
            st.write("") # Spacer between cards
    else:
        st.info(f"No mats listed for {query_day}.")

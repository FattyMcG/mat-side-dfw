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
        margin-bottom: 12px;
        border: 1px solid #eee;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .gym-title { color: #1f1f1f; font-size: 1.3rem; font-weight: 800; margin-bottom: 2px; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1rem; }
    .style-tag {
        display: inline-block;
        background-color: #e8f0fe;
        color: #1967d2;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .stButton button { width: 100%; border-radius: 8px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. Fix: Robust Data Merging
@st.cache_data
def load_data():
    # Load sheets
    mats = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
    schools = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
    
    # Clean whitespace from all string columns to prevent merge errors
    mats = mats.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    schools = schools.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Merge on School name
    # We use 'left' join so even if a school is missing from the Schools sheet, the Mat still shows up
    df = pd.merge(mats, schools[['School', 'Website', 'Phone']], on='School', how='left')
    
    # Create sortable time
    df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
    return df

try:
    df = load_data()
    
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
    
    # 4. Filter and Display
    filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')
    if sel_style != "All":
        filtered = filtered[filtered['Gi or Nogi'] == sel_style]

    st.divider()

    if not filtered.empty:
        for _, row in filtered.iterrows():
            with st.container():
                st.markdown(f"""
                    <div class="mat-card">
                        <div class="gym-title">{row['School']}</div>
                        <div class="time-badge">🕒 {row['Start Time']}</div>
                        <div style="color: #666; margin-bottom: 8px;">📍 {row['City']}</div>
                        <span class="style-tag">{row['Gi or Nogi']}</span>
                        {f'<div style="margin-top:8px; font-size:0.85rem; color:#444; border-left: 2px solid #ddd; padding-left: 8px;">{row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
                    </div>
                """, unsafe_allow_html=True)
                
                # Action Buttons
                b1, b2 = st.columns(2)
                with b1:
                    # Google Maps URL
                    map_q = f"{row['School']} {row['Address']} {row['City']}".replace(" ", "+")
                    st.link_button("📍 Directions", f"https://www.google.com/maps/search/?api=1&query={map_q}")
                with b2:
                    if pd.notna(row['Website']):
                        st.link_button("🌐 Website", row['Website'])
                    else:
                        st.button("No Website", disabled=True)
    else:
        st.info(f"No mats listed for {query_day}. Time for a rest day?")

except Exception as e:
    st.error("Wait, I hit a snag with the data files. Make sure both CSVs are uploaded to GitHub!")
    st.write(e)

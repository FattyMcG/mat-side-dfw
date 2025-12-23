import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Optimized Page Config for Mobile
st.set_page_config(
    page_title="DFW Mat Side", 
    page_icon="🥋", 
    layout="centered", # Centered is often better for mobile readability
    initial_sidebar_state="collapsed" # Hide sidebar by default on mobile
)

# Custom CSS for a "Native App" Vibe on iPhone
st.markdown("""
    <style>
    /* Main container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Custom Card Styling */
    .mat-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    .mat-time {
        color: #d32f2f;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .school-name {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 5px;
    }
    
    .style-tag {
        display: inline-block;
        background-color: #333;
        color: white;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.8rem;
        text-transform: uppercase;
        margin-top: 5px;
    }
    
    /* Make buttons full width for thumbs */
    .stButton button {
        width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading & Merging
@st.cache_data
def load_and_prep_data():
    # Load both files
    mats_df = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
    schools_df = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
    
    # Cleaning
    mats_df['Day'] = mats_df['Day'].str.strip()
    mats_df['School'] = mats_df['School'].str.strip()
    schools_df['School'] = schools_df['School'].str.strip()
    
    # Merge to get Website/Phone info from the Schools sheet
    df = pd.merge(mats_df, schools_df[['School', 'Website', 'Phone']], on='School', how='left')
    
    # Sortable time logic
    df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
    return df

df = load_and_prep_data()

# 3. Top-Level Mobile Filters (No Sidebar needed)
st.title("🥋 DFW Mat Side")

# Day selector - using a selectbox for clean mobile UI
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
current_day = datetime.now().strftime("%A")

col1, col2 = st.columns(2)
with col1:
    selected_day = st.selectbox("📅 Day", ["Today"] + days_of_week)
with col2:
    style_filter = st.selectbox("🥋 Style", ["All", "Gi", "No Gi", "Both"])

day_to_query = current_day if selected_day == "Today" else selected_day

# 4. Filtering Logic
filtered_df = df[df['Day'] == day_to_query].sort_values(by='sort_time')

if style_filter != "All":
    filtered_df = filtered_df[filtered_df['Gi or Nogi'] == style_filter]

# 5. Mobile-Optimized List View
st.write(f"### {day_to_query} Schedule")

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        # Using HTML for the "Card" look
        st.markdown(f"""
            <div class="mat-card">
                <div class="mat-time">🕒 {row['Start Time']}</div>
                <div class="school-name">{row['School']}</div>
                <div style="color: #666; font-size: 0.9rem;">📍 {row['City']}</div>
                <div class="style-tag">{row['Gi or Nogi']}</div>
                {f'<div style="font-style: italic; margin-top: 10px; font-size: 0.85rem;">"{row["Notes"]}"</div>' if pd.notna(row['Notes']) else ''}
            </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons (Map and Website)
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Google Maps Link
            search_query = f"{row['School']} {row['Address']} {row['City']}".replace(" ", "+")
            map_url = f"https://www.google.com/maps/search/?api=1&query={search_query}"
            st.link_button("📍 Directions", map_url)
            
        with btn_col2:
            if pd.notna(row['Website']):
                st.link_button("🌐 Website", row['Website'])
            else:
                st.button("No Link", disabled=True)
        
        st.markdown("---")
else:
    st.info("No mats found for this selection. Rest up or find another day!")

# Footer for Mobile
st.markdown("<br><br><div style='text-align: center; color: gray;'>OSS 🥋 - DFW Mat Side v1.0</div>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Mat Side DFW", page_icon="🥋", layout="wide")

# Custom CSS to make the multi-select look more like "buttons" (Streamlit hack)
st.markdown("""
    <style>
    .stMultiSelect div[data-baseweb="tag"] {
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥋 Mat Side DFW")

# 2. Load and Clean Data
@st.cache_data
def load_data():
    df = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
    df['Day'] = df['Day'].str.strip()
    
    # Convert 'Start Time' to a datetime object so we can sort it properly
    # This handles formats like "11:00 AM"
    df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
    return df

df = load_data()

# 3. Sidebar Setup
st.sidebar.header("Find a Training Session")

days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
current_day = datetime.now().strftime("%A")

selected_day = st.sidebar.selectbox("Choose a Day", ["Today"] + days_of_week)
day_to_query = current_day if selected_day == "Today" else selected_day

# Style Toggles (using multiselect which acts as toggle buttons)
style_options = ["Gi", "No Gi", "Both"]
selected_styles = st.sidebar.multiselect("Select Style(s)", style_options, default=style_options)

# 4. Filter and Sort
mask = (df['Day'] == day_to_query) & (df['Gi or Nogi'].isin(selected_styles))
filtered_df = df[mask].sort_values(by='sort_time')

# 5. Map View
st.subheader(f"📍 Mats in DFW: {day_to_query}")

# For the map to work, we'll use a placeholder or coordinates if available. 
# Streamlit's st.map needs 'lat' and 'lon'. 
# Note: For real-time address geocoding, we'd need a Google Maps API key, 
# but for now, let's display the list and a placeholder map.
if not filtered_df.empty:
    # 6. List View (Sorted by Time)
    for _, row in filtered_df.iterrows():
        with st.expander(f"**{row['Start Time']}** - {row['School']} ({row['City']})"):
            st.write(f"🏠 **Address:** {row['Address']}")
            st.write(f"🥋 **Style:** {row['Gi or Nogi']}")
            if pd.notna(row['Notes']):
                st.info(f"Note: {row['Notes']}")
            
            # Button to open in Google Maps
            map_url = f"https://www.google.com/maps/search/?api=1&query={row['School']}+{row['Address']}".replace(' ', '+')
            st.link_button("Open in Google Maps", map_url)
else:
    st.warning("No mats found for this selection. Try another day!")

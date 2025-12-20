import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Setup Page Vibe
st.set_page_config(page_title="Mat Side DFW", page_icon="🥋", layout="wide")

st.title("🥋 Mat Side DFW")
st.subheader("DFW's Ultimate Open Mat Finder")

# 2. Load Data (Using your uploaded CSV)
@st.cache_data
def load_data():
    df = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
    # Clean up day names (stripping whitespace)
    df['Day'] = df['Day'].str.strip()
    return df

df = load_data()

# 3. Sidebar Navigation & Filters
st.sidebar.header("Filter Your Roll")

# Get current day for the "Today" feature
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
current_day = datetime.now().strftime("%A")

# Day Selection
selected_day = st.sidebar.selectbox(
    "Choose a Day", 
    ["Today"] + days_of_week,
    index=0
)

# Style Filter
style_options = df['Gi or Nogi'].unique().tolist()
selected_style = st.sidebar.multiselect("Style", style_options, default=style_options)

# 4. Logic: Filtering the Data
if selected_day == "Today":
    query_day = current_day
    st.info(f"Showing Open Mats for Today ({current_day})")
else:
    query_day = selected_day
    st.info(f"Showing Open Mats for {selected_day}")

filtered_df = df[df['Day'] == query_day]
filtered_df = filtered_df[filtered_df['Gi or Nogi'].isin(selected_style)]

# 5. Display the Results
if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {row['School']}")
                st.caption(f"📍 {row['Address']}, {row['City']}")
            with col2:
                st.markdown(f"**🕒 {row['Start Time']}**")
                st.markdown(f"`{row['Gi or Nogi']}`")
            
            if pd.notna(row['Notes']):
                st.write(f"📝 *{row['Notes']}*")
            st.divider()
else:
    st.warning(f"No open mats found for {query_day} with the selected filters.")

# Phase 2 Preview in Sidebar
st.sidebar.divider()
st.sidebar.write("🔜 **Coming Soon:** School Directory & Local Competitions")
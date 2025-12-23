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
    .gym-title { color: #1f1f1f; font-size: 1.4rem; font-weight: 800; margin-bottom: 2px; }
    .time-badge { color: #d32f2f; font-weight: 700; font-size: 1.1rem; }
    .style-tag {
        display: inline-block;
        background-color: #f0f2f6;
        color: #31333F;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 5px;
    }
    /* Style for the day buttons to make them look uniform */
    div.stButton > button {
        border-radius: 20px;
        padding: 5px 10px;
        font-size: 0.8rem;
    }
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
        st.error(f"Error loading CSV files: {e}")
        return pd.DataFrame()

df = load_data()

# 3. Dynamic Day Button Logic
st.title("🥋 DFW Mat Side")

# Calculate day order starting from today
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
# Rotate the list so today is first
ordered_days = days_full[today_idx:] + days_full[:today_idx]

# Create button row using columns
st.write("### Select a Day")
cols = st.columns(4) # Show 4 buttons, then wrap to next row
cols2 = st.columns(3) # Remaining 3 days

# Use session state to remember which day is clicked
if 'selected_day' not in st.session_state:
    st.session_state.selected_day = ordered_days[0]

# Generate first row of buttons
for i, day in enumerate(ordered_days[:4]):
    label = "Today" if i == 0 else day[:3] # Show "Today" or abbreviated day
    if cols[i].button(label, key=f"btn_{day}", type="primary" if st.session_state.selected_day == day else "secondary"):
        st.session_state.selected_day = day

# Generate second row of buttons
for i, day in enumerate(ordered_days[4:]):
    if cols2[i].button(day[:3], key=f"btn_{day}", type="primary" if st.session_state.selected_day == day else "secondary"):
        st.session_state.selected_day = day

# 4. Style Dropdown (below buttons)
sel_style = st.selectbox("🥋 Filter by Style", ["All", "Gi", "No Gi", "Both"])

# 5. Filter & Display
query_day = st.session_state.selected_day
filtered = df[df['Day'].str.contains(query_day, na=False, case=False)].sort_values('sort_time')

if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()
st.write(f"**Showing: {query_day}**")

if not filtered.empty:
    for i, row in filtered.iterrows():
        st.markdown(f"""
            <div class="mat-card">
                <div class="gym-title">{row['School']}</div>
                <div class="time-badge">🕒 {row['Start Time']}</div>
                <div style="color: #666;">📍 {row['City']}</div>
                <span class="style-tag">{row['Gi or Nogi']}</span>
                {f'<div style="margin-top:10px; font-size:0.9rem; color:#444; font-style: italic;">Note: {row["Notes"]}</div>' if pd.notna(row['Notes']) else ''}
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
                st.button("No Website", disabled=True, key=f"no_web_{i}")
        st.write("") 
else:
    st.info(f"No mats found for {query_day}.")

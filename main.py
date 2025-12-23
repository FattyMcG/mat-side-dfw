import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="DFW Mat Side", page_icon="🥋", layout="centered")

# 2. Advanced CSS (Keeping your existing styles exactly as they were)
st.markdown("""
    <style>
    h1, [data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
    }
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        gap: 0px !important; 
        background-color: #e0e0e0 !important; 
        border-radius: 8px;
        padding: 4px;
    }
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-size: 0.9rem !important;
        font-weight: 900 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #ffffff !important;
        border-radius: 6px !important;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.2);
    }
    .mat-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 2px solid #000000;
    }
    .gym-title { color: #000000 !important; font-size: 1.4rem; font-weight: 900; line-height: 1.2; }
    .time-badge { color: #d32f2f !important; font-weight: 800; font-size: 1.1rem; margin: 5px 0px; }
    .location-text { color: #000000 !important; font-weight: 600; margin-bottom: 5px; }
    .style-text { color: #000000 !important; font-weight: 900; font-size: 0.95rem; text-transform: uppercase; margin-top: 8px; }
    
    /* Ensure action buttons are compact for 4-across layout */
    .stButton button {
        padding: 2px 5px !important;
        font-size: 0.7rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading (Now including Email and Phone from your Schools sheet)
@st.cache_data
def load_data():
    try:
        mats = pd.read_csv("DFW Open Mats - Tracker - Open Mats.csv")
        schools = pd.read_csv("DFW Open Mats - Tracker - Schools.csv")
        mats = mats.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        schools = schools.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        # Merging Website, Phone, and Email
        df = pd.merge(mats, schools[['School', 'Website', 'Phone', 'Email']], on='School', how='left')
        df['sort_time'] = pd.to_datetime(df['Start Time'], errors='coerce').dt.time
        return df
    except:
        return pd.DataFrame()

df = load_data()

# 4. Day Label Logic
days_full = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today_idx = datetime.now().weekday()
ordered_days = days_full[today_idx:] + days_full[:today_idx]
day_labels = {day: ("Tdy" if i == 0 else day[0]) for i, day in enumerate(ordered_days)}

st.title("DFW Mat Side")

selected_day_label = st.radio("Day Selector", options=ordered_days, format_func=lambda x: day_labels[x], label_visibility="collapsed")
sel_style = st.selectbox("🥋 Filter Style", ["All", "Gi", "No Gi", "Both"])

filtered = df[df['Day'].str.contains(selected_day_label, na=False, case=False)].sort_values('sort_time')
if sel_style != "All":
    filtered = filtered[filtered['Gi or Nogi'] == sel_style]

st.divider()

# 7. Card Display with 4 Action Buttons
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
        
        # ACTION BUTTONS: 4-Column Layout
        b1, b2, b3, b4 = st.columns(4)
        
        with b1:
            q = f"{row['School']} {row['Address']}".replace(" ", "+")
            st.link_button("📍 Maps", f"https://www.google.com/maps/search/?api=1&query={q}")
        
        with b2:
            if pd.notna(row['Website']) and str(row['Website']) != 'nan':
                st.link_button("🌐 Web", row['Website'])
            else:
                st.button("None", disabled=True, key=f"nw_{i}")

        with b3:
            if pd.notna(row['Phone']) and str(row['Phone']) != 'nan':
                # Actionable tel: link
                st.link_button("📞 Call", f"tel:{row['Phone']}")
            else:
                st.button("N/A", disabled=True, key=f"np_{i}")

        with b4:
            if pd.notna(row['Email']) and str(row['Email']) != 'nan':
                # Actionable mailto: link
                st.link_button("✉️ Mail", f"mailto:{row['Email']}")
            else:
                st.button("N/A", disabled=True, key=f"ne_{i}")
else:
    st.info(f"No mats found for {selected_day_label}.")


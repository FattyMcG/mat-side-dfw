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

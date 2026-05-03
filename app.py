import streamlit as st
import re
import io
import base64
from typing import List, Tuple
import pandas as pd
from datetime import datetime
import re as _re
import requests


# Set page config
st.set_page_config(
    page_title="Mutate for Digest - Bioinformatics Tool",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a reset button using Streamlit session state
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]

if "reset" not in st.session_state:
    st.session_state["reset"] = False

if st.sidebar.button("🔄 Reset Page"):
    reset_app()
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ENHANCED CSS — Bioinformatics Lab Aesthetic
# Dark science + vivid neon accents inspired by DNA gel imaging & lab equipment
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Orbitron:wght@700;900&display=swap');

    /* ── Root Palette ── */
    :root {
        --dna-teal:    #00e5c3;
        --dna-violet:  #a259ff;
        --dna-lime:    #b4f442;
        --dna-coral:   #ff6b6b;
        --dna-amber:   #ffba08;
        --dna-blue:    #4cc9f0;
        --dna-pink:    #f72585;
        --dark-base:   #0a0e1a;
        --dark-card:   #111827;
        --dark-panel:  #1a2235;
        --dark-border: rgba(0, 229, 195, 0.18);
        --text-main:   #e8f4f8;
        --text-muted:  #8fa3b1;
    }

    /* ── Global reset ── */
    * { box-sizing: border-box; }

    html, body, .stApp {
        background: var(--dark-base) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-main) !important;
    }

    /* ── Animated helix background on body ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 10% 20%, rgba(162,89,255,0.07) 0%, transparent 60%),
            radial-gradient(ellipse 60% 80% at 85% 70%, rgba(0,229,195,0.06) 0%, transparent 55%),
            radial-gradient(ellipse 50% 50% at 50% 50%, rgba(76,201,240,0.04) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--dark-base); }
    ::-webkit-scrollbar-thumb { background: var(--dna-teal); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--dna-violet); }

    /* ── Main header ── */
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #112240 50%, #0d1b2a 100%);
        border: 1px solid var(--dark-border);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: 0 0 60px rgba(0,229,195,0.08), 0 0 120px rgba(162,89,255,0.05);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -2px; left: -2px; right: -2px; bottom: -2px;
        background: linear-gradient(90deg, var(--dna-teal), var(--dna-violet), var(--dna-blue), var(--dna-teal));
        background-size: 300% 100%;
        border-radius: 21px;
        z-index: -1;
        animation: borderShimmer 4s linear infinite;
        opacity: 0.6;
    }

    @keyframes borderShimmer {
        0%   { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }

    .main-header h1 {
        font-family: 'Orbitron', monospace !important;
        font-size: 2.6rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, var(--dna-teal), var(--dna-blue), var(--dna-violet));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.4rem 0 !important;
        letter-spacing: 2px;
        text-shadow: none;
        animation: pulseGlow 3s ease-in-out infinite;
    }

    @keyframes pulseGlow {
        0%, 100% { filter: brightness(1); }
        50%       { filter: brightness(1.2); }
    }

    .main-header h3 {
        color: var(--dna-teal) !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase;
        margin: 0 0 0.8rem 0 !important;
        opacity: 0.9;
    }

    .main-header p {
        color: var(--text-muted) !important;
        font-size: 0.95rem !important;
        margin: 0 !important;
        max-width: 640px;
        margin-left: auto !important;
        margin-right: auto !important;
        line-height: 1.6;
    }

    /* ── DNA strand decorative dots ── */
    .main-header::after {
        content: '● ○ ● ○ ● ○ ● ○ ● ○ ● ○ ● ○ ● ○ ● ○ ● ○';
        position: absolute;
        bottom: 10px;
        left: 0; right: 0;
        text-align: center;
        font-size: 8px;
        letter-spacing: 6px;
        color: rgba(0,229,195,0.25);
        pointer-events: none;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1420 0%, #0f1a2e 100%) !important;
        border-right: 1px solid var(--dark-border) !important;
    }

    section[data-testid="stSidebar"] * {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-main) !important;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .sidebar-header {
        color: var(--dna-teal) !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
    }

    section[data-testid="stSidebar"] .stMarkdown h2 {
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--dna-teal) !important;
        border-bottom: 1px solid rgba(0,229,195,0.2);
        padding-bottom: 0.4rem;
        margin-bottom: 0.8rem;
    }

    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-size: 0.8rem !important;
        color: var(--dna-violet) !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* ── Selectbox / Multiselect / Radio ── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: var(--dark-panel) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 10px !important;
        color: var(--text-main) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stSelectbox > div > div:focus-within,
    .stMultiSelect > div > div:focus-within {
        border-color: var(--dna-teal) !important;
        box-shadow: 0 0 0 3px rgba(0,229,195,0.15) !important;
    }

    /* Multiselect tags */
    .stMultiSelect span[data-baseweb="tag"] {
        background: linear-gradient(90deg, rgba(0,229,195,0.2), rgba(162,89,255,0.2)) !important;
        border: 1px solid rgba(0,229,195,0.4) !important;
        border-radius: 6px !important;
        color: var(--dna-teal) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.75rem !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, var(--dark-panel), #0f2340) !important;
        border: 1px solid rgba(0,229,195,0.35) !important;
        color: var(--dna-teal) !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.25s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0,229,195,0.12), rgba(162,89,255,0.12)) !important;
        border-color: var(--dna-teal) !important;
        box-shadow: 0 0 20px rgba(0,229,195,0.2) !important;
        transform: translateY(-1px);
        color: #ffffff !important;
    }

    /* Primary analyze button */
    .stButton > button[kind="primary"],
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #00b894, #0984e3, #6c5ce7) !important;
        background-size: 200% auto !important;
        border: none !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        letter-spacing: 1px;
        box-shadow: 0 4px 24px rgba(0,229,195,0.25) !important;
        animation: gradientShift 3s ease infinite !important;
        text-transform: uppercase;
    }

    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 32px rgba(0,229,195,0.35), 0 0 60px rgba(162,89,255,0.15) !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(180,244,66,0.1), rgba(0,229,195,0.1)) !important;
        border: 1px solid rgba(180,244,66,0.4) !important;
        color: var(--dna-lime) !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, rgba(180,244,66,0.2), rgba(0,229,195,0.15)) !important;
        box-shadow: 0 0 20px rgba(180,244,66,0.2) !important;
        transform: translateY(-1px);
    }

    /* ── Text area ── */
    .stTextArea textarea {
        background: var(--dark-panel) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 12px !important;
        color: var(--text-main) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.6 !important;
        transition: border-color 0.2s ease;
    }

    .stTextArea textarea:focus {
        border-color: var(--dna-teal) !important;
        box-shadow: 0 0 0 3px rgba(0,229,195,0.12), 0 0 20px rgba(0,229,195,0.08) !important;
        outline: none !important;
    }

    /* ── File uploader ── */
    .stFileUploader > div {
        background: var(--dark-panel) !important;
        border: 2px dashed rgba(0,229,195,0.3) !important;
        border-radius: 14px !important;
        transition: all 0.25s ease;
    }

    .stFileUploader > div:hover {
        border-color: var(--dna-teal) !important;
        background: rgba(0,229,195,0.04) !important;
    }

    /* ── Radio buttons ── */
    .stRadio > div {
        gap: 0.5rem;
    }

    .stRadio label {
        background: var(--dark-panel) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 8px !important;
        padding: 0.3rem 0.8rem !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stRadio label:hover {
        border-color: var(--dna-teal) !important;
        background: rgba(0,229,195,0.06) !important;
    }

    /* ── Slider ── */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--dna-teal), var(--dna-violet)) !important;
    }

    .stSlider > div > div > div > div > div {
    }

    /* ── DataFrames / Tables ── */
    .stDataFrame {
        border: 1px solid var(--dark-border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    .stDataFrame thead tr th {
        background: linear-gradient(135deg, #0d1b2a, #1a2a45) !important;
        color: var(--dna-teal) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border-bottom: 1px solid var(--dark-border) !important;
        padding: 0.8rem 1rem !important;
    }

    .stDataFrame tbody tr td {
        background: var(--dark-card) !important;
        color: var(--text-main) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
        border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        padding: 0.6rem 1rem !important;
    }

    .stDataFrame tbody tr:hover td {
        background: rgba(0,229,195,0.05) !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: var(--dna-teal) !important;
    }

    /* ── Section headings ── */
    .stMarkdown h2 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        color: var(--text-main) !important;
        position: relative;
        padding-left: 1rem;
        margin-top: 1.5rem !important;
    }

    .stMarkdown h2::before {
        content: '';
        position: absolute;
        left: 0; top: 15%; bottom: 15%;
        width: 3px;
        border-radius: 2px;
        background: linear-gradient(180deg, var(--dna-teal), var(--dna-violet));
    }

    .stMarkdown h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        color: var(--dna-blue) !important;
        letter-spacing: 0.5px;
    }

    /* ── Alert/Info/Success/Warning ── */
    .stSuccess > div {
        background: linear-gradient(135deg, rgba(0,184,148,0.12), rgba(0,229,195,0.08)) !important;
        border: 1px solid rgba(0,229,195,0.35) !important;
        border-radius: 10px !important;
        color: var(--dna-teal) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stInfo > div {
        background: linear-gradient(135deg, rgba(76,201,240,0.1), rgba(162,89,255,0.08)) !important;
        border: 1px solid rgba(76,201,240,0.3) !important;
        border-radius: 10px !important;
        color: var(--dna-blue) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stWarning > div {
        background: linear-gradient(135deg, rgba(255,186,8,0.1), rgba(255,107,107,0.08)) !important;
        border: 1px solid rgba(255,186,8,0.3) !important;
        border-radius: 10px !important;
        color: var(--dna-amber) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .stError > div {
        background: linear-gradient(135deg, rgba(247,37,133,0.1), rgba(255,107,107,0.08)) !important;
        border: 1px solid rgba(247,37,133,0.35) !important;
        border-radius: 10px !important;
        color: var(--dna-coral) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* ── Custom component boxes ── */
    .feature-box {
        background: linear-gradient(135deg, rgba(247,37,133,0.12) 0%, rgba(255,107,107,0.08) 100%);
        border: 1px solid rgba(247,37,133,0.3);
        padding: 1.4rem;
        border-radius: 14px;
        margin: 1rem 0;
        color: var(--text-main);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 500;
        position: relative;
        overflow: hidden;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .feature-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, var(--dna-pink), var(--dna-coral));
        border-radius: 4px 0 0 4px;
    }

    .feature-box:hover {
        border-color: rgba(247,37,133,0.5);
        box-shadow: 0 0 24px rgba(247,37,133,0.12);
    }

    /* Result box — sequence output */
    .result-box {
        background: linear-gradient(135deg, rgba(76,201,240,0.06) 0%, rgba(0,229,195,0.04) 100%);
        border: 1px solid rgba(76,201,240,0.25);
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        color: var(--text-main);
        position: relative;
        overflow: hidden;
        transition: box-shadow 0.3s ease;
    }

    .result-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, var(--dna-blue), var(--dna-teal));
    }

    .result-box:hover {
        box-shadow: 0 0 30px rgba(76,201,240,0.1);
    }

    .result-box h4 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--dna-blue);
        font-weight: 600;
        margin: 0 0 1rem 0;
        font-size: 1rem;
        letter-spacing: 0.5px;
    }

    /* Info box — how-it-works */
    .info-box {
        background: linear-gradient(135deg, rgba(0,229,195,0.08) 0%, rgba(76,201,240,0.05) 100%);
        border: 1px solid rgba(0,229,195,0.22);
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin: 1rem 0;
        color: var(--text-main);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
        position: relative;
        overflow: hidden;
    }

    .info-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, var(--dna-teal), var(--dna-blue));
    }

    .info-box h4 {
        color: var(--dna-teal);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        margin: 0 0 0.8rem 0;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .info-box ol li,
    .info-box ul li {
        color: var(--text-main);
        margin-bottom: 0.4rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .info-box b {
        color: var(--dna-teal);
    }

    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, rgba(255,186,8,0.08) 0%, rgba(255,107,107,0.06) 100%);
        border: 1px solid rgba(255,186,8,0.28);
        padding: 1rem 1.3rem;
        border-radius: 14px;
        margin: 1rem 0;
        color: var(--text-main);
        font-family: 'Space Grotesk', sans-serif;
        position: relative;
    }

    .warning-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, var(--dna-amber), var(--dna-coral));
        border-radius: 4px 0 0 4px;
    }

    .warning-box h4 {
        color: var(--dna-amber);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .warning-box p {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        margin: 0.2rem 0 !important;
    }

    .warning-box strong {
        color: var(--dna-amber) !important;
    }

    /* ── Stats container ── */
    .stats-container {
        display: flex;
        justify-content: space-around;
        gap: 1rem;
        margin: 1.8rem 0;
        flex-wrap: wrap;
    }

    .stat-box {
        background: linear-gradient(135deg, var(--dark-card), var(--dark-panel));
        border: 1px solid var(--dark-border);
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        text-align: center;
        min-width: 140px;
        flex: 1;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .stat-box::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--dna-teal), var(--dna-violet), var(--dna-blue));
        border-radius: 0 0 14px 14px;
    }

    .stat-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,229,195,0.12);
    }

    .stat-box h3 {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: var(--dna-teal) !important;
        margin: 0 0 0.3rem 0 !important;
        letter-spacing: 1px;
    }

    .stat-box p {
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin: 0 !important;
        font-weight: 500 !important;
    }

    /* ── DNA Sequence display ── */
    .dna-sequence {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 13px !important;
        line-height: 1.8 !important;
        background: rgba(10, 14, 26, 0.9) !important;
        padding: 1.2rem !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0,229,195,0.15) !important;
        word-break: break-all !important;
        color: var(--text-main) !important;
    }

    /* ── Restriction site highlight ── */
    .restriction-site {
        background: rgba(255,186,8,0.15) !important;
        border: 1px solid rgba(255,186,8,0.4) !important;
        padding: 0.15rem 0.4rem !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        color: var(--dna-amber) !important;
        font-family: 'JetBrains Mono', monospace !important;
        box-shadow: 0 0 8px rgba(255,186,8,0.15);
    }

    /* ── Mutation highlight ── */
    .mutation-highlight {
        background: rgba(247,37,133,0.15) !important;
        border: 1px solid rgba(247,37,133,0.4) !important;
        padding: 0.15rem 0.4rem !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        color: var(--dna-pink) !important;
        font-family: 'JetBrains Mono', monospace !important;
        box-shadow: 0 0 8px rgba(247,37,133,0.12);
    }

    /* ── Mutation animation blocks ── */
    @keyframes fadeInMove {
        0%   { opacity: 0; transform: translateY(24px) scale(0.97); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    .mutation-anim-block {
        animation: fadeInMove 0.7s cubic-bezier(.4,0,.2,1);
    }

    .mutation-aa-change {
        background: rgba(247,37,133,0.15);
        color: var(--dna-pink);
        border-radius: 6px;
        padding: 0.2em 0.6em;
        font-weight: 700;
        border: 1px solid rgba(247,37,133,0.35);
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05em;
        letter-spacing: 1px;
    }

    .mutation-arrow {
        font-size: 1.5em;
        margin: 0 0.5em;
        vertical-align: middle;
        color: var(--dna-blue);
        animation: fadeInMove 1s cubic-bezier(.4,0,.2,1);
    }

    .mutation-silent {
        color: var(--dna-teal) !important;
        font-size: 0.95em;
        margin-left: 0.5em;
        font-weight: 600;
        background: rgba(0,229,195,0.1);
        padding: 0.15em 0.7em;
        border-radius: 20px;
        border: 1px solid rgba(0,229,195,0.3);
        display: inline-block;
        letter-spacing: 0.5px;
    }

    .mutation-nonsilent {
        color: var(--dna-coral) !important;
        font-size: 0.95em;
        margin-left: 0.5em;
        font-weight: 600;
        background: rgba(255,107,107,0.1);
        padding: 0.15em 0.7em;
        border-radius: 20px;
        border: 1px solid rgba(255,107,107,0.3);
        display: inline-block;
        letter-spacing: 0.5px;
    }

    /* ── Column divider ── */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }

    /* ── Expander / Detail blocks ── */
    .streamlit-expanderHeader {
        background: var(--dark-panel) !important;
        border: 1px solid var(--dark-border) !important;
        border-radius: 10px !important;
        color: var(--dna-teal) !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }

    /* ── Label text everywhere ── */
    label, .stMarkdown p {
        color: var(--text-muted) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.9rem !important;
    }

    /* Override for content text in boxes (allow inline styling) */
    .info-box p, .result-box p, .feature-box p, .warning-box p {
        color: inherit !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--dark-border) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Section header pill ── */
    .section-pill {
        display: inline-block;
        background: linear-gradient(90deg, rgba(0,229,195,0.15), rgba(162,89,255,0.1));
        border: 1px solid rgba(0,229,195,0.3);
        color: var(--dna-teal);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        margin-bottom: 0.5rem;
    }

    /* ── Spinner text ── */
    .stSpinner p {
        color: var(--dna-teal) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
    }

    /* ── Footer ── */
    footer { display: none !important; }
    #MainMenu { visibility: hidden; }

    /* ── Block container ── */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px !important;
    }

    /* ── Animated nucleotide colors in sequence ── */
    span[style*="color:#1f77b4"] { color: #4cc9f0 !important; }   /* A = bright blue  */
    span[style*="color:#d62728"] { color: #ff6b6b !important; }   /* T = coral        */
    span[style*="color:#2ca02c"] { color: #b4f442 !important; }   /* G = lime green   */
    span[style*="color:#ff7f0e"] { color: #ffba08 !important; }   /* C = amber        */

</style>
""", unsafe_allow_html=True)

# Core bioinformatics functions (from your main.py)
def right_num(number, filler, width, suffix):
    if filler == "":
        filler = " "
    return str(int(number)).rjust(width, filler) + suffix

def convert_degenerates(seq: str) -> str:
    degenerates = {
        'N': '[ACGT]', 'R': '[AG]', 'Y': '[CT]', 'S': '[GC]',
        'W': '[AT]', 'K': '[GT]', 'M': '[AC]', 'B': '[CGT]',
        'D': '[AGT]', 'H': '[ACT]', 'V': '[ACG]'
    }
    pattern = ''
    for char in seq.upper():
        pattern += degenerates.get(char, char)
    return pattern

class RestrictionSite:
    def __init__(self, label: str, position: int, cut_distance: int, iupac_pattern: str):
        self.label = label
        self.position = position
        self.cut_distance = cut_distance
        self.iupac_pattern = iupac_pattern
        self.number_of_cuts = 0

class RestrictionSiteCollection:
    def __init__(self):
        self.restriction_sites: List[RestrictionSite] = []

    def add_restriction_site(self, restriction_site: RestrictionSite):
        self.restriction_sites.append(restriction_site)

    def sort_restriction_sites(self):
        self.restriction_sites.sort(key=lambda x: -x.position)

def translate_dna(dna_sequence: str, genetic_code_dict: dict) -> str:
    """Translate DNA sequence to amino acids"""
    clean_dna = re.sub(r'[^A-Za-z]', '', dna_sequence.upper())
    if len(clean_dna) < 3:
        return ""
    
    amino_acids = []
    for i in range(0, len(clean_dna) - 2, 3):
        codon = clean_dna[i:i+3]
        amino_acid = genetic_code_dict.get(codon, 'X')
        amino_acids.append(amino_acid)
    
    return ''.join(amino_acids)

def build_mutated_restriction_sites(restriction_sites: List[str]) -> List[str]:
    mutated_sites = []
    for site in restriction_sites:
        match = re.search(r'/([^/]+)/', site)
        pattern = match.group(1).lower() if match else ''
        label = re.search(r'\([^\(]+\)', site).group(0)
        cut_distance = float(re.search(r'\)\D*(\d+)', site).group(1))

        single_degen = []
        double_degen = []

        for i in range(len(pattern)):
            if pattern[i] not in ('n', 'N'):
                single_degen.append(pattern[:i] + 'N' + pattern[i+1:])

        if len(pattern) > 6:
            for item in single_degen:
                for j in range(len(item)):
                    if item[j] not in ('n', 'N'):
                        double_degen.append(item[:j] + 'N' + item[j+1:])

        for s in single_degen + double_degen:
            mutated_sites.append(f"/{s}/ {label}{cut_distance}")

    return mutated_sites

def find_restriction_sites(sequence: str, items: List[str], conformation: str) -> RestrictionSiteCollection:
    look_ahead = 50
    lower_limit = 0
    upper_limit = len(sequence)
    shift_value = 0
    collection = RestrictionSiteCollection()

    if conformation == "circular":
        shift_value = len(sequence[:look_ahead])
        sequence = sequence[-look_ahead:] + sequence + sequence[:look_ahead]
        lower_limit += shift_value
        upper_limit += shift_value

    for item in items:
        iupac_pattern = re.search(r'/([^/]+)/', item).group(1)
        match_exp = re.compile(convert_degenerates(iupac_pattern), re.IGNORECASE)
        cut_distance = int(re.search(r'\)\D*(\d+)', item).group(1))
        label = re.search(r'\([^\(]+\)', item).group(0)[1:-1]

        matches = list(match_exp.finditer(sequence))

        for match in matches:
            pos = match.start() - cut_distance
            if lower_limit <= pos < upper_limit:
                collection.add_restriction_site(
                    RestrictionSite(f"{label} at position {pos - shift_value + 1}", 
                                  pos - shift_value, cut_distance, iupac_pattern)
                )

    return collection

# Streamlit App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧬 Mutate for Digest</h1>
        <h3>Restriction Site &amp; Mutation Analysis</h3>
        <p>Find restriction enzyme sites in your DNA, and see what small changes could add new sites. Check how these changes affect the protein.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.markdown("## 🔧 Configuration")
    
    # Sample files download
    st.sidebar.markdown("### 📥 Download Sample Files")
    
    
    sample_dna = """>CDS1
atgtctgattcgctaaatcatccatcgagttctacggtgcatgcagatgatggattcgag
ccaccaacatctccggaagacaacaacaaaaaaccgtctttagaacaaattaaacaggaa
agagaagcgttgtttacggatctattcgcagatcgtcgacgaagcgctcgttctgtgatt
gaagaagctttccaaaacgaactcatgagtgctgaaccagtccagccaaacgtgccgaat
ccacattcgattcccattcgtttccgtcatcaaccagttgctggacctgctcatgatgtt
ttcggagacgcggtgcattcaatttttcaaaaaataatgtccagaggagtgaacgcggat
tatagtcattggatgtcatattggatcgcgttgggaatcgacaaaaaaacacaaatgaac
tatcatatgaaaccgttttgcaaagatacttatgcaactgaaggctccttagaagcgaaa
caaacatttactgataaaatcaggtcagctgttgaggaaattatctggaagtccgctgaa
tattgtgatattcttagcgagaagtggacaggaattcatgtgtcggccgaccaactgaaa
ggtcaaagaaataagcaagaagatcgttttgtggcttatccaaatggacaatacatgaat
cgtggacagagtgacatttcacttcttgcggtgttcgatgggcatggcggacacgagtgc
tctcaatatgcagctgctcatttctgggaagcatggtccgatgctcaacatcatcattca
caagatatgaaacttgacgaactcctagaaaaggctctagaaacattggacgaaagaatg
acagtcagaagtgttcgagaatcttggaaaggtggaaccactgctgtctgctgtgctgtt
gatttgaacactaatcaaatcgcatttgcctggcttggagattcaccaggttacatcatg
tcaaacttggagttccgcaaattcactactgaacactccccgtctgacccggaggaatgt
cgacgagtcgaagaagtcggtggccagatttttgtgatcggtggtgagctccgtgtgaat
ggagtactcaacctgacgcgagcactaggagacgtacctggaagaccaatgatatccaac
aaacctgataccttactgaagacgatcgaacctgcggattatcttgttttgttggcctgt
gacgggatttctgacgtcttcaacactagtgatttgtacaatttggttcaggcttttgtc
aatgaatatgacgtagaagattatcacgaacttgcacgctacatttgcaatcaagcagtt
tcagctggaagtgctgacaatgtgacagtagttataggtttcctccgtccaccagaagac
gtttggcgtgtaatgaaaacagactcggatgatgaagagagcgagctcgaggaagaagat
gacaatgaatag"""


    if st.sidebar.button("📄 Download Sample DNA"):
        st.sidebar.download_button(
            label="💾 Download DNA FASTA",
            data=sample_dna,
            file_name="sample_dna.fasta",
            mime="text/plain"
        )
    
    # Comprehensive restriction enzyme database
    restriction_enzymes_db = {
        "EcoRI": "/GAATTC/ (EcoRI)1",
        "BamHI": "/GGATCC/ (BamHI)1", 
        "HindIII": "/AAGCTT/ (HindIII)1",
        "PstI": "/CTGCAG/ (PstI)1",
        "SalI": "/GTCGAC/ (SalI)1",
        "XbaI": "/TCTAGA/ (XbaI)1",
        "SacI": "/GAGCTC/ (SacI)1",
        "KpnI": "/GGTACC/ (KpnI)1",
        "SmaI": "/CCCGGG/ (SmaI)3",
        "XhoI": "/CTCGAG/ (XhoI)1",
        "NotI": "/GCGGCCGC/ (NotI)2",
        "ApaI": "/GGGCCC/ (ApaI)1",
        "BglII": "/AGATCT/ (BglII)1",
        "ClaI": "/ATCGAT/ (ClaI)2",
        "DraI": "/TTTAAA/ (DraI)3",
        "EcoRV": "/GATATC/ (EcoRV)3",
        "HaeII": "/RGCGCY/ (HaeII)3",
        "HpaI": "/GTTAAC/ (HpaI)3",
        "MluI": "/ACGCGT/ (MluI)1",
        "NcoI": "/CCATGG/ (NcoI)1",
        "NdeI": "/CATATG/ (NdeI)2",
        "NheI": "/GCTAGC/ (NheI)1",
        "NruI": "/TCGCGA/ (NruI)3",
        "PvuII": "/CAGCTG/ (PvuII)3",
        "ScaI": "/AGTACT/ (ScaI)3",
        "SpeI": "/ACTAGT/ (SpeI)1",
        "SphI": "/GCATGC/ (SphI)1",
        "StuI": "/AGGCCT/ (StuI)3",
        "TaqI": "/TCGA/ (TaqI)1",
        "XmaI": "/CCCGGG/ (XmaI)1",
        "AseI": "/ATTAAT/ (AseI)3",
        "AvrII": "/CCTAGG/ (AvrII)1",
        "BspEI": "/TCCGGA/ (BspEI)1",
        "BssHII": "/GCGCGC/ (BssHII)1",
        "BstXI": "/CCANNNNNNTGG/ (BstXI)8",
        "EagI": "/CGGCCG/ (EagI)1",
        "FseI": "/GGCCGGCC/ (FseI)6",
        "PacI": "/TTAATTAA/ (PacI)5",
        "PmeI": "/GTTTAAAC/ (PmeI)4",
        "SbfI": "/CCTGCAGG/ (SbfI)6",
        "SgrAI": "/CRCCGGYG/ (SgrAI)2",
        "SrfI": "/GCCCGGGC/ (SrfI)4",
        "SwaI": "/ATTTAAAT/ (SwaI)4",
        "AflII": "/CTTAAG/ (AflII)1",
        "AgeI": "/ACCGGT/ (AgeI)1",
        "AlwNI": "/CAGNNNCTG/ (AlwNI)6",
        "BsiWI": "/CGTACG/ (BsiWI)1",
        "BspHI": "/TCATGA/ (BspHI)1",
        "Eco53kI": "/GAGCTC/ (Eco53kI)3",
        "HincII": "/GTYRAC/ (HincII)3",
        "MscI": "/TGGCCA/ (MscI)3",
        "PflMI": "/CCANNNNNTGG/ (PflMI)7",
        "PshAI": "/GACNNNNGTC/ (PshAI)5",
        "PvuI": "/CGATCG/ (PvuI)4",
        "SacII": "/CCGCGG/ (SacII)4"
    }

    # Parameters
    st.sidebar.markdown("### ⚙️ Analysis Parameters")
    topology = st.sidebar.selectbox("DNA Topology", ["linear", "circular"], help="Choose DNA conformation")
    bases_per_line = st.sidebar.slider("Bases per line", 30, 120, 60, help="Number of bases to display per line")
    reading_frame = st.sidebar.multiselect(
        "Reading Frame(s)",
        ["1", "2", "3"],
        default=["1"],
        help="Select one or more translation reading frames"
    )
    if not reading_frame:
        st.sidebar.warning("Please select at least one reading frame.")
    
    # Restriction enzyme selection
    st.sidebar.markdown("### 🔬 Restriction Enzyme Selection")
    
    # Option to use custom enzymes or select from database
    enzyme_input_method = st.sidebar.radio("Choose enzyme input method:", 
                                         ["Select from Database", "Custom Input"])
    
    restriction_sites_list = []
    
    if enzyme_input_method == "Select from Database":
        selected_enzymes = st.sidebar.multiselect(
            "Select restriction enzymes:",
            options=list(restriction_enzymes_db.keys()),
            default=["EcoRI", "BamHI", "HindIII"],
            help="Choose from common restriction enzymes"
        )
        
        if selected_enzymes:
            restriction_sites_list = [restriction_enzymes_db[enzyme] for enzyme in selected_enzymes]
            
        # Display selected enzymes
        if restriction_sites_list:
            st.sidebar.markdown("**Selected Enzymes:**")
            for enzyme in selected_enzymes:
                pattern = restriction_enzymes_db[enzyme].split('(')[0].strip('/')
                st.sidebar.write(f"• {enzyme}: {pattern}")
    else:
        # Custom input (will be handled in main content area)
        pass

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🧬 DNA Sequence Input")
        
        # Input method selection
        input_method = st.radio("Choose input method:", ["Text Input", "File Upload"])
        
        dna_input = ""
        if input_method == "Text Input":
            dna_input = st.text_area(
                "Enter DNA sequence (FASTA format):",
                height=200,
                placeholder=">Your_Sequence_Name\nATGCGTACGTAGCTAGCTAG...",
                help="Enter your DNA sequence in FASTA format"
            )
        else:
            uploaded_file = st.file_uploader("Upload FASTA file", type=['fasta', 'fa', 'txt'])
            if uploaded_file:
                dna_input = uploaded_file.read().decode('utf-8')
                st.text_area("Uploaded sequence:", dna_input, height=100, disabled=True)

        st.markdown("## 🔬 Restriction Sites")
        
        if enzyme_input_method == "Custom Input":
            restriction_sites_input = st.text_area(
                "Enter restriction sites (one per line):",
                value="""/GAATTC/ (EcoRI)1
/AAGCTT/ (HindIII)1
/GGATCC/ (BamHI)1""",
                height=150,
                help="Format: /PATTERN/ (Name)CutDistance"
            )
            restriction_sites_list = [site.strip() for site in restriction_sites_input.split('\n') if site.strip()]
        else:
            # Show selected enzymes from database
            if restriction_sites_list:
                st.success(f"✅ Selected {len(restriction_sites_list)} restriction enzymes from database")
                
                # Display in a nice format
                enzyme_display = "\n".join([f"• {site.split('(')[1].split(')')[0]}: {site.split('(')[0].strip('/')}" 
                                          for site in restriction_sites_list])
                st.markdown(f"""
                <div class="info-box">
                    <h4>🧬 Selected Restriction Enzymes:</h4>
                    <pre style="font-family:'JetBrains Mono',monospace; font-size:0.85rem; color:var(--dna-teal); margin:0;">{enzyme_display}</pre>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Please select at least one restriction enzyme from the sidebar!")

    with col2:
        st.markdown("## ℹ️ Information")
        
        st.markdown("""
        <div class="info-box" style="max-height: 300px; overflow-y: auto;">
            <h4>🧬 How This Tool Works</h4>
            <ol style="padding-left: 1.2em; margin:0;">
            <li><b>Input DNA Sequence:</b> Paste or upload your DNA in FASTA format.</li>
            <li><b>Select Restriction Enzymes:</b> Choose from the database or enter custom patterns.</li>
            <li><b>Scan for Sites:</b> Searches your DNA for exact matches and shows positions.</li>
            <li><b>Suggest Mutations:</b> Finds where a small change could create a new site.</li>
            <li><b>Protein Translation:</b> Translates DNA to amino acids in your chosen reading frame.</li>
            <li><b>Visual Results:</b> Color-coded sequences and tables for easy analysis.</li>
            <li><b>Sequence Visualization:</b> DNA displayed with cut sites highlighted and labeled.</li>
            <li><b>Download Everything:</b> Export tables and sequences for further analysis.</li>
            </ol>
            <p style="font-size: 0.85em; color: var(--text-muted); margin-top: 0.6rem; margin-bottom:0;">
            <b>Tip:</b> Designed for cloning, mutagenesis, and synthetic biology.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4>⚠️ Input Format</h4>
            <p><strong>DNA:</strong> FASTA format with header line</p>
            <p><strong>Sites:</strong> /PATTERN/ (Name)Distance</p>
        </div>
        """, unsafe_allow_html=True)

    # Analysis button
    if st.button("🚀 Analyze Sequence", type="primary", width="stretch"):
        if dna_input and restriction_sites_list:
            with st.spinner("Analyzing DNA sequence..."):
                # Process input
                dna_sequences = [dna_input.strip()]
                
                # Genetic code dictionary
                genetic_code_dict = {
                    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
                    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
                    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
                    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
                    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
                    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
                    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
                    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
                    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
                    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
                    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
                    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
                    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
                    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
                    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
                    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G'
                }
                
                # Process each sequence
                for fasta in dna_sequences:
                    lines = fasta.strip().split('\n')
                    title = lines[0][1:] if lines[0].startswith('>') else "Untitled"
                    new_dna = ''.join(lines[1:])
                    new_dna = re.sub(r'[^acgtACGT]', '', new_dna)
                    
                    if not new_dna:
                        st.error("No valid DNA sequence found!")
                        return
                    
                    # Display results header
                    st.markdown("## 📊 Analysis Results")
                    
                    # Sequence statistics
                    gc_content = (new_dna.upper().count('G') + new_dna.upper().count('C')) / len(new_dna) * 100
                    
                    st.markdown(f"""
                    <div class="stats-container">
                        <div class="stat-box">
                            <h3>{len(new_dna)}</h3>
                            <p>Base Pairs</p>
                        </div>
                        <div class="stat-box">
                            <h3>{gc_content:.1f}%</h3>
                            <p>GC Content</p>
                        </div>
                        <div class="stat-box">
                            <h3>{topology.title()}</h3>
                            <p>Topology</p>
                        </div>
                        <div class="stat-box">
                            <h3>{len(restriction_sites_list)}</h3>
                            <p>Enzymes</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Find restriction sites
                    normal_collection = find_restriction_sites(new_dna, restriction_sites_list, topology)
                    mutated_sites = build_mutated_restriction_sites(restriction_sites_list)
                    mutant_collection = find_restriction_sites(new_dna, mutated_sites, topology)
                    
                    # Display found sites
                    st.markdown("### 🎯 Found Restriction Sites")
                    if normal_collection.restriction_sites:
                        sites_data = []
                        for site in normal_collection.restriction_sites:
                            sites_data.append({
                                'Site': site.label,
                                'Position': site.position + 1,
                                'Pattern': site.iupac_pattern,
                                'Cut Distance': site.cut_distance
                            })
                        
                        df_sites = pd.DataFrame(sites_data)
                        st.dataframe(df_sites, width="stretch")
                    else:
                        st.info("No restriction sites found with current parameters.")
                    
                    # Display potential mutations
                    st.markdown("### 🧪 Potential Mutation Sites")
                    if mutant_collection.restriction_sites:
                        mut_data = []
                        for site in mutant_collection.restriction_sites:
                            mut_data.append({
                                'Mutation Site': site.label,
                                'Position': site.position + 1,
                                'Pattern': site.iupac_pattern,
                                'Cut Distance': site.cut_distance
                            })
                        
                        df_mutations = pd.DataFrame(mut_data)
                        st.dataframe(df_mutations, width="stretch")
                    else:
                        st.info("No potential mutation sites found.")
                    
                    # Sequence visualization
                    st.markdown("### 🧬 Sequence Visualization")
                    # Prepare a map of cut positions to enzyme names
                    cut_annotations = {}
                    for site in normal_collection.restriction_sites:
                        cut_pos = site.position
                        # Clamp cut_pos to valid range
                        if 0 <= cut_pos < len(new_dna):
                            # If multiple enzymes cut at same position, join names
                            if cut_pos not in cut_annotations:
                                cut_annotations[cut_pos] = []
                            cut_annotations[cut_pos].append(site.label.split(" at")[0])

                    nucleotide_colors = {
                        'A': '#1f77b4',  # Blue
                        'T': '#d62728',  # Red
                        'G': '#2ca02c',  # Green
                        'C': '#ff7f0e',  # Orange
                    }
                    formatted_sequence = ""
                    i = 0
                    while i < len(new_dna):
                        line_num = str(i + 1).rjust(8)
                        sequence_chunk = new_dna[i:i + bases_per_line]
                        colored_chunk = ""
                        j = 0
                        while j < len(sequence_chunk):
                            codon = sequence_chunk[j:j+3]
                            codon_colored = ""
                            for k, nt in enumerate(codon):
                                seq_pos = i + j + k
                                color = nucleotide_colors.get(nt.upper(), "#888")
                                # Check if this position is a cut site
                                if seq_pos in cut_annotations:
                                    # Add enzyme name above, only once per cut site
                                    enzyme_names = ", ".join(cut_annotations[seq_pos])
                                    codon_colored += (
                                        f"<div style='display:inline-block; text-align:center;'>"
                                        f"<span style='font-size:18px; background:#ffeaa7; color:#ed8936; font-weight:bold; border-radius:4px; padding:2px 6px; margin-bottom:2px;'>{enzyme_names}</span><br>"
                                        f"<span class='restriction-site' style='background:#fff3cd; color:#856404; font-weight:bold;'>{nt.upper()}</span>"
                                        f"</div>"
                                    )
                                else:
                                    codon_colored += f"<span style='color:{color}; font-weight:bold;'>{nt.upper()}</span>"
                            colored_chunk += codon_colored + " "
                            j += 3
                        formatted_sequence += f"{line_num} {colored_chunk.strip()}<br>"
                        i += bases_per_line

                    # For each selected reading frame, generate results
                    mutated_sites_info_all_frames = []
                    formatted_translation_all = {}
                    formatted_mut_translation_all = {}

                    for rf in reading_frame:
                        rf_offset = int(rf) - 1
                        dna_for_translation = new_dna[rf_offset:]
                        translation = translate_dna(dna_for_translation, genetic_code_dict)

                        # Format translation (no highlights in original)
                        formatted_translation = ""
                        amino_per_line = bases_per_line // 3
                        for i in range(0, len(translation), amino_per_line):
                            line_num = str(i + 1).rjust(8)
                            aa_chunk = translation[i:i + amino_per_line]
                            aa_display = " ".join(aa_chunk)
                            formatted_translation += f"{line_num} {aa_display}<br>"

                        formatted_translation_all[rf] = formatted_translation

                        # Translation (Mutated Sequence)
                        mutated_dna = list(new_dna)
                        aa_mut_cut_positions = set()
                        mutated_sites_info = []

                        # For each potential mutation site, check if it causes an amino acid change
                        for site in mutant_collection.restriction_sites:
                            pos = site.position
                            pattern = site.iupac_pattern.upper()
                            if 0 <= pos < len(mutated_dna) - len(pattern) + 1:
                                original_seq = ''.join(mutated_dna[pos:pos+len(pattern)])
                                mutated_seq = list(original_seq)
                                for i, base in enumerate(pattern):
                                    if base != 'N' and mutated_seq[i] != base:
                                        mutated_seq[i] = base
                                # Apply mutation temporarily
                                temp_dna = mutated_dna.copy()
                                temp_dna[pos:pos+len(pattern)] = mutated_seq
                                mutated_dna_str = ''.join(temp_dna)
                                mutated_translation = translate_dna(mutated_dna_str[rf_offset:], genetic_code_dict)
                                # Find which amino acids changed
                                for idx in range(min(len(translation), len(mutated_translation))):
                                    if translation[idx] != mutated_translation[idx]:
                                        codon_start = rf_offset + idx * 3
                                        codon_end = codon_start + 3
                                        if pos >= codon_start and pos < codon_end:
                                            aa_mut_cut_positions.add(idx)
                                            mutated_sites_info.append({
                                                "enzyme": site.label.split(" at")[0],
                                                "pos": pos+1,
                                                "original_seq": original_seq,
                                                "mutated_seq": ''.join(mutated_seq),
                                                "aa_idx": idx+1,
                                                "orig_aa": translation[idx],
                                                "mut_aa": mutated_translation[idx],
                                                "reading_frame": rf
                                            })
                                            break
                        # Apply all mutations for display
                        for info in mutated_sites_info:
                            pos = info["pos"] - 1
                            pattern = info["mutated_seq"]
                            mutated_dna[pos:pos+len(pattern)] = list(pattern)
                        mutated_translation = translate_dna(''.join(mutated_dna)[rf_offset:], genetic_code_dict)

                        # Format mutated translation with highlights at all changed amino acids
                        formatted_mut_translation = ""
                        for i in range(0, len(mutated_translation), amino_per_line):
                            line_num = str(i + 1).rjust(8)
                            aa_chunk = mutated_translation[i:i + amino_per_line]
                            aa_display = ""
                            for j, aa in enumerate(aa_chunk):
                                idx = i + j
                                if idx in aa_mut_cut_positions:
                                    aa_display += f"<span class='mutation-highlight' style='background:#f8d7da; color:#721c24; font-weight:bold;'>{aa}</span> "
                                else:
                                    aa_display += f"{aa} "
                            formatted_mut_translation += f"{line_num} {aa_display.strip()}<br>"

                        formatted_mut_translation_all[rf] = formatted_mut_translation
                        mutated_sites_info_all_frames.extend(mutated_sites_info)

                        # Show results for this reading frame
                        # First show DNA sequence, then amino acid sequence below
                        st.markdown(f"""
                        <div class="result-box">
                            <h4>📝 {title} (Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line; font-size:20px;">
                                {formatted_sequence}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="result-box">
                            <h4>🧬 Amino Acid Sequence (Original, Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line; font-size:22px;">
                                {formatted_translation}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div class="result-box">
                            <h4>🧬 Amino Acid Sequence (With Mutation, Reading Frame {rf})</h4>
                            <div class="dna-sequence" style="max-height:350px; overflow-y:auto; overflow-x:hidden; white-space:pre-line; font-size:22px;">
                                {formatted_mut_translation}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # DNA sequence visualization (shown only once if multiple frames)
                    # (Already shown above for each frame, so skip here)

                    # Mutation information (show ALL possible mutations, for ALL reading frames, with clear indication of protein-changing vs silent)
                    if mutant_collection.restriction_sites:
                        bg_gradients = [
                            "linear-gradient(135deg, rgba(247,37,133,0.12) 0%, rgba(255,107,107,0.08) 100%)",
                            "linear-gradient(135deg, rgba(0,229,195,0.10) 0%, rgba(76,201,240,0.07) 100%)",
                            "linear-gradient(135deg, rgba(162,89,255,0.12) 0%, rgba(76,201,240,0.08) 100%)",
                            "linear-gradient(135deg, rgba(255,186,8,0.10) 0%, rgba(255,107,107,0.07) 100%)",
                            "linear-gradient(135deg, rgba(180,244,66,0.10) 0%, rgba(0,229,195,0.07) 100%)",
                            "linear-gradient(135deg, rgba(76,201,240,0.10) 0%, rgba(162,89,255,0.08) 100%)",
                        ]
                        # CSS for animation and highlights
                        st.markdown("""
                        <style>
                        @keyframes fadeInMove {
                            0% { opacity: 0; transform: translateY(30px) scale(0.98); }
                            100% { opacity: 1; transform: translateY(0) scale(1); }
                        }
                        .mutation-anim-block {
                            animation: fadeInMove 0.9s cubic-bezier(.4,0,.2,1);
                        }
                        .mutation-aa-change {
                            background: rgba(247,37,133,0.15);
                            color: #f72585;
                            border-radius: 6px;
                            padding: 0.2em 0.5em;
                            font-weight: bold;
                            border: 1px solid rgba(247,37,133,0.35);
                            font-family: 'JetBrains Mono', monospace;
                            font-size: 1.1em;
                            transition: background 0.4s;
                        }
                        .mutation-arrow {
                            font-size: 1.7em;
                            margin: 0 0.5em;
                            vertical-align: middle;
                            animation: fadeInMove 1.2s cubic-bezier(.4,0,.2,1);
                            color: #4cc9f0;
                        }
                        .mutation-silent {
                            color: #00e5c3 !important;
                            font-size: 1.0em;
                            margin-left: 0.5em;
                            font-weight: bold;
                            background: rgba(0,229,195,0.1);
                            padding: 0.15em 0.7em;
                            border-radius: 20px;
                            border: 1px solid rgba(0,229,195,0.3);
                            box-shadow: 0 0 8px rgba(0,229,195,0.1);
                            display: inline-block;
                        }
                        .mutation-nonsilent {
                            color: #ff6b6b !important;
                            font-size: 1.0em;
                            margin-left: 0.5em;
                            font-weight: bold;
                            background: rgba(255,107,107,0.1);
                            padding: 0.15em 0.7em;
                            border-radius: 20px;
                            border: 1px solid rgba(255,107,107,0.3);
                            box-shadow: 0 0 8px rgba(255,107,107,0.1);
                            display: inline-block;
                        }
                        </style>
                        """, unsafe_allow_html=True)

                        # For each mutation site, for each reading frame, show info
                        enzyme_blocks = []
                        for idx, site in enumerate(mutant_collection.restriction_sites):
                            pos = site.position
                            pattern = site.iupac_pattern.upper()
                            # Try to extract enzyme name from label or fallback
                            enzyme = site.label.split(" at")[0]
                            # Clean enzyme name for display (remove extra chars if any)
                            enzyme_display = enzyme
                            # Try to get enzyme name from pattern if label is not clean
                            if enzyme_display.startswith("(") and enzyme_display.endswith(")"):
                                enzyme_display = enzyme_display[1:-1]
                            # If enzyme name is empty, fallback to pattern
                            if not enzyme_display.strip():
                                enzyme_display = pattern
                            # Use first two uppercase letters for icon, or fallback to 'E'
                            enzyme_icon = ''.join([c for c in enzyme_display if c.isalnum()])[:2].upper() or "E"

                            original_seq = new_dna[pos:pos+len(pattern)] if 0 <= pos < len(new_dna) - len(pattern) + 1 else ""
                            mutated_seq = ""
                            # Build mutated sequence (replace non-N with pattern base)
                            if original_seq:
                                mutated_seq_list = list(original_seq)
                                for i, base in enumerate(pattern):
                                    if base != 'N' and mutated_seq_list[i] != base:
                                        mutated_seq_list[i] = base
                                mutated_seq = ''.join(mutated_seq_list)
                            # For each reading frame, check effect
                            for rf in reading_frame:
                                rf_offset = int(rf) - 1
                                # Only consider if mutation overlaps a codon in this frame
                                codon_start = ((pos - rf_offset) // 3) * 3 + rf_offset
                                codon_end = codon_start + 3
                                if codon_start < 0 or codon_end > len(new_dna):
                                    continue
                                # Apply mutation to a copy
                                temp_dna = list(new_dna)
                                if original_seq and mutated_seq:
                                    temp_dna[pos:pos+len(pattern)] = list(mutated_seq)
                                mutated_dna_str = ''.join(temp_dna)
                                translation = translate_dna(new_dna[rf_offset:], genetic_code_dict)
                                mutated_translation = translate_dna(mutated_dna_str[rf_offset:], genetic_code_dict)
                                aa_idx = ((pos - rf_offset) // 3) + 1
                                # Find which amino acid(s) in this codon changed
                                orig_aa = translation[aa_idx-1] if aa_idx-1 < len(translation) else "-"
                                mut_aa = mutated_translation[aa_idx-1] if aa_idx-1 < len(mutated_translation) else "-"
                                is_silent = orig_aa == mut_aa
                                # Only show if original_seq and mutated_seq are valid
                                if not original_seq or not mutated_seq:
                                    continue
                                block = f"""
                                <div class="mutation-anim-block" style="background: {bg_gradients[idx % len(bg_gradients)]}; border: 1px solid rgba(0,229,195,0.15); border-radius: 14px; margin-bottom: 1.2rem; padding: 1.4rem; box-shadow: 0 2px 16px rgba(0,0,0,0.2); transition: box-shadow 0.3s, border-color 0.3s;">
                                    <div style="display: flex; align-items: center; gap: 1.2rem;">
                                        <div style="flex-shrink:0;">
                                            <span style="display:inline-block; background:linear-gradient(135deg,rgba(255,186,8,0.2),rgba(255,107,107,0.15)); color:#ffba08; font-weight:700; border-radius:50%; width:52px; height:52px; text-align:center; line-height:52px; font-size:1.4em; border:1.5px solid rgba(255,186,8,0.4); font-family:'Orbitron',monospace; box-shadow:0 0 16px rgba(255,186,8,0.15);">
                                                {enzyme_icon}
                                            </span>
                                        </div>
                                        <div style="flex-grow:1;">
                                            <h4 style="margin:0 0 0.4em 0; color:#e8f4f8; font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.05rem;">{enzyme_display}</h4>
                                            <div style="font-size:0.95em; margin-bottom:0.6em; color:#8fa3b1;">
                                                <b style="color:#4cc9f0;">Restriction site</b> can be introduced at: <span style="color:#f72585; font-family:'JetBrains Mono',monospace;">Position {pos+1}</span> &nbsp;(Reading Frame {rf})
                                            </div>
                                            <div style="display:flex; align-items:center; gap:0.7em; margin-bottom:0.5em;">
                                                <span style="font-family:'JetBrains Mono',monospace; background:rgba(0,0,0,0.3); border-radius:6px; padding:0.25em 0.6em; border:1px solid rgba(255,255,255,0.1); color:#e8f4f8; font-size:0.9em;">
                                                    {original_seq}
                                                </span>
                                                <span class="mutation-arrow">→</span>
                                                <span style="font-family:'JetBrains Mono',monospace; background:rgba(255,186,8,0.12); border-radius:6px; padding:0.25em 0.6em; border:1px solid rgba(255,186,8,0.35); color:#ffba08; font-size:0.9em; font-weight:600;">
                                                    {mutated_seq}
                                                </span>
                                            </div>
                                            <div style="margin-top:0.5em; font-size:1.0em;">
                                                <span style="color:#8fa3b1; font-size:0.9em;">Amino acid change:</span>
                                                <span class="mutation-aa-change">{orig_aa}{aa_idx}{mut_aa}</span>
                                                {f"<span class='mutation-silent'>&#10004; Silent</span>" if is_silent else "<span class='mutation-nonsilent'>&#9888; Protein may change</span>"}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                """
                                enzyme_blocks.append(block)
                        # Only render as HTML if there is at least one valid block
                        if enzyme_blocks:
                            st.markdown(
                                f"""
                                <div class="info-box" style="max-height: 520px; overflow-y: auto; padding-right: 1em;">
                                    <h4 style="margin-bottom:1em;">🔄 Mutation Information — All Reading Frames</h4>
                                    {''.join(enzyme_blocks)}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.info("No valid mutation information available.")
                    else:
                        st.info("No potential mutation sites found for any reading frame.")

                    # For download, generate results for all selected reading frames
                    st.markdown("### 💾 Download Results")

                    # --- Dynamic summary for the report ---
                    summary_lines = []
                    summary_lines.append(f"The sequence analyzed is <b>{title}</b> with length <b>{len(new_dna)} bp</b> and GC content <b>{gc_content:.1f}%</b>.")
                    if normal_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(normal_collection.restriction_sites)}</b> restriction site(s) were found in the sequence for the selected enzymes.")
                    else:
                        summary_lines.append("No restriction sites were found for the selected enzymes in the sequence.")
                    if mutant_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(mutant_collection.restriction_sites)}</b> potential mutation site(s) were identified where a single or double base change could introduce a new restriction site.")
                    else:
                        summary_lines.append("No potential mutation sites were found where a new restriction site could be introduced by a small change.")
                    # Count protein-changing mutations across all frames
                    total_mutated_sites_info = [info for info in mutated_sites_info_all_frames]
                    if total_mutated_sites_info:
                        summary_lines.append(f"<b>{len(total_mutated_sites_info)}</b> mutation(s) would also change the protein sequence at the restriction site position (highlighted in the report).")
                    else:
                        summary_lines.append("None of the potential mutation sites would change the protein sequence at the restriction site position.")
                    summary_lines.append("This report provides a summary of restriction sites, possible new sites by mutation, and the effect of these changes on the protein translation. Use this to plan cloning or mutagenesis experiments and to check if introducing a restriction site will also alter the protein.")

                    html_summary = "<ul style='font-size:1.1em;'>" + "".join([f"<li>{line}</li>" for line in summary_lines]) + "</ul>"

                    # Prepare HTML sections for each reading frame
                    html_rf_sections = ""
                    plain_rf_sections = ""
                    for rf in reading_frame:
                        rf_title = f"Reading Frame {rf}"
                        formatted_translation = formatted_translation_all[rf]
                        formatted_mut_translation = formatted_mut_translation_all[rf]
                        mutated_sites_info = [info for info in mutated_sites_info_all_frames if info["reading_frame"] == rf]
                        html_rf_sections += f"""
                        <div class="section">
                            <h2>🔬 Protein Translation (Original, {rf_title})</h2>
                            <div class="aa-sequence">{formatted_translation}</div>
                        </div>
                        <div class="section">
                            <h2>🧬 Protein Translation (With Mutation, {rf_title})</h2>
                            <div class="aa-sequence">{formatted_mut_translation}</div>
                        </div>
                        <div class="section">
                            <h2>🔄 Mutation Information ({rf_title})</h2>
                            {"".join([
                                f"<div class='enzyme-block'><b>{info['enzyme']}</b> can be introduced at <b>position {info['pos']}</b> by changing <span class='dna-sequence' style='display:inline;background:#f8f9fa;'>{info['original_seq']}</span> → <span class='dna-sequence' style='display:inline;background:#ffeaa7;'>{info['mutated_seq']}</span>. This causes an amino acid change at position <span class='mutation-highlight'>{info['aa_idx']}</span>: <span class='mutation-highlight'>{info['orig_aa']}→{info['mut_aa']}</span>.</div>"
                                for info in mutated_sites_info
                            ]) if mutated_sites_info else "<i>No potential mutation sites found that would change the amino acid at a restriction site position in this reading frame.</i>"}
                        </div>
                        """
                        # Plain text for this reading frame
                        plain_rf_sections += f"\n=== PROTEIN TRANSLATION (Original, {rf_title}) ===\n"
                        plain_rf_sections += _re.sub('<[^<]+?>', '', formatted_translation.replace('<br>', '\n')) + "\n"
                        plain_rf_sections += f"\n=== PROTEIN TRANSLATION (With Mutation, {rf_title}) ===\n"
                        plain_rf_sections += _re.sub('<[^<]+?>', '', formatted_mut_translation.replace('<br>', '\n')) + "\n"
                        plain_rf_sections += f"\n=== MUTATION INFORMATION ({rf_title}) ===\n"
                        if mutated_sites_info:
                            for mutated_site_info in mutated_sites_info:
                                plain_rf_sections += (
                                    f"Restriction enzyme {mutated_site_info['enzyme']} can be introduced at position {mutated_site_info['pos']} "
                                    f"by changing {mutated_site_info['original_seq']} to {mutated_site_info['mutated_seq']}. "
                                    f"This causes an amino acid change at position {mutated_site_info['aa_idx']} from "
                                    f"{mutated_site_info['orig_aa']} to {mutated_site_info['mut_aa']}.\n"
                                )
                            plain_rf_sections += (
                                "\nThe highlighted amino acids in the mutated translation indicate where new restriction sites could be introduced "
                                "by nucleotide changes that also alter the amino acid. Refer to the 'Found Restriction Sites' section above for the exact enzyme and position.\n"
                            )
                        else:
                            plain_rf_sections += "No potential mutation sites found that would change the amino acid at a restriction site position in this reading frame.\n"

                    # Prepare a visually enhanced HTML report for download
                    # --- Enhanced dynamic summary for the report ---
                    summary_lines = []
                    summary_lines.append(f"The sequence analyzed is <b>{title}</b> with length <b>{len(new_dna)} bp</b> and GC content <b>{gc_content:.1f}%</b>.")
                    summary_lines.append(f"<b>DNA topology:</b> {topology.title()}.")
                    summary_lines.append(f"<b>Restriction enzymes analyzed:</b> {', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}.")
                    summary_lines.append(f"<b>Reading frame(s) selected:</b> {', '.join(reading_frame)}.")
                    if normal_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(normal_collection.restriction_sites)}</b> restriction site(s) were found in the sequence for the selected enzymes.")
                    else:
                        summary_lines.append("No restriction sites were found for the selected enzymes in the sequence.")
                    if mutant_collection.restriction_sites:
                        summary_lines.append(f"<b>{len(mutant_collection.restriction_sites)}</b> potential mutation site(s) were identified where a single or double base change could introduce a new restriction site.")
                    else:
                        summary_lines.append("No potential mutation sites were found where a new restriction site could be introduced by a small change.")
                    # Count protein-changing mutations across all frames
                    total_mutated_sites_info = [info for info in mutated_sites_info_all_frames]
                    if total_mutated_sites_info:
                        summary_lines.append(f"<b>{len(total_mutated_sites_info)}</b> mutation(s) would also change the protein sequence at the restriction site position (highlighted in the report).")
                    else:
                        summary_lines.append("None of the potential mutation sites would change the protein sequence at the restriction site position.")
                    # Add more details about reading frames and translation
                    summary_lines.append(f"Protein translation was performed for reading frame(s): <b>{', '.join(reading_frame)}</b>.")
                    for rf in reading_frame:
                        rf_mut = [info for info in mutated_sites_info_all_frames if info["reading_frame"] == rf]
                        summary_lines.append(
                            f"In reading frame <b>{rf}</b>: "
                            f"{'No protein-changing mutations detected.' if not rf_mut else f'<b>{len(rf_mut)}</b> mutation(s) would alter the amino acid sequence.'}"
                        )
                    summary_lines.append("This report provides a summary of restriction sites, possible new sites by mutation, and the effect of these changes on the protein translation. Use this to plan cloning or mutagenesis experiments and to check if introducing a restriction site will also alter the protein.")

                    html_summary = "<ul style='font-size:1.1em;'>" + "".join([f"<li>{line}</li>" for line in summary_lines]) + "</ul>"

                    # Prepare a visually enhanced HTML report for download
                    html_report = f"""
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Mutate for Digest Analysis Results</title>
                        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
                        <style>
                            * {{
                                margin: 0;
                                padding: 0;
                                box-sizing: border-box;
                            }}
                            
                            body {{
                                font-family: 'Space Grotesk', sans-serif;
                                background: linear-gradient(135deg, #0a0e1a 0%, #1a1f3a 100%);
                                color: #e8f4f8;
                                line-height: 1.6;
                                padding: 0;
                                margin: 0;
                            }}
                            
                            .page-wrapper {{
                                min-height: 100vh;
                                background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0f1a2e 100%);
                            }}
                            
                            .header {{
                                background: linear-gradient(135deg, #0d1b2a 0%, #112240 50%, #0d1b2a 100%);
                                color: #e8f4f8;
                                padding: 3em 2em;
                                border-radius: 0 0 20px 20px;
                                text-align: center;
                                border-bottom: 2px solid rgba(0, 229, 195, 0.3);
                                box-shadow: 0 8px 32px rgba(0, 229, 195, 0.1), 0 0 60px rgba(162, 89, 255, 0.05);
                                position: relative;
                                overflow: hidden;
                            }}
                            
                            .header::before {{
                                content: '';
                                position: absolute;
                                top: 0; left: 0; right: 0; bottom: 0;
                                background: radial-gradient(ellipse 80% 60% at 50% 20%, rgba(0,229,195,0.08) 0%, transparent 60%);
                                pointer-events: none;
                            }}
                            
                            .header h1 {{
                                font-family: 'Orbitron', monospace;
                                font-size: 2.8em;
                                font-weight: 900;
                                background: linear-gradient(90deg, #00e5c3, #4cc9f0, #a259ff);
                                -webkit-background-clip: text;
                                -webkit-text-fill-color: transparent;
                                background-clip: text;
                                margin-bottom: 0.5em;
                                letter-spacing: 2px;
                                position: relative;
                                z-index: 1;
                            }}
                            
                            .header .subtitle {{
                                font-size: 1.2em;
                                color: #00e5c3;
                                letter-spacing: 3px;
                                text-transform: uppercase;
                                margin-bottom: 1em;
                                position: relative;
                                z-index: 1;
                            }}
                            
                            .header .timestamp {{
                                color: #8fa3b1;
                                font-size: 0.95em;
                                position: relative;
                                z-index: 1;
                            }}
                            
                            .container {{
                                max-width: 1200px;
                                margin: 0 auto;
                                padding: 0 1em;
                            }}
                            
                            .section {{
                                background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
                                border: 1px solid rgba(0, 229, 195, 0.18);
                                border-radius: 16px;
                                margin: 2.5em auto;
                                padding: 2.5em;
                                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 20px rgba(0, 229, 195, 0.08);
                                position: relative;
                                overflow: hidden;
                                transition: all 0.3s ease;
                            }}
                            
                            .section::before {{
                                content: '';
                                position: absolute;
                                top: 0; left: 0;
                                width: 4px;
                                height: 100%;
                                background: linear-gradient(180deg, #00e5c3, #a259ff);
                                border-radius: 16px 0 0 16px;
                            }}
                            
                            .section h2 {{
                                font-family: 'Space Grotesk', sans-serif;
                                font-size: 1.8em;
                                font-weight: 700;
                                color: #e8f4f8;
                                margin-bottom: 1.5em;
                                display: flex;
                                align-items: center;
                                gap: 0.8em;
                                letter-spacing: 0.5px;
                                position: relative;
                                z-index: 1;
                            }}
                            
                            .section h2::after {{
                                content: '';
                                flex-grow: 1;
                                height: 2px;
                                background: linear-gradient(90deg, rgba(0, 229, 195, 0.4), transparent);
                                border-radius: 1px;
                            }}
                            
                            .section h3 {{
                                font-family: 'Space Grotesk', sans-serif;
                                font-size: 1.3em;
                                font-weight: 600;
                                color: #4cc9f0;
                                margin: 1.5em 0 1em 0;
                                letter-spacing: 0.5px;
                            }}
                            
                            .stats-container {{
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                gap: 1.5em;
                                margin-bottom: 2em;
                            }}
                            
                            .stat-box {{
                                background: linear-gradient(135deg, rgba(0, 229, 195, 0.1), rgba(76, 201, 240, 0.08));
                                border: 1px solid rgba(0, 229, 195, 0.25);
                                border-radius: 12px;
                                padding: 1.8em;
                                text-align: center;
                                position: relative;
                                overflow: hidden;
                                transition: all 0.3s ease;
                            }}
                            
                            .stat-box::before {{
                                content: '';
                                position: absolute;
                                top: 0; left: 0; right: 0; bottom: 0;
                                background: radial-gradient(circle at 50% 50%, rgba(0, 229, 195, 0.15), transparent 70%);
                                opacity: 0;
                                transition: opacity 0.3s ease;
                            }}
                            
                            .stat-box:hover {{
                                transform: translateY(-4px);
                                box-shadow: 0 12px 24px rgba(0, 229, 195, 0.15);
                                border-color: rgba(0, 229, 195, 0.4);
                            }}
                            
                            .stat-box:hover::before {{
                                opacity: 1;
                            }}
                            
                            .stat-value {{
                                font-family: 'Orbitron', monospace;
                                font-size: 2.5em;
                                font-weight: 900;
                                color: #00e5c3;
                                line-height: 1;
                                margin-bottom: 0.5em;
                                position: relative;
                                z-index: 1;
                                letter-spacing: 1px;
                            }}
                            
                            .stat-label {{
                                font-size: 0.85em;
                                color: #8fa3b1;
                                text-transform: uppercase;
                                letter-spacing: 1.5px;
                                font-weight: 600;
                                position: relative;
                                z-index: 1;
                            }}
                            
                            .summary-box {{
                                background: linear-gradient(135deg, rgba(0, 229, 195, 0.08), rgba(76, 201, 240, 0.05));
                                border: 1px solid rgba(0, 229, 195, 0.22);
                                border-radius: 12px;
                                padding: 2em;
                                margin-bottom: 2em;
                                position: relative;
                                overflow: hidden;
                            }}
                            
                            .summary-box::before {{
                                content: '';
                                position: absolute;
                                top: 0; left: 0;
                                width: 4px;
                                height: 100%;
                                background: linear-gradient(180deg, #00e5c3, #4cc9f0);
                            }}
                            
                            .summary-box ul {{
                                list-style: none;
                                padding: 0;
                                margin: 0;
                            }}
                            
                            .summary-box li {{
                                padding: 0.8em 0 0.8em 1.5em;
                                color: #e8f4f8;
                                font-size: 1.05em;
                                line-height: 1.7;
                                position: relative;
                                border-bottom: 1px solid rgba(0, 229, 195, 0.1);
                            }}
                            
                            .summary-box li:last-child {{
                                border-bottom: none;
                            }}
                            
                            .summary-box li::before {{
                                content: '●';
                                position: absolute;
                                left: 0;
                                color: #00e5c3;
                                font-weight: bold;
                            }}
                            
                            .summary-box b {{
                                color: #00e5c3;
                                font-weight: 700;
                            }}
                            
                            .info-table {{
                                width: 100%;
                                border-collapse: collapse;
                                margin: 1.5em 0;
                                background: rgba(10, 14, 26, 0.5);
                                border-radius: 10px;
                                overflow: hidden;
                            }}
                            
                            .info-table th {{
                                background: linear-gradient(90deg, rgba(0, 229, 195, 0.15), rgba(76, 201, 240, 0.1));
                                color: #00e5c3;
                                padding: 1em;
                                text-align: left;
                                font-weight: 700;
                                text-transform: uppercase;
                                letter-spacing: 1px;
                                font-size: 0.9em;
                                border-bottom: 2px solid rgba(0, 229, 195, 0.2);
                            }}
                            
                            .info-table td {{
                                padding: 1em;
                                border-bottom: 1px solid rgba(0, 229, 195, 0.1);
                                color: #e8f4f8;
                                font-family: 'JetBrains Mono', monospace;
                            }}
                            
                            .info-table tr:hover {{
                                background: rgba(0, 229, 195, 0.05);
                            }}
                            
                            .dna-sequence {{
                                font-family: 'JetBrains Mono', monospace;
                                font-size: 0.95em;
                                background: rgba(10, 14, 26, 0.8);
                                border: 1px solid rgba(0, 229, 195, 0.2);
                                border-radius: 10px;
                                padding: 1.5em;
                                margin: 1.5em 0;
                                overflow-x: auto;
                                white-space: pre-wrap;
                                word-break: break-all;
                                line-height: 1.8;
                                color: #000000;
                                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
                            }}
                            
                            .aa-sequence {{
                                font-family: 'JetBrains Mono', monospace;
                                font-size: 1.1em;
                                background: rgba(10, 14, 26, 0.8);
                                border: 1px solid rgba(76, 201, 240, 0.2);
                                border-radius: 10px;
                                padding: 1.5em;
                                margin: 1.5em 0;
                                overflow-x: auto;
                                white-space: pre-wrap;
                                word-break: break-all;
                                line-height: 2;
                                color: #e8f4f8;
                                box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
                                letter-spacing: 0.5em;
                            }}
                            
                            .restriction-site {{
                                background: rgba(255, 186, 8, 0.2);
                                color: #ffba08;
                                font-weight: 700;
                                border-radius: 4px;
                                padding: 0.2em 0.5em;
                                border: 1px solid rgba(255, 186, 8, 0.4);
                                box-shadow: 0 0 8px rgba(255, 186, 8, 0.15);
                            }}
                            
                            .mutation-highlight {{
                                background: rgba(247, 37, 133, 0.2);
                                color: #f72585;
                                font-weight: 700;
                                border-radius: 4px;
                                padding: 0.2em 0.5em;
                                border: 1px solid rgba(247, 37, 133, 0.4);
                                box-shadow: 0 0 8px rgba(247, 37, 133, 0.15);
                            }}
                            
                            .enzyme-block {{
                                background: linear-gradient(135deg, rgba(247, 37, 133, 0.12), rgba(255, 107, 107, 0.08));
                                border: 1px solid rgba(255, 186, 8, 0.28);
                                border-radius: 12px;
                                padding: 1.5em;
                                margin: 1.5em 0;
                                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                                position: relative;
                                overflow: hidden;
                                transition: all 0.3s ease;
                            }}
                            
                            .enzyme-block::before {{
                                content: '';
                                position: absolute;
                                top: 0; left: 0;
                                width: 4px;
                                height: 100%;
                                background: linear-gradient(180deg, #ffba08, #ff6b6b);
                            }}
                            
                            .enzyme-block:hover {{
                                box-shadow: 0 8px 24px rgba(255, 186, 8, 0.15);
                                border-color: rgba(255, 186, 8, 0.4);
                                transform: translateX(2px);
                            }}
                            
                            .enzyme-header {{
                                display: flex;
                                align-items: center;
                                gap: 1em;
                                margin-bottom: 1em;
                            }}
                            
                            .enzyme-icon {{
                                display: inline-flex;
                                align-items: center;
                                justify-content: center;
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, rgba(255, 186, 8, 0.3), rgba(255, 107, 107, 0.2));
                                border: 2px solid rgba(255, 186, 8, 0.4);
                                border-radius: 50%;
                                font-weight: 700;
                                color: #ffba08;
                                font-size: 1.3em;
                                font-family: 'Orbitron', monospace;
                                box-shadow: 0 0 16px rgba(255, 186, 8, 0.15);
                            }}
                            
                            .enzyme-name {{
                                font-size: 1.2em;
                                font-weight: 700;
                                color: #ffba08;
                                font-family: 'Space Grotesk', sans-serif;
                            }}
                            
                            .enzyme-details {{
                                margin-left: 3.5em;
                            }}
                            
                            .enzyme-details p {{
                                margin: 0.5em 0;
                                color: #e8f4f8;
                                font-size: 1em;
                            }}
                            
                            .mutation-sequence {{
                                display: inline-block;
                                font-family: 'JetBrains Mono', monospace;
                                border-radius: 6px;
                                padding: 0.4em 0.8em;
                                margin: 0 0.5em;
                                font-weight: 700;
                                font-size: 1.1em;
                                letter-spacing: 0.5px;
                            }}
                            
                            .mutation-sequence.original {{
                                background: #a3d5ff;
                                border: 2px solid #0066cc;
                                color: #000000;
                            }}
                            
                            .mutation-sequence.mutated {{
                                background: #ffd580;
                                border: 2px solid #ff8c00;
                                color: #000000;
                            }}
                            
                            .mutation-arrow {{
                                font-size: 1.5em;
                                margin: 0 0.5em;
                                vertical-align: middle;
                                color: #4cc9f0;
                            }}
                            
                            .amino-change {{
                                background: rgba(247, 37, 133, 0.15);
                                color: #f72585;
                                border-radius: 6px;
                                padding: 0.3em 0.8em;
                                font-weight: 700;
                                border: 1px solid rgba(247, 37, 133, 0.35);
                                font-family: 'JetBrains Mono', monospace;
                                display: inline-block;
                                margin: 0 0.5em;
                            }}
                        
                            .mutation-badge {{
                                display: inline-block;
                                padding: 0.3em 0.8em;
                                border-radius: 20px;
                                font-size: 0.9em;
                                font-weight: 600;
                                margin-left: 1em;
                            }}
                            
                            .mutation-badge.silent {{
                                background: rgba(0, 229, 195, 0.15);
                                border: 1px solid rgba(0, 229, 195, 0.3);
                                color: #00e5c3;
                            }}
                            
                            .mutation-badge.nonsilent {{
                                background: rgba(255, 107, 107, 0.15);
                                border: 1px solid rgba(255, 107, 107, 0.3);
                                color: #ff6b6b;
                            }}
                            
                            .list-item {{
                                padding: 1em;
                                background: rgba(0, 229, 195, 0.06);
                                border-left: 4px solid rgba(0, 229, 195, 0.3);
                                border-radius: 4px;
                                margin: 0.8em 0;
                                color: #e8f4f8;
                            }}
                            
                            .footer {{
                                text-align: center;
                                padding: 2em;
                                color: #8fa3b1;
                                font-size: 0.9em;
                                border-top: 1px solid rgba(0, 229, 195, 0.1);
                                margin-top: 3em;
                            }}
                            
                            .footer strong {{
                                color: #00e5c3;
                            }}
                            
                            @media print {{
                                body {{ background: white; color: #000; }}
                                .section {{ background: white; color: #000; border-color: #ddd; }}
                                .stat-box {{ background: #f5f5f5; }}
                            }}
                            
                            @keyframes fadeIn {{
                                from {{ opacity: 0; transform: translateY(10px); }}
                                to {{ opacity: 1; transform: translateY(0); }}
                            }}
                            
                            .section {{
                                animation: fadeIn 0.6s ease-out;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="page-wrapper">
                            <div class="header">
                                <div class="subtitle">🧬 Restriction Site Analysis</div>
                                <h1>Mutate for Digest</h1>
                                <div class="timestamp">Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
                            </div>
                            
                            <div class="container">
                                <!-- Summary Section -->
                                <div class="section">
                                    <h2>📋 Executive Summary</h2>
                                    <div class="summary-box">
                                        {html_summary}
                                    </div>
                                </div>
                                
                                <!-- Sequence Statistics -->
                                <div class="section">
                                    <h2>📊 Sequence Statistics</h2>
                                    <div class="stats-container">
                                        <div class="stat-box">
                                            <div class="stat-value">{len(new_dna)}</div>
                                            <div class="stat-label">Base Pairs</div>
                                        </div>
                                        <div class="stat-box">
                                            <div class="stat-value">{gc_content:.1f}%</div>
                                            <div class="stat-label">GC Content</div>
                                        </div>
                                        <div class="stat-box">
                                            <div class="stat-value">{topology.title()}</div>
                                            <div class="stat-label">DNA Topology</div>
                                        </div>
                                        <div class="stat-box">
                                            <div class="stat-value">{len(restriction_sites_list)}</div>
                                            <div class="stat-label">Enzymes Analyzed</div>
                                        </div>
                                    </div>
                                    
                                    <h3>Analysis Parameters</h3>
                                    <table class="info-table">
                                        <tr>
                                            <th>Parameter</th>
                                            <th>Value</th>
                                        </tr>
                                        <tr>
                                            <td>Sequence Name</td>
                                            <td><strong>{title}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>Sequence Length</td>
                                            <td><strong>{len(new_dna)} bp</strong></td>
                                        </tr>
                                        <tr>
                                            <td>GC Content</td>
                                            <td><strong>{gc_content:.1f}%</strong></td>
                                        </tr>
                                        <tr>
                                            <td>DNA Topology</td>
                                            <td><strong>{topology.title()}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>Reading Frames</td>
                                            <td><strong>{', '.join(reading_frame)}</strong></td>
                                        </tr>
                                        <tr>
                                            <td>Restriction Enzymes</td>
                                            <td><strong>{', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}</strong></td>
                                        </tr>
                                    </table>
                                </div>
                                
                                <!-- Found Restriction Sites -->
                                <div class="section">
                                    <h2>🎯 Found Restriction Sites</h2>
                                    {"" if normal_collection.restriction_sites else "<p style='color: #8fa3b1; font-style: italic;'>No restriction sites found with current parameters.</p>"}
                                    {f"<table class='info-table'>{''.join([f'<tr><td><span class=restriction-site>{site.label}</span></td><td>{site.iupac_pattern}</td><td>{site.cut_distance}</td></tr>' for site in normal_collection.restriction_sites])}</table>" if normal_collection.restriction_sites else ""}
                                </div>
                                
                                <!-- Potential Mutation Sites -->
                                <div class="section">
                                    <h2>🧪 Potential Mutation Sites</h2>
                                    {"" if mutant_collection.restriction_sites else "<p style='color: #8fa3b1; font-style: italic;'>No potential mutation sites found.</p>"}
                                    {f"<table class='info-table'>{''.join([f'<tr><td><span class=mutation-highlight>{site.label}</span></td><td>{site.iupac_pattern}</td><td>{site.cut_distance}</td></tr>' for site in mutant_collection.restriction_sites])}</table>" if mutant_collection.restriction_sites else ""}
                                </div>
                                
                                <!-- DNA Sequence Visualization -->
                                <div class="section">
                                    <h2>🧬 DNA Sequence Visualization</h2>
                                    <p style="color: #8fa3b1; margin-bottom: 1em;">Highlighted positions indicate restriction enzyme cut sites.</p>
                                    <div class="dna-sequence">{formatted_sequence}</div>
                                </div>
                                
                                <!-- Protein Translation Results -->
                                {html_rf_sections}
                                
                                <!-- Footer -->
                                <div class="footer">
                                    <strong>Mutate for Digest</strong> | Advanced Bioinformatics Analysis Tool<br>
                                    This report is generated for research purposes. Always verify results experimentally.
                                </div>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    # Also provide a plain text version for compatibility
                    plain_text = f"""Mutate for Digest Analysis Results
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
{"".join([_re.sub('<[^<]+?>', '', line) for line in summary_lines])}

Sequence: {title}
Length: {len(new_dna)} bp
GC Content: {gc_content:.1f}%
Topology: {topology}
Restriction Sites Analyzed: {', '.join([site.split('(')[1].split(')')[0] for site in restriction_sites_list])}

=== RESTRICTION SITES FOUND ===
"""
                    if normal_collection.restriction_sites:
                        for site in normal_collection.restriction_sites:
                            plain_text += f"{site.label} - Pattern: {site.iupac_pattern} - Cut Distance: {site.cut_distance}\n"
                    else:
                        plain_text += "No restriction sites found with current parameters.\n"

                    plain_text += "\n=== POTENTIAL MUTATION SITES ===\n"
                    if mutant_collection.restriction_sites:
                        for site in mutant_collection.restriction_sites:
                            plain_text += f"{site.label} - Pattern: {site.iupac_pattern} - Cut Distance: {site.cut_distance}\n"
                    else:
                        plain_text += "No potential mutation sites found.\n"

                    plain_text += "\n=== DNA SEQUENCE (with cut site annotations) ===\n"
                    plain_seq = _re.sub('<[^<]+?>', '', formatted_sequence.replace('<br>', '\n'))
                    plain_text += plain_seq + "\n"

                    plain_text += plain_rf_sections

                    # Download buttons for both HTML (visual) and plain text
                    st.download_button(
                        label="📄 Download Visual HTML Report",
                        data=html_report,
                        file_name=f"mutate_digest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                    st.download_button(
                        label="📄 Download Plain Text Results",
                        data=plain_text,
                        file_name=f"mutate_digest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )

if __name__ == "__main__":
    main()

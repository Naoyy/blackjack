"""
Blackjack Streamlit App — Entry Point
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="Blackjack 🃏",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* =========================================================
   FONTS
   ========================================================= */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

/* =========================================================
   GLOBAL BACKGROUND
   ========================================================= */
.stApp {
    background: radial-gradient(ellipse at top, #0f2017 0%, #0a0a0f 70%);
    color: #e8e8e8;
}

/* =========================================================
   TABS
   ========================================================= */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #0f0f1a;
    border-radius: 12px;
    padding: 5px;
    border: 1px solid #2a2a3a;
    flex-wrap: wrap;       /* wrap on small screens */
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 7px 14px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.4px;
    color: #888 !important;
    background: transparent !important;
    border: none !important;
    white-space: nowrap;
}
.stTabs [aria-selected="true"] {
    background: #1a1a2e !important;
    color: #fbbf24 !important;
    border: 1px solid #3a3a5a !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 16px; }

/* =========================================================
   BUTTONS
   ========================================================= */
.stButton > button {
    background: linear-gradient(135deg, #1a1a2e, #16213e) !important;
    color: #e8e8e8 !important;
    border: 1px solid #3a3a5a !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.15s ease !important;
    padding: 10px 12px !important;
    min-height: 44px !important;   /* touch-friendly */
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a2a4e, #1a2a5e) !important;
    border-color: #fbbf24 !important;
    color: #fbbf24 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(251,191,36,0.2) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #166534, #15803d) !important;
    border-color: #22c55e !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #15803d, #16a34a) !important;
    border-color: #4ade80 !important;
    box-shadow: 0 4px 16px rgba(34,197,94,0.3) !important;
}
.stButton > button:disabled {
    opacity: 0.38 !important;
    cursor: not-allowed !important;
    transform: none !important;
}

/* =========================================================
   DATAFRAME / ALERTS / DIVIDER
   ========================================================= */
.stDataFrame { border-radius: 8px; overflow: hidden; }
.stAlert { border-radius: 8px !important; }
#MainMenu, footer, header { visibility: hidden; }
hr { border-color: #2a2a3a !important; margin: 20px 0 !important; }

/* =========================================================
   GAME TABLE  (green felt card area)
   ========================================================= */
.bj-table {
    background: linear-gradient(135deg, #0a4f2a, #0d6635);
    border-radius: 16px;
    padding: 18px 20px;
    margin: 10px 0;
    border: 3px solid #2d8a50;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    overflow: hidden;           /* prevents any child from leaking out */
}
.bj-divider {
    border-top: 1px solid rgba(255,255,255,0.12);
    margin: 10px 0;
}
.bj-hand { margin: 6px 0; }
.bj-hand-label {
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.bj-cards-row {
    display: flex;
    flex-wrap: wrap;           /* wrap cards on narrow screens */
    align-items: center;
    gap: 2px;
}
.bj-score {
    font-size: 13px;
    color: rgba(255,255,255,0.5);
    margin-left: 6px;
}

/* =========================================================
   CARDS
   ========================================================= */
.bj-card {
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 74px;
    border-radius: 7px;
    background: #f8f5f0;
    border: 2px solid #ddd;
    margin: 3px;
    font-weight: 700;
    box-shadow: 0 3px 10px rgba(0,0,0,0.3);
    line-height: 1.1;
    flex-shrink: 0;
}
.bj-card-hidden {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 74px;
    border-radius: 7px;
    background: linear-gradient(135deg, #1a1a2e 25%, #16213e 100%);
    border: 2px solid #4a4a6a;
    margin: 3px;
    font-size: 20px;
    color: #4a4a6a;
    font-weight: bold;
    box-shadow: 0 3px 10px rgba(0,0,0,0.4);
    flex-shrink: 0;
}
.bj-rank { font-size: 16px; }
.bj-suit { font-size: 19px; }

/* =========================================================
   HEADER / CAPITAL
   ========================================================= */
.bj-header {
    text-align: center;
    padding: 8px 0 16px;
}
.bj-logo { font-size: 38px; }
.bj-title {
    margin: 0 !important;
    font-size: 1.9rem !important;
    letter-spacing: 3px;
}
.bj-capital {
    text-align: center;
    margin-bottom: 16px;
}
.bj-capital-label {
    font-size: 1rem;
    color: #888;
}
.bj-capital span {
    font-size: 1.55rem;
    font-weight: 700;
}

/* =========================================================
   MISC GAME ELEMENTS
   ========================================================= */
.bj-hint {
    text-align: center;
    color: #aaa;
    margin-bottom: 8px;
    font-size: 0.9rem;
}
.bj-msg {
    text-align: center;
    font-size: 1rem;
    color: #fbbf24;
    margin-bottom: 6px;
}
.bj-gain-row {
    text-align: center;
    margin: 10px 0;
}
.bj-gain-cap {
    color: #888;
    font-size: 0.88rem;
}
.bj-broke {
    text-align: center;
    padding: 20px;
    background: #1a0a0a;
    border-radius: 12px;
    border: 1px solid #7f1d1d;
    margin-bottom: 16px;
}
.bj-broke-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #f87171;
    margin: 8px 0 4px;
}
.bj-broke-sub {
    font-size: 0.88rem;
    color: #888;
    margin: 0;
}

/* =========================================================
   RESPONSIVE — narrow screens (≤ 480 px, e.g. phones)
   ========================================================= */
@media (max-width: 480px) {
    .bj-title  { font-size: 1.5rem !important; letter-spacing: 2px; }
    .bj-logo   { font-size: 28px; }
    .bj-capital span { font-size: 1.25rem; }

    /* Smaller cards so 5+ cards still fit */
    .bj-card, .bj-card-hidden {
        width: 42px !important;
        height: 60px !important;
        margin: 2px !important;
        border-radius: 5px !important;
    }
    .bj-rank { font-size: 13px !important; }
    .bj-suit { font-size: 15px !important; }
    .bj-card-hidden { font-size: 16px !important; }

    .bj-table {
        padding: 12px 14px !important;
        border-radius: 10px !important;
    }
    .bj-hand-label { font-size: 10px !important; }

    /* Action buttons: smaller text, still touch-friendly */
    .stButton > button {
        font-size: 0.78rem !important;
        padding: 8px 6px !important;
        min-height: 40px !important;
    }

    /* Tabs: smaller padding */
    .stTabs [data-baseweb="tab"] {
        padding: 6px 10px !important;
        font-size: 0.78rem !important;
    }
}

/* =========================================================
   RESPONSIVE — medium screens (481–768 px, small tablets)
   ========================================================= */
@media (min-width: 481px) and (max-width: 768px) {
    .bj-card, .bj-card-hidden {
        width: 48px !important;
        height: 68px !important;
    }
    .bj-rank { font-size: 15px !important; }
    .bj-suit { font-size: 17px !important; }
}
</style>
""", unsafe_allow_html=True)

# ---- Import pages ----
from pages import game, rules, stats

# ---- Session state init ----
from config import Wallet
if "history" not in st.session_state:
    st.session_state.history = []
if "capital" not in st.session_state:
    st.session_state.capital = Wallet.STARTING_CAPITAL

# ---- Tabs ----
tabs = st.tabs(["🃏 Start Game", "📖 Check Rules", "📊 Check Stats"])
with tabs[0]: game.render()
with tabs[1]: rules.render()
with tabs[2]: stats.render()

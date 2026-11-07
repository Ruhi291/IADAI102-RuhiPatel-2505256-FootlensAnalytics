from pathlib import Path

import streamlit as st

from src.components import (
    initialize_state,
    load_data,
    render_global_controls,
)

st.set_page_config(
    page_title="FootLens Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "FootLens Analytics — Football Injury Intelligence Platform"
    },
)

PAGES_DIR = Path(__file__).resolve().parent / "pages"

initialize_state()

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1550px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }

    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 15px;
        padding: 18px;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 750;
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
    }

    div[data-testid="stButton"] button {
        border-radius: 10px;
        font-weight: 600;
    }

    div[data-testid="stMultiSelect"] {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

navigation = st.navigation(
    {
        "Analytics": [
            st.Page(
                str(PAGES_DIR / "home.py"),
                title="Home",
                icon="🏠",
                default=True,
            ),
            st.Page(
                str(PAGES_DIR / "injuries.py"),
                title="Injuries",
                icon="🩺",
            ),
            st.Page(
                str(PAGES_DIR / "matches.py"),
                title="Matches",
                icon="⚽",
            ),
            st.Page(
                str(PAGES_DIR / "recovery.py"),
                title="Recovery",
                icon="📈",
            ),
            st.Page(
                str(PAGES_DIR / "club_battle.py"),
                title="Club Battle",
                icon="🏆",
            ),
            st.Page(
                str(PAGES_DIR / "insights.py"),
                title="Insights",
                icon="📊",
            ),
            st.Page(
                str(PAGES_DIR / "settings.py"),
                title="Settings",
                icon="⚙️",
            ),
        ]
    },
    position="top",
    expanded=True,
)

st.title("⚽ FOOTLENS ANALYTICS")

try:
    raw_df, cleaned_df = load_data()

except (FileNotFoundError, ValueError, KeyError) as error:
    st.error("Unable to load or process the football injury dataset.")
    st.exception(error)
    st.stop()

render_global_controls(cleaned_df)

st.divider()

navigation.run()
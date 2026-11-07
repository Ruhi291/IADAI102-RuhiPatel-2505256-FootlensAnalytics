import html

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.preprocess import load_raw_data, preprocess_data
from src.visualizations import PALETTES


DEFAULT_SETTINGS = {
    "appearance": "Night Stadium",
    "palette": "Stadium Neon",
    "impact_metric": "Goal Difference",
    "leaderboard_size": 10,
    "min_matches": 1,
    "chart_height": 460,
    "animation_enabled": True,
    "animation_speed": 700,
    "show_labels": True,
    "show_insights": True,
    "show_tables": True,
}


@st.cache_data(show_spinner="Loading football data...")
def load_data():
    raw_df = load_raw_data()
    cleaned_df = preprocess_data(raw_df)

    return raw_df, cleaned_df


def initialize_state():
    for key, value in DEFAULT_SETTINGS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_settings():
    initialize_state()

    return {
        key: st.session_state.get(key, value)
        for key, value in DEFAULT_SETTINGS.items()
    }


def reset_all():
    for key in [
        "filter_clubs",
        "filter_seasons",
        "filter_injuries",
        "filter_positions",
        "filter_age",
    ]:
        st.session_state.pop(key, None)

    for key, value in DEFAULT_SETTINGS.items():
        st.session_state[key] = value


def get_filter_options(df):
    return {
        "clubs": sorted(
            df["Club"].dropna().astype(str).unique().tolist()
        ),
        "seasons": sorted(
            df["Season"].dropna().astype(str).unique().tolist()
        ),
        "injuries": sorted(
            df["Injury_Type"].dropna().astype(str).unique().tolist()
        ),
        "positions": sorted(
            df["Position"].dropna().astype(str).unique().tolist()
        ),
    }


def format_value(value, decimals=1, suffix=""):
    if value is None or pd.isna(value):
        return "N/A"

    if isinstance(value, (int, np.integer)):
        formatted = f"{value:,}"
    else:
        formatted = f"{value:,.{decimals}f}"

    return f"{formatted}{suffix}"


def apply_theme():
    settings = get_settings()

    dark_mode = settings["appearance"] == "Night Stadium"

    if dark_mode:
        background = "#07111F"
        surface = "#101F32"
        text = "#F1F5F9"
        muted = "#94A3B8"
        border = "#26364A"
        accent = "#00E5A8"
    else:
        background = "#F5F7FB"
        surface = "#FFFFFF"
        text = "#172033"
        muted = "#64748B"
        border = "#DCE4EF"
        accent = "#047857"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {background};
            color: {text};
        }}

        [data-testid="stHeader"] {{
            background-color: {background};
        }}

        .block-container {{
            max-width: 1550px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        h1 {{
            font-weight: 800 !important;
            letter-spacing: -1px;
        }}

        h2, h3 {{
            letter-spacing: -0.4px;
        }}

        div[data-testid="stMetric"] {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 16px;
            padding: 18px;
            min-height: 110px;
        }}

        div[data-testid="stMetricLabel"] {{
            color: {muted};
        }}

        div[data-testid="stMetricValue"] {{
            color: {text};
            font-weight: 750;
        }}

        div[data-testid="stExpander"] {{
            border: 1px solid {border};
            border-radius: 14px;
        }}

        div[data-testid="stPlotlyChart"] {{
            border-radius: 14px;
        }}

        .footlens-insight {{
            background: {surface};
            border-left: 4px solid {accent};
            border-radius: 12px;
            padding: 16px 20px;
            margin: 12px 0;
            color: {text};
            line-height: 1.6;
        }}

        .footlens-section {{
            margin-top: 20px;
            margin-bottom: 12px;
        }}

        .footlens-section h3 {{
            color: {text};
            margin-bottom: 5px;
        }}

        .footlens-section p {{
            color: {muted};
            margin-top: 0;
            font-size: 14px;
        }}

        .footlens-badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            background: {surface};
            border: 1px solid {border};
            color: {text};
            font-size: 13px;
            margin: 4px 6px 4px 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section(title, description=None):
    safe_title = html.escape(str(title))

    description_html = ""

    if description:
        safe_description = html.escape(str(description))
        description_html = f"<p>{safe_description}</p>"

    st.markdown(
        f"""
        <div class="footlens-section">
            <h3>{safe_title}</h3>
            {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight(message, label="Analytical Insight"):
    settings = get_settings()

    if not settings["show_insights"]:
        return

    safe_label = html.escape(str(label))
    safe_message = html.escape(str(message))

    st.markdown(
        f"""
        <div class="footlens-insight">
            <strong>{safe_label}</strong>
            <br>
            {safe_message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(kpis):
    if not kpis:
        return

    columns = st.columns(len(kpis))

    for column, item in zip(columns, kpis):
        with column:
            st.metric(
                label=item.get("label", ""),
                value=item.get("value", "N/A"),
                delta=item.get("delta"),
                help=item.get("help"),
            )


def render_chart(fig, key=None):
    settings = get_settings()

    if fig is None:
        st.info("No chart data is available.")
        return

    if not isinstance(fig, go.Figure):
        st.error("The visualization could not be displayed.")
        return

    fig.update_layout(
        height=settings["chart_height"],
        margin=dict(l=25, r=25, t=65, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        transition=dict(
            duration=350 if settings["animation_enabled"] else 0,
            easing="cubic-in-out",
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=key,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "FootLens_Chart",
                "scale": 2,
            },
        },
    )


def render_table(df, title=None, height=350):
    settings = get_settings()

    if not settings["show_tables"]:
        return

    if title:
        st.subheader(title)

    if df is None or df.empty:
        st.info("No records are available for this table.")
        return

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=height,
    )


def render_download(
    df,
    filename="footlens_filtered_data.csv",
    label="Download CSV",
    key=None,
):
    if df is None or df.empty:
        return

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=key,
    )


def render_settings_controls():
    initialize_state()

    st.markdown("#### Appearance")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.selectbox(
            "Dashboard Theme",
            ["Night Stadium", "Daylight Arena"],
            key="appearance",
        )

    with c2:
        st.selectbox(
            "Chart Color Palette",
            list(PALETTES.keys()),
            key="palette",
        )

    with c3:
        st.selectbox(
            "Performance Indicator",
            ["Goal Difference", "Points Per Match"],
            key="impact_metric",
        )

    st.markdown("#### Analysis Preferences")

    c4, c5, c6 = st.columns(3)

    with c4:
        st.slider(
            "Leaderboard Size",
            min_value=5,
            max_value=20,
            key="leaderboard_size",
        )

    with c5:
        st.slider(
            "Minimum Sampled Matches",
            min_value=1,
            max_value=3,
            key="min_matches",
        )

    with c6:
        st.slider(
            "Chart Height",
            min_value=350,
            max_value=750,
            step=5,
            key="chart_height",
        )

    st.markdown("#### Animation")

    a1, a2 = st.columns(2)

    with a1:
        st.toggle(
            "Enable Chart Animations",
            key="animation_enabled",
        )

    with a2:
        st.slider(
            "Animation Frame Duration (ms)",
            min_value=200,
            max_value=1500,
            step=100,
            key="animation_speed",
        )

    st.markdown("#### Display Preferences")

    d1, d2, d3 = st.columns(3)

    with d1:
        st.toggle(
            "Show Chart Labels",
            key="show_labels",
        )

    with d2:
        st.toggle(
            "Show Analytical Insights",
            key="show_insights",
        )

    with d3:
        st.toggle(
            "Show Detailed Tables",
            key="show_tables",
        )


def render_global_controls(df):
    initialize_state()

    options = get_filter_options(df)

    st.markdown("#### Explore Football Data")

    reset_col, info_col = st.columns([1, 5])

    with reset_col:
        st.button(
            "Reset All",
            on_click=reset_all,
            use_container_width=True,
            key="reset_global",
        )

    with info_col:
        st.caption(
            "Filter the dataset to explore different "
            "football clubs, seasons, injuries, and players."
        )

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.multiselect(
            "Football Clubs",
            options=options["clubs"],
            default=options["clubs"],
            key="filter_clubs",
        )

    with f2:
        st.multiselect(
            "Seasons",
            options=options["seasons"],
            default=options["seasons"],
            key="filter_seasons",
        )

    with f3:
        st.multiselect(
            "Injury Types",
            options=options["injuries"],
            default=options["injuries"],
            key="filter_injuries",
        )

    with f4:
        st.multiselect(
            "Playing Positions",
            options=options["positions"],
            default=options["positions"],
            key="filter_positions",
        )

    valid_ages = df["Age"].dropna()

    with st.expander("Advanced Settings & Personalization"):
        if not valid_ages.empty:
            minimum_age = int(valid_ages.min())
            maximum_age = int(valid_ages.max())

            if minimum_age < maximum_age:
                st.slider(
                    "Player Age Range",
                    min_value=minimum_age,
                    max_value=maximum_age,
                    value=(minimum_age, maximum_age),
                    key="filter_age",
                )

        render_settings_controls()

    apply_theme()


def get_filtered_data():
    _, df = load_data()

    options = get_filter_options(df)

    selected_clubs = st.session_state.get(
        "filter_clubs", options["clubs"]
    )

    selected_seasons = st.session_state.get(
        "filter_seasons", options["seasons"]
    )

    selected_injuries = st.session_state.get(
        "filter_injuries", options["injuries"]
    )

    selected_positions = st.session_state.get(
        "filter_positions", options["positions"]
    )

    mask = (
        df["Club"].isin(selected_clubs)
        & df["Season"].isin(selected_seasons)
        & df["Injury_Type"].isin(selected_injuries)
        & df["Position"].isin(selected_positions)
    )

    selected_age = st.session_state.get("filter_age")

    if selected_age is not None:
        mask = mask & df["Age"].between(
            selected_age[0], selected_age[1]
        )

    return df.loc[mask.fillna(False)].copy()


def render_filter_summary(filtered_df):
    _, full_df = load_data()

    st.caption(
        f"Showing {len(filtered_df):,} of "
        f"{len(full_df):,} recorded injury episodes"
    )


def require_data(df):
    if df is None or df.empty:
        st.warning(
            "No records match the current filters. "
            "Adjust your selections or click Reset All."
        )
        st.stop()


def get_palette():
    settings = get_settings()

    return PALETTES.get(
        settings["palette"],
        PALETTES["Stadium Neon"],
    )


def get_impact_metric():
    settings = get_settings()

    if settings["impact_metric"] == "Points Per Match":
        return "Points_Per_Match_Drop"

    return "Team_Performance_Drop"


def get_qualified_impact_data(df):
    settings = get_settings()

    metric = get_impact_metric()

    minimum_matches = settings["min_matches"]

    valid = df[
        (df["Before_Matches"] >= minimum_matches)
        & (df["During_Matches"] >= minimum_matches)
    ].copy()

    return valid.dropna(subset=[metric])


def render_footer():
    st.divider()

    st.caption(
        "FOOTLENS ANALYTICS • Football Injury Intelligence Platform"
    )
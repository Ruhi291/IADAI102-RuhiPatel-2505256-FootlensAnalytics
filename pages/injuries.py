import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.components import (
    get_filtered_data,
    get_settings,
    get_palette,
    render_kpis,
    render_chart,
    render_table,
    render_section,
    render_insight,
    render_filter_summary,
    render_download,
    require_data,
    render_footer,
    format_value,
)

from src.metrics import (
    get_club_injury_rankings,
    get_injury_heatmap,
    get_injury_type_impact,
    get_monthly_injury_trends,
    get_position_analysis,
    get_seasonal_analysis,
    get_most_injured_players,
)

from src.visualizations import (
    plot_injury_heatmap,
    plot_club_injury_rankings,
    plot_monthly_injury_trend,
)

from src.advanced_visualizations import (
    plot_animated_injury_race,
    plot_injury_pitch,
)


df = get_filtered_data()
settings = get_settings()

palette = settings["palette"]
colors = get_palette()
dark_mode = settings["appearance"] == "Night Stadium"
leaderboard_size = settings["leaderboard_size"]
show_labels = settings["show_labels"]

require_data(df)

st.header("Injury Intelligence")

st.write(
    "Explore football injury patterns, playing positions, "
    "seasonal trends, and recovery statistics through "
    "interactive visualizations."
)

render_filter_summary(df)

st.divider()


valid_recovery = df["Recovery_Days"].dropna()
valid_dates = df["Injury_Date"].dropna()

most_common_injury = (
    df["Injury_Type"].dropna().mode()
)

most_affected_club = (
    df["Club"].dropna().mode()
)

common_injury = (
    str(most_common_injury.iloc[0])
    if not most_common_injury.empty
    else "N/A"
)

top_club = (
    str(most_affected_club.iloc[0])
    if not most_affected_club.empty
    else "N/A"
)

render_kpis([
    {
        "label": "Injury Episodes",
        "value": f"{len(df):,}",
        "help": "Recorded injury episodes in the selected dataset",
    },
    {
        "label": "Players Affected",
        "value": f"{df['Player'].nunique():,}",
        "help": "Unique players represented in the selected records",
    },
    {
        "label": "Injury Categories",
        "value": f"{df['Injury_Type'].nunique():,}",
        "help": "Distinct recorded injury descriptions",
    },
    {
        "label": "Average Recovery",
        "value": format_value(
            valid_recovery.mean(),
            1,
            " days"
        ),
        "help": "Mean recovery duration among records with valid dates",
    },
    {
        "label": "Median Recovery",
        "value": format_value(
            valid_recovery.median(),
            1,
            " days"
        ),
        "help": "Median recorded recovery duration",
    },
    {
        "label": "Records With Dates",
        "value": f"{len(valid_dates):,}",
        "help": "Injury records containing a valid injury date",
    },
])

st.divider()


render_section(
    "Animated Injury Timeline",
    "Press Play to explore how recorded injuries "
    "vary between clubs across different months."
)

animation_fig = plot_animated_injury_race(
    df,
    palette=palette,
    dark_mode=dark_mode,
    animation_speed=settings["animation_speed"],
    animation_enabled=settings["animation_enabled"],
)

animation_fig.update_layout(height=650)

st.plotly_chart(
    animation_fig,
    use_container_width=True,
    key="injuries_animated_race",
    config={
        "displaylogo": False,
        "responsive": True,
        "scrollZoom": False,
    },
)

st.caption(
    "The animation shows injury episodes recorded in each "
    "month. It does not represent cumulative injuries or "
    "injury risk per match."
)

if not settings["animation_enabled"]:
    st.info(
        "Animation is currently disabled. Enable it under "
        "Advanced Settings & Personalization to use Play/Pause."
    )

st.divider()


render_section(
    "Interactive Football Pitch",
    "Explore the distribution of recorded injuries "
    "across playing positions."
)

available_positions = sorted(
    df["Position"].dropna().astype(str).unique().tolist()
)

position_options = ["All Positions"] + available_positions

selected_position = st.selectbox(
    "Highlight a playing position",
    options=position_options,
    key="injuries_pitch_position",
)

pitch_df = df.copy()

pitch_fig = plot_injury_pitch(
    pitch_df,
    palette=palette,
    dark_mode=dark_mode,
    selected_position=(
        selected_position.title()
        if selected_position != "All Positions"
        else None
    ),
)

pitch_fig.update_layout(height=600)

st.plotly_chart(
    pitch_fig,
    use_container_width=True,
    key="injuries_football_pitch",
    config={
        "displaylogo": False,
        "responsive": True,
    },
)

st.caption(
    "The football pitch represents players' recorded playing "
    "positions, not the physical locations where injuries occurred."
)

if selected_position != "All Positions":

    position_records = df[
        df["Position"].astype(str).str.casefold()
        == selected_position.casefold()
    ]

    position_recovery = position_records["Recovery_Days"].mean()

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric(
            "Selected Position",
            selected_position,
        )

    with p2:
        st.metric(
            "Recorded Injuries",
            len(position_records),
        )

    with p3:
        st.metric(
            "Average Recovery",
            format_value(
                position_recovery,
                1,
                " days"
            ),
        )

st.divider()


render_section(
    "Injuries by Playing Position",
    "Compare injury frequencies and recovery durations "
    "across different football positions."
)

position_data = get_position_analysis(df)

if not position_data.empty:

    pos_left, pos_right = st.columns(2)

    with pos_left:

        position_fig = px.bar(
            position_data.sort_values("Injury_Count"),
            x="Injury_Count",
            y="Position",
            orientation="h",
            color="Injury_Count",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Injury Frequency by Position",
            hover_data=[
                "Players_Affected",
                "Average_Recovery",
            ],
        )

        position_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Recorded Injury Episodes",
            yaxis_title="",
        )

        render_chart(
            position_fig,
            key="injuries_position_frequency",
        )

    with pos_right:

        recovery_position = position_data.dropna(
            subset=["Average_Recovery"]
        )

        recovery_fig = px.bar(
            recovery_position.sort_values("Average_Recovery"),
            x="Average_Recovery",
            y="Position",
            orientation="h",
            color="Average_Recovery",
            color_continuous_scale=[
                colors[2],
                colors[0],
            ],
            title="Average Recovery by Position",
        )

        recovery_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Average Recovery (Days)",
            yaxis_title="",
        )

        render_chart(
            recovery_fig,
            key="injuries_position_recovery",
        )

    render_table(
        position_data,
        title="Playing Position Statistics",
    )

st.divider()


render_section(
    "Club and Month Injury Heatmap",
    "Identify which football clubs and calendar months "
    "have higher recorded injury frequencies."
)

heatmap_data = get_injury_heatmap(df)

if not heatmap_data.empty:

    heatmap_fig = plot_injury_heatmap(
        heatmap_data,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        heatmap_fig,
        key="injuries_monthly_heatmap",
    )

    highest_month = heatmap_data.sum(axis=0).idxmax()
    highest_count = int(heatmap_data.sum(axis=0).max())

    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    render_insight(
        f"{month_names[int(highest_month)]} has the highest "
        f"number of recorded injury episodes across the "
        f"selected clubs and seasons ({highest_count}). "
        "This represents an observed frequency, not an "
        "exposure-adjusted injury rate."
    )

else:

    st.info(
        "No dated injury records are available "
        "for the current selection."
    )

st.divider()


render_section(
    "Monthly Injury Trends",
    "Explore how recorded injuries change over time."
)

monthly_data = get_monthly_injury_trends(df)

if not monthly_data.empty:

    monthly_fig = plot_monthly_injury_trend(
        monthly_data,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        monthly_fig,
        key="injuries_monthly_trend",
    )

    peak_month = monthly_data.loc[
        monthly_data["Injury_Count"].idxmax()
    ]

    peak_year = int(peak_month["Injury_Year"])
    peak_month_number = int(peak_month["Injury_Month"])
    peak_count = int(peak_month["Injury_Count"])

    render_insight(
        f"The highest recorded monthly injury count "
        f"occurred in {month_names[peak_month_number]} "
        f"{peak_year}, with {peak_count} injury episodes "
        "in the selected dataset."
    )

st.divider()


render_section(
    "Injury Category Explorer",
    "Compare the frequency and recovery characteristics "
    "of different recorded injuries."
)

injury_data = df.dropna(
    subset=["Injury_Type"]
).copy()

injury_data["Injury_Category"] = (
    injury_data["Injury_Type"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.capitalize()
)

injury_counts = (
    injury_data["Injury_Category"]
    .value_counts()
    .reset_index()
)

injury_counts.columns = [
    "Injury_Category",
    "Injury_Count",
]

top_injuries = injury_counts.head(leaderboard_size)

injury_left, injury_right = st.columns(2)

with injury_left:

    injury_frequency_fig = px.bar(
        top_injuries.sort_values("Injury_Count"),
        x="Injury_Count",
        y="Injury_Category",
        orientation="h",
        color="Injury_Count",
        color_continuous_scale=[
            colors[1],
            colors[0],
        ],
        title="Most Common Recorded Injuries",
    )

    injury_frequency_fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Recorded Injury Episodes",
        yaxis_title="",
    )

    render_chart(
        injury_frequency_fig,
        key="injuries_category_frequency",
    )

with injury_right:

    injury_recovery = (
        injury_data.groupby("Injury_Category")
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
        )
        .reset_index()
    )

    injury_recovery = injury_recovery[
        injury_recovery["Injury_Category"].isin(
            top_injuries["Injury_Category"]
        )
    ].dropna(subset=["Average_Recovery"])

    recovery_fig = px.bar(
        injury_recovery.sort_values("Average_Recovery"),
        x="Average_Recovery",
        y="Injury_Category",
        orientation="h",
        color="Average_Recovery",
        color_continuous_scale=[
            colors[2],
            colors[0],
        ],
        title="Average Recovery by Injury Category",
        hover_data=["Injury_Count"],
    )

    recovery_fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Average Recovery (Days)",
        yaxis_title="",
    )

    render_chart(
        recovery_fig,
        key="injuries_category_recovery",
    )

render_table(
    injury_recovery.sort_values(
        "Injury_Count",
        ascending=False
    ),
    title="Injury Category Statistics",
)

st.divider()


render_section(
    "Seasonal Injury Intelligence",
    "Compare injury frequencies and recovery durations "
    "across football seasons."
)

seasonal_data = get_seasonal_analysis(df)

if not seasonal_data.empty:

    season_left, season_right = st.columns(2)

    with season_left:

        season_fig = px.bar(
            seasonal_data,
            x="Season",
            y="Injury_Count",
            color="Season",
            color_discrete_sequence=colors,
            title="Recorded Injuries by Season",
        )

        season_fig.update_layout(
            showlegend=False,
            xaxis_title="Football Season",
            yaxis_title="Injury Episodes",
        )

        render_chart(
            season_fig,
            key="injuries_season_count",
        )

    with season_right:

        season_recovery = seasonal_data.dropna(
            subset=["Average_Recovery"]
        )

        season_recovery_fig = px.line(
            season_recovery,
            x="Season",
            y="Average_Recovery",
            markers=True,
            title="Average Recovery Duration by Season",
        )

        season_recovery_fig.update_traces(
            line=dict(
                color=colors[0],
                width=3,
            ),
            marker=dict(
                size=11,
                color=colors[1],
            ),
        )

        season_recovery_fig.update_layout(
            xaxis_title="Football Season",
            yaxis_title="Average Recovery (Days)",
        )

        render_chart(
            season_recovery_fig,
            key="injuries_season_recovery",
        )

    render_table(
        seasonal_data,
        title="Seasonal Injury Statistics",
    )

st.divider()


render_section(
    "Club Injury Intelligence",
    "Compare injury frequency, affected players, "
    "and recovery patterns across football clubs."
)

club_data = get_club_injury_rankings(df)

if not club_data.empty:

    club_fig = plot_club_injury_rankings(
        club_data,
        palette=palette,
        dark_mode=dark_mode,
        show_labels=show_labels,
    )

    render_chart(
        club_fig,
        key="injuries_club_rankings",
    )

    render_table(
        club_data,
        title="Club Injury Comparison",
    )

st.divider()


render_section(
    "Frequently Injured Players",
    "Identify players with multiple recorded "
    "injury episodes."
)

player_data = get_most_injured_players(
    df,
    top_n=leaderboard_size,
)

render_table(
    player_data,
    title="Player Injury Leaderboard",
)

st.divider()


render_section(
    "Injury Intelligence Report",
    "Generate observations from the currently "
    "selected football injury records."
)

if st.button(
    "Generate Injury Insights",
    type="primary",
    use_container_width=True,
    key="injuries_generate_insights",
):

    insights = []

    club_counts = df["Club"].value_counts()

    if not club_counts.empty:

        insights.append(
            f"{club_counts.index[0]} has the highest "
            f"recorded injury count ({club_counts.iloc[0]})."
        )

    if not injury_counts.empty:

        most_frequent = injury_counts.iloc[0]

        insights.append(
            f"{most_frequent['Injury_Category']} is the "
            f"most frequently recorded injury category, "
            f"with {int(most_frequent['Injury_Count'])} episodes."
        )

    if not valid_recovery.empty:

        insights.append(
            f"The median recorded recovery period is "
            f"{valid_recovery.median():.1f} days."
        )

    if not position_data.empty:

        top_position = position_data.iloc[0]

        insights.append(
            f"{top_position['Position']} has the most "
            f"recorded injury episodes among playing positions "
            f"({int(top_position['Injury_Count'])})."
        )

    insights.append(
        "These observations describe the available records. "
        "Differences in injury frequency do not establish "
        "differences in injury risk without exposure data."
    )

    st.session_state["injuries_report"] = {
        "filters": (
            tuple(sorted(df["Injury_ID"].tolist())),
            palette,
        ),
        "insights": insights,
    }


saved_report = st.session_state.get("injuries_report")

if saved_report is not None:

    current_signature = (
        tuple(sorted(df["Injury_ID"].tolist())),
        palette,
    )

    if saved_report["filters"] == current_signature:

        for number, message in enumerate(
            saved_report["insights"],
            start=1,
        ):

            render_insight(
                message,
                label=f"Finding {number}",
            )

    else:

        st.info(
            "Your filters have changed. Generate the report "
            "again to see updated observations."
        )

st.divider()


render_section(
    "Injury Dataset Explorer",
    "Explore and download the injury records "
    "included in the current analysis."
)

preview_columns = [
    "Player",
    "Club",
    "Season",
    "Position",
    "Age",
    "Injury_Type",
    "Injury_Date",
    "Return_Date",
    "Recovery_Days",
    "Recovery_Category",
]

st.dataframe(
    df[preview_columns],
    use_container_width=True,
    hide_index=True,
    height=360,
)

render_download(
    df,
    filename="footlens_injury_data.csv",
    label="Download Injury Analysis Dataset",
    key="injuries_download",
)

render_footer()
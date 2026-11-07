import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.components import (
    get_filtered_data,
    get_settings,
    get_palette,
    get_impact_metric,
    render_kpis,
    render_chart,
    render_table,
    render_section,
    render_insight,
    render_filter_summary,
    render_download,
    render_footer,
    format_value,
    require_data,
)

from src.advanced_visualizations import (
    plot_club_injury_comparison,
)


df = get_filtered_data()
settings = get_settings()

palette = settings["palette"]
colors = get_palette()
dark_mode = settings["appearance"] == "Night Stadium"
leaderboard_size = settings["leaderboard_size"]
show_labels = settings["show_labels"]
min_matches = settings["min_matches"]

require_data(df)

st.header("Club Battle Arena")

st.write(
    "Select two football clubs and compare their injury patterns, "
    "player recovery, match performance, and seasonal trends "
    "through an interactive head-to-head analysis."
)

render_filter_summary(df)

st.divider()


available_clubs = sorted(
    df["Club"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

if len(available_clubs) < 2:
    st.warning(
        "Club Battle requires at least two clubs in the "
        "current dataset. Select additional clubs using "
        "the global Football Clubs filter."
    )
    st.stop()


render_section(
    "Choose Your Clubs",
    "Select two different teams to begin the comparison."
)

selector_left, selector_middle, selector_right = st.columns(
    [5, 1, 5]
)

with selector_left:
    club_a = st.selectbox(
        "Club A",
        options=available_clubs,
        index=0,
        key="battle_club_a",
    )

with selector_middle:
    st.markdown(
        "<h2 style='text-align:center;padding-top:25px;'>VS</h2>",
        unsafe_allow_html=True,
    )

with selector_right:
    club_b = st.selectbox(
        "Club B",
        options=available_clubs,
        index=1,
        key="battle_club_b",
    )

if club_a == club_b:
    st.warning(
        "Please select two different football clubs "
        "for a meaningful head-to-head comparison."
    )
    st.stop()


club_a_df = df[df["Club"] == club_a].copy()
club_b_df = df[df["Club"] == club_b].copy()

battle_df = df[
    df["Club"].isin([club_a, club_b])
].copy()

metric_column = get_impact_metric()

metric_description = (
    "Points Per Match"
    if metric_column == "Points_Per_Match_Drop"
    else "Goal Difference"
)

club_colors = {
    club_a: colors[0],
    club_b: colors[1 % len(colors)],
}


def calculate_club_statistics(club_df):
    recovery = club_df["Recovery_Days"].dropna()

    rating = club_df["Rating_Change"].dropna()

    complete_impact = club_df[
        (club_df["Before_Matches"] >= min_matches)
        & (club_df["During_Matches"] >= min_matches)
    ].dropna(subset=[metric_column])

    return {
        "Injury Episodes": int(len(club_df)),
        "Players Affected": int(club_df["Player"].nunique()),
        "Injury Categories": int(club_df["Injury_Type"].nunique()),
        "Average Recovery": (
            float(recovery.mean())
            if not recovery.empty
            else np.nan
        ),
        "Median Recovery": (
            float(recovery.median())
            if not recovery.empty
            else np.nan
        ),
        "Average Rating Change": (
            float(rating.mean())
            if not rating.empty
            else np.nan
        ),
        "Valid Rating Comparisons": int(len(rating)),
        "Average Performance Decline": (
            float(complete_impact[metric_column].mean())
            if not complete_impact.empty
            else np.nan
        ),
        "Valid Impact Comparisons": int(len(complete_impact)),
        "Episodes With Decline": int(
            complete_impact[metric_column].gt(0).sum()
        ),
        "Decline Percentage": (
            float(
                complete_impact[metric_column].gt(0).mean() * 100
            )
            if not complete_impact.empty
            else np.nan
        ),
        "Positive Rating Changes": int(
            rating.gt(0).sum()
        ),
    }


stats_a = calculate_club_statistics(club_a_df)
stats_b = calculate_club_statistics(club_b_df)


def comparison_dataframe():
    metrics = [
        "Injury Episodes",
        "Players Affected",
        "Injury Categories",
        "Average Recovery",
        "Median Recovery",
        "Average Rating Change",
        "Valid Rating Comparisons",
        "Average Performance Decline",
        "Valid Impact Comparisons",
        "Episodes With Decline",
        "Decline Percentage",
        "Positive Rating Changes",
    ]

    return pd.DataFrame(
        {
            "Metric": metrics,
            club_a: [stats_a[item] for item in metrics],
            club_b: [stats_b[item] for item in metrics],
        }
    )


comparison_df = comparison_dataframe()

st.divider()


render_section(
    "Head-to-Head Scorecards",
    "Compare the most important injury and "
    "performance indicators for both clubs."
)

score_left, score_right = st.columns(2)

with score_left:
    with st.container(border=True):
        st.markdown(f"### {club_a}")

        st.metric(
            "Recorded Injury Episodes",
            f"{stats_a['Injury Episodes']:,}",
        )

        st.metric(
            "Players Affected",
            f"{stats_a['Players Affected']:,}",
        )

        st.metric(
            "Average Recovery",
            format_value(
                stats_a["Average Recovery"],
                1,
                " days",
            ),
        )

        st.metric(
            "Average Rating Change",
            format_value(
                stats_a["Average Rating Change"],
                2,
            ),
        )

        st.metric(
            "Average Performance Decline",
            format_value(
                stats_a["Average Performance Decline"],
                2,
            ),
        )

        st.caption(
            f"{stats_a['Valid Impact Comparisons']} "
            "valid impact comparisons"
        )

with score_right:
    with st.container(border=True):
        st.markdown(f"### {club_b}")

        st.metric(
            "Recorded Injury Episodes",
            f"{stats_b['Injury Episodes']:,}",
        )

        st.metric(
            "Players Affected",
            f"{stats_b['Players Affected']:,}",
        )

        st.metric(
            "Average Recovery",
            format_value(
                stats_b["Average Recovery"],
                1,
                " days",
            ),
        )

        st.metric(
            "Average Rating Change",
            format_value(
                stats_b["Average Rating Change"],
                2,
            ),
        )

        st.metric(
            "Average Performance Decline",
            format_value(
                stats_b["Average Performance Decline"],
                2,
            ),
        )

        st.caption(
            f"{stats_b['Valid Impact Comparisons']} "
            "valid impact comparisons"
        )

st.caption(
    "Injury counts are recorded episodes, not exposure-adjusted "
    "injury rates. Lower injury counts do not necessarily mean "
    "a club has a lower underlying injury risk."
)

st.divider()


render_section(
    "Club Comparison Dashboard",
    "View both clubs' calculated statistics side by side."
)

render_table(
    comparison_df.round(2),
    title="Head-to-Head Statistical Comparison",
    height=460,
)

st.divider()


render_section(
    "Team Performance Battle",
    "Compare sampled team performance before injuries, "
    "during player absence, and after players return."
)

performance_metric = st.radio(
    "Select Performance Measure",
    options=["Goal Difference", "Points Per Match"],
    horizontal=True,
    key="battle_performance_measure",
)

if performance_metric == "Goal Difference":
    phase_columns = {
        "Before Injury": "Before_Avg_GD",
        "During Absence": "During_Avg_GD",
        "After Return": "After_Avg_GD",
    }

    axis_label = "Average Goal Difference"

else:
    phase_columns = {
        "Before Injury": "Before_PPM",
        "During Absence": "During_PPM",
        "After Return": "After_PPM",
    }

    axis_label = "Average Points Per Match"


performance_rows = []

for club_name, club_data in [
    (club_a, club_a_df),
    (club_b, club_b_df),
]:
    for phase_name, column_name in phase_columns.items():
        values = club_data[column_name].dropna()

        performance_rows.append(
            {
                "Club": club_name,
                "Phase": phase_name,
                "Average_Performance": (
                    values.mean()
                    if not values.empty
                    else np.nan
                ),
                "Valid_Episodes": len(values),
            }
        )

performance_data = pd.DataFrame(performance_rows)

performance_fig = px.line(
    performance_data,
    x="Phase",
    y="Average_Performance",
    color="Club",
    markers=True,
    color_discrete_map=club_colors,
    category_orders={
        "Phase": [
            "Before Injury",
            "During Absence",
            "After Return",
        ]
    },
    title=f"{club_a} vs {club_b} — Performance Journey",
    hover_data={
        "Valid_Episodes": True,
        "Average_Performance": ":.2f",
    },
)

performance_fig.update_traces(
    line=dict(width=4),
    marker=dict(size=13),
)

performance_fig.update_layout(
    xaxis_title="Injury Phase",
    yaxis_title=axis_label,
)

if performance_metric == "Goal Difference":
    performance_fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#94A3B8",
    )

render_chart(
    performance_fig,
    key="battle_performance_journey",
)

render_insight(
    "These lines compare average sampled match statistics "
    "across injury episodes for each club. They do not "
    "establish that player injuries caused differences "
    "in team performance."
)

st.divider()


render_section(
    "Goal Difference and Points Per Match",
    "Compare two key football performance indicators "
    "during player absence."
)

impact_comparison = []

for club_name, club_data in [
    (club_a, club_a_df),
    (club_b, club_b_df),
]:
    qualified = club_data[
        (club_data["Before_Matches"] >= min_matches)
        & (club_data["During_Matches"] >= min_matches)
    ]

    for name, column in [
        ("Goal Difference Decline", "Team_Performance_Drop"),
        ("Points Per Match Decline", "Points_Per_Match_Drop"),
    ]:
        valid = qualified[column].dropna()

        impact_comparison.append(
            {
                "Club": club_name,
                "Indicator": name,
                "Average_Decline": (
                    valid.mean()
                    if not valid.empty
                    else np.nan
                ),
                "Valid_Episodes": len(valid),
            }
        )

impact_data = pd.DataFrame(impact_comparison)

impact_left, impact_right = st.columns(2)

with impact_left:
    goal_data = impact_data[
        impact_data["Indicator"] == "Goal Difference Decline"
    ]

    goal_fig = px.bar(
        goal_data,
        x="Club",
        y="Average_Decline",
        color="Club",
        color_discrete_map=club_colors,
        title="Average Goal Difference Decline",
        hover_data=["Valid_Episodes"],
    )

    goal_fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Goal Difference Decline",
    )

    if show_labels:
        goal_fig.update_traces(
            texttemplate="%{y:.2f}",
            textposition="outside",
        )

    render_chart(
        goal_fig,
        key="battle_goal_difference",
    )

with impact_right:
    ppm_data = impact_data[
        impact_data["Indicator"] == "Points Per Match Decline"
    ]

    ppm_fig = px.bar(
        ppm_data,
        x="Club",
        y="Average_Decline",
        color="Club",
        color_discrete_map=club_colors,
        title="Average Points Per Match Decline",
        hover_data=["Valid_Episodes"],
    )

    ppm_fig.update_layout(
        showlegend=False,
        xaxis_title="",
        yaxis_title="Points Per Match Decline",
    )

    if show_labels:
        ppm_fig.update_traces(
            texttemplate="%{y:.2f}",
            textposition="outside",
        )

    render_chart(
        ppm_fig,
        key="battle_points_per_match",
    )

st.caption(
    f"Only episodes with at least {min_matches} sampled matches "
    "before injury and during absence are included. "
    "Positive decline values indicate worse sampled "
    "performance during absence."
)

st.divider()


render_section(
    "Injury Type Battle",
    "Discover which injuries appear most frequently "
    "in the records of each club."
)

injury_fig = plot_club_injury_comparison(
    battle_df,
    club_a=club_a,
    club_b=club_b,
    palette=palette,
    dark_mode=dark_mode,
    top_n=leaderboard_size,
)

render_chart(
    injury_fig,
    key="battle_injury_type_comparison",
)

injury_type_summary = (
    battle_df.dropna(subset=["Injury_Type"])
    .groupby(["Injury_Type", "Club"])
    .size()
    .unstack(fill_value=0)
    .reindex(columns=[club_a, club_b], fill_value=0)
    .reset_index()
)

render_table(
    injury_type_summary,
    title="Injury Type Comparison Table",
)

st.divider()


render_section(
    "Recovery Duration Battle",
    "Compare the distribution of recorded recovery "
    "durations between the two clubs."
)

valid_recovery = battle_df.dropna(
    subset=["Recovery_Days"]
).copy()

if not valid_recovery.empty:
    recovery_left, recovery_right = st.columns(2)

    with recovery_left:
        recovery_fig = px.box(
            valid_recovery,
            x="Club",
            y="Recovery_Days",
            color="Club",
            color_discrete_map=club_colors,
            points="outliers",
            title="Recovery Duration Distribution",
        )

        recovery_fig.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Recovery Duration (Days)",
        )

        render_chart(
            recovery_fig,
            key="battle_recovery_box",
        )

    with recovery_right:
        recovery_hist = px.histogram(
            valid_recovery,
            x="Recovery_Days",
            color="Club",
            barmode="overlay",
            nbins=25,
            opacity=0.65,
            color_discrete_map=club_colors,
            title="Recovery Duration Frequency",
        )

        recovery_hist.update_layout(
            xaxis_title="Recovery Duration (Days)",
            yaxis_title="Recorded Injury Episodes",
        )

        render_chart(
            recovery_hist,
            key="battle_recovery_histogram",
        )

    recovery_summary = (
        valid_recovery.groupby("Club")
        .agg(
            Valid_Records=("Recovery_Days", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Shortest_Recovery=("Recovery_Days", "min"),
            Longest_Recovery=("Recovery_Days", "max"),
        )
        .reset_index()
        .round(2)
    )

    render_table(
        recovery_summary,
        title="Club Recovery Statistics",
    )

else:
    st.info(
        "No valid recovery durations are available "
        "for the selected clubs."
    )

st.divider()


render_section(
    "Seasonal Injury Battle",
    "Compare recorded injury episodes between "
    "the clubs across football seasons."
)

seasonal_data = (
    battle_df.groupby(["Season", "Club"])
    .size()
    .reset_index(name="Injury_Count")
)

if not seasonal_data.empty:
    seasonal_fig = px.bar(
        seasonal_data,
        x="Season",
        y="Injury_Count",
        color="Club",
        barmode="group",
        color_discrete_map=club_colors,
        title="Season-by-Season Injury Comparison",
    )

    seasonal_fig.update_layout(
        xaxis_title="Football Season",
        yaxis_title="Recorded Injury Episodes",
    )

    if show_labels:
        seasonal_fig.update_traces(
            textposition="outside",
            texttemplate="%{y}",
        )

    render_chart(
        seasonal_fig,
        key="battle_seasonal_injuries",
    )

    seasonal_pivot = pd.pivot_table(
        seasonal_data,
        index="Season",
        columns="Club",
        values="Injury_Count",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    render_table(
        seasonal_pivot,
        title="Seasonal Injury Comparison",
    )

st.divider()


render_section(
    "Playing Position Battle",
    "Explore the distribution of recorded injuries "
    "across playing positions in both clubs."
)

position_data = (
    battle_df.dropna(subset=["Position"])
    .groupby(["Position", "Club"])
    .size()
    .reset_index(name="Injury_Count")
)

if not position_data.empty:
    position_fig = px.bar(
        position_data,
        x="Position",
        y="Injury_Count",
        color="Club",
        barmode="group",
        color_discrete_map=club_colors,
        title="Injury Frequency by Playing Position",
    )

    position_fig.update_layout(
        xaxis_title="Playing Position",
        yaxis_title="Recorded Injury Episodes",
        xaxis_tickangle=-30,
    )

    render_chart(
        position_fig,
        key="battle_position_comparison",
    )

    position_pivot = pd.pivot_table(
        position_data,
        index="Position",
        columns="Club",
        values="Injury_Count",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    render_table(
        position_pivot,
        title="Position Comparison Statistics",
    )

st.divider()


render_section(
    "Head-to-Head Radar",
    "Compare normalized injury, recovery, and performance "
    "indicators on a common visual scale."
)

radar_metrics = [
    ("Recorded Injuries", "Injury Episodes", False),
    ("Players Affected", "Players Affected", False),
    ("Median Recovery", "Median Recovery", False),
    ("Rating Change", "Average Rating Change", True),
    (
        "Performance Stability",
        "Average Performance Decline",
        False,
    ),
]

radar_values_a = []
radar_values_b = []
radar_labels = []

for label, field, higher_is_better in radar_metrics:
    value_a = stats_a[field]
    value_b = stats_b[field]

    if not np.isfinite(value_a) or not np.isfinite(value_b):
        continue

    lower = min(value_a, value_b)
    upper = max(value_a, value_b)

    if np.isclose(lower, upper):
        normalized_a = 50.0
        normalized_b = 50.0
    else:
        normalized_a = (
            (value_a - lower) / (upper - lower) * 100
        )
        normalized_b = (
            (value_b - lower) / (upper - lower) * 100
        )

    if not higher_is_better:
        normalized_a = 100 - normalized_a
        normalized_b = 100 - normalized_b

    radar_labels.append(label)
    radar_values_a.append(normalized_a)
    radar_values_b.append(normalized_b)

if len(radar_labels) >= 3:
    radar_fig = go.Figure()

    radar_fig.add_trace(
        go.Scatterpolar(
            r=radar_values_a + [radar_values_a[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            fillcolor="rgba(0,229,168,0.12)",
            line=dict(
                color=club_colors[club_a],
                width=3,
            ),
            name=club_a,
        )
    )

    radar_fig.add_trace(
        go.Scatterpolar(
            r=radar_values_b + [radar_values_b[0]],
            theta=radar_labels + [radar_labels[0]],
            fill="toself",
            fillcolor="rgba(96,165,250,0.12)",
            line=dict(
                color=club_colors[club_b],
                width=3,
            ),
            name=club_b,
        )
    )

    radar_fig.update_layout(
        title="Normalized Club Comparison",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
            ),
        ),
        showlegend=True,
    )

    render_chart(
        radar_fig,
        key="battle_radar",
    )

    st.caption(
        "Radar scores are relative to these two selected clubs, "
        "not universal rankings. Higher scores indicate more "
        "favorable values for the chosen indicator. Equal values "
        "receive 50 points each. Scores are normalized independently "
        "for each indicator and should not be combined into an "
        "overall measure of club quality."
    )

else:
    st.info(
        "Insufficient complete indicators are available "
        "to construct the radar comparison."
    )

st.divider()


render_section(
    "Club Battle Verdict",
    "See which club has the more favorable observed "
    "value for each selected indicator."
)

verdict_rules = [
    ("Fewer Injury Episodes", "Injury Episodes", "lower"),
    ("Shorter Median Recovery", "Median Recovery", "lower"),
    (
        "Better Average Rating Change",
        "Average Rating Change",
        "higher",
    ),
    (
        "Smaller Performance Decline",
        "Average Performance Decline",
        "lower",
    ),
]

verdict_rows = []

for indicator, field, preference in verdict_rules:
    value_a = stats_a[field]
    value_b = stats_b[field]

    if not np.isfinite(value_a) or not np.isfinite(value_b):
        winner = "Insufficient Data"

    elif np.isclose(value_a, value_b):
        winner = "Tie"

    elif preference == "lower":
        winner = club_a if value_a < value_b else club_b

    else:
        winner = club_a if value_a > value_b else club_b

    verdict_rows.append(
        {
            "Indicator": indicator,
            club_a: (
                round(value_a, 2)
                if pd.notna(value_a)
                else np.nan
            ),
            club_b: (
                round(value_b, 2)
                if pd.notna(value_b)
                else np.nan
            ),
            "More Favorable Observation": winner,
        }
    )

verdict_df = pd.DataFrame(verdict_rows)

render_table(
    verdict_df,
    title="Head-to-Head Indicator Results",
    height=260,
)

st.caption(
    "These verdicts compare the selected observations only. "
    "Fewer recorded injuries may reflect differences in "
    "player exposure or dataset coverage. The verdicts "
    "do not establish which club is objectively better."
)

st.divider()


render_section(
    "Club Battle Intelligence Report",
    "Generate a data-backed comparison of "
    "the selected football clubs."
)

current_signature = (
    club_a,
    club_b,
    tuple(sorted(battle_df["Injury_ID"].astype(str).tolist())),
    metric_column,
    min_matches,
)

if st.button(
    "Generate Club Battle Report",
    type="primary",
    use_container_width=True,
    key="battle_generate_report",
):
    insights = []

    if stats_a["Injury Episodes"] != stats_b["Injury Episodes"]:
        more_injuries = (
            club_a
            if stats_a["Injury Episodes"] > stats_b["Injury Episodes"]
            else club_b
        )

        insights.append(
            f"{more_injuries} has more recorded injury episodes "
            "in the selected dataset."
        )
    else:
        insights.append(
            "Both clubs have the same number of "
            "recorded injury episodes."
        )

    if (
        pd.notna(stats_a["Median Recovery"])
        and pd.notna(stats_b["Median Recovery"])
    ):
        insights.append(
            f"The median recovery duration is "
            f"{stats_a['Median Recovery']:.1f} days for {club_a} "
            f"and {stats_b['Median Recovery']:.1f} days for {club_b}."
        )

    if (
        pd.notna(stats_a["Average Performance Decline"])
        and pd.notna(stats_b["Average Performance Decline"])
    ):
        insights.append(
            f"The average observed {metric_description.lower()} "
            f"decline is {stats_a['Average Performance Decline']:.2f} "
            f"for {club_a} and "
            f"{stats_b['Average Performance Decline']:.2f} "
            f"for {club_b}."
        )

    if (
        pd.notna(stats_a["Average Rating Change"])
        and pd.notna(stats_b["Average Rating Change"])
    ):
        insights.append(
            f"Average post-return rating change is "
            f"{stats_a['Average Rating Change']:+.2f} for "
            f"{club_a} and {stats_b['Average Rating Change']:+.2f} "
            f"for {club_b}."
        )

    insights.append(
        "All comparisons are observational. Recorded injury "
        "frequency, recovery time, and match results can be "
        "affected by exposure, squad size, injury severity, "
        "opposition strength, and other unmeasured factors."
    )

    st.session_state["battle_report"] = {
        "signature": current_signature,
        "insights": insights,
    }


saved_report = st.session_state.get("battle_report")

if saved_report is not None:
    if saved_report["signature"] == current_signature:
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
            "Your club selection or analysis settings have changed. "
            "Generate the report again to update the findings."
        )

st.divider()


render_section(
    "Club Battle Dataset Explorer",
    "Explore and download injury episodes "
    "from the two selected clubs."
)

explorer_columns = [
    "Injury_ID",
    "Player",
    "Club",
    "Season",
    "Position",
    "Age",
    "Injury_Type",
    "Injury_Date",
    "Return_Date",
    "Recovery_Days",
    "Before_Avg_Rating",
    "After_Avg_Rating",
    "Rating_Change",
    "Before_Avg_GD",
    "During_Avg_GD",
    "After_Avg_GD",
    "Team_Performance_Drop",
    "Points_Per_Match_Drop",
]

st.dataframe(
    battle_df[explorer_columns],
    use_container_width=True,
    hide_index=True,
    height=380,
)

render_download(
    battle_df,
    filename="footlens_club_battle_data.csv",
    label="Download Club Battle Dataset",
    key="battle_download",
)

render_footer()
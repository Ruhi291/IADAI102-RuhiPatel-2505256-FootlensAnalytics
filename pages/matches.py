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
    get_qualified_impact_data,
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
    get_top_impact_injuries,
    get_match_result_comparison,
    get_match_performance_summary,
    get_club_comparison,
    get_injury_type_impact,
    generate_manager_insights,
)

from src.visualizations import (
    plot_top_injury_impact,
    plot_match_results,
    plot_club_performance,
)

from src.advanced_visualizations import (
    plot_team_performance_journey,
)


df = get_filtered_data()
settings = get_settings()

palette = settings["palette"]
colors = get_palette()
dark_mode = settings["appearance"] == "Night Stadium"
leaderboard_size = settings["leaderboard_size"]
min_matches = settings["min_matches"]
show_labels = settings["show_labels"]
impact_metric = settings["impact_metric"]

require_data(df)

metric = get_impact_metric()

metric_label = (
    "Points Per Match Decline"
    if metric == "Points_Per_Match_Drop"
    else "Goal Difference Decline"
)

qualified_df = get_qualified_impact_data(df)

st.header("Match Performance Intelligence")

st.write(
    "Analyze match outcomes, player absence, goal difference, "
    "points per match, and football team performance "
    "across injury phases."
)

render_filter_summary(df)

st.caption(
    f"Selected performance indicator: {impact_metric} | "
    f"Minimum sampled matches per comparison phase: {min_matches}"
)

st.divider()


valid_impact = qualified_df.dropna(
    subset=[metric]
).copy()

valid_count = len(valid_impact)

average_drop = (
    valid_impact[metric].mean()
    if valid_count > 0
    else np.nan
)

median_drop = (
    valid_impact[metric].median()
    if valid_count > 0
    else np.nan
)

decline_count = (
    int(valid_impact[metric].gt(0).sum())
    if valid_count > 0
    else 0
)

improvement_count = (
    int(valid_impact[metric].lt(0).sum())
    if valid_count > 0
    else 0
)

decline_percentage = (
    decline_count / valid_count * 100
    if valid_count > 0
    else np.nan
)

unchanged_count = (
    int(valid_impact[metric].eq(0).sum())
    if valid_count > 0
    else 0
)

render_section(
    "Match Performance Overview",
    "Key statistics derived from valid before-injury "
    "and during-absence match comparisons."
)

render_kpis([
    {
        "label": "Valid Comparisons",
        "value": f"{valid_count:,}",
        "help": "Injury episodes meeting the selected match sample requirement",
    },
    {
        "label": "Average Decline",
        "value": format_value(average_drop, 2),
        "help": "Mean difference between before-injury and absence performance",
    },
    {
        "label": "Median Decline",
        "value": format_value(median_drop, 2),
        "help": "Median performance difference across valid injury episodes",
    },
    {
        "label": "Episodes With Decline",
        "value": f"{decline_count:,}",
        "help": "Episodes with worse sampled performance during absence",
    },
    {
        "label": "Episodes With Improvement",
        "value": f"{improvement_count:,}",
        "help": "Episodes with better sampled performance during absence",
    },
    {
        "label": "Decline Percentage",
        "value": format_value(decline_percentage, 1, "%"),
        "help": "Percentage of valid episodes showing a positive decline index",
    },
])

st.caption(
    "Positive decline values indicate worse sampled team "
    "performance during player absence. Negative values indicate "
    "better sampled performance. These differences do not establish causation."
)

if valid_count == 0:
    st.warning(
        "No injury episodes meet the selected performance comparison "
        "requirements. Reduce the minimum sampled matches setting "
        "or change your dataset filters."
    )

st.divider()


render_section(
    "Team Performance Journey",
    "Explore how average team performance differs "
    "before injury, during absence, and after recovery."
)

journey_df = df[
    (df["Before_Matches"] >= min_matches)
    & (df["During_Matches"] >= min_matches)
    & (df["After_Matches"] >= min_matches)
].copy()

if not journey_df.empty:
    journey_fig = plot_team_performance_journey(
        journey_df,
        metric=impact_metric,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        journey_fig,
        key="matches_performance_journey",
    )

    st.caption(
        f"Performance journey based on {len(journey_df):,} "
        "injury episodes meeting the minimum match-count requirement "
        "in all three phases."
    )

    render_insight(
        "This visualization compares sampled team performance "
        "before a player's injury, during their absence, and "
        "after their return. Differences may also reflect "
        "opponent strength, squad rotation, and other factors."
    )

else:
    st.info(
        "Not enough records contain the required three-phase "
        "match samples for the selected settings."
    )

st.divider()


render_section(
    "Largest Observed Team Performance Declines",
    "Discover which injury episodes are associated "
    "with the greatest decline in sampled team performance."
)

top_impact = get_top_impact_injuries(
    df,
    top_n=leaderboard_size,
    metric=metric,
    min_matches=min_matches,
)

if not top_impact.empty:

    if metric == "Team_Performance_Drop":

        impact_fig = plot_top_injury_impact(
            top_impact,
            palette=palette,
            dark_mode=dark_mode,
            show_labels=show_labels,
        )

    else:

        chart_data = top_impact.copy()

        chart_data["Player_Label"] = (
            chart_data["Player"].astype(str)
            + " | "
            + chart_data["Club"].astype(str)
        )

        chart_data = chart_data.sort_values(metric)

        impact_fig = px.bar(
            chart_data,
            x=metric,
            y="Player_Label",
            orientation="h",
            color=metric,
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Largest Observed Points Per Match Declines",
            hover_data={
                "Player": True,
                "Club": True,
                "Injury_Type": True,
                "Before_Matches": True,
                "During_Matches": True,
                metric: ":.2f",
                "Player_Label": False,
            },
        )

        impact_fig.update_layout(
            height=520,
            coloraxis_showscale=False,
            xaxis_title="Points Per Match Decline",
            yaxis_title="",
        )

        if show_labels:
            impact_fig.update_traces(
                texttemplate="%{x:.2f}",
                textposition="outside",
                cliponaxis=False,
            )

    render_chart(
        impact_fig,
        key="matches_top_impact",
    )

    render_insight(
        "The ranking identifies injury episodes associated "
        "with large observed performance declines. "
        "Each comparison uses sampled matches and should not "
        "be interpreted as a causal estimate of injury impact."
    )

    impact_columns = [
        "Player",
        "Club",
        "Season",
        "Injury_Type",
        "Recovery_Days",
        "Before_Matches",
        "During_Matches",
        "Before_Avg_GD",
        "During_Avg_GD",
        "Before_PPM",
        "During_PPM",
        metric,
    ]

    render_table(
        top_impact[impact_columns],
        title="Injury Impact Leaderboard",
        height=350,
    )

else:

    st.info(
        "No valid injury impact comparisons are available "
        "for the current filters."
    )

st.divider()


render_section(
    "Match Outcomes Across Injury Phases",
    "Compare the number of wins, draws, and losses "
    "recorded before, during, and after player absence."
)

match_results = get_match_result_comparison(df)

match_fig = plot_match_results(
    match_results,
    palette=palette,
    dark_mode=dark_mode,
    show_labels=show_labels,
)

render_chart(
    match_fig,
    key="matches_results_comparison",
)

render_insight(
    "Match outcomes are counted from the available injury "
    "records. The same underlying football match may appear "
    "in more than one injury episode, so these totals should "
    "not be interpreted as unique league matches."
)

st.divider()


render_section(
    "Win Rate Intelligence",
    "Compare the percentage of sampled matches won "
    "across injury phases."
)

match_summary = get_match_performance_summary(df)

win_rate_data = match_summary.copy()

phase_colors = {
    "Before": colors[1],
    "During": colors[4],
    "After": colors[0],
}

win_rate_fig = px.bar(
    win_rate_data,
    x="Phase",
    y="Win_Rate",
    color="Phase",
    color_discrete_map=phase_colors,
    category_orders={
        "Phase": ["Before", "During", "After"],
    },
    title="Win Percentage Across Injury Phases",
    hover_data={
        "Wins": True,
        "Draws": True,
        "Losses": True,
        "Sampled_Matches": True,
        "Win_Rate": ":.2f",
    },
)

win_rate_fig.update_layout(
    showlegend=False,
    yaxis_title="Win Rate (%)",
    xaxis_title="Injury Phase",
    yaxis_range=[0, 100],
)

if show_labels:
    win_rate_fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="outside",
    )

render_chart(
    win_rate_fig,
    key="matches_win_rates",
)

render_table(
    match_summary,
    title="Match Outcome Statistics",
    height=200,
)

st.divider()


render_section(
    "Points Per Match Analysis",
    "Compare average football points earned "
    "across the three injury phases."
)

points_fig = px.line(
    match_summary,
    x="Phase",
    y="Points_Per_Match",
    markers=True,
    category_orders={
        "Phase": ["Before", "During", "After"],
    },
    title="Points Per Match Across Injury Phases",
)

points_fig.update_traces(
    line=dict(
        color=colors[0],
        width=4,
    ),
    marker=dict(
        size=14,
        color=[
            colors[1],
            colors[4],
            colors[0],
        ],
        line=dict(
            color="#FFFFFF",
            width=2,
        ),
    ),
)

points_fig.update_layout(
    xaxis_title="Injury Phase",
    yaxis_title="Points Per Match",
    yaxis_range=[0, 3.2],
)

render_chart(
    points_fig,
    key="matches_points_comparison",
)

st.caption(
    "Points per match uses the standard football scoring system: "
    "three points for a win, one for a draw, and zero for a loss."
)

st.divider()


render_section(
    "Club Performance Intelligence",
    "Compare sampled goal difference and points per match "
    "across football clubs."
)

club_comparison = get_club_comparison(df)

if not club_comparison.empty:

    club_fig = plot_club_performance(
        club_comparison,
        metric=(
            "PPM"
            if impact_metric == "Points Per Match"
            else "GD"
        ),
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        club_fig,
        key="matches_club_performance",
    )

    render_table(
        club_comparison,
        title="Club Performance Statistics",
        height=350,
    )

st.divider()


render_section(
    "Performance Decline by Football Club",
    "Compare the average change in team performance "
    "associated with recorded player absences."
)

club_impact = (
    valid_impact.groupby("Club")
    .agg(
        Injury_Episodes=("Injury_ID", "count"),
        Average_Decline=(metric, "mean"),
        Median_Decline=(metric, "median"),
    )
    .reset_index()
)

if not club_impact.empty:

    club_impact_fig = px.bar(
        club_impact.sort_values("Average_Decline"),
        x="Average_Decline",
        y="Club",
        orientation="h",
        color="Average_Decline",
        color_continuous_scale=[
            colors[1],
            colors[0],
        ],
        title="Average Performance Decline by Club",
        hover_data={
            "Injury_Episodes": True,
            "Median_Decline": ":.2f",
            "Average_Decline": ":.2f",
        },
    )

    club_impact_fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title=metric_label,
        yaxis_title="",
    )

    render_chart(
        club_impact_fig,
        key="matches_club_impact",
    )

    render_table(
        club_impact,
        title="Club Impact Comparison",
    )

st.divider()


render_section(
    "Injury Category Impact",
    "Examine how performance changes differ "
    "between recorded injury categories."
)

injury_impact = (
    valid_impact.groupby("Injury_Type", dropna=False)
    .agg(
        Injury_Episodes=("Injury_ID", "count"),
        Average_Decline=(metric, "mean"),
        Median_Decline=(metric, "median"),
        Average_Recovery=("Recovery_Days", "mean"),
    )
    .reset_index()
)

if not injury_impact.empty:

    category_options = [
        1,
        2,
        3,
        5,
        10,
    ]

    minimum_episodes = st.selectbox(
        "Minimum Injury Episodes per Category",
        options=category_options,
        index=2,
        key="matches_category_minimum",
    )

    injury_impact = injury_impact[
        injury_impact["Injury_Episodes"]
        >= minimum_episodes
    ].copy()

    if not injury_impact.empty:

        injury_impact = injury_impact.sort_values(
            "Average_Decline",
            ascending=False,
        )

        category_chart_data = injury_impact.head(
            leaderboard_size
        )

        category_fig = px.bar(
            category_chart_data.sort_values("Average_Decline"),
            x="Average_Decline",
            y="Injury_Type",
            orientation="h",
            color="Average_Decline",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Average Performance Decline by Injury Type",
            hover_data={
                "Injury_Episodes": True,
                "Median_Decline": ":.2f",
                "Average_Recovery": ":.1f",
            },
        )

        category_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title=metric_label,
            yaxis_title="",
        )

        render_chart(
            category_fig,
            key="matches_injury_category_impact",
        )

        render_table(
            injury_impact,
            title="Injury Category Performance Statistics",
        )

    else:

        st.info(
            "No injury categories meet the selected "
            "minimum episode requirement."
        )

st.divider()


render_section(
    "Player Absence Explorer",
    "Select a player to examine the sampled match "
    "results associated with their recorded injuries."
)

available_players = sorted(
    df["Player"].dropna().astype(str).unique().tolist()
)

if available_players:

    selected_player = st.selectbox(
        "Choose a Football Player",
        options=available_players,
        key="matches_player_selector",
    )

    player_df = df[
        df["Player"] == selected_player
    ].copy()

    player_episodes = player_df.sort_values(
        "Injury_Date",
        na_position="last",
    )

    episode_options = player_episodes["Injury_ID"].tolist()

    selected_episode = st.selectbox(
        "Choose an Injury Episode",
        options=episode_options,
        format_func=lambda injury_id: (
            f"Episode {injury_id}"
        ),
        key="matches_injury_episode",
    )

    episode = player_df[
        player_df["Injury_ID"] == selected_episode
    ].iloc[0]

    e1, e2, e3, e4 = st.columns(4)

    with e1:

        st.metric(
            "Injury Type",
            str(episode["Injury_Type"]),
        )

    with e2:

        st.metric(
            "Recovery Duration",
            format_value(
                episode["Recovery_Days"],
                0,
                " days",
            ),
        )

    with e3:

        st.metric(
            "Goal Difference Decline",
            format_value(
                episode["Team_Performance_Drop"],
                2,
            ),
        )

    with e4:

        st.metric(
            "Points Per Match Decline",
            format_value(
                episode["Points_Per_Match_Drop"],
                2,
            ),
        )

    player_phase_data = pd.DataFrame({
        "Phase": [
            "Before Injury",
            "During Absence",
            "After Return",
        ],
        "Goal Difference": [
            episode["Before_Avg_GD"],
            episode["During_Avg_GD"],
            episode["After_Avg_GD"],
        ],
        "Points Per Match": [
            episode["Before_PPM"],
            episode["During_PPM"],
            episode["After_PPM"],
        ],
    })

    player_fig = px.line(
        player_phase_data,
        x="Phase",
        y=impact_metric,
        markers=True,
        title=f"{selected_player} — Team Performance Timeline",
    )

    player_fig.update_traces(
        line=dict(
            color=colors[0],
            width=4,
        ),
        marker=dict(
            size=13,
        ),
    )

    player_fig.update_layout(
        xaxis_title="Injury Phase",
        yaxis_title=impact_metric,
    )

    render_chart(
        player_fig,
        key="matches_player_timeline",
    )

    player_summary_columns = [
        "Injury_ID",
        "Player",
        "Club",
        "Season",
        "Injury_Type",
        "Before_Matches",
        "During_Matches",
        "After_Matches",
        "Before_Avg_GD",
        "During_Avg_GD",
        "After_Avg_GD",
        "Before_PPM",
        "During_PPM",
        "After_PPM",
        "Team_Performance_Drop",
        "Points_Per_Match_Drop",
    ]

    render_table(
        player_episodes[player_summary_columns],
        title="Player Injury and Match History",
    )

st.divider()


render_section(
    "Match Performance Distribution",
    "Explore the distribution of recorded team "
    "performance changes across injury episodes."
)

if not valid_impact.empty:

    distribution_fig = px.histogram(
        valid_impact,
        x=metric,
        nbins=25,
        marginal="box",
        color_discrete_sequence=[colors[0]],
        title="Distribution of Team Performance Changes",
    )

    distribution_fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="#94A3B8",
    )

    distribution_fig.update_layout(
        xaxis_title=metric_label,
        yaxis_title="Injury Episodes",
        bargap=0.08,
    )

    render_chart(
        distribution_fig,
        key="matches_impact_distribution",
    )

st.divider()


render_section(
    "Match Intelligence Report",
    "Generate statistical findings based on the "
    "currently selected football injury records."
)

if st.button(
    "Generate Match Intelligence Report",
    type="primary",
    use_container_width=True,
    key="matches_generate_report",
):

    insights = []

    if not valid_impact.empty:

        insights.append(
            f"The average observed {metric_label.lower()} "
            f"across {valid_count} valid injury episodes "
            f"is {average_drop:.2f}."
        )

        insights.append(
            f"{decline_percentage:.1f}% of valid injury "
            f"episodes show worse sampled team performance "
            "during player absence."
        )

        if not club_impact.empty:

            highest_club = club_impact.loc[
                club_impact["Average_Decline"].idxmax()
            ]

            insights.append(
                f"{highest_club['Club']} has the highest "
                f"average observed performance decline "
                f"({highest_club['Average_Decline']:.2f}) "
                f"among its {int(highest_club['Injury_Episodes'])} "
                "valid injury comparisons."
            )

    before_row = match_summary[
        match_summary["Phase"] == "Before"
    ].iloc[0]

    during_row = match_summary[
        match_summary["Phase"] == "During"
    ].iloc[0]

    if (
        pd.notna(before_row["Win_Rate"])
        and pd.notna(during_row["Win_Rate"])
    ):

        win_difference = (
            before_row["Win_Rate"]
            - during_row["Win_Rate"]
        )

        insights.append(
            "The difference between the sampled "
            "before-injury and during-absence win rates "
            f"is {win_difference:.2f} percentage points."
        )

    insights.append(
        "The analysis uses sampled match observations. "
        "Match results may be influenced by opponent strength, "
        "player rotation, team selection, and other factors. "
        "The comparisons do not demonstrate causation."
    )

    st.session_state["matches_report"] = {
        "signature": (
            tuple(sorted(df["Injury_ID"].tolist())),
            impact_metric,
            min_matches,
        ),
        "insights": insights,
    }


saved_report = st.session_state.get("matches_report")

if saved_report is not None:

    current_signature = (
        tuple(sorted(df["Injury_ID"].tolist())),
        impact_metric,
        min_matches,
    )

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
            "Your filters or performance settings have changed. "
            "Generate the report again to update its findings."
        )

st.divider()


render_section(
    "Match Performance Dataset Explorer",
    "View and download the processed match performance "
    "records used in the analysis."
)

explorer_columns = [
    "Player",
    "Club",
    "Season",
    "Injury_Type",
    "Before_Matches",
    "During_Matches",
    "After_Matches",
    "Before_Wins",
    "During_Wins",
    "After_Wins",
    "Before_Avg_GD",
    "During_Avg_GD",
    "After_Avg_GD",
    "Before_PPM",
    "During_PPM",
    "After_PPM",
    "Team_Performance_Drop",
    "Points_Per_Match_Drop",
]

st.dataframe(
    df[explorer_columns],
    use_container_width=True,
    hide_index=True,
    height=380,
)

render_download(
    df,
    filename="footlens_match_performance_data.csv",
    label="Download Match Performance Dataset",
    key="matches_download",
)

render_footer()
import streamlit as st
import pandas as pd
import plotly.express as px

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
    require_data,
    render_download,
    format_value,
    render_footer
)

from src.metrics import (
    get_dashboard_kpis,
    get_club_injury_rankings,
    get_monthly_injury_trends,
    get_injury_heatmap,
    get_match_performance_summary,
    get_most_injured_players,
    get_club_comparison,
    generate_manager_insights
)

from src.visualizations import (
    plot_monthly_injury_trend,
    plot_club_injury_rankings,
    plot_injury_heatmap,
    plot_injury_type_distribution,
    plot_club_performance
)

from src.advanced_visualizations import (
    plot_team_performance_journey
)


df = get_filtered_data()

settings = get_settings()

palette = settings["palette"]

colors = get_palette()

dark_mode = settings["appearance"] == "Night Stadium"

leaderboard_size = settings["leaderboard_size"]

show_labels = settings["show_labels"]

require_data(df)


st.header("Football Intelligence Command Center")

st.write(
    "Explore football injuries, player recovery, "
    "team performance, and injury patterns through "
    "interactive analytics."
)

render_filter_summary(df)

st.divider()


kpis = get_dashboard_kpis(df)

render_kpis([
    {
        "label": "Injury Episodes",
        "value": f"{kpis['total_injuries']:,}",
        "help": "Total recorded injury episodes"
    },
    {
        "label": "Players Affected",
        "value": f"{kpis['total_players']:,}",
        "help": "Unique football players in the selected records"
    },
    {
        "label": "Football Clubs",
        "value": f"{kpis['total_clubs']:,}",
        "help": "Number of clubs represented"
    },
    {
        "label": "Seasons",
        "value": f"{kpis['total_seasons']:,}",
        "help": "Number of seasons represented"
    },
    {
        "label": "Median Recovery",
        "value": format_value(
            kpis["median_recovery"],
            0,
            " days"
        ),
        "help": "Median recorded time between injury and return"
    },
    {
        "label": "Valid Impact Records",
        "value": f"{kpis['valid_impact_records']:,}",
        "help": "Injury episodes with valid goal-difference comparisons"
    }
])

st.divider()


render_section(
    "Performance Intelligence",
    "Compare sampled team performance before, during, "
    "and after player injuries."
)

impact_metric = get_impact_metric()

valid_impact = df.dropna(
    subset=[impact_metric]
)

average_impact = (
    valid_impact[impact_metric].mean()
    if not valid_impact.empty
    else float("nan")
)

decline_count = (
    int((valid_impact[impact_metric] > 0).sum())
    if not valid_impact.empty
    else 0
)

decline_percentage = (
    decline_count / len(valid_impact) * 100
    if len(valid_impact) > 0
    else float("nan")
)

rating_data = df.dropna(
    subset=["Rating_Change"]
)

improved_players = (
    int((rating_data["Rating_Change"] > 0).sum())
    if not rating_data.empty
    else 0
)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Average Performance Drop",
        format_value(average_impact, 2)
    )

with c2:
    st.metric(
        "Episodes With Decline",
        decline_count
    )

with c3:
    st.metric(
        "Decline Percentage",
        format_value(
            decline_percentage,
            1,
            "%"
        )
    )

with c4:
    st.metric(
        "Improved Rating Episodes",
        improved_players
    )


st.caption(
    "Performance changes represent associations "
    "in sampled matches, not proof that an injury "
    "caused the team's results."
)

st.divider()


render_section(
    "Team Performance Journey",
    "Follow the changes in team performance "
    "across three injury phases."
)

performance_metric = settings["impact_metric"]

performance_fig = plot_team_performance_journey(
    df,
    metric=performance_metric,
    palette=palette,
    dark_mode=dark_mode
)

render_chart(
    performance_fig,
    key="home_performance_journey"
)


match_summary = get_match_performance_summary(df)

render_table(
    match_summary,
    title="Match Performance Summary",
    height=180
)

render_insight(
    "The performance journey compares the average "
    "recorded team statistics before injury, during "
    "player absence, and after the player's return. "
    "Differences may also reflect opponent strength, "
    "team selection, and other factors."
)

st.divider()


render_section(
    "Injury Intelligence",
    "Explore changes in recorded injury frequency "
    "across time and football clubs."
)

monthly_data = get_monthly_injury_trends(df)

if not monthly_data.empty:

    monthly_fig = plot_monthly_injury_trend(
        monthly_data,
        palette=palette,
        dark_mode=dark_mode
    )

    render_chart(
        monthly_fig,
        key="home_monthly_injuries"
    )

else:

    st.info(
        "No dated injury records are available "
        "for the selected filters."
    )


left, right = st.columns(2)

with left:

    render_section(
        "Club Injury Rankings",
        "Compare the number of recorded "
        "injury episodes across football clubs."
    )

    club_rankings = get_club_injury_rankings(df)

    if not club_rankings.empty:

        club_fig = plot_club_injury_rankings(
            club_rankings,
            palette=palette,
            dark_mode=dark_mode,
            show_labels=show_labels
        )

        render_chart(
            club_fig,
            key="home_club_rankings"
        )

with right:

    render_section(
        "Common Injury Types",
        "Explore the distribution of frequently "
        "recorded injuries."
    )

    injury_fig = plot_injury_type_distribution(
        df,
        palette=palette,
        dark_mode=dark_mode
    )

    render_chart(
        injury_fig,
        key="home_injury_distribution"
    )

st.divider()


render_section(
    "Injury Frequency Heatmap",
    "Identify months and clubs with higher "
    "recorded injury frequencies."
)

heatmap_data = get_injury_heatmap(df)

if not heatmap_data.empty:

    heatmap_fig = plot_injury_heatmap(
        heatmap_data,
        palette=palette,
        dark_mode=dark_mode
    )

    render_chart(
        heatmap_fig,
        key="home_injury_heatmap"
    )

else:

    st.info(
        "No valid injury dates are available "
        "for the current selection."
    )


render_insight(
    "This heatmap shows the number of recorded "
    "injury episodes across clubs and months. "
    "It helps identify injury clusters and "
    "seasonal patterns in the available dataset."
)

st.divider()


render_section(
    "Club Performance Comparison",
    "Compare goal difference or points per match "
    "across football clubs and injury phases."
)

club_comparison = get_club_comparison(df)

comparison_metric = (
    "PPM"
    if performance_metric == "Points Per Match"
    else "GD"
)

if not club_comparison.empty:

    comparison_fig = plot_club_performance(
        club_comparison,
        metric=comparison_metric,
        palette=palette,
        dark_mode=dark_mode
    )

    render_chart(
        comparison_fig,
        key="home_club_performance"
    )

st.divider()


render_section(
    "Football Injury Leaderboard",
    "Discover the most frequently injured players "
    "in the selected records."
)

top_players = get_most_injured_players(
    df,
    top_n=leaderboard_size
)

render_table(
    top_players,
    title="Most Frequently Injured Players",
    height=350
)

st.divider()


render_section(
    "Managerial Intelligence",
    "Generate data-backed observations "
    "based on your selected filters."
)

if st.button(
    "Generate Football Intelligence Report",
    type="primary",
    use_container_width=True,
    key="home_generate_report"
):

    insights = generate_manager_insights(df)

    st.session_state["home_report"] = insights


if "home_report" in st.session_state:

    st.info(
        "The report is generated from the data "
        "available when you last clicked the button. "
        "Regenerate it after changing filters."
    )

    for number, message in enumerate(
        st.session_state["home_report"],
        start=1
    ):

        render_insight(
            message,
            label=f"Finding {number}"
        )

st.divider()


render_section(
    "Explore More Analytics",
    "Open a specialized analytics page "
    "to investigate the data in greater detail."
)

nav1, nav2, nav3 = st.columns(3)

with nav1:

    st.page_link(
        "pages/injuries.py",
        label="Injury Intelligence",
        icon="🩺",
        use_container_width=True
    )

    st.caption(
        "Explore injury trends, football positions, "
        "monthly animation, and injury clusters."
    )

with nav2:

    st.page_link(
        "pages/matches.py",
        label="Match Performance",
        icon="⚽",
        use_container_width=True
    )

    st.caption(
        "Analyze performance drops, match outcomes, "
        "and team performance comparisons."
    )

with nav3:

    st.page_link(
        "pages/recovery.py",
        label="Recovery Lab",
        icon="📈",
        use_container_width=True
    )

    st.caption(
        "Explore player recovery timelines, "
        "rating changes, and comeback rankings."
    )


nav4, nav5, nav6 = st.columns(3)

with nav4:

    st.page_link(
        "pages/club_battle.py",
        label="Club Battle",
        icon="🏆",
        use_container_width=True
    )

with nav5:

    st.page_link(
        "pages/insights.py",
        label="Insights Studio",
        icon="📊",
        use_container_width=True
    )

with nav6:

    st.page_link(
        "pages/settings.py",
        label="Settings & Data",
        icon="⚙️",
        use_container_width=True
    )

st.divider()


render_section(
    "Dataset Explorer",
    "Preview the injury records currently "
    "included in your analysis."
)

preview_columns = [
    "Player",
    "Club",
    "Season",
    "Position",
    "Injury_Type",
    "Injury_Date",
    "Return_Date",
    "Recovery_Days",
    "Rating_Change",
    "Team_Performance_Drop"
]

st.dataframe(
    df[preview_columns].head(50),
    use_container_width=True,
    hide_index=True,
    height=300
)

render_download(
    df,
    filename="footlens_home_filtered_data.csv",
    label="Download Filtered Dataset",
    key="home_download_data"
)


render_footer()
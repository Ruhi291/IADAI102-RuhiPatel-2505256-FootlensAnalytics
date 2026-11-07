import numpy as np
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

from src.visualizations import (
    plot_recovery_distribution,
    plot_recovery_vs_rating,
)

from src.advanced_visualizations import (
    plot_recovery_bubble_explorer,
)


df = get_filtered_data()
settings = get_settings()

palette = settings["palette"]
colors = get_palette()
dark_mode = settings["appearance"] == "Night Stadium"
leaderboard_size = settings["leaderboard_size"]
show_labels = settings["show_labels"]

require_data(df)

st.header("Player Recovery & Comeback Intelligence")

st.write(
    "Explore recovery durations, player ratings, comeback "
    "performance, and injury patterns through interactive "
    "football analytics."
)

render_filter_summary(df)

st.divider()


valid_recovery = df.dropna(
    subset=["Recovery_Days"]
).copy()

valid_ratings = df.dropna(
    subset=[
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
    ]
).copy()

recovery_count = len(valid_recovery)
rating_count = len(valid_ratings)

average_recovery = (
    valid_recovery["Recovery_Days"].mean()
    if recovery_count > 0
    else np.nan
)

median_recovery = (
    valid_recovery["Recovery_Days"].median()
    if recovery_count > 0
    else np.nan
)

longest_recovery = (
    valid_recovery["Recovery_Days"].max()
    if recovery_count > 0
    else np.nan
)

average_rating_change = (
    valid_ratings["Rating_Change"].mean()
    if rating_count > 0
    else np.nan
)

improved_count = (
    int(valid_ratings["Rating_Change"].gt(0).sum())
    if rating_count > 0
    else 0
)

improved_percentage = (
    improved_count / rating_count * 100
    if rating_count > 0
    else np.nan
)


render_section(
    "Recovery Performance Overview",
    "Key statistics describing injury recovery "
    "and post-return player performance."
)

render_kpis([
    {
        "label": "Recorded Injuries",
        "value": f"{len(df):,}",
        "help": "Total injury episodes matching the current filters",
    },
    {
        "label": "Valid Recovery Records",
        "value": f"{recovery_count:,}",
        "help": "Injury episodes with a valid recovery duration",
    },
    {
        "label": "Average Recovery",
        "value": format_value(
            average_recovery,
            1,
            " days",
        ),
        "help": "Mean recovery duration across valid records",
    },
    {
        "label": "Median Recovery",
        "value": format_value(
            median_recovery,
            1,
            " days",
        ),
        "help": "Median recovery duration across valid records",
    },
    {
        "label": "Average Rating Change",
        "value": format_value(
            average_rating_change,
            2,
        ),
        "help": "Mean difference between post-return and pre-injury ratings",
    },
    {
        "label": "Positive Rating Changes",
        "value": format_value(
            improved_percentage,
            1,
            "%",
        ),
        "help": "Percentage of valid rating comparisons showing improvement",
    },
])

st.caption(
    f"Recovery statistics use {recovery_count:,} valid records. "
    f"Rating-change statistics use {rating_count:,} valid comparisons. "
    "Missing observations are excluded only from analyses "
    "that require those values."
)

st.divider()


render_section(
    "Recovery Duration Distribution",
    "Explore how long football players take "
    "to return after recorded injuries."
)

if not valid_recovery.empty:

    recovery_fig = plot_recovery_distribution(
        valid_recovery,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        recovery_fig,
        key="recovery_duration_distribution",
    )

    q1 = valid_recovery["Recovery_Days"].quantile(0.25)
    q3 = valid_recovery["Recovery_Days"].quantile(0.75)

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "25th Percentile",
            format_value(q1, 1, " days"),
        )

    with r2:
        st.metric(
            "Median Recovery",
            format_value(median_recovery, 1, " days"),
        )

    with r3:
        st.metric(
            "75th Percentile",
            format_value(q3, 1, " days"),
        )

    render_insight(
        f"The median recorded recovery period is "
        f"{median_recovery:.1f} days. The middle 50% "
        f"of recorded recovery durations fall between "
        f"{q1:.1f} and {q3:.1f} days."
    )

else:

    st.info(
        "No valid recovery-duration records are available "
        "for the current filters."
    )

st.divider()


render_section(
    "Recovery Category Explorer",
    "Compare the number of injury episodes "
    "across recorded recovery categories."
)

category_data = df.dropna(
    subset=["Recovery_Category"]
).copy()

if not category_data.empty:

    category_summary = (
        category_data.groupby(
            "Recovery_Category",
            dropna=False,
        )
        .agg(
            Injury_Episodes=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Players_Affected=("Player", "nunique"),
        )
        .reset_index()
        .sort_values(
            "Injury_Episodes",
            ascending=False,
        )
    )

    category_left, category_right = st.columns(2)

    with category_left:

        category_fig = px.pie(
            category_summary,
            names="Recovery_Category",
            values="Injury_Episodes",
            hole=0.58,
            color_discrete_sequence=colors,
            title="Distribution of Recovery Categories",
        )

        category_fig.update_traces(
            textposition="inside",
            textinfo="percent",
        )

        render_chart(
            category_fig,
            key="recovery_category_distribution",
        )

    with category_right:

        category_bar = px.bar(
            category_summary,
            x="Recovery_Category",
            y="Average_Recovery",
            color="Recovery_Category",
            color_discrete_sequence=colors,
            title="Average Duration by Recovery Category",
        )

        category_bar.update_layout(
            showlegend=False,
            xaxis_title="Recovery Category",
            yaxis_title="Average Recovery (Days)",
        )

        if show_labels:
            category_bar.update_traces(
                texttemplate="%{y:.1f}",
                textposition="outside",
            )

        render_chart(
            category_bar,
            key="recovery_category_average",
        )

    render_table(
        category_summary,
        title="Recovery Category Statistics",
    )

else:

    st.info(
        "No recovery category data is available."
    )

st.divider()


render_section(
    "Advanced Recovery Bubble Explorer",
    "Investigate the relationship between age, "
    "recovery duration, player ratings, and performance changes."
)

bubble_data = df.dropna(
    subset=[
        "Age",
        "Recovery_Days",
        "Rating_Change",
    ]
).copy()

if not bubble_data.empty:

    bubble_fig = plot_recovery_bubble_explorer(
        bubble_data,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        bubble_fig,
        key="recovery_bubble_explorer",
    )

    st.caption(
        "Each bubble represents a recorded injury episode. "
        "The horizontal axis shows player age, the vertical "
        "axis shows recovery duration, and the bubble color "
        "represents the player's rating change after returning."
    )

else:

    st.info(
        "There are no complete age, recovery, and "
        "rating-change observations for the current filters."
    )

st.divider()


render_section(
    "Player Age and Recovery",
    "Examine whether older players have different "
    "recovery durations in the recorded dataset."
)

age_data = df.dropna(
    subset=[
        "Age",
        "Recovery_Days",
    ]
).copy()

if not age_data.empty:

    age_left, age_right = st.columns([3, 2])

    with age_left:

        age_fig = px.scatter(
            age_data,
            x="Age",
            y="Recovery_Days",
            color="Position",
            color_discrete_sequence=colors,
            opacity=0.72,
            hover_name="Player",
            hover_data=[
                "Club",
                "Season",
                "Injury_Type",
            ],
            title="Player Age vs Recovery Duration",
        )

        if age_data["Age"].nunique() > 1:

            x_values = age_data["Age"].to_numpy(
                dtype=float
            )

            y_values = age_data["Recovery_Days"].to_numpy(
                dtype=float
            )

            if len(x_values) >= 2:

                slope, intercept = np.polyfit(
                    x_values,
                    y_values,
                    1,
                )

                x_line = np.linspace(
                    x_values.min(),
                    x_values.max(),
                    100,
                )

                y_line = slope * x_line + intercept

                age_fig.add_trace(
                    go.Scatter(
                        x=x_line,
                        y=y_line,
                        mode="lines",
                        name="Linear Trend",
                        line=dict(
                            color="#F59E0B",
                            width=3,
                            dash="dash",
                        ),
                        hoverinfo="skip",
                    )
                )

        age_fig.update_layout(
            xaxis_title="Player Age (Years)",
            yaxis_title="Recovery Duration (Days)",
        )

        render_chart(
            age_fig,
            key="recovery_age_scatter",
        )

    with age_right:

        age_correlation = age_data[
            ["Age", "Recovery_Days"]
        ].corr(method="pearson").iloc[0, 1]

        st.metric(
            "Pearson Correlation",
            format_value(age_correlation, 3),
        )

        st.metric(
            "Complete Observations",
            f"{len(age_data):,}",
        )

        if pd.isna(age_correlation):

            correlation_message = (
                "A correlation could not be calculated "
                "because the selected observations "
                "have insufficient variation."
            )

        elif abs(age_correlation) < 0.2:

            correlation_message = (
                "The selected data shows a very weak "
                "linear relationship between player "
                "age and recovery duration."
            )

        elif abs(age_correlation) < 0.4:

            correlation_message = (
                "The selected data shows a weak "
                "linear relationship between player "
                "age and recovery duration."
            )

        elif abs(age_correlation) < 0.6:

            correlation_message = (
                "The selected data shows a moderate "
                "linear relationship between player "
                "age and recovery duration."
            )

        else:

            correlation_message = (
                "The selected data shows a relatively "
                "strong linear relationship between "
                "player age and recovery duration."
            )

        render_insight(correlation_message)

        st.caption(
            "Correlation describes association, not causation. "
            "Injury severity, injury type, player fitness, "
            "and medical treatment may affect recovery time."
        )

st.divider()


render_section(
    "Recovery Duration and Rating Changes",
    "Explore whether longer recovery periods "
    "are associated with changes in player performance ratings."
)

recovery_rating_data = df.dropna(
    subset=[
        "Recovery_Days",
        "Rating_Change",
    ]
).copy()

if not recovery_rating_data.empty:

    rating_recovery_fig = plot_recovery_vs_rating(
        recovery_rating_data,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        rating_recovery_fig,
        key="recovery_rating_relationship",
    )

    recovery_rating_correlation = (
        recovery_rating_data[
            ["Recovery_Days", "Rating_Change"]
        ]
        .corr()
        .iloc[0, 1]
    )

    st.metric(
        "Recovery–Rating Correlation",
        format_value(
            recovery_rating_correlation,
            3,
        ),
    )

    st.caption(
        f"Based on {len(recovery_rating_data):,} complete "
        "recovery and rating-change comparisons. "
        "A correlation does not establish that recovery "
        "duration caused a player's rating to change."
    )

else:

    st.info(
        "No complete recovery and player-rating "
        "comparisons are available."
    )

st.divider()


render_section(
    "Player Comeback Leaderboard",
    "Identify recorded injury episodes with the "
    "strongest improvements in post-return player ratings."
)

if not valid_ratings.empty:

    leaderboard = (
        valid_ratings[
            valid_ratings["Rating_Change"] > 0
        ]
        .sort_values(
            "Rating_Change",
            ascending=False,
        )
        .head(leaderboard_size)
        .copy()
    )

    if not leaderboard.empty:

        leaderboard["Player_Label"] = (
            leaderboard["Player"].astype(str)
            + " | "
            + leaderboard["Club"].astype(str)
        )

        leaderboard_fig = px.bar(
            leaderboard.sort_values("Rating_Change"),
            x="Rating_Change",
            y="Player_Label",
            orientation="h",
            color="Rating_Change",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Top Post-Injury Rating Improvements",
            hover_data={
                "Player": True,
                "Club": True,
                "Season": True,
                "Injury_Type": True,
                "Recovery_Days": True,
                "Before_Avg_Rating": ":.2f",
                "After_Avg_Rating": ":.2f",
                "Rating_Change": ":.2f",
                "Player_Label": False,
            },
        )

        leaderboard_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Post-Return Rating Improvement",
            yaxis_title="",
        )

        if show_labels:
            leaderboard_fig.update_traces(
                texttemplate="%{x:+.2f}",
                textposition="outside",
                cliponaxis=False,
            )

        render_chart(
            leaderboard_fig,
            key="recovery_comeback_leaderboard",
        )

        leaderboard_columns = [
            "Player",
            "Club",
            "Season",
            "Position",
            "Injury_Type",
            "Recovery_Days",
            "Before_Avg_Rating",
            "After_Avg_Rating",
            "Rating_Change",
        ]

        render_table(
            leaderboard[leaderboard_columns],
            title="Top Comeback Performances",
            height=350,
        )

        top_comeback = leaderboard.iloc[0]

        render_insight(
            f"{top_comeback['Player']} recorded the largest "
            f"positive rating change among the selected "
            f"injury episodes (+{top_comeback['Rating_Change']:.2f}). "
            "This represents an observed improvement after return, "
            "not proof that the injury led to better performance."
        )

    else:

        st.info(
            "No positive post-return rating changes "
            "are present in the selected records."
        )

else:

    st.info(
        "No valid before-and-after player rating "
        "comparisons are available."
    )

st.divider()


render_section(
    "Before vs After Player Ratings",
    "Compare the distribution of recorded player ratings "
    "before injuries and after players return."
)

if not valid_ratings.empty:

    rating_comparison = valid_ratings[
        [
            "Before_Avg_Rating",
            "After_Avg_Rating",
        ]
    ].rename(
        columns={
            "Before_Avg_Rating": "Before Injury",
            "After_Avg_Rating": "After Return",
        }
    )

    rating_long = rating_comparison.melt(
        var_name="Phase",
        value_name="Average_Rating",
    )

    rating_left, rating_right = st.columns(2)

    with rating_left:

        ratings_box = px.box(
            rating_long,
            x="Phase",
            y="Average_Rating",
            color="Phase",
            color_discrete_sequence=colors,
            points="outliers",
            title="Rating Distribution by Phase",
        )

        ratings_box.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Player Match Rating",
        )

        render_chart(
            ratings_box,
            key="recovery_rating_boxplot",
        )

    with rating_right:

        rating_means = (
            rating_long.groupby("Phase")[
                "Average_Rating"
            ]
            .mean()
            .reindex([
                "Before Injury",
                "After Return",
            ])
            .reset_index()
        )

        rating_bar = px.bar(
            rating_means,
            x="Phase",
            y="Average_Rating",
            color="Phase",
            color_discrete_sequence=colors,
            title="Average Player Rating Comparison",
        )

        rating_bar.update_layout(
            showlegend=False,
            xaxis_title="",
            yaxis_title="Average Player Rating",
        )

        if show_labels:
            rating_bar.update_traces(
                texttemplate="%{y:.2f}",
                textposition="outside",
            )

        render_chart(
            rating_bar,
            key="recovery_rating_averages",
        )

    rating_change_summary = pd.DataFrame({
        "Metric": [
            "Average Rating Before Injury",
            "Average Rating After Return",
            "Average Rating Change",
            "Median Rating Change",
            "Positive Rating Changes",
            "Negative Rating Changes",
            "Unchanged Ratings",
        ],
        "Value": [
            valid_ratings["Before_Avg_Rating"].mean(),
            valid_ratings["After_Avg_Rating"].mean(),
            valid_ratings["Rating_Change"].mean(),
            valid_ratings["Rating_Change"].median(),
            int(valid_ratings["Rating_Change"].gt(0).sum()),
            int(valid_ratings["Rating_Change"].lt(0).sum()),
            int(valid_ratings["Rating_Change"].eq(0).sum()),
        ],
    })

    render_table(
        rating_change_summary,
        title="Before-and-After Rating Statistics",
        height=280,
    )

st.divider()


render_section(
    "Recovery by Injury Type",
    "Compare average recovery duration "
    "across recorded injury categories."
)

if not valid_recovery.empty:

    injury_recovery = (
        valid_recovery.dropna(
            subset=["Injury_Type"]
        )
        .groupby("Injury_Type")
        .agg(
            Injury_Episodes=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Maximum_Recovery=("Recovery_Days", "max"),
        )
        .reset_index()
    )

    minimum_category_records = st.slider(
        "Minimum Recovery Records per Injury Type",
        min_value=1,
        max_value=10,
        value=3,
        key="recovery_injury_minimum",
    )

    injury_recovery = injury_recovery[
        injury_recovery["Injury_Episodes"]
        >= minimum_category_records
    ].copy()

    if not injury_recovery.empty:

        injury_recovery = injury_recovery.sort_values(
            "Average_Recovery",
            ascending=False,
        )

        injury_chart_data = injury_recovery.head(
            leaderboard_size
        )

        injury_fig = px.bar(
            injury_chart_data.sort_values(
                "Average_Recovery"
            ),
            x="Average_Recovery",
            y="Injury_Type",
            orientation="h",
            color="Average_Recovery",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Average Recovery Duration by Injury Type",
            hover_data={
                "Injury_Episodes": True,
                "Median_Recovery": ":.1f",
                "Maximum_Recovery": ":.1f",
            },
        )

        injury_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Average Recovery (Days)",
            yaxis_title="",
        )

        if show_labels:
            injury_fig.update_traces(
                texttemplate="%{x:.1f}",
                textposition="outside",
                cliponaxis=False,
            )

        render_chart(
            injury_fig,
            key="recovery_injury_type_comparison",
        )

        render_table(
            injury_recovery,
            title="Injury Type Recovery Statistics",
            height=350,
        )

    else:

        st.info(
            "No injury categories meet the selected "
            "minimum record requirement."
        )

st.divider()


render_section(
    "Recovery by Playing Position",
    "Explore whether recorded recovery durations "
    "vary across football playing positions."
)

if not valid_recovery.empty:

    position_recovery = (
        valid_recovery.dropna(
            subset=["Position"]
        )
        .groupby("Position")
        .agg(
            Injury_Episodes=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Players_Affected=("Player", "nunique"),
        )
        .reset_index()
        .sort_values(
            "Average_Recovery",
            ascending=False,
        )
    )

    position_fig = px.bar(
        position_recovery.sort_values(
            "Average_Recovery"
        ),
        x="Average_Recovery",
        y="Position",
        orientation="h",
        color="Average_Recovery",
        color_continuous_scale=[
            colors[2],
            colors[0],
        ],
        title="Average Recovery Duration by Playing Position",
        hover_data={
            "Injury_Episodes": True,
            "Median_Recovery": ":.1f",
            "Players_Affected": True,
        },
    )

    position_fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Average Recovery (Days)",
        yaxis_title="",
    )

    render_chart(
        position_fig,
        key="recovery_position_comparison",
    )

    render_table(
        position_recovery,
        title="Position Recovery Statistics",
    )

st.divider()


render_section(
    "Individual Player Recovery Explorer",
    "Select a football player and injury episode "
    "to examine their recovery and rating history."
)

available_players = sorted(
    df["Player"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

if available_players:

    selected_player = st.selectbox(
        "Select a Football Player",
        options=available_players,
        key="recovery_selected_player",
    )

    player_data = df[
        df["Player"].astype(str) == selected_player
    ].copy()

    player_data = player_data.sort_values(
        "Injury_Date",
        na_position="last",
    )

    player_injury_count = len(player_data)

    player_average_recovery = (
        player_data["Recovery_Days"].mean()
    )

    player_average_rating_change = (
        player_data["Rating_Change"].mean()
    )

    player_club = (
        player_data["Club"].iloc[0]
        if not player_data.empty
        else "N/A"
    )

    st.markdown(f"### {selected_player}")

    st.caption(f"Club: {player_club}")

    p1, p2, p3 = st.columns(3)

    with p1:

        st.metric(
            "Recorded Injury Episodes",
            player_injury_count,
        )

    with p2:

        st.metric(
            "Average Recovery",
            format_value(
                player_average_recovery,
                1,
                " days",
            ),
        )

    with p3:

        st.metric(
            "Average Rating Change",
            format_value(
                player_average_rating_change,
                2,
            ),
        )

    player_episode_options = (
        player_data["Injury_ID"].tolist()
    )

    selected_episode = st.selectbox(
        "Select an Injury Episode",
        options=player_episode_options,
        format_func=lambda injury_id: (
            f"Injury Episode {injury_id}"
        ),
        key="recovery_selected_episode",
    )

    episode = player_data[
        player_data["Injury_ID"] == selected_episode
    ].iloc[0]

    episode_left, episode_right = st.columns(2)

    with episode_left:

        st.markdown("#### Injury Information")

        st.write(
            f"**Injury Type:** {episode['Injury_Type']}"
        )

        st.write(
            f"**Season:** {episode['Season']}"
        )

        st.write(
            f"**Position:** {episode['Position']}"
        )

        st.write(
            "**Injury Date:** "
            f"{episode['Injury_Date']}"
        )

        st.write(
            "**Return Date:** "
            f"{episode['Return_Date']}"
        )

        st.write(
            "**Recovery Duration:** "
            f"{format_value(episode['Recovery_Days'], 0, ' days')}"
        )

    with episode_right:

        st.markdown("#### Performance Information")

        st.write(
            "**Average Rating Before Injury:** "
            f"{format_value(episode['Before_Avg_Rating'], 2)}"
        )

        st.write(
            "**Average Rating After Return:** "
            f"{format_value(episode['After_Avg_Rating'], 2)}"
        )

        st.write(
            "**Rating Change:** "
            f"{format_value(episode['Rating_Change'], 2)}"
        )

        st.write(
            "**Comeback Status:** "
            f"{episode['Comeback_Status']}"
        )

        st.write(
            "**Team Performance Decline:** "
            f"{format_value(episode['Team_Performance_Drop'], 2)}"
        )

    episode_rating_values = [
        episode["Before_Avg_Rating"],
        episode["After_Avg_Rating"],
    ]

    episode_chart = go.Figure()

    episode_chart.add_trace(
        go.Scatter(
            x=[
                "Before Injury",
                "After Return",
            ],
            y=episode_rating_values,
            mode="lines+markers",
            line=dict(
                color=colors[0],
                width=4,
            ),
            marker=dict(
                size=16,
                color=[
                    colors[1],
                    colors[0],
                ],
                line=dict(
                    color="#FFFFFF",
                    width=2,
                ),
            ),
            name="Player Rating",
            hovertemplate=(
                "%{x}<br>"
                "Average Rating: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    episode_chart.update_layout(
        title=f"{selected_player} — Before vs After Rating",
        xaxis_title="Injury Phase",
        yaxis_title="Average Player Rating",
    )

    render_chart(
        episode_chart,
        key="recovery_selected_episode_chart",
    )

    player_history_columns = [
        "Injury_ID",
        "Player",
        "Club",
        "Season",
        "Injury_Type",
        "Injury_Date",
        "Return_Date",
        "Recovery_Days",
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
        "Comeback_Status",
    ]

    render_table(
        player_data[player_history_columns],
        title="Player Recovery History",
    )

st.divider()


render_section(
    "Recovery Intelligence Report",
    "Generate data-backed observations about "
    "player recovery and comeback performance."
)

if st.button(
    "Generate Recovery Intelligence Report",
    type="primary",
    use_container_width=True,
    key="recovery_generate_report",
):

    insights = []

    if not valid_recovery.empty:

        insights.append(
            f"The average recovery duration across "
            f"{recovery_count:,} valid injury episodes "
            f"is {average_recovery:.1f} days."
        )

        insights.append(
            f"The median recovery duration is "
            f"{median_recovery:.1f} days, while the "
            f"longest recorded recovery period "
            f"is {longest_recovery:.0f} days."
        )

    if not valid_ratings.empty:

        insights.append(
            f"{improved_percentage:.1f}% of injury episodes "
            f"with valid before-and-after rating comparisons "
            "show a positive rating change after return."
        )

        insights.append(
            f"The average post-return rating change is "
            f"{average_rating_change:+.2f} across "
            f"{rating_count:,} valid rating comparisons."
        )

    if not age_data.empty:

        correlation = (
            age_data[
                ["Age", "Recovery_Days"]
            ]
            .corr()
            .iloc[0, 1]
        )

        if pd.notna(correlation):

            insights.append(
                "The Pearson correlation between player "
                f"age and recovery duration is {correlation:+.3f} "
                "in the selected observations."
            )

    insights.append(
        "Recovery duration and rating changes are observational. "
        "They may reflect differences in injury severity, "
        "player characteristics, medical treatment, "
        "and match conditions."
    )

    st.session_state["recovery_report"] = {
        "signature": tuple(
            sorted(
                df["Injury_ID"].astype(str).tolist()
            )
        ),
        "insights": insights,
    }


saved_report = st.session_state.get(
    "recovery_report"
)

if saved_report is not None:

    current_signature = tuple(
        sorted(
            df["Injury_ID"].astype(str).tolist()
        )
    )

    if saved_report["signature"] == current_signature:

        for number, insight in enumerate(
            saved_report["insights"],
            start=1,
        ):

            render_insight(
                insight,
                label=f"Finding {number}",
            )

    else:

        st.info(
            "Your filters have changed. Generate the "
            "report again for updated recovery insights."
        )

st.divider()


render_section(
    "Recovery Dataset Explorer",
    "Explore the filtered recovery records "
    "and download the processed dataset."
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
    "Recovery_Category",
    "Before_Avg_Rating",
    "After_Avg_Rating",
    "Rating_Change",
    "Comeback_Status",
]

st.dataframe(
    df[explorer_columns],
    use_container_width=True,
    hide_index=True,
    height=380,
)

render_download(
    df,
    filename="footlens_recovery_data.csv",
    label="Download Recovery Analysis Dataset",
    key="recovery_download",
)

render_footer()
# ============================================================
# FOOTLENS ANALYTICS
# Mathematics for AI-II | Summative Assessment
#
# MODULE: Interactive Data Visualizations
# ============================================================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ------------------------------------------------------------
# 1. COLOR PALETTES
# ------------------------------------------------------------

PALETTES = {
    "Stadium Neon": [
        "#00E5A8", "#38BDF8", "#A78BFA",
        "#FBBF24", "#FB7185", "#2DD4BF"
    ],
    "Champions League": [
        "#60A5FA", "#818CF8", "#C084FC",
        "#F472B6", "#22D3EE", "#FACC15"
    ],
    "Sunset Arena": [
        "#FB7185", "#F97316", "#FBBF24",
        "#A3E635", "#2DD4BF", "#38BDF8"
    ],
    "Classic Football": [
        "#22C55E", "#84CC16", "#FACC15",
        "#F97316", "#3B82F6", "#A855F7"
    ]
}


def get_colors(palette="Stadium Neon"):
    """Return the colors for a selected dashboard palette."""
    return PALETTES.get(palette, PALETTES["Stadium Neon"])


# ------------------------------------------------------------
# 2. APPLY PROFESSIONAL CHART STYLING
# ------------------------------------------------------------

def style_chart(
    fig,
    title="",
    dark_mode=True,
    height=430,
    show_legend=True
):
    """
    Apply consistent styling to every Plotly chart.
    """

    text_color = "#F1F5F9" if dark_mode else "#172033"
    grid_color = "#26364A" if dark_mode else "#E2E8F0"

    fig.update_layout(
        title={
            "text": title,
            "x": 0.02,
            "xanchor": "left",
            "font": {
                "size": 19,
                "color": text_color
            }
        },
        font={
            "family": "Arial, sans-serif",
            "size": 12,
            "color": text_color
        },
        height=height,
        margin=dict(l=30, r=25, t=75, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        automargin=True
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        zeroline=False,
        automargin=True
    )

    return fig


# ------------------------------------------------------------
# 3. TOP INJURY IMPACT BAR CHART
# ------------------------------------------------------------

def plot_top_injury_impact(
    impact_df,
    palette="Stadium Neon",
    dark_mode=True,
    show_labels=True
):
    """
    Show injuries associated with the greatest
    decline in team goal difference.
    """

    colors = get_colors(palette)

    data = impact_df.copy()

    if data.empty:
        return go.Figure()

    data["Label"] = (
        data["Player"].astype(str)
        + " | "
        + data["Club"].astype(str)
    )

    data = data.sort_values("Team_Performance_Drop")

    fig = px.bar(
        data,
        x="Team_Performance_Drop",
        y="Label",
        orientation="h",
        color="Team_Performance_Drop",
        color_continuous_scale=[
            colors[1],
            colors[0]
        ],
        hover_data={
            "Player": True,
            "Club": True,
            "Injury_Type": True,
            "Recovery_Days": ":.0f",
            "Before_Avg_GD": ":.2f",
            "During_Avg_GD": ":.2f",
            "Team_Performance_Drop": ":.2f",
            "Label": False
        }
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Goal Difference Decline",
        yaxis_title=""
    )

    if show_labels:
        fig.update_traces(
            texttemplate="%{x:.2f}",
            textposition="outside",
            cliponaxis=False
        )

    return style_chart(
        fig,
        "Top Injuries by Team Performance Decline",
        dark_mode,
        height=500,
        show_legend=False
    )


# ------------------------------------------------------------
# 4. PLAYER PERFORMANCE TIMELINE
# ------------------------------------------------------------

def plot_player_timeline(
    timeline_df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Compare a player's average ratings before
    and after recorded injury episodes.
    """

    if timeline_df.empty:
        return go.Figure()

    colors = get_colors(palette)

    data = timeline_df.copy()

    data["Episode"] = (
        "Injury "
        + data["Injury_ID"].astype(str)
    )

    phase_order = [
        "Before Injury",
        "After Injury"
    ]

    data["Phase"] = pd.Categorical(
        data["Phase"],
        categories=phase_order,
        ordered=True
    )

    fig = px.line(
        data.sort_values(["Injury_ID", "Phase"]),
        x="Phase",
        y="Average_Rating",
        color="Episode",
        markers=True,
        line_group="Injury_ID",
        color_discrete_sequence=colors,
        hover_data=[
            "Player",
            "Club",
            "Injury_Type",
            "Injury_Date"
        ]
    )

    fig.update_traces(
        line_width=3,
        marker_size=11
    )

    fig.update_layout(
        xaxis_title="Injury Phase",
        yaxis_title="Average Player Rating"
    )

    return style_chart(
        fig,
        "Player Performance Before and After Injury",
        dark_mode,
        height=450
    )


# ------------------------------------------------------------
# 5. CLUB × MONTH INJURY HEATMAP
# ------------------------------------------------------------

def plot_injury_heatmap(
    heatmap_df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Display injury frequency across clubs and months.
    """

    colors = get_colors(palette)

    months = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    data = heatmap_df.reindex(
        columns=range(1, 13),
        fill_value=0
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=data.values,
            x=months,
            y=data.index,
            colorscale=[
                [0, "#142536"],
                [0.4, colors[1]],
                [1, colors[0]]
            ],
            text=data.values,
            texttemplate="%{text}",
            hovertemplate=(
                "Club: %{y}<br>"
                "Month: %{x}<br>"
                "Injuries: %{z}<extra></extra>"
            ),
            colorbar=dict(
                title="Injuries"
            )
        )
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Football Club"
    )

    return style_chart(
        fig,
        "Injury Frequency Heatmap by Club and Month",
        dark_mode,
        height=460,
        show_legend=False
    )


# ------------------------------------------------------------
# 6. AGE VS. PERFORMANCE DROP
# ------------------------------------------------------------

def plot_age_performance_scatter(
    df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Explore the relationship between player age
    and team performance decline.
    """

    data = df.dropna(
        subset=["Age", "Team_Performance_Drop"]
    ).copy()

    if data.empty:
        return go.Figure()

    colors = get_colors(palette)

    fig = px.scatter(
        data,
        x="Age",
        y="Team_Performance_Drop",
        color="Club",
        size="FIFA_Rating",
        size_max=20,
        opacity=0.75,
        color_discrete_sequence=colors,
        hover_data=[
            "Player",
            "Injury_Type",
            "Recovery_Days",
            "Season"
        ]
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#94A3B8"
    )

    fig.update_layout(
        xaxis_title="Player Age",
        yaxis_title="Team Goal Difference Decline"
    )

    return style_chart(
        fig,
        "Player Age vs Team Performance Decline",
        dark_mode,
        height=460
    )


# ------------------------------------------------------------
# 7. MATCH RESULT COMPARISON
# ------------------------------------------------------------

def plot_match_results(
    results_df,
    palette="Stadium Neon",
    dark_mode=True,
    show_labels=True
):
    """
    Compare wins, draws and losses in
    sampled matches across injury phases.
    """

    colors = get_colors(palette)

    fig = px.bar(
        results_df,
        x="Phase",
        y="Count",
        color="Result",
        barmode="group",
        color_discrete_map={
            "Wins": colors[0],
            "Draws": colors[3],
            "Losses": colors[4]
        },
        category_orders={
            "Phase": ["Before", "During", "After"],
            "Result": ["Wins", "Draws", "Losses"]
        }
    )

    if show_labels:
        fig.update_traces(
            texttemplate="%{y}",
            textposition="outside"
        )

    fig.update_layout(
        xaxis_title="Injury Phase",
        yaxis_title="Recorded Match Results"
    )

    return style_chart(
        fig,
        "Match Outcomes Across Injury Phases",
        dark_mode
    )


# ------------------------------------------------------------
# 8. CLUB INJURY RANKINGS
# ------------------------------------------------------------

def plot_club_injury_rankings(
    club_df,
    palette="Stadium Neon",
    dark_mode=True,
    show_labels=True
):
    """
    Rank football clubs by recorded injuries.
    """

    colors = get_colors(palette)

    data = club_df.sort_values("Injury_Count")

    fig = px.bar(
        data,
        x="Injury_Count",
        y="Club",
        orientation="h",
        color="Injury_Count",
        color_continuous_scale=[
            colors[1],
            colors[0]
        ],
        hover_data=[
            "Players_Affected",
            "Average_Recovery",
            "Average_Impact"
        ]
    )

    fig.update_layout(
        coloraxis_showscale=False,
        xaxis_title="Recorded Injury Episodes",
        yaxis_title=""
    )

    if show_labels:
        fig.update_traces(
            texttemplate="%{x}",
            textposition="outside"
        )

    return style_chart(
        fig,
        "Clubs with the Most Recorded Injuries",
        dark_mode,
        show_legend=False
    )


# ------------------------------------------------------------
# 9. RECOVERY DURATION DISTRIBUTION
# ------------------------------------------------------------

def plot_recovery_distribution(
    df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Show the distribution of recovery durations.
    """

    colors = get_colors(palette)

    data = df.dropna(
        subset=["Recovery_Days"]
    )

    fig = px.histogram(
        data,
        x="Recovery_Days",
        nbins=30,
        color_discrete_sequence=[colors[0]],
        marginal="box"
    )

    fig.update_layout(
        xaxis_title="Recovery Duration (Days)",
        yaxis_title="Number of Injury Episodes",
        bargap=0.08
    )

    return style_chart(
        fig,
        "Distribution of Recovery Durations",
        dark_mode,
        height=460,
        show_legend=False
    )


# ------------------------------------------------------------
# 10. INJURY TYPE DISTRIBUTION
# ------------------------------------------------------------

def plot_injury_type_distribution(
    df,
    palette="Stadium Neon",
    dark_mode=True,
    top_n=8
):
    """
    Show the most frequently recorded injury types.
    """

    colors = get_colors(palette)

    counts = (
        df["Injury_Type"]
        .value_counts()
        .head(top_n)
        .reset_index()
    )

    counts.columns = [
        "Injury_Type",
        "Count"
    ]

    fig = px.pie(
        counts,
        names="Injury_Type",
        values="Count",
        hole=0.58,
        color_discrete_sequence=colors
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "%{label}<br>"
            "Injuries: %{value}<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    return style_chart(
        fig,
        "Distribution of Common Injury Types",
        dark_mode,
        height=470
    )


# ------------------------------------------------------------
# 11. CLUB PERFORMANCE COMPARISON
# ------------------------------------------------------------

def plot_club_performance(
    club_df,
    metric="GD",
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Compare team performance before, during,
    and after player absence.
    """

    colors = get_colors(palette)

    if metric == "PPM":
        columns = [
            "Before_PPM",
            "During_PPM",
            "After_PPM"
        ]
        y_title = "Average Points Per Match"
    else:
        columns = [
            "Before_GD",
            "During_GD",
            "After_GD"
        ]
        y_title = "Average Goal Difference"

    data = club_df.melt(
        id_vars="Club",
        value_vars=columns,
        var_name="Phase",
        value_name="Performance"
    )

    data["Phase"] = (
        data["Phase"]
        .str.split("_")
        .str[0]
    )

    fig = px.bar(
        data,
        x="Club",
        y="Performance",
        color="Phase",
        barmode="group",
        color_discrete_map={
            "Before": colors[1],
            "During": colors[4],
            "After": colors[0]
        }
    )

    fig.update_layout(
        xaxis_title="Football Club",
        yaxis_title=y_title
    )

    return style_chart(
        fig,
        "Club Performance Across Injury Phases",
        dark_mode,
        height=470
    )


# ------------------------------------------------------------
# 12. MONTHLY INJURY TREND
# ------------------------------------------------------------

def plot_monthly_injury_trend(
    monthly_df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Show recorded injury patterns over time.
    """

    colors = get_colors(palette)

    data = monthly_df.copy()

    if data.empty:
        return go.Figure()

    data["Date"] = pd.to_datetime(
        {
            "year": data["Injury_Year"].astype(int),
            "month": data["Injury_Month"].astype(int),
            "day": 1
        }
    )

    data = data.sort_values("Date")

    fig = px.line(
        data,
        x="Date",
        y="Injury_Count",
        markers=True,
        color_discrete_sequence=[colors[0]]
    )

    fig.update_traces(
        line_width=3,
        marker_size=8,
        fill="tozeroy",
        fillcolor="rgba(0,229,168,0.10)"
    )

    fig.update_layout(
        xaxis_title="Injury Month",
        yaxis_title="Recorded Injury Episodes"
    )

    return style_chart(
        fig,
        "Monthly Injury Trends",
        dark_mode,
        height=450,
        show_legend=False
    )


# ------------------------------------------------------------
# 13. RECOVERY VS. PLAYER RATING CHANGE
# ------------------------------------------------------------

def plot_recovery_vs_rating(
    df,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Explore recovery duration and changes
    in average player ratings.
    """

    data = df.dropna(
        subset=[
            "Recovery_Days",
            "Rating_Change"
        ]
    ).copy()

    colors = get_colors(palette)

    fig = px.scatter(
        data,
        x="Recovery_Days",
        y="Rating_Change",
        color="Comeback_Status",
        color_discrete_map={
            "Improved": colors[0],
            "Declined": colors[4],
            "Unchanged": colors[3]
        },
        opacity=0.7,
        hover_data=[
            "Player",
            "Club",
            "Injury_Type",
            "Season"
        ]
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#94A3B8"
    )

    fig.update_layout(
        xaxis_title="Recovery Duration (Days)",
        yaxis_title="Change in Average Player Rating"
    )

    return style_chart(
        fig,
        "Recovery Duration vs Player Rating Change",
        dark_mode,
        height=460
    )


# ------------------------------------------------------------
# 14. HEAD-TO-HEAD CLUB COMPARISON
# ------------------------------------------------------------

def plot_club_battle(
    club_df,
    club_a,
    club_b,
    palette="Stadium Neon",
    dark_mode=True
):
    """
    Compare two clubs across injury-related metrics.
    """

    colors = get_colors(palette)

    selected = club_df[
        club_df["Club"].isin([club_a, club_b])
    ].copy()

    metrics = {
        "Injuries": "Injury_Count",
        "Median Recovery": "Median_Recovery",
        "Rating Change": "Average_Rating_Change"
    }

    records = []

    for _, row in selected.iterrows():
        for label, column in metrics.items():
            records.append({
                "Club": row["Club"],
                "Metric": label,
                "Value": row[column]
            })

    data = pd.DataFrame(records)

    fig = px.bar(
        data,
        x="Metric",
        y="Value",
        color="Club",
        barmode="group",
        color_discrete_sequence=[
            colors[0],
            colors[1]
        ],
        facet_col="Metric",
        facet_col_wrap=3
    )

    fig.update_yaxes(
        matches=None,
        showticklabels=True
    )

    fig.update_xaxes(
        showticklabels=False,
        title_text=""
    )

    fig.for_each_annotation(
        lambda a: a.update(
            text=a.text.split("=")[-1]
        )
    )

    fig.update_layout(
        yaxis_title="",
        bargap=0.25
    )

    return style_chart(
        fig,
        f"Club Battle: {club_a} vs {club_b}",
        dark_mode,
        height=420
    )
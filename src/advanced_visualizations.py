import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.visualizations import PALETTES


POSITION_COORDINATES = {
    "Goalkeeper": (10, 50),
    "Center Back": (27, 50),
    "Left Back": (30, 82),
    "Right Back": (30, 18),
    "Defensive Midfielder": (43, 50),
    "Central Midfielder": (58, 50),
    "Left Midfielder": (57, 82),
    "Right Midfielder": (57, 18),
    "Attacking Midfielder": (72, 50),
    "Left Winger": (80, 85),
    "Right Winger": (80, 15),
    "Center Forward": (88, 50)
}


def get_chart_colors(palette="Stadium Neon"):
    return PALETTES.get(
        palette,
        PALETTES["Stadium Neon"]
    )


def empty_figure(message="No data available", dark_mode=True):
    fig = go.Figure()

    color = "#E2E8F0" if dark_mode else "#334155"

    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=17, color=color)
    )

    fig.update_layout(
        height=430,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    return fig


def apply_chart_style(fig, dark_mode=True, height=460):
    text_color = "#F1F5F9" if dark_mode else "#172033"
    grid_color = "#26364A" if dark_mode else "#E2E8F0"

    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color=text_color
        ),
        margin=dict(l=35, r=30, t=75, b=45),
        hoverlabel=dict(
            bgcolor="#152238",
            font_color="#FFFFFF"
        )
    )

    fig.update_xaxes(
        gridcolor=grid_color,
        zeroline=False,
        automargin=True
    )

    fig.update_yaxes(
        gridcolor=grid_color,
        zeroline=False,
        automargin=True
    )

    return fig


def plot_animated_injury_race(
    df,
    palette="Stadium Neon",
    dark_mode=True,
    animation_speed=700,
    animation_enabled=True
):
    valid = df.dropna(
        subset=["Injury_Date", "Club"]
    ).copy()

    if valid.empty:
        return empty_figure(
            "No dated injury records available",
            dark_mode
        )

    valid["Month_Date"] = (
        valid["Injury_Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        valid.groupby(["Month_Date", "Club"])
        .size()
        .reset_index(name="Injuries")
    )

    months = pd.date_range(
        monthly["Month_Date"].min(),
        monthly["Month_Date"].max(),
        freq="MS"
    )

    clubs = sorted(monthly["Club"].unique())

    index = pd.MultiIndex.from_product(
        [months, clubs],
        names=["Month_Date", "Club"]
    )

    monthly = (
        monthly
        .set_index(["Month_Date", "Club"])
        .reindex(index, fill_value=0)
        .reset_index()
    )

    monthly["Month"] = (
        monthly["Month_Date"].dt.strftime("%b %Y")
    )

    colors = get_chart_colors(palette)

    color_map = {
        club: colors[i % len(colors)]
        for i, club in enumerate(clubs)
    }

    max_count = max(int(monthly["Injuries"].max()), 1)

    frames = []

    for month in months:
        frame_data = monthly[
            monthly["Month_Date"] == month
        ].sort_values("Injuries", ascending=False)

        month_label = month.strftime("%b %Y")

        traces = []

        for club in clubs:
            row = frame_data[
                frame_data["Club"] == club
            ]

            count = int(row["Injuries"].iloc[0])

            traces.append(
                go.Bar(
                    x=[count],
                    y=[club],
                    orientation="h",
                    name=club,
                    marker_color=color_map[club],
                    text=[count],
                    textposition="outside",
                    showlegend=False,
                    hovertemplate=(
                        f"Club: {club}<br>"
                        f"Month: {month_label}<br>"
                        "Injuries: %{x}<extra></extra>"
                    )
                )
            )

        frames.append(
            go.Frame(
                data=traces,
                name=month_label,
                layout=go.Layout(
                    title_text=(
                        f"Recorded Injuries — {month_label}"
                    )
                )
            )
        )

    initial_month = months[0]

    initial_data = monthly[
        monthly["Month_Date"] == initial_month
    ]

    fig = go.Figure()

    for club in clubs:
        row = initial_data[
            initial_data["Club"] == club
        ]

        count = int(row["Injuries"].iloc[0])

        fig.add_trace(
            go.Bar(
                x=[count],
                y=[club],
                orientation="h",
                name=club,
                marker_color=color_map[club],
                text=[count],
                textposition="outside",
                showlegend=False,
                hovertemplate=(
                    f"Club: {club}<br>"
                    "Injuries: %{x}<extra></extra>"
                )
            )
        )

    fig.frames = frames

    duration = (
        max(200, min(1500, int(animation_speed)))
        if animation_enabled
        else 0
    )

    if animation_enabled:
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    showactive=False,
                    x=0,
                    y=1.18,
                    buttons=[
                        dict(
                            label="▶ Play",
                            method="animate",
                            args=[
                                None,
                                {
                                    "frame": {
                                        "duration": duration,
                                        "redraw": True
                                    },
                                    "transition": {
                                        "duration": 0
                                    },
                                    "fromcurrent": True,
                                    "mode": "immediate"
                                }
                            ]
                        ),
                        dict(
                            label="⏸ Pause",
                            method="animate",
                            args=[
                                [None],
                                {
                                    "frame": {
                                        "duration": 0,
                                        "redraw": False
                                    },
                                    "transition": {
                                        "duration": 0
                                    },
                                    "mode": "immediate"
                                }
                            ]
                        )
                    ]
                )
            ]
        )

    slider_steps = []

    for month in months:
        label = month.strftime("%b %Y")

        slider_steps.append(
            dict(
                label=label,
                method="animate",
                args=[
                    [label],
                    {
                        "frame": {
                            "duration": 0,
                            "redraw": True
                        },
                        "transition": {
                            "duration": 0
                        },
                        "mode": "immediate"
                    }
                ]
            )
        )

    fig.update_layout(
        title=(
            "Recorded Injuries by Club — "
            f"{initial_month.strftime('%b %Y')}"
        ),
        xaxis=dict(
            title="Recorded Injury Episodes",
            range=[0, max_count * 1.3],
            dtick=1
        ),
        yaxis=dict(
            title="",
            categoryorder="array",
            categoryarray=clubs,
            autorange="reversed"
        ),
        barmode="overlay",
        sliders=[
            dict(
                active=0,
                steps=slider_steps,
                x=0.05,
                y=-0.12,
                len=0.9,
                currentvalue=dict(
                    prefix="Month: "
                )
            )
        ]
    )

    return apply_chart_style(
        fig,
        dark_mode,
        height=620
    )


def plot_injury_pitch(
    df,
    palette="Stadium Neon",
    dark_mode=True,
    selected_position=None
):
    valid = df.dropna(
        subset=["Position"]
    ).copy()

    if valid.empty:
        return empty_figure(
            "No playing-position data available",
            dark_mode
        )

    valid["Position"] = (
        valid["Position"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    position_counts = (
        valid.groupby("Position")
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Players_Affected=("Player", "nunique"),
            Average_Recovery=("Recovery_Days", "mean")
        )
        .reset_index()
    )

    position_counts = position_counts[
        position_counts["Position"].isin(
            POSITION_COORDINATES
        )
    ].copy()

    if position_counts.empty:
        return empty_figure(
            "No recognized football positions",
            dark_mode
        )

    colors = get_chart_colors(palette)

    pitch_color = "#0B5137" if dark_mode else "#27865C"
    line_color = "rgba(255,255,255,0.75)"

    fig = go.Figure()

    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=100,
        y1=100,
        fillcolor=pitch_color,
        line_color=line_color,
        line_width=3,
        layer="below"
    )

    for x in [20, 40, 60, 80]:
        fig.add_shape(
            type="rect",
            x0=x,
            y0=0,
            x1=x + 20,
            y1=100,
            fillcolor="rgba(255,255,255,0.035)",
            line_width=0,
            layer="below"
        )

    fig.add_shape(
        type="line",
        x0=50,
        y0=0,
        x1=50,
        y1=100,
        line=dict(
            color=line_color,
            width=2
        )
    )

    fig.add_shape(
        type="circle",
        x0=50 - 11,
        y0=50 - 11,
        x1=50 + 11,
        y1=50 + 11,
        line=dict(
            color=line_color,
            width=2
        )
    )

    fig.add_shape(
        type="circle",
        x0=49.4,
        y0=49.4,
        x1=50.6,
        y1=50.6,
        fillcolor=line_color,
        line_width=0
    )

    fig.add_shape(
        type="rect",
        x0=0,
        y0=20,
        x1=16,
        y1=80,
        line=dict(
            color=line_color,
            width=2
        )
    )

    fig.add_shape(
        type="rect",
        x0=84,
        y0=20,
        x1=100,
        y1=80,
        line=dict(
            color=line_color,
            width=2
        )
    )

    fig.add_shape(
        type="rect",
        x0=0,
        y0=36,
        x1=6,
        y1=64,
        line=dict(
            color=line_color,
            width=2
        )
    )

    fig.add_shape(
        type="rect",
        x0=94,
        y0=36,
        x1=100,
        y1=64,
        line=dict(
            color=line_color,
            width=2
        )
    )

    max_injuries = max(
        int(position_counts["Injury_Count"].max()),
        1
    )

    for _, row in position_counts.iterrows():
        position = row["Position"]

        x, y = POSITION_COORDINATES[position]

        count = int(row["Injury_Count"])

        marker_size = (
            20 + 35 * count / max_injuries
        )

        highlighted = (
            selected_position is None
            or selected_position == "All Positions"
            or selected_position == position
        )

        marker_color = (
            colors[0]
            if highlighted
            else "#64748B"
        )

        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[str(count)],
                textposition="middle center",
                textfont=dict(
                    color="#FFFFFF",
                    size=13
                ),
                marker=dict(
                    size=marker_size,
                    color=marker_color,
                    opacity=0.93 if highlighted else 0.3,
                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                ),
                name=position,
                customdata=[[
                    position,
                    count,
                    int(row["Players_Affected"]),
                    (
                        float(row["Average_Recovery"])
                        if pd.notna(row["Average_Recovery"])
                        else np.nan
                    )
                ]],
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Recorded Injuries: %{customdata[1]}<br>"
                    "Players Affected: %{customdata[2]}<br>"
                    "Average Recovery: "
                    "%{customdata[3]:.1f} days"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title="Interactive Injury Map by Playing Position",
        showlegend=False,
        height=600,
        xaxis=dict(
            range=[-5, 105],
            visible=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[-5, 105],
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(
            l=15,
            r=15,
            t=65,
            b=15
        )
    )

    return fig


def plot_recovery_bubble_explorer(
    df,
    palette="Stadium Neon",
    dark_mode=True
):
    valid = df.dropna(
        subset=[
            "Age",
            "Recovery_Days",
            "Rating_Change"
        ]
    ).copy()

    if valid.empty:
        return empty_figure(
            "No complete recovery comparisons available",
            dark_mode
        )

    colors = get_chart_colors(palette)

    valid["Bubble_Size"] = pd.to_numeric(
        valid["FIFA_Rating"],
        errors="coerce"
    )

    valid["Bubble_Size"] = (
        valid["Bubble_Size"]
        .fillna(valid["Bubble_Size"].median())
        .fillna(50)
        .clip(lower=1)
    )

    fig = px.scatter(
        valid,
        x="Age",
        y="Recovery_Days",
        size="Bubble_Size",
        color="Rating_Change",
        color_continuous_scale=[
            colors[4],
            "#94A3B8",
            colors[0]
        ],
        color_continuous_midpoint=0,
        size_max=34,
        opacity=0.75,
        hover_name="Player",
        hover_data={
            "Club": True,
            "Injury_Type": True,
            "Season": True,
            "Recovery_Days": ":.0f",
            "Rating_Change": ":.2f",
            "Bubble_Size": False
        },
        title="Recovery Explorer: Age, Duration and Rating Change"
    )

    fig.update_layout(
        xaxis_title="Player Age",
        yaxis_title="Recovery Duration (Days)",
        coloraxis_colorbar=dict(
            title="Rating Change"
        )
    )

    return apply_chart_style(
        fig,
        dark_mode,
        height=500
    )


def plot_team_performance_journey(
    df,
    metric="Goal Difference",
    palette="Stadium Neon",
    dark_mode=True
):
    colors = get_chart_colors(palette)

    if metric == "Points Per Match":
        columns = [
            "Before_PPM",
            "During_PPM",
            "After_PPM"
        ]
        label = "Average Points Per Match"
    else:
        columns = [
            "Before_Avg_GD",
            "During_Avg_GD",
            "After_Avg_GD"
        ]
        label = "Average Goal Difference"

    phases = [
        "Before Injury",
        "During Absence",
        "After Return"
    ]

    values = [
        df[column].mean()
        for column in columns
    ]

    if all(pd.isna(value) for value in values):
        return empty_figure(
            "No performance comparisons available",
            dark_mode
        )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=phases,
            y=values,
            mode="lines+markers+text",
            line=dict(
                color=colors[0],
                width=4,
                shape="spline"
            ),
            marker=dict(
                size=16,
                color=[
                    colors[1],
                    colors[4],
                    colors[0]
                ],
                line=dict(
                    color="#FFFFFF",
                    width=2
                )
            ),
            text=[
                f"{value:.2f}" if pd.notna(value) else "N/A"
                for value in values
            ],
            textposition="top center",
            textfont=dict(size=14),
            hovertemplate=(
                "%{x}<br>"
                f"{label}: "
                "%{y:.2f}<extra></extra>"
            ),
            showlegend=False
        )
    )

    if metric == "Goal Difference":
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#94A3B8"
        )

    fig.update_layout(
        title="Team Performance Across Injury Phases",
        xaxis_title="Injury Phase",
        yaxis_title=label
    )

    return apply_chart_style(
        fig,
        dark_mode,
        height=470
    )


def plot_club_injury_comparison(
    df,
    club_a,
    club_b,
    palette="Stadium Neon",
    dark_mode=True,
    top_n=8
):
    selected = df[
        df["Club"].isin([club_a, club_b])
    ].copy()

    if selected.empty:
        return empty_figure(
            "No matching club records",
            dark_mode
        )

    counts = (
        selected.groupby(["Club", "Injury_Type"])
        .size()
        .reset_index(name="Injury_Count")
    )

    top_types = (
        counts.groupby("Injury_Type")["Injury_Count"]
        .sum()
        .nlargest(top_n)
        .index
    )

    counts = counts[
        counts["Injury_Type"].isin(top_types)
    ]

    colors = get_chart_colors(palette)

    fig = px.bar(
        counts,
        x="Injury_Type",
        y="Injury_Count",
        color="Club",
        barmode="group",
        color_discrete_map={
            club_a: colors[0],
            club_b: colors[1]
        },
        title=f"Injury Comparison: {club_a} vs {club_b}",
        hover_data={
            "Injury_Count": True
        }
    )

    fig.update_layout(
        xaxis_title="Injury Type",
        yaxis_title="Recorded Injury Episodes",
        xaxis_tickangle=-35
    )

    return apply_chart_style(
        fig,
        dark_mode,
        height=500
    )
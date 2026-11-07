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

from src.visualizations import (
    plot_top_injury_impact,
    plot_injury_heatmap,
    plot_age_performance_scatter,
)

from src.metrics import (
    get_top_impact_injuries,
    get_injury_heatmap,
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

impact_column = get_impact_metric()

impact_label = (
    "Points Per Match Decline"
    if impact_column == "Points_Per_Match_Drop"
    else "Goal Difference Decline"
)


def safe_mean(series):
    values = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    return float(values.mean()) if not values.empty else np.nan


def safe_median(series):
    values = pd.to_numeric(
        series,
        errors="coerce",
    ).dropna()

    return float(values.median()) if not values.empty else np.nan


def safe_correlation(data, x_column, y_column, method="pearson"):
    valid = data[[x_column, y_column]].apply(
        pd.to_numeric,
        errors="coerce",
    ).dropna()

    if (
        len(valid) < 3
        or valid[x_column].nunique() < 2
        or valid[y_column].nunique() < 2
    ):
        return np.nan, len(valid)

    correlation = valid[x_column].corr(
        valid[y_column],
        method=method,
    )

    return float(correlation), len(valid)


def correlation_description(value):
    if pd.isna(value):
        return "Insufficient variation or observations"

    magnitude = abs(value)

    if magnitude < 0.2:
        strength = "very weak"
    elif magnitude < 0.4:
        strength = "weak"
    elif magnitude < 0.6:
        strength = "moderate"
    elif magnitude < 0.8:
        strength = "strong"
    else:
        strength = "very strong"

    if value > 0:
        direction = "positive"
    elif value < 0:
        direction = "negative"
    else:
        direction = "no"

    return f"{strength.capitalize()} {direction} linear association"


def show_question(number, title, description):
    st.markdown(f"### Research Question {number}")

    st.subheader(title)

    st.write(description)


def make_bar(
    data,
    x_column,
    y_column,
    title,
    color_column=None,
    horizontal=False,
):
    if horizontal:
        fig = px.bar(
            data,
            x=x_column,
            y=y_column,
            orientation="h",
            color=color_column,
            color_continuous_scale=(
                [colors[1], colors[0]]
                if color_column
                else None
            ),
            color_discrete_sequence=[colors[0]],
            title=title,
        )
    else:
        fig = px.bar(
            data,
            x=x_column,
            y=y_column,
            color=color_column,
            color_continuous_scale=(
                [colors[1], colors[0]]
                if color_column
                else None
            ),
            color_discrete_sequence=[colors[0]],
            title=title,
        )

    fig.update_layout(
        coloraxis_showscale=False,
    )

    if show_labels:
        fig.update_traces(
            texttemplate=(
                "%{x:.2f}" if horizontal else "%{y:.2f}"
            ),
            textposition="outside",
            cliponaxis=False,
        )

    return fig


st.header("Research & Statistical Insights Studio")

st.write(
    "Investigate five research questions using statistical "
    "analysis, interactive visualizations, grouped summaries, "
    "correlations, and evidence-based observations."
)

render_filter_summary(df)

st.caption(
    "All results describe the currently selected injury episodes. "
    "Comparisons are observational and do not establish causality."
)

st.divider()


qualified_df = get_qualified_impact_data(df)

valid_rating_df = df.dropna(
    subset=[
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
    ]
).copy()

valid_recovery_df = df.dropna(
    subset=["Recovery_Days"]
).copy()

valid_dates_df = df.dropna(
    subset=["Injury_Date"]
).copy()


render_section(
    "Research Data Overview",
    "Understand the sample size and completeness "
    "of the records used in the analysis."
)

render_kpis([
    {
        "label": "Injury Episodes",
        "value": f"{len(df):,}",
        "help": "Number of selected recorded injury episodes",
    },
    {
        "label": "Unique Players",
        "value": f"{df['Player'].nunique():,}",
        "help": "Number of unique football players",
    },
    {
        "label": "Football Clubs",
        "value": f"{df['Club'].nunique():,}",
        "help": "Number of clubs represented",
    },
    {
        "label": "Impact Comparisons",
        "value": f"{len(qualified_df):,}",
        "help": "Valid comparisons meeting the selected match requirement",
    },
    {
        "label": "Rating Comparisons",
        "value": f"{len(valid_rating_df):,}",
        "help": "Episodes with valid before-and-after player ratings",
    },
    {
        "label": "Recovery Records",
        "value": f"{len(valid_recovery_df):,}",
        "help": "Episodes with valid recovery durations",
    },
])

coverage_data = pd.DataFrame({
    "Analysis": [
        "Injury Dates",
        "Recovery Durations",
        "Player Rating Comparisons",
        "Team Performance Comparisons",
    ],
    "Complete_Records": [
        len(valid_dates_df),
        len(valid_recovery_df),
        len(valid_rating_df),
        len(qualified_df),
    ],
})

coverage_data["Coverage_Percent"] = (
    coverage_data["Complete_Records"]
    / len(df)
    * 100
)

coverage_fig = px.bar(
    coverage_data,
    x="Analysis",
    y="Coverage_Percent",
    color="Coverage_Percent",
    color_continuous_scale=[
        colors[1],
        colors[0],
    ],
    title="Analytical Data Coverage",
)

coverage_fig.update_layout(
    coloraxis_showscale=False,
    xaxis_title="Analysis",
    yaxis_title="Complete Records (%)",
    yaxis_range=[0, 105],
)

render_chart(
    coverage_fig,
    key="insights_data_coverage",
)

render_table(
    coverage_data.round(2),
    title="Data Coverage Statistics",
    height=220,
)

st.divider()


show_question(
    1,
    "Which Injuries Are Associated With the Greatest Team Performance Decline?",
    "Identify the injury episodes associated with the "
    "largest observed decreases in goal difference "
    "or points per match during player absence.",
)

st.latex(
    r"\text{Performance Drop}="
    r"\overline{P}_{\text{before}}-"
    r"\overline{P}_{\text{during}}"
)

st.caption(
    "P represents the selected team performance measure. "
    "A positive result indicates a decline during absence."
)

top_impact = get_top_impact_injuries(
    df,
    top_n=leaderboard_size,
    metric=impact_column,
    min_matches=min_matches,
)

if not top_impact.empty:

    top_impact = top_impact.copy()

    if impact_column == "Team_Performance_Drop":

        impact_fig = plot_top_injury_impact(
            top_impact,
            palette=palette,
            dark_mode=dark_mode,
            show_labels=show_labels,
        )

    else:

        top_impact["Player_Label"] = (
            top_impact["Player"].astype(str)
            + " | "
            + top_impact["Club"].astype(str)
        )

        impact_chart_data = top_impact.sort_values(
            impact_column
        )

        impact_fig = make_bar(
            impact_chart_data,
            impact_column,
            "Player_Label",
            "Largest Observed Performance Declines",
            color_column=impact_column,
            horizontal=True,
        )

    render_chart(
        impact_fig,
        key="insights_question_1_chart",
    )

    highest_impact = top_impact.loc[
        top_impact[impact_column].idxmax()
    ]

    render_insight(
        f"The largest observed {impact_label.lower()} "
        f"is associated with {highest_impact['Player']} "
        f"({highest_impact['Club']}), with a value of "
        f"{highest_impact[impact_column]:.2f}. "
        "This is a comparison of sampled matches, "
        "not a causal estimate."
        ,
        label="Research Finding 1",
    )

    impact_columns = [
        "Player",
        "Club",
        "Season",
        "Injury_Type",
        "Before_Matches",
        "During_Matches",
        impact_column,
    ]

    render_table(
        top_impact[impact_columns],
        title="Highest Observed Performance Declines",
    )

else:

    st.info(
        "No valid performance comparisons are available "
        "for the current settings."
    )

st.divider()


show_question(
    2,
    "How Do Match Results Change During Player Absence?",
    "Compare recorded wins, draws, losses, win percentages, "
    "and points per match before injury, during absence, "
    "and after player return.",
)

phase_names = [
    "Before",
    "During",
    "After",
]

outcome_rows = []

for phase in phase_names:

    wins = pd.to_numeric(
        df[f"{phase}_Wins"],
        errors="coerce",
    ).sum(min_count=1)

    draws = pd.to_numeric(
        df[f"{phase}_Draws"],
        errors="coerce",
    ).sum(min_count=1)

    losses = pd.to_numeric(
        df[f"{phase}_Losses"],
        errors="coerce",
    ).sum(min_count=1)

    total = (
        wins + draws + losses
        if pd.notna(wins)
        and pd.notna(draws)
        and pd.notna(losses)
        else np.nan
    )

    win_rate = (
        wins / total * 100
        if pd.notna(total) and total > 0
        else np.nan
    )

    points_per_match = (
        (wins * 3 + draws) / total
        if pd.notna(total) and total > 0
        else np.nan
    )

    outcome_rows.append({
        "Phase": phase,
        "Wins": wins,
        "Draws": draws,
        "Losses": losses,
        "Sampled_Matches": total,
        "Win_Rate": win_rate,
        "Points_Per_Match": points_per_match,
    })


outcome_df = pd.DataFrame(outcome_rows)

outcomes_long = outcome_df.melt(
    id_vars="Phase",
    value_vars=[
        "Wins",
        "Draws",
        "Losses",
    ],
    var_name="Result",
    value_name="Count",
)

outcome_fig = px.bar(
    outcomes_long,
    x="Phase",
    y="Count",
    color="Result",
    barmode="group",
    color_discrete_map={
        "Wins": colors[0],
        "Draws": colors[1],
        "Losses": colors[4],
    },
    category_orders={
        "Phase": phase_names,
    },
    title="Recorded Match Outcomes Across Injury Phases",
)

outcome_fig.update_layout(
    xaxis_title="Injury Phase",
    yaxis_title="Sampled Match Observations",
)

render_chart(
    outcome_fig,
    key="insights_question_2_outcomes",
)


result_left, result_right = st.columns(2)

with result_left:

    win_fig = px.bar(
        outcome_df,
        x="Phase",
        y="Win_Rate",
        color="Phase",
        color_discrete_sequence=colors,
        category_orders={
            "Phase": phase_names,
        },
        title="Win Rate Across Injury Phases",
    )

    win_fig.update_layout(
        showlegend=False,
        xaxis_title="Injury Phase",
        yaxis_title="Win Rate (%)",
        yaxis_range=[0, 105],
    )

    render_chart(
        win_fig,
        key="insights_question_2_win_rate",
    )


with result_right:

    ppm_fig = px.line(
        outcome_df,
        x="Phase",
        y="Points_Per_Match",
        markers=True,
        category_orders={
            "Phase": phase_names,
        },
        title="Points Per Match Across Injury Phases",
    )

    ppm_fig.update_traces(
        line=dict(
            color=colors[0],
            width=4,
        ),
        marker=dict(
            size=12,
        ),
    )

    ppm_fig.update_layout(
        xaxis_title="Injury Phase",
        yaxis_title="Points Per Match",
    )

    render_chart(
        ppm_fig,
        key="insights_question_2_ppm",
    )


render_table(
    outcome_df.round(2),
    title="Match Outcome Statistics",
    height=200,
)

before_win_rate = outcome_df.loc[
    outcome_df["Phase"] == "Before",
    "Win_Rate",
].iloc[0]

during_win_rate = outcome_df.loc[
    outcome_df["Phase"] == "During",
    "Win_Rate",
].iloc[0]

if pd.notna(before_win_rate) and pd.notna(during_win_rate):

    win_rate_difference = (
        before_win_rate - during_win_rate
    )

    render_insight(
        f"The sampled win rate changes from "
        f"{before_win_rate:.1f}% before injury "
        f"to {during_win_rate:.1f}% during absence. "
        f"The difference is {win_rate_difference:+.1f} "
        "percentage points when calculated as before "
        "minus during. Recorded match observations may "
        "overlap between injury episodes.",
        label="Research Finding 2",
    )

st.divider()


show_question(
    3,
    "How Does Recovery Duration Relate to Player Performance After Return?",
    "Investigate the relationship between recovery duration "
    "and the difference between player ratings before injury "
    "and after their return.",
)

st.latex(
    r"\Delta R="
    r"\overline{R}_{\text{after}}-"
    r"\overline{R}_{\text{before}}"
)

st.caption(
    "Positive rating changes represent higher average "
    "post-return ratings. Negative values indicate lower ratings."
)

recovery_rating = df.dropna(
    subset=[
        "Recovery_Days",
        "Rating_Change",
    ]
).copy()

if not recovery_rating.empty:

    recovery_fig = px.scatter(
        recovery_rating,
        x="Recovery_Days",
        y="Rating_Change",
        color="Injury_Type",
        color_discrete_sequence=colors,
        opacity=0.75,
        hover_name="Player",
        hover_data=[
            "Club",
            "Season",
            "Position",
        ],
        title="Recovery Duration vs Player Rating Change",
    )

    recovery_fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#94A3B8",
    )

    recovery_fig.update_layout(
        xaxis_title="Recovery Duration (Days)",
        yaxis_title="Post-Return Rating Change",
        legend_title="Injury Type",
    )

    render_chart(
        recovery_fig,
        key="insights_question_3_scatter",
    )

    recovery_pearson, recovery_n = safe_correlation(
        recovery_rating,
        "Recovery_Days",
        "Rating_Change",
        method="pearson",
    )

    recovery_spearman, _ = safe_correlation(
        recovery_rating,
        "Recovery_Days",
        "Rating_Change",
        method="spearman",
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.metric(
            "Pearson Correlation",
            format_value(recovery_pearson, 3),
        )

    with r2:
        st.metric(
            "Spearman Correlation",
            format_value(recovery_spearman, 3),
        )

    with r3:
        st.metric(
            "Complete Observations",
            f"{recovery_n:,}",
        )

    if pd.notna(recovery_pearson):

        render_insight(
            f"The Pearson correlation between recovery "
            f"duration and post-return rating change is "
            f"{recovery_pearson:+.3f}, based on "
            f"{recovery_n} complete observations. "
            f"This represents a "
            f"{correlation_description(recovery_pearson).lower()}. "
            "The relationship is observational and may be "
            "influenced by injury type and severity.",
            label="Research Finding 3",
        )

    else:

        render_insight(
            "The current selection does not contain enough "
            "variation to estimate a reliable correlation.",
            label="Research Finding 3",
        )

    recovery_summary = (
        recovery_rating.groupby("Recovery_Category")
        .agg(
            Episodes=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Average_Rating_Change=("Rating_Change", "mean"),
            Median_Rating_Change=("Rating_Change", "median"),
        )
        .reset_index()
    )

    render_table(
        recovery_summary.round(2),
        title="Recovery Category and Rating Change Summary",
    )

else:

    st.info(
        "No complete recovery and rating-change "
        "observations are available."
    )

st.divider()


show_question(
    4,
    "Does Player Age Relate to Recovery Duration and Performance Change?",
    "Examine whether player age is associated with "
    "recovery time or changes in post-return ratings.",
)

age_recovery = df.dropna(
    subset=[
        "Age",
        "Recovery_Days",
    ]
).copy()

age_rating = df.dropna(
    subset=[
        "Age",
        "Rating_Change",
    ]
).copy()

if not age_recovery.empty:

    age_fig = px.scatter(
        age_recovery,
        x="Age",
        y="Recovery_Days",
        color="Position",
        color_discrete_sequence=colors,
        opacity=0.72,
        hover_name="Player",
        hover_data=[
            "Club",
            "Injury_Type",
        ],
        title="Player Age vs Recovery Duration",
    )

    age_fig.update_layout(
        xaxis_title="Player Age (Years)",
        yaxis_title="Recovery Duration (Days)",
    )

    render_chart(
        age_fig,
        key="insights_question_4_age_recovery",
    )

else:

    st.info(
        "No complete age and recovery records are available."
    )


if not age_rating.empty:

    age_rating_fig = plot_age_performance_scatter(
        age_rating,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        age_rating_fig,
        key="insights_question_4_age_rating",
    )


age_recovery_pearson, age_recovery_n = safe_correlation(
    df,
    "Age",
    "Recovery_Days",
)

age_rating_pearson, age_rating_n = safe_correlation(
    df,
    "Age",
    "Rating_Change",
)

age_recovery_spearman, _ = safe_correlation(
    df,
    "Age",
    "Recovery_Days",
    method="spearman",
)

age_rating_spearman, _ = safe_correlation(
    df,
    "Age",
    "Rating_Change",
    method="spearman",
)

age_correlation_table = pd.DataFrame({
    "Relationship": [
        "Age vs Recovery Duration",
        "Age vs Rating Change",
    ],
    "Pearson": [
        age_recovery_pearson,
        age_rating_pearson,
    ],
    "Spearman": [
        age_recovery_spearman,
        age_rating_spearman,
    ],
    "Complete_Observations": [
        age_recovery_n,
        age_rating_n,
    ],
})

render_table(
    age_correlation_table.round(3),
    title="Age Relationship Statistics",
    height=160,
)

if pd.notna(age_recovery_pearson):

    render_insight(
        f"Player age and recovery duration show a "
        f"{correlation_description(age_recovery_pearson).lower()} "
        f"(Pearson r = {age_recovery_pearson:+.3f}; "
        f"n = {age_recovery_n}). "
        "This does not establish that age causes "
        "differences in recovery duration.",
        label="Research Finding 4",
    )

else:

    render_insight(
        "The current filters do not provide enough "
        "variation to estimate the relationship "
        "between age and recovery duration.",
        label="Research Finding 4",
    )

st.divider()


show_question(
    5,
    "Which Clubs and Months Have the Highest Recorded Injury Frequencies?",
    "Compare injury episode counts across clubs "
    "and calendar months to identify observed "
    "concentrations and seasonal patterns.",
)

heatmap_df = get_injury_heatmap(df)

if not heatmap_df.empty:

    heatmap_fig = plot_injury_heatmap(
        heatmap_df,
        palette=palette,
        dark_mode=dark_mode,
    )

    render_chart(
        heatmap_fig,
        key="insights_question_5_heatmap",
    )

    club_totals = heatmap_df.sum(axis=1).sort_values(
        ascending=False
    )

    month_totals = heatmap_df.sum(axis=0).sort_values(
        ascending=False
    )

    top_club = club_totals.index[0]
    top_club_count = int(club_totals.iloc[0])

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

    top_month = int(month_totals.index[0])
    top_month_count = int(month_totals.iloc[0])

    q5_left, q5_right = st.columns(2)

    with q5_left:

        club_frequency = (
            df["Club"]
            .value_counts()
            .reset_index()
        )

        club_frequency.columns = [
            "Club",
            "Injury_Count",
        ]

        club_fig = px.bar(
            club_frequency,
            x="Club",
            y="Injury_Count",
            color="Club",
            color_discrete_sequence=colors,
            title="Recorded Injuries by Club",
        )

        club_fig.update_layout(
            showlegend=False,
            xaxis_title="Football Club",
            yaxis_title="Injury Episodes",
        )

        render_chart(
            club_fig,
            key="insights_question_5_clubs",
        )

    with q5_right:

        month_frequency = pd.DataFrame({
            "Month": [
                month_names[int(month)]
                for month in month_totals.index
            ],
            "Injury_Count": month_totals.values,
        })

        month_fig = px.bar(
            month_frequency,
            x="Month",
            y="Injury_Count",
            color="Injury_Count",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title="Recorded Injuries by Calendar Month",
        )

        month_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Month",
            yaxis_title="Injury Episodes",
        )

        render_chart(
            month_fig,
            key="insights_question_5_months",
        )

    render_insight(
        f"{top_club} has the highest dated injury count "
        f"({top_club_count}) in the current selection. "
        f"{month_names[top_month]} has the highest "
        f"calendar-month count ({top_month_count}). "
        "These are observed frequencies rather than "
        "exposure-adjusted injury rates.",
        label="Research Finding 5",
    )

    heatmap_table = heatmap_df.reset_index()

    render_table(
        heatmap_table,
        title="Club-by-Month Injury Frequency Pivot",
        height=320,
    )

else:

    st.info(
        "No dated injury observations are available "
        "for the current filters."
    )

st.divider()


render_section(
    "Statistical Laboratory",
    "Inspect descriptive statistics, numerical distributions, "
    "and correlation relationships."
)

numeric_columns = [
    "Age",
    "FIFA_Rating",
    "Recovery_Days",
    "Before_Avg_Rating",
    "After_Avg_Rating",
    "Rating_Change",
    "Before_Avg_GD",
    "During_Avg_GD",
    "After_Avg_GD",
    "Before_PPM",
    "During_PPM",
    "After_PPM",
    "Team_Performance_Drop",
    "Points_Per_Match_Drop",
]

numeric_df = df[numeric_columns].apply(
    pd.to_numeric,
    errors="coerce",
)

selected_statistics = st.multiselect(
    "Choose Numerical Variables",
    options=numeric_columns,
    default=[
        "Age",
        "Recovery_Days",
        "Rating_Change",
        "Team_Performance_Drop",
    ],
    key="insights_statistical_variables",
)

if selected_statistics:

    selected_numeric = numeric_df[
        selected_statistics
    ].copy()

    descriptive = selected_numeric.describe().T

    descriptive["median"] = selected_numeric.median()

    descriptive["missing"] = selected_numeric.isna().sum()

    descriptive["variance"] = selected_numeric.var()

    descriptive = descriptive[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "median",
            "75%",
            "max",
            "variance",
            "missing",
        ]
    ]

    render_table(
        descriptive.reset_index().rename(
            columns={"index": "Variable"}
        ).round(3),
        title="Descriptive Statistical Summary",
        height=400,
    )

    if len(selected_statistics) >= 2:

        correlation_method = st.selectbox(
            "Correlation Method",
            options=[
                "Pearson",
                "Spearman",
            ],
            key="insights_correlation_method",
        )

        correlation_matrix = selected_numeric.corr(
            method=correlation_method.lower()
        )

        correlation_fig = px.imshow(
            correlation_matrix,
            text_auto=".2f",
            color_continuous_scale=[
                colors[4],
                "#94A3B8",
                colors[0],
            ],
            zmin=-1,
            zmax=1,
            color_continuous_midpoint=0,
            title=(
                f"{correlation_method} "
                "Correlation Matrix"
            ),
            aspect="auto",
        )

        correlation_fig.update_layout(
            coloraxis_colorbar=dict(
                title="Correlation"
            ),
        )

        render_chart(
            correlation_fig,
            key="insights_correlation_matrix",
        )

        st.caption(
            "Pearson correlation measures linear association. "
            "Spearman correlation measures monotonic association "
            "using ranks. Both range from -1 to +1 and do not "
            "establish cause-and-effect relationships."
        )

else:

    st.info(
        "Select at least one numerical variable "
        "to view descriptive statistics."
    )

st.divider()


render_section(
    "Interactive Data Aggregation Studio",
    "Group records by football characteristics and "
    "calculate aggregated statistics."
)

group_options = [
    "Club",
    "Season",
    "Position",
    "Injury_Type",
    "Recovery_Category",
]

metric_options = {
    "Injury Episode Count": None,
    "Average Recovery Days": "Recovery_Days",
    "Average Player Rating Change": "Rating_Change",
    "Average Team Performance Decline": "Team_Performance_Drop",
    "Average Points Per Match Decline": "Points_Per_Match_Drop",
    "Average Player Age": "Age",
}

agg_left, agg_right = st.columns(2)

with agg_left:

    selected_group = st.selectbox(
        "Group Records By",
        options=group_options,
        key="insights_group_by",
    )

with agg_right:

    selected_aggregation = st.selectbox(
        "Calculate",
        options=list(metric_options.keys()),
        key="insights_aggregation_metric",
    )


selected_metric_column = metric_options[
    selected_aggregation
]

if selected_metric_column is None:

    grouped_data = (
        df.groupby(
            selected_group,
            dropna=False,
        )
        .size()
        .reset_index(name="Result")
    )

else:

    grouped_data = (
        df.groupby(
            selected_group,
            dropna=False,
        )[selected_metric_column]
        .mean()
        .reset_index(name="Result")
    )

grouped_data = grouped_data.dropna(
    subset=["Result"]
).sort_values(
    "Result",
    ascending=False,
)

if not grouped_data.empty:

    grouped_chart = px.bar(
        grouped_data.head(leaderboard_size),
        x=selected_group,
        y="Result",
        color="Result",
        color_continuous_scale=[
            colors[1],
            colors[0],
        ],
        title=(
            f"{selected_aggregation} "
            f"by {selected_group}"
        ),
    )

    grouped_chart.update_layout(
        coloraxis_showscale=False,
        xaxis_title=selected_group,
        yaxis_title=selected_aggregation,
    )

    render_chart(
        grouped_chart,
        key="insights_grouped_analysis",
    )

    render_table(
        grouped_data.round(3),
        title="Grouped Statistical Results",
    )


st.markdown("#### Pivot Table Explorer")

pivot_left, pivot_middle, pivot_right = st.columns(3)

with pivot_left:

    pivot_rows = st.selectbox(
        "Pivot Rows",
        options=[
            "Club",
            "Season",
            "Position",
        ],
        key="insights_pivot_rows",
    )

with pivot_middle:

    pivot_columns_options = [
        column
        for column in [
            "Season",
            "Club",
            "Position",
            "Recovery_Category",
        ]
        if column != pivot_rows
    ]

    pivot_columns = st.selectbox(
        "Pivot Columns",
        options=pivot_columns_options,
        key="insights_pivot_columns",
    )

with pivot_right:

    pivot_value_choice = st.selectbox(
        "Pivot Measure",
        options=[
            "Injury Count",
            "Average Recovery",
            "Average Rating Change",
        ],
        key="insights_pivot_measure",
    )


if pivot_value_choice == "Injury Count":

    pivot_df = pd.pivot_table(
        df,
        index=pivot_rows,
        columns=pivot_columns,
        values="Injury_ID",
        aggfunc="count",
        fill_value=0,
    )

elif pivot_value_choice == "Average Recovery":

    pivot_df = pd.pivot_table(
        df,
        index=pivot_rows,
        columns=pivot_columns,
        values="Recovery_Days",
        aggfunc="mean",
    )

else:

    pivot_df = pd.pivot_table(
        df,
        index=pivot_rows,
        columns=pivot_columns,
        values="Rating_Change",
        aggfunc="mean",
    )


if not pivot_df.empty:

    render_table(
        pivot_df.reset_index().round(2),
        title="Interactive Pivot Table",
        height=350,
    )

    st.caption(
        "Pivot tables summarize the selected dataset "
        "across two categorical dimensions."
    )

else:

    st.info(
        "The selected pivot combination has "
        "no complete observations."
    )

st.divider()


render_section(
    "Research Conclusions",
    "Generate a concise summary of findings "
    "from the currently selected dataset."
)

current_signature = (
    tuple(sorted(df["Injury_ID"].astype(str).tolist())),
    impact_column,
    min_matches,
)


if st.button(
    "Generate Research Conclusions",
    type="primary",
    use_container_width=True,
    key="insights_generate_conclusions",
):

    conclusions = []

    valid_impact = qualified_df.dropna(
        subset=[impact_column]
    )

    if not valid_impact.empty:

        mean_drop = valid_impact[
            impact_column
        ].mean()

        decline_share = (
            valid_impact[impact_column]
            .gt(0)
            .mean()
            * 100
        )

        conclusions.append(
            f"Across {len(valid_impact):,} valid injury "
            f"comparisons, the average observed "
            f"{impact_label.lower()} is {mean_drop:+.2f}. "
            f"{decline_share:.1f}% show a positive decline value."
        )

    if (
        pd.notna(before_win_rate)
        and pd.notna(during_win_rate)
    ):

        conclusions.append(
            f"The sampled match win rate is "
            f"{before_win_rate:.1f}% before injury "
            f"and {during_win_rate:.1f}% during player absence."
        )

    if pd.notna(recovery_pearson) if not recovery_rating.empty else False:

        conclusions.append(
            f"Recovery duration and player rating change "
            f"have a Pearson correlation of "
            f"{recovery_pearson:+.3f} in the selected data."
        )

    if pd.notna(age_recovery_pearson):

        conclusions.append(
            f"Player age and recovery duration "
            f"have a Pearson correlation of "
            f"{age_recovery_pearson:+.3f}."
        )

    if not heatmap_df.empty:

        conclusions.append(
            f"{top_club} has the highest number of dated "
            f"injury episodes among the selected clubs. "
            f"{month_names[top_month]} is the most frequently "
            "represented injury month."
        )

    conclusions.append(
        "Missing dates, incomplete rating comparisons, "
        "and limited sampled matches affect which episodes "
        "contribute to individual analyses."
    )

    conclusions.append(
        "The dataset supports descriptive and correlational "
        "analysis, but the findings cannot establish that "
        "injuries caused changes in match performance "
        "or player ratings."
    )

    st.session_state["insights_report"] = {
        "signature": current_signature,
        "conclusions": conclusions,
    }


saved_report = st.session_state.get(
    "insights_report"
)

if saved_report is not None:

    if saved_report["signature"] == current_signature:

        for number, conclusion in enumerate(
            saved_report["conclusions"],
            start=1,
        ):

            render_insight(
                conclusion,
                label=f"Conclusion {number}",
            )

    else:

        st.info(
            "Your filters or analysis settings have changed. "
            "Generate the conclusions again for updated results."
        )

st.divider()


render_section(
    "Research Limitations",
    "Interpret the findings in the context "
    "of the available observational data."
)

with st.expander(
    "Understanding Data Quality and Interpretation",
    expanded=True,
):

    st.markdown(
        """
        **Missing information**

        Some records have missing injury dates, return dates,
        recovery durations, or player rating comparisons.
        Individual analyses use only the observations with
        the required valid fields.

        **Limited match samples**

        Match performance is calculated from the available
        before-injury, during-absence, and after-return
        match observations rather than full-season results.

        **Repeated observations**

        Individual injury episodes may include overlapping
        football matches. Match totals therefore represent
        sampled observations, not necessarily unique matches.

        **Selection and confounding**

        Injury severity, playing time, opponent strength,
        player fitness, squad selection, and tactical decisions
        may influence the observed relationships.

        **Correlation is not causation**

        A relationship between injury characteristics and
        football performance does not establish that one
        variable caused the other.

        **Injury counts versus injury risk**

        Recorded injury frequencies are not adjusted for
        player minutes, number of matches, or squad exposure.
        They should not be interpreted as injury rates.
        """
    )

st.divider()


render_section(
    "Research Dataset Explorer",
    "Inspect and download the processed records "
    "underlying the statistical analysis."
)

research_columns = [
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
    "Before_PPM",
    "During_PPM",
    "After_PPM",
    "Team_Performance_Drop",
    "Points_Per_Match_Drop",
]

st.dataframe(
    df[research_columns],
    use_container_width=True,
    hide_index=True,
    height=380,
)

render_download(
    df,
    filename="footlens_research_analysis.csv",
    label="Download Research Dataset",
    key="insights_download",
)

render_footer()
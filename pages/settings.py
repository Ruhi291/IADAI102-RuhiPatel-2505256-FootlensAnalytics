import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.components import (
    load_data,
    get_filtered_data,
    get_settings,
    get_palette,
    reset_all,
    render_kpis,
    render_chart,
    render_table,
    render_section,
    render_insight,
    render_filter_summary,
    render_download,
    render_footer,
    format_value,
)

from src.visualizations import PALETTES


raw_df, cleaned_df = load_data()

df = get_filtered_data()

settings = get_settings()

colors = get_palette()

st.header("Settings & Data Management")

st.write(
    "Personalize your football analytics experience, "
    "inspect dataset quality, explore processed records, "
    "and manage data exports."
)

render_filter_summary(df)

st.divider()


def apply_preferences():
    setting_names = [
        "appearance",
        "palette",
        "impact_metric",
        "leaderboard_size",
        "min_matches",
        "chart_height",
        "animation_enabled",
        "animation_speed",
        "show_labels",
        "show_insights",
        "show_tables",
    ]

    for name in setting_names:
        edit_key = f"settings_edit_{name}"

        if edit_key in st.session_state:
            st.session_state[name] = st.session_state[edit_key]


def reset_preferences():
    reset_all()

    defaults = {
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

    for name, value in defaults.items():
        st.session_state[f"settings_edit_{name}"] = value


render_section(
    "Dashboard Personalization",
    "Customize the visual appearance and analytical "
    "behavior of your FootLens dashboard."
)

st.info(
    "These preferences are shared across the seven pages. "
    "You can also access them through the Advanced Settings "
    "& Personalization panel at the top of the application."
)

with st.form("dashboard_preferences_form"):

    st.markdown("#### Appearance")

    appearance_col, palette_col = st.columns(2)

    with appearance_col:

        appearance_options = [
            "Night Stadium",
            "Daylight Arena",
        ]

        st.selectbox(
            "Dashboard Theme",
            options=appearance_options,
            index=appearance_options.index(
                settings["appearance"]
            ),
            key="settings_edit_appearance",
        )

    with palette_col:

        palette_options = list(PALETTES.keys())

        st.selectbox(
            "Chart Color Palette",
            options=palette_options,
            index=palette_options.index(
                settings["palette"]
            ),
            key="settings_edit_palette",
        )

    st.markdown("#### Analytical Preferences")

    analysis_col1, analysis_col2, analysis_col3 = st.columns(3)

    with analysis_col1:

        metric_options = [
            "Goal Difference",
            "Points Per Match",
        ]

        st.selectbox(
            "Team Performance Indicator",
            options=metric_options,
            index=metric_options.index(
                settings["impact_metric"]
            ),
            key="settings_edit_impact_metric",
        )

    with analysis_col2:

        st.slider(
            "Leaderboard Size",
            min_value=5,
            max_value=20,
            value=settings["leaderboard_size"],
            key="settings_edit_leaderboard_size",
        )

    with analysis_col3:

        st.slider(
            "Minimum Sampled Matches",
            min_value=1,
            max_value=3,
            value=settings["min_matches"],
            key="settings_edit_min_matches",
        )

    st.markdown("#### Visualization Preferences")

    visual_col1, visual_col2 = st.columns(2)

    with visual_col1:

        st.slider(
            "Chart Height",
            min_value=350,
            max_value=750,
            value=settings["chart_height"],
            step=5,
            key="settings_edit_chart_height",
        )

    with visual_col2:

        st.slider(
            "Animation Frame Duration (ms)",
            min_value=200,
            max_value=1500,
            value=settings["animation_speed"],
            step=100,
            key="settings_edit_animation_speed",
        )

    st.markdown("#### Display Controls")

    toggle_col1, toggle_col2, toggle_col3 = st.columns(3)

    with toggle_col1:

        st.toggle(
            "Enable Animations",
            value=settings["animation_enabled"],
            key="settings_edit_animation_enabled",
        )

        st.toggle(
            "Show Chart Labels",
            value=settings["show_labels"],
            key="settings_edit_show_labels",
        )

    with toggle_col2:

        st.toggle(
            "Show Analytical Insights",
            value=settings["show_insights"],
            key="settings_edit_show_insights",
        )

        st.toggle(
            "Show Detailed Tables",
            value=settings["show_tables"],
            key="settings_edit_show_tables",
        )

    with toggle_col3:

        st.caption(
            "Changes will be applied to the shared "
            "dashboard preferences when you save."
        )

    st.form_submit_button(
        "Apply Dashboard Preferences",
        type="primary",
        use_container_width=True,
        on_click=apply_preferences,
    )


st.button(
    "Restore Default Settings",
    on_click=reset_preferences,
    use_container_width=True,
    key="settings_restore_defaults",
)

st.divider()


render_section(
    "Current Configuration",
    "Review the preferences currently active "
    "throughout FootLens Analytics."
)

active_settings = get_settings()

configuration_data = pd.DataFrame(
    [
        {
            "Setting": key.replace("_", " ").title(),
            "Current Value": str(value),
        }
        for key, value in active_settings.items()
    ]
)

st.dataframe(
    configuration_data,
    use_container_width=True,
    hide_index=True,
    height=400,
)

st.divider()


render_section(
    "Dataset Overview",
    "Understand the size and structure of the "
    "football injury dataset."
)

total_raw_rows = len(raw_df)
total_clean_rows = len(cleaned_df)
total_columns = len(cleaned_df.columns)

unique_players = cleaned_df["Player"].nunique()
unique_clubs = cleaned_df["Club"].nunique()

unique_seasons = cleaned_df["Season"].nunique()

duplicate_rows = int(raw_df.duplicated().sum())

render_kpis([
    {
        "label": "Raw Records",
        "value": f"{total_raw_rows:,}",
        "help": "Total records in the original dataset",
    },
    {
        "label": "Processed Records",
        "value": f"{total_clean_rows:,}",
        "help": "Total records after preprocessing",
    },
    {
        "label": "Processed Columns",
        "value": f"{total_columns:,}",
        "help": "Total available processed variables",
    },
    {
        "label": "Unique Players",
        "value": f"{unique_players:,}",
        "help": "Distinct players in the processed dataset",
    },
    {
        "label": "Football Clubs",
        "value": f"{unique_clubs:,}",
        "help": "Distinct clubs represented",
    },
    {
        "label": "Seasons",
        "value": f"{unique_seasons:,}",
        "help": "Distinct football seasons",
    },
])

st.caption(
    f"Original dataset: {total_raw_rows:,} rows. "
    f"Processed dataset: {total_clean_rows:,} rows. "
    f"Exact duplicate raw rows detected: {duplicate_rows:,}."
)

st.divider()


render_section(
    "Dataset Quality Dashboard",
    "Inspect missing values, completeness, and "
    "the availability of important analytical variables."
)

missing_counts = cleaned_df.isna().sum()

quality_df = pd.DataFrame({
    "Column": cleaned_df.columns,
    "Data_Type": cleaned_df.dtypes.astype(str).values,
    "Missing_Values": missing_counts.values,
    "Complete_Values": (
        len(cleaned_df) - missing_counts
    ).values,
    "Unique_Values": [
        cleaned_df[column].nunique(dropna=True)
        for column in cleaned_df.columns
    ],
})

quality_df["Missing_Percentage"] = (
    quality_df["Missing_Values"]
    / max(len(cleaned_df), 1)
    * 100
)

quality_df["Completeness_Percentage"] = (
    100 - quality_df["Missing_Percentage"]
)

quality_df = quality_df.sort_values(
    "Missing_Values",
    ascending=False,
)

total_cells = (
    len(cleaned_df) * len(cleaned_df.columns)
)

missing_cells = int(
    cleaned_df.isna().sum().sum()
)

complete_cells = total_cells - missing_cells

overall_completeness = (
    complete_cells / total_cells * 100
    if total_cells > 0
    else np.nan
)

columns_with_missing = int(
    (missing_counts > 0).sum()
)

q1, q2, q3, q4 = st.columns(4)

with q1:

    st.metric(
        "Overall Cell Completeness",
        format_value(
            overall_completeness,
            1,
            "%",
        ),
    )

with q2:

    st.metric(
        "Missing Cells",
        f"{missing_cells:,}",
    )

with q3:

    st.metric(
        "Columns With Missing Values",
        f"{columns_with_missing:,}",
    )

with q4:

    st.metric(
        "Complete Cells",
        f"{complete_cells:,}",
    )


missing_chart_data = quality_df[
    quality_df["Missing_Values"] > 0
].copy()

if not missing_chart_data.empty:

    missing_fig = px.bar(
        missing_chart_data.sort_values(
            "Missing_Percentage"
        ),
        x="Missing_Percentage",
        y="Column",
        orientation="h",
        color="Missing_Percentage",
        color_continuous_scale=[
            colors[1],
            colors[0],
        ],
        title="Missing Values by Dataset Column",
        hover_data={
            "Missing_Values": True,
            "Complete_Values": True,
            "Missing_Percentage": ":.2f",
        },
    )

    missing_fig.update_layout(
        height=max(
            460,
            len(missing_chart_data) * 24,
        ),
        coloraxis_showscale=False,
        xaxis_title="Missing Values (%)",
        yaxis_title="",
    )

    render_chart(
        missing_fig,
        key="settings_missing_values",
    )

else:

    st.success(
        "No missing values were found in "
        "the processed dataset."
    )


st.dataframe(
    quality_df.round(2),
    use_container_width=True,
    hide_index=True,
    height=420,
)

render_insight(
    "Missing values are retained where information "
    "cannot be reliably inferred. Analyses that require "
    "specific fields exclude records missing those fields. "
    "Derived columns may inherit missing values from "
    "their source variables.",
    label="Data Quality Interpretation",
)

st.divider()


render_section(
    "Analytical Data Coverage",
    "Check how many injury records can contribute "
    "to the main research analyses."
)

coverage_fields = {
    "Injury Date": ["Injury_Date"],
    "Return Date": ["Return_Date"],
    "Recovery Duration": ["Recovery_Days"],
    "Age and Recovery": [
        "Age",
        "Recovery_Days",
    ],
    "Player Rating Comparison": [
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
    ],
    "Goal Difference Comparison": [
        "Before_Avg_GD",
        "During_Avg_GD",
        "Team_Performance_Drop",
    ],
    "Points Per Match Comparison": [
        "Before_PPM",
        "During_PPM",
        "Points_Per_Match_Drop",
    ],
}

coverage_rows = []

for analysis_name, required_columns in coverage_fields.items():

    valid_count = int(
        cleaned_df[required_columns]
        .notna()
        .all(axis=1)
        .sum()
    )

    coverage_rows.append({
        "Analysis": analysis_name,
        "Valid_Records": valid_count,
        "Missing_Required_Fields": (
            len(cleaned_df) - valid_count
        ),
        "Coverage_Percentage": (
            valid_count / max(len(cleaned_df), 1) * 100
        ),
    })


coverage_df = pd.DataFrame(coverage_rows)

coverage_fig = px.bar(
    coverage_df.sort_values(
        "Coverage_Percentage"
    ),
    x="Coverage_Percentage",
    y="Analysis",
    orientation="h",
    color="Coverage_Percentage",
    color_continuous_scale=[
        colors[1],
        colors[0],
    ],
    title="Coverage of Key Research Variables",
)

coverage_fig.update_layout(
    coloraxis_showscale=False,
    xaxis_title="Records With Complete Required Fields (%)",
    yaxis_title="",
    xaxis_range=[0, 105],
)

render_chart(
    coverage_fig,
    key="settings_analytical_coverage",
)

st.dataframe(
    coverage_df.round(2),
    use_container_width=True,
    hide_index=True,
    height=290,
)

st.caption(
    "Coverage is based on the complete processed dataset, "
    "not the currently filtered selection. Some analyses "
    "also apply minimum sampled-match requirements."
)

st.divider()


render_section(
    "Date and Recovery Validation",
    "Review date completeness and recovery-duration "
    "consistency after preprocessing."
)

injury_dates = pd.to_datetime(
    cleaned_df["Injury_Date"],
    errors="coerce",
)

return_dates = pd.to_datetime(
    cleaned_df["Return_Date"],
    errors="coerce",
)

recovery_values = pd.to_numeric(
    cleaned_df["Recovery_Days"],
    errors="coerce",
)

missing_injury_dates = int(
    injury_dates.isna().sum()
)

missing_return_dates = int(
    return_dates.isna().sum()
)

missing_recovery = int(
    recovery_values.isna().sum()
)

negative_recovery = int(
    recovery_values.lt(0).sum()
)

negative_date_intervals = int(
    (
        return_dates.notna()
        & injury_dates.notna()
        & (return_dates < injury_dates)
    ).sum()
)

date_quality = pd.DataFrame({
    "Validation Check": [
        "Missing Injury Dates",
        "Missing Return Dates",
        "Missing Recovery Durations",
        "Negative Recovery Durations",
        "Return Date Before Injury Date",
    ],
    "Affected Records": [
        missing_injury_dates,
        missing_return_dates,
        missing_recovery,
        negative_recovery,
        negative_date_intervals,
    ],
})

st.dataframe(
    date_quality,
    use_container_width=True,
    hide_index=True,
    height=220,
)

if negative_date_intervals > 0 or negative_recovery > 0:

    st.warning(
        "Some processed records contain inconsistent "
        "recovery durations or date ordering. "
        "Review these records before interpreting "
        "recovery statistics."
    )

else:

    st.success(
        "No negative recovery durations or reversed "
        "injury/return date intervals were detected "
        "in the processed dataset."
    )

st.divider()


render_section(
    "Data Types & Column Explorer",
    "Inspect the structure and values of "
    "individual dataset columns."
)

column_options = sorted(
    cleaned_df.columns.tolist()
)

selected_column = st.selectbox(
    "Select a Dataset Column",
    options=column_options,
    key="settings_column_selector",
)

column_series = cleaned_df[selected_column]

column_left, column_right = st.columns(2)

with column_left:

    st.metric(
        "Column Data Type",
        str(column_series.dtype),
    )

    st.metric(
        "Unique Non-Missing Values",
        int(column_series.nunique(dropna=True)),
    )

with column_right:

    st.metric(
        "Complete Values",
        int(column_series.notna().sum()),
    )

    st.metric(
        "Missing Values",
        int(column_series.isna().sum()),
    )


if pd.api.types.is_numeric_dtype(column_series):

    numeric_values = pd.to_numeric(
        column_series,
        errors="coerce",
    ).dropna()

    if not numeric_values.empty:

        distribution_fig = px.histogram(
            x=numeric_values,
            nbins=30,
            color_discrete_sequence=[colors[0]],
            title=f"Distribution of {selected_column}",
        )

        distribution_fig.update_layout(
            xaxis_title=selected_column,
            yaxis_title="Record Count",
        )

        render_chart(
            distribution_fig,
            key="settings_column_distribution",
        )

else:

    value_counts = (
        column_series.astype("string")
        .fillna("Missing")
        .value_counts()
        .head(15)
        .reset_index()
    )

    value_counts.columns = [
        "Value",
        "Count",
    ]

    if not value_counts.empty:

        value_fig = px.bar(
            value_counts.sort_values("Count"),
            x="Count",
            y="Value",
            orientation="h",
            color="Count",
            color_continuous_scale=[
                colors[1],
                colors[0],
            ],
            title=f"Most Frequent Values: {selected_column}",
        )

        value_fig.update_layout(
            coloraxis_showscale=False,
            xaxis_title="Records",
            yaxis_title="",
        )

        render_chart(
            value_fig,
            key="settings_column_values",
        )

st.divider()


render_section(
    "Interactive Dataset Explorer",
    "Search, filter, and inspect individual football "
    "injury records."
)

search_query = st.text_input(
    "Search Records",
    placeholder=(
        "Search by player, club, season, "
        "position, or injury type..."
    ),
    key="settings_data_search",
)

explorer_columns = st.multiselect(
    "Choose Columns to Display",
    options=cleaned_df.columns.tolist(),
    default=[
        "Injury_ID",
        "Player",
        "Club",
        "Season",
        "Position",
        "Age",
        "Injury_Type",
        "Recovery_Days",
        "Rating_Change",
        "Team_Performance_Drop",
    ],
    key="settings_explorer_columns",
)

explorer_df = df.copy()

search_columns = [
    "Player",
    "Club",
    "Season",
    "Position",
    "Injury_Type",
]

if search_query.strip():

    search_mask = pd.Series(
        False,
        index=explorer_df.index,
    )

    for column in search_columns:

        search_mask = (
            search_mask
            | explorer_df[column]
            .astype("string")
            .str.contains(
                search_query.strip(),
                case=False,
                regex=False,
                na=False,
            )
        )

    explorer_df = explorer_df[
        search_mask
    ].copy()


sort_column = st.selectbox(
    "Sort Records By",
    options=cleaned_df.columns.tolist(),
    index=cleaned_df.columns.get_loc("Player"),
    key="settings_sort_column",
)

descending = st.toggle(
    "Sort Descending",
    value=False,
    key="settings_sort_descending",
)

explorer_df = explorer_df.sort_values(
    sort_column,
    ascending=not descending,
    na_position="last",
)

maximum_rows = max(
    1,
    min(len(explorer_df), 500)
)

display_limit = st.number_input(
    "Maximum Rows to Display",
    min_value=1,
    max_value=500,
    value=100,
    step=25,
    key="settings_display_rows",
)

st.caption(
    f"Search results: {len(explorer_df):,} records. "
    f"Displaying up to {display_limit:,} records."
)

if explorer_columns:

    st.dataframe(
        explorer_df[explorer_columns].head(
            display_limit
        ),
        use_container_width=True,
        hide_index=True,
        height=450,
    )

else:

    st.info(
        "Select at least one column to display "
        "the dataset explorer."
    )

st.divider()


render_section(
    "Dataset Download Center",
    "Export raw, processed, filtered, or "
    "search-result datasets as CSV files."
)

download_col1, download_col2, download_col3 = st.columns(3)

with download_col1:

    with st.container(border=True):

        st.markdown("#### Original Dataset")

        st.caption(
            f"{len(raw_df):,} records | "
            f"{len(raw_df.columns):,} columns"
        )

        render_download(
            raw_df,
            filename="footlens_original_dataset.csv",
            label="Download Raw CSV",
            key="settings_download_raw",
        )

with download_col2:

    with st.container(border=True):

        st.markdown("#### Processed Dataset")

        st.caption(
            f"{len(cleaned_df):,} records | "
            f"{len(cleaned_df.columns):,} columns"
        )

        render_download(
            cleaned_df,
            filename="footlens_processed_dataset.csv",
            label="Download Processed CSV",
            key="settings_download_processed",
        )

with download_col3:

    with st.container(border=True):

        st.markdown("#### Filtered Dataset")

        st.caption(
            f"{len(df):,} records | "
            f"{len(df.columns):,} columns"
        )

        render_download(
            df,
            filename="footlens_filtered_dataset.csv",
            label="Download Filtered CSV",
            key="settings_download_filtered",
        )


if not explorer_df.empty:

    render_download(
        explorer_df,
        filename="footlens_search_results.csv",
        label="Download Current Search Results",
        key="settings_download_search",
    )

st.divider()


render_section(
    "Data Processing Documentation",
    "Understand how FootLens prepares and "
    "interprets football injury records."
)

with st.expander(
    "Dataset Cleaning and Feature Engineering",
    expanded=True,
):

    st.markdown(
        """
        **1. Data loading**

        The original football injury dataset is loaded
        from the project's `data` directory.

        **2. Data standardization**

        The preprocessing module standardizes relevant
        categorical fields and converts numerical values
        into appropriate data types.

        **3. Date processing**

        Injury and return dates are converted into
        datetime values where valid.

        **4. Recovery duration**

        Recovery duration represents the recorded
        number of days associated with a player's
        injury and return.

        **5. Player performance comparison**

        Player rating change is calculated as:

        `Rating Change = After Rating - Before Rating`

        **6. Team performance comparison**

        Observed goal-difference decline is calculated as:

        `Performance Drop = Before Average GD - During Average GD`

        **7. Points per match**

        Match points follow the standard football
        scoring system:

        `Win = 3 points | Draw = 1 point | Loss = 0 points`

        **8. Analytical datasets**

        Individual visualizations use the records
        with the fields required for that analysis.
        """
    )


with st.expander(
    "Statistical Interpretation and Limitations"
):

    st.markdown(
        """
        **Observational comparisons**

        Differences in team or player performance
        are associations found in the dataset.
        They do not establish causation.

        **Missing information**

        Not every injury episode has complete
        injury dates, recovery durations, or
        performance-rating comparisons.

        **Sampled matches**

        The dataset contains limited sampled
        match observations before injury,
        during absence, and after return.

        **Potential repeated matches**

        The same football match may be represented
        in multiple injury episodes.

        **Confounding variables**

        Opponent quality, player minutes, tactical
        changes, squad selection, and injury severity
        may influence observed results.

        **Injury frequency**

        Recorded injury counts are not
        exposure-adjusted injury rates.
        """
    )

st.divider()


render_section(
    "Application Information",
    "Review the technology and analytical "
    "components used in FootLens Analytics."
)

application_info = pd.DataFrame({
    "Component": [
        "Application Framework",
        "Data Processing",
        "Numerical Computing",
        "Interactive Visualizations",
        "Dashboard Architecture",
        "Primary Dataset",
    ],
    "Technology": [
        "Streamlit",
        "Pandas",
        "NumPy",
        "Plotly",
        "Seven-Page Navigation",
        "Football Player Injuries and Team Performance",
    ],
})

st.dataframe(
    application_info,
    use_container_width=True,
    hide_index=True,
    height=250,
)

render_footer()
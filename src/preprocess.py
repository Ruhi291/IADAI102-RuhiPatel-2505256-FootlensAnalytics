# ============================================================
# FOOTLENS ANALYTICS
# Player Injuries and Team Performance Dashboard
#
# Mathematics for AI-II | Summative Assessment
#
# MODULE: Data Preprocessing and Feature Engineering
# ============================================================

from pathlib import Path
import re

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# 1. DATASET LOCATION
# ------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "player_injuries_impact.csv"


# ------------------------------------------------------------
# 2. LOAD RAW DATASET
# ------------------------------------------------------------

def load_raw_data():

    """
    Load the original football injury dataset.
    """

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH,
        na_values=[
            "N.A.",
            "NA",
            "N/A",
            "null",
            "NULL",
            ""
        ]
    )

    return df


# ------------------------------------------------------------
# 3. CLEAN PLAYER RATINGS
# ------------------------------------------------------------

def clean_player_rating(value):

    """
    Convert player ratings into numerical values.

    Examples:
    6.3(S) -> 6.3
    7.4    -> 7.4
    N.A.   -> NaN

    The (S) suffix is retained separately during preprocessing.
    """

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    # Extract a valid numerical rating.
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*(?:\(S\))?",
        value,
        flags=re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return np.nan


# ------------------------------------------------------------
# 4. CLEAN MATCH RESULTS
# ------------------------------------------------------------

def clean_match_result(value):

    """
    Standardize match results into:
    Win, Draw, Loss or Missing.
    """

    if pd.isna(value):
        return np.nan

    value = str(value).strip().lower()

    result_mapping = {
        "win": "Win",
        "w": "Win",
        "draw": "Draw",
        "d": "Draw",
        "lose": "Loss",
        "loss": "Loss",
        "lost": "Loss",
        "l": "Loss"
    }

    return result_mapping.get(value, np.nan)


# ------------------------------------------------------------
# 5. CONVERT RESULTS INTO FOOTBALL POINTS
# ------------------------------------------------------------

def calculate_match_points(result):

    """
    Standard football scoring:
    Win  = 3 points
    Draw = 1 point
    Loss = 0 points
    """

    points_mapping = {
        "Win": 3,
        "Draw": 1,
        "Loss": 0
    }

    return points_mapping.get(result, np.nan)


# ------------------------------------------------------------
# 6. AVERAGE NUMERICAL VALUES
# ------------------------------------------------------------

def calculate_average(df, columns):

    """
    Calculate row-wise means.

    Missing values are ignored.
    Rows with no valid values remain NaN.
    """

    return df[columns].mean(
        axis=1,
        skipna=True
    )


# ------------------------------------------------------------
# 7. MAIN DATA CLEANING FUNCTION
# ------------------------------------------------------------

def preprocess_data(raw_df):

    """
    Clean the dataset and engineer new features
    for football injury impact analysis.
    """

    df = raw_df.copy()

    # --------------------------------------------------------
    # A. REMOVE DUPLICATES
    # --------------------------------------------------------

    df = df.drop_duplicates().reset_index(drop=True)

    # Assign a unique identifier to each injury record.
    df["Injury_ID"] = np.arange(1, len(df) + 1)

    # --------------------------------------------------------
    # B. RENAME IMPORTANT COLUMNS
    # --------------------------------------------------------

    df = df.rename(columns={
        "Name": "Player",
        "Team Name": "Club",
        "FIFA rating": "FIFA_Rating",
        "Injury": "Injury_Type",
        "Date of Injury": "Injury_Date",
        "Date of return": "Return_Date"
    })

    # --------------------------------------------------------
    # C. CLEAN TEXT COLUMNS
    # --------------------------------------------------------

    text_columns = [
        "Player",
        "Club",
        "Position",
        "Season",
        "Injury_Type"
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

        df[column] = df[column].replace(
            ["", "N.A.", "NA", "N/A"],
            pd.NA
        )

    # --------------------------------------------------------
    # D. CLEAN NUMERICAL COLUMNS
    # --------------------------------------------------------

    df["Age"] = pd.to_numeric(
        df["Age"],
        errors="coerce"
    )

    df["FIFA_Rating"] = pd.to_numeric(
        df["FIFA_Rating"],
        errors="coerce"
    )

    # Impossible ages or FIFA ratings are marked missing.
    df.loc[
        ~df["Age"].between(15, 50),
        "Age"
    ] = np.nan

    df.loc[
        ~df["FIFA_Rating"].between(0, 100),
        "FIFA_Rating"
    ] = np.nan

    # --------------------------------------------------------
    # E. CONVERT INJURY DATES
    # --------------------------------------------------------

    df["Injury_Date"] = pd.to_datetime(
        df["Injury_Date"],
        format="%b %d, %Y",
        errors="coerce"
    )

    df["Return_Date"] = pd.to_datetime(
        df["Return_Date"],
        format="%b %d, %Y",
        errors="coerce"
    )

    # --------------------------------------------------------
    # F. CALCULATE RECOVERY DURATION
    # --------------------------------------------------------

    df["Recovery_Days"] = (
        df["Return_Date"] - df["Injury_Date"]
    ).dt.days

    # Negative recovery duration is invalid.
    df.loc[
        df["Recovery_Days"] < 0,
        "Recovery_Days"
    ] = np.nan

    # --------------------------------------------------------
    # G. CREATE TIME-BASED FEATURES
    # --------------------------------------------------------

    df["Injury_Year"] = df["Injury_Date"].dt.year

    df["Injury_Month"] = df["Injury_Date"].dt.month

    df["Injury_Month_Name"] = (
        df["Injury_Date"].dt.strftime("%b")
    )

    df["Injury_Quarter"] = (
        df["Injury_Date"].dt.quarter
    )

    # --------------------------------------------------------
    # H. CREATE RECOVERY DURATION CATEGORIES
    # --------------------------------------------------------

    df["Recovery_Category"] = pd.cut(
        df["Recovery_Days"],
        bins=[-1, 7, 28, 90, np.inf],
        labels=[
            "Short (0-7 days)",
            "Moderate (8-28 days)",
            "Long (29-90 days)",
            "Extended (90+ days)"
        ]
    )

    # These are analytical duration categories,
    # not clinical classifications of injury severity.

    # --------------------------------------------------------
    # I. CLEAN MATCH DATA FOR EACH INJURY PHASE
    # --------------------------------------------------------

    phases = [
        "before_injury",
        "missed_match",
        "after_injury"
    ]

    for phase in phases:

        for match_number in range(1, 4):

            prefix = f"Match{match_number}_{phase}"

            result_col = f"{prefix}_Result"
            gd_col = f"{prefix}_GD"

            # Standardize match result.
            df[result_col] = df[result_col].apply(
                clean_match_result
            )

            # Convert goal difference to numeric.
            df[gd_col] = pd.to_numeric(
                df[gd_col],
                errors="coerce"
            )

            # Calculate match points.
            df[f"{prefix}_Points"] = (
                df[result_col].apply(
                    calculate_match_points
                )
            )

            # Clean individual player ratings.
            if phase != "missed_match":

                rating_col = f"{prefix}_Player_rating"

                # Preserve whether the original rating
                # contained the (S) suffix.
                df[f"{prefix}_S_Flag"] = (
                    df[rating_col]
                    .astype("string")
                    .str.contains(
                        r"\(S\)",
                        case=False,
                        na=False,
                        regex=True
                    )
                )

                df[rating_col] = (
                    df[rating_col].apply(
                        clean_player_rating
                    )
                )

    # --------------------------------------------------------
    # J. CALCULATE PHASE-WISE PERFORMANCE METRICS
    # --------------------------------------------------------

    phase_names = {
        "before_injury": "Before",
        "missed_match": "During",
        "after_injury": "After"
    }

    for phase, label in phase_names.items():

        result_columns = [
            f"Match{i}_{phase}_Result"
            for i in range(1, 4)
        ]

        gd_columns = [
            f"Match{i}_{phase}_GD"
            for i in range(1, 4)
        ]

        points_columns = [
            f"Match{i}_{phase}_Points"
            for i in range(1, 4)
        ]

        # Number of matches with a recorded result.
        df[f"{label}_Matches"] = (
            df[result_columns]
            .notna()
            .sum(axis=1)
        )

        # Total points in sampled matches.
        df[f"{label}_Total_Points"] = (
            df[points_columns]
            .sum(axis=1, min_count=1)
        )

        # Average points per match.
        df[f"{label}_PPM"] = (
            calculate_average(
                df,
                points_columns
            )
        )

        # Average team goal difference.
        df[f"{label}_Avg_GD"] = (
            calculate_average(
                df,
                gd_columns
            )
        )

        # Number of wins.
        df[f"{label}_Wins"] = (
            df[result_columns]
            .eq("Win")
            .sum(axis=1)
        )

        # Number of draws.
        df[f"{label}_Draws"] = (
            df[result_columns]
            .eq("Draw")
            .sum(axis=1)
        )

        # Number of losses.
        df[f"{label}_Losses"] = (
            df[result_columns]
            .eq("Loss")
            .sum(axis=1)
        )

        # Win percentage.
        df[f"{label}_Win_Rate"] = (
            df[f"{label}_Wins"]
            .div(
                df[f"{label}_Matches"].replace(
                    0, np.nan
                )
            )
            .mul(100)
        )

    # --------------------------------------------------------
    # K. CALCULATE PLAYER RATINGS
    # --------------------------------------------------------

    before_rating_columns = [
        f"Match{i}_before_injury_Player_rating"
        for i in range(1, 4)
    ]

    after_rating_columns = [
        f"Match{i}_after_injury_Player_rating"
        for i in range(1, 4)
    ]

    df["Before_Avg_Rating"] = calculate_average(
        df,
        before_rating_columns
    )

    df["After_Avg_Rating"] = calculate_average(
        df,
        after_rating_columns
    )

    df["Rating_Change"] = (
        df["After_Avg_Rating"]
        - df["Before_Avg_Rating"]
    )

    # Positive rating change means an improvement.
    df["Comeback_Status"] = np.select(
        [
            df["Rating_Change"] > 0,
            df["Rating_Change"] < 0,
            df["Rating_Change"] == 0
        ],
        [
            "Improved",
            "Declined",
            "Unchanged"
        ],
        default="Insufficient Data"
    )

    # --------------------------------------------------------
    # L. CALCULATE TEAM PERFORMANCE CHANGE
    # --------------------------------------------------------

    # Positive value means goal difference worsened
    # during the player's absence.
    df["Team_Performance_Drop"] = (
        df["Before_Avg_GD"]
        - df["During_Avg_GD"]
    )

    # Positive value means points per match decreased
    # during the player's absence.
    df["Points_Per_Match_Drop"] = (
        df["Before_PPM"]
        - df["During_PPM"]
    )

    # Difference in win percentage.
    df["Win_Rate_Drop"] = (
        df["Before_Win_Rate"]
        - df["During_Win_Rate"]
    )

    # Change after the player returned.
    df["Team_Recovery_GD"] = (
        df["After_Avg_GD"]
        - df["During_Avg_GD"]
    )

    df["Team_Recovery_PPM"] = (
        df["After_PPM"]
        - df["During_PPM"]
    )

    # --------------------------------------------------------
    # M. CREATE DATA COMPLETENESS FEATURES
    # --------------------------------------------------------

    df["Has_Before_Rating"] = (
        df["Before_Avg_Rating"].notna()
    )

    df["Has_After_Rating"] = (
        df["After_Avg_Rating"].notna()
    )

    df["Has_Complete_Rating_Comparison"] = (
        df["Has_Before_Rating"]
        & df["Has_After_Rating"]
    )

    df["Has_Impact_Comparison"] = (
        df["Before_Matches"].gt(0)
        & df["During_Matches"].gt(0)
        & df["Before_Avg_GD"].notna()
        & df["During_Avg_GD"].notna()
    )

    # --------------------------------------------------------
    # N. FINAL DATA ORGANIZATION
    # --------------------------------------------------------

    df = df.sort_values(
        by=["Injury_Date", "Club", "Player"],
        na_position="last"
    ).reset_index(drop=True)

    return df


# ------------------------------------------------------------
# 8. PLAYER-LEVEL SUMMARY
# ------------------------------------------------------------

def create_player_summary(df):

    """
    Summarize injury records for each player and club.
    """

    summary = (
        df.groupby(
            ["Player", "Club"],
            dropna=False
        )
        .agg(
            Injury_Count=("Injury_ID", "count"),

            Average_Age=("Age", "mean"),

            Average_Recovery_Days=(
                "Recovery_Days", "mean"
            ),

            Average_Before_Rating=(
                "Before_Avg_Rating", "mean"
            ),

            Average_After_Rating=(
                "After_Avg_Rating", "mean"
            ),

            Average_Rating_Change=(
                "Rating_Change", "mean"
            ),

            Average_Team_Impact=(
                "Team_Performance_Drop", "mean"
            )
        )
        .reset_index()
    )

    return summary


# ------------------------------------------------------------
# 9. CLUB-LEVEL SUMMARY
# ------------------------------------------------------------

def create_club_summary(df):

    """
    Calculate injury and performance statistics
    for each football club.
    """

    summary = (
        df.groupby("Club", dropna=False)
        .agg(
            Total_Injuries=("Injury_ID", "count"),

            Unique_Players=("Player", "nunique"),

            Average_Recovery_Days=(
                "Recovery_Days", "mean"
            ),

            Average_Performance_Drop=(
                "Team_Performance_Drop", "mean"
            ),

            Average_PPM_Drop=(
                "Points_Per_Match_Drop", "mean"
            ),

            Average_Rating_Change=(
                "Rating_Change", "mean"
            )
        )
        .reset_index()
    )

    return summary


# ------------------------------------------------------------
# 10. DATA QUALITY REPORT
# ------------------------------------------------------------

def create_data_quality_report(raw_df, cleaned_df):

    """
    Generate a report describing data quality
    and preprocessing results.
    """

    report = {
        "Original_Rows": len(raw_df),

        "Cleaned_Rows": len(cleaned_df),

        "Duplicate_Rows_Removed": (
            len(raw_df) - len(cleaned_df)
        ),

        "Missing_Injury_Dates": (
            cleaned_df["Injury_Date"].isna().sum()
        ),

        "Missing_Return_Dates": (
            cleaned_df["Return_Date"].isna().sum()
        ),

        "Missing_Recovery_Durations": (
            cleaned_df["Recovery_Days"].isna().sum()
        ),

        "Valid_Rating_Comparisons": (
            cleaned_df[
                "Has_Complete_Rating_Comparison"
            ].sum()
        ),

        "Valid_Impact_Comparisons": (
            cleaned_df[
                "Has_Impact_Comparison"
            ].sum()
        )
    }

    return pd.DataFrame(
        list(report.items()),
        columns=["Quality_Metric", "Value"]
    )


# ------------------------------------------------------------
# 11. LOAD AND PREPROCESS DATA
# ------------------------------------------------------------

def load_and_preprocess():

    """
    Main function used by the Streamlit application.
    """

    raw_df = load_raw_data()

    cleaned_df = preprocess_data(raw_df)

    return cleaned_df


# ------------------------------------------------------------
# 12. RUN MODULE DIRECTLY FOR VERIFICATION
# ------------------------------------------------------------

if __name__ == "__main__":

    raw_data = load_raw_data()

    cleaned_data = preprocess_data(raw_data)

    print("\nFOOTLENS ANALYTICS")
    print("=" * 50)

    print(
        "\nOriginal dataset shape:",
        raw_data.shape
    )

    print(
        "Cleaned dataset shape:",
        cleaned_data.shape
    )

    print("\nPreview of cleaned records:")

    display_columns = [
        "Player",
        "Club",
        "Injury_Type",
        "Recovery_Days",
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
        "Team_Performance_Drop"
    ]

    print(
        cleaned_data[display_columns]
        .head()
        .to_string(index=False)
    )

    print("\nData Quality Report:")

    print(
        create_data_quality_report(
            raw_data,
            cleaned_data
        ).to_string(index=False)
    )

    print("\nPreprocessing completed successfully!")
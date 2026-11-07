import numpy as np
import pandas as pd


def get_dashboard_kpis(df):
    return {
        "total_injuries": len(df),
        "total_players": df["Player"].nunique(),
        "total_clubs": df["Club"].nunique(),
        "total_seasons": df["Season"].nunique(),
        "average_recovery": df["Recovery_Days"].mean(),
        "median_recovery": df["Recovery_Days"].median(),
        "average_performance_drop": df["Team_Performance_Drop"].mean(),
        "average_rating_change": df["Rating_Change"].mean(),
        "valid_impact_records": int(df["Team_Performance_Drop"].notna().sum()),
        "valid_rating_records": int(df["Rating_Change"].notna().sum())
    }


def get_most_injured_players(df, top_n=10):
    return (
        df.groupby(["Player", "Club"], dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Average_Rating_Change=("Rating_Change", "mean")
        )
        .reset_index()
        .sort_values(
            ["Injury_Count", "Player"],
            ascending=[False, True]
        )
        .head(top_n)
    )


def get_club_injury_rankings(df):
    return (
        df.groupby("Club", dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Players_Affected=("Player", "nunique"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Average_Impact=("Team_Performance_Drop", "mean"),
            Average_PPM_Drop=("Points_Per_Match_Drop", "mean")
        )
        .reset_index()
        .sort_values("Injury_Count", ascending=False)
    )


def get_top_impact_injuries(
    df,
    top_n=10,
    metric="Team_Performance_Drop",
    min_matches=1
):
    valid = df[
        (df["Before_Matches"] >= min_matches)
        & (df["During_Matches"] >= min_matches)
    ].dropna(subset=[metric])

    return (
        valid.sort_values(metric, ascending=False)
        .head(top_n)
        .copy()
    )


def get_comeback_leaderboard(df, top_n=10):
    return (
        df.dropna(
            subset=[
                "Before_Avg_Rating",
                "After_Avg_Rating",
                "Rating_Change"
            ]
        )
        .sort_values("Rating_Change", ascending=False)
        .head(top_n)
        .copy()
    )


def get_injury_heatmap(df):
    valid = df.dropna(subset=["Club", "Injury_Month"])

    if valid.empty:
        return pd.DataFrame(columns=range(1, 13), dtype=int)

    heatmap = pd.pivot_table(
        valid,
        index="Club",
        columns="Injury_Month",
        values="Injury_ID",
        aggfunc="count",
        fill_value=0
    )

    return heatmap.reindex(columns=range(1, 13), fill_value=0)


def get_match_result_comparison(df):
    records = []

    for phase in ["Before", "During", "After"]:
        for result in ["Wins", "Draws", "Losses"]:
            records.append({
                "Phase": phase,
                "Result": result,
                "Count": int(df[f"{phase}_{result}"].sum())
            })

    return pd.DataFrame(records)


def get_match_performance_summary(df):
    records = []

    for phase in ["Before", "During", "After"]:
        wins = df[f"{phase}_Wins"].sum()
        draws = df[f"{phase}_Draws"].sum()
        losses = df[f"{phase}_Losses"].sum()
        total = wins + draws + losses

        records.append({
            "Phase": phase,
            "Wins": int(wins),
            "Draws": int(draws),
            "Losses": int(losses),
            "Sampled_Matches": int(total),
            "Win_Rate": wins / total * 100 if total else np.nan,
            "Points_Per_Match": (3 * wins + draws) / total if total else np.nan
        })

    return pd.DataFrame(records)


def get_injury_type_impact(df):
    return (
        df.groupby("Injury_Type", dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Average_Performance_Drop=("Team_Performance_Drop", "mean"),
            Average_Rating_Change=("Rating_Change", "mean"),
            Valid_Impact_Records=("Team_Performance_Drop", "count")
        )
        .reset_index()
        .sort_values("Injury_Count", ascending=False)
    )


def get_age_correlations(df):
    comparisons = {
        "Age vs Recovery Duration": "Recovery_Days",
        "Age vs Player Rating Change": "Rating_Change",
        "Age vs Team Performance Drop": "Team_Performance_Drop"
    }

    records = []

    for label, column in comparisons.items():
        valid = df[["Age", column]].dropna()

        if (
            len(valid) >= 3
            and valid["Age"].nunique() > 1
            and valid[column].nunique() > 1
        ):
            correlation = valid["Age"].corr(valid[column])
        else:
            correlation = np.nan

        records.append({
            "Comparison": label,
            "Pearson_Correlation": correlation,
            "Sample_Size": len(valid)
        })

    return pd.DataFrame(records)


def get_recovery_statistics(df):
    valid = df["Recovery_Days"].dropna()

    if valid.empty:
        return {
            "mean": np.nan,
            "median": np.nan,
            "minimum": np.nan,
            "maximum": np.nan,
            "std": np.nan
        }

    return {
        "mean": valid.mean(),
        "median": valid.median(),
        "minimum": valid.min(),
        "maximum": valid.max(),
        "std": valid.std()
    }


def get_club_comparison(df):
    return (
        df.groupby("Club", dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Before_GD=("Before_Avg_GD", "mean"),
            During_GD=("During_Avg_GD", "mean"),
            After_GD=("After_Avg_GD", "mean"),
            Before_PPM=("Before_PPM", "mean"),
            During_PPM=("During_PPM", "mean"),
            After_PPM=("After_PPM", "mean"),
            Average_Rating_Change=("Rating_Change", "mean"),
            Median_Recovery=("Recovery_Days", "median"),
            Average_Impact=("Team_Performance_Drop", "mean"),
            Average_PPM_Drop=("Points_Per_Match_Drop", "mean")
        )
        .reset_index()
    )


def get_monthly_injury_trends(df):
    return (
        df.dropna(subset=["Injury_Year", "Injury_Month"])
        .groupby(["Injury_Year", "Injury_Month"])
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean")
        )
        .reset_index()
        .sort_values(["Injury_Year", "Injury_Month"])
    )


def get_player_performance_timeline(df, player):
    player_df = df[df["Player"] == player].copy()
    records = []

    for _, row in player_df.iterrows():
        for phase, column in [
            ("Before Injury", "Before_Avg_Rating"),
            ("After Injury", "After_Avg_Rating")
        ]:
            records.append({
                "Injury_ID": row["Injury_ID"],
                "Player": row["Player"],
                "Club": row["Club"],
                "Injury_Type": row["Injury_Type"],
                "Injury_Date": row["Injury_Date"],
                "Phase": phase,
                "Average_Rating": row[column]
            })

    return pd.DataFrame(
        records,
        columns=[
            "Injury_ID",
            "Player",
            "Club",
            "Injury_Type",
            "Injury_Date",
            "Phase",
            "Average_Rating"
        ]
    )


def get_position_analysis(df):
    return (
        df.groupby("Position", dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Players_Affected=("Player", "nunique"),
            Average_Recovery=("Recovery_Days", "mean"),
            Average_Impact=("Team_Performance_Drop", "mean"),
            Average_Rating_Change=("Rating_Change", "mean")
        )
        .reset_index()
        .sort_values("Injury_Count", ascending=False)
    )


def get_seasonal_analysis(df):
    return (
        df.groupby("Season", dropna=False)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Unique_Players=("Player", "nunique"),
            Average_Recovery=("Recovery_Days", "mean"),
            Average_Impact=("Team_Performance_Drop", "mean")
        )
        .reset_index()
        .sort_values("Season")
    )


def get_recovery_categories(df):
    return (
        df.groupby("Recovery_Category", observed=True)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Rating_Change=("Rating_Change", "mean"),
            Average_Impact=("Team_Performance_Drop", "mean")
        )
        .reset_index()
    )


def generate_manager_insights(df):
    if df.empty:
        return ["No records match the selected filters."]

    insights = []

    club_counts = df["Club"].value_counts()

    if not club_counts.empty:
        insights.append(
            f"{club_counts.index[0]} has the most recorded injury episodes "
            f"({club_counts.iloc[0]}) in the selected data."
        )

    valid_impact = df.dropna(subset=["Team_Performance_Drop"])

    if not valid_impact.empty:
        top = valid_impact.loc[
            valid_impact["Team_Performance_Drop"].idxmax()
        ]

        insights.append(
            f"The largest observed goal-difference decline is associated "
            f"with {top['Player']} ({top['Club']}), with a change of "
            f"{top['Team_Performance_Drop']:.2f} goals per sampled match."
        )

    valid_ratings = df.dropna(subset=["Rating_Change"])

    if not valid_ratings.empty:
        percentage = valid_ratings["Rating_Change"].gt(0).mean() * 100

        insights.append(
            f"{percentage:.1f}% of injury episodes with valid rating "
            f"comparisons show a higher average post-injury rating."
        )

    recovery = df["Recovery_Days"].dropna()

    if not recovery.empty:
        insights.append(
            f"The median recorded recovery duration is "
            f"{recovery.median():.0f} days."
        )

    insights.append(
        "The analysis uses sampled match observations. "
        "Associations do not establish causation."
    )

    return insights


def get_data_coverage(df):
    fields = {
        "Injury Date": "Injury_Date",
        "Return Date": "Return_Date",
        "Recovery Duration": "Recovery_Days",
        "Player Rating Comparison": "Rating_Change",
        "Team Performance Impact": "Team_Performance_Drop"
    }

    records = []
    total = len(df)

    for label, column in fields.items():
        available = int(df[column].notna().sum())

        records.append({
            "Metric": label,
            "Available_Records": available,
            "Missing_Records": total - available,
            "Coverage_Percent": available / total * 100 if total else 0
        })

    return pd.DataFrame(records)


def get_club_battle_summary(df, club_a, club_b):
    selected = df[df["Club"].isin([club_a, club_b])]
    return get_club_comparison(selected)


def get_recovery_impact_analysis(df):
    return (
        df.groupby("Recovery_Category", observed=True)
        .agg(
            Injury_Count=("Injury_ID", "count"),
            Average_Recovery=("Recovery_Days", "mean"),
            Average_Rating_Change=("Rating_Change", "mean"),
            Average_GD_Drop=("Team_Performance_Drop", "mean"),
            Average_PPM_Drop=("Points_Per_Match_Drop", "mean")
        )
        .reset_index()
    )


def get_statistical_summary(df):
    numerical_columns = [
        "Age",
        "FIFA_Rating",
        "Recovery_Days",
        "Before_Avg_Rating",
        "After_Avg_Rating",
        "Rating_Change",
        "Team_Performance_Drop",
        "Points_Per_Match_Drop"
    ]

    return (
        df[numerical_columns]
        .describe()
        .transpose()
        .reset_index()
        .rename(columns={"index": "Metric"})
    )


def get_correlation_matrix(df):
    numerical_columns = [
        "Age",
        "FIFA_Rating",
        "Recovery_Days",
        "Rating_Change",
        "Team_Performance_Drop",
        "Points_Per_Match_Drop"
    ]

    return df[numerical_columns].corr()


import unittest

import numpy as np
import pandas as pd

from src.preprocess import (
    load_raw_data,
    preprocess_data,
    clean_player_rating,
    clean_match_result,
    calculate_match_points,
    create_player_summary,
    create_club_summary,
    create_data_quality_report
)

from src.metrics import (
    get_dashboard_kpis,
    get_age_correlations,
    get_injury_heatmap
)


class TestFootLensProcessing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Load the actual dataset once for all tests.
        """
        cls.raw_df = load_raw_data()
        cls.clean_df = preprocess_data(cls.raw_df)

    # --------------------------------------------------------
    # TEST 1: DATASET LOADING
    # --------------------------------------------------------

    def test_dataset_loading(self):

        self.assertFalse(self.raw_df.empty)

        self.assertGreater(
            len(self.raw_df),
            0
        )

        self.assertIn(
            "Age",
            self.raw_df.columns
        )

    # --------------------------------------------------------
    # TEST 2: PLAYER RATING CLEANING
    # --------------------------------------------------------

    def test_player_rating_cleaning(self):

        self.assertEqual(
            clean_player_rating("6.3(S)"),
            6.3
        )

        self.assertEqual(
            clean_player_rating("7.5"),
            7.5
        )

        self.assertTrue(
            np.isnan(clean_player_rating("N.A."))
        )

    # --------------------------------------------------------
    # TEST 3: MATCH RESULT STANDARDIZATION
    # --------------------------------------------------------

    def test_match_result_cleaning(self):

        self.assertEqual(
            clean_match_result("W"),
            "Win"
        )

        self.assertEqual(
            clean_match_result("Draw"),
            "Draw"
        )

        self.assertEqual(
            clean_match_result("lost"),
            "Loss"
        )

    # --------------------------------------------------------
    # TEST 4: FOOTBALL POINT CALCULATIONS
    # --------------------------------------------------------

    def test_match_points(self):

        self.assertEqual(
            calculate_match_points("Win"),
            3
        )

        self.assertEqual(
            calculate_match_points("Draw"),
            1
        )

        self.assertEqual(
            calculate_match_points("Loss"),
            0
        )

        self.assertTrue(
            np.isnan(calculate_match_points("Unknown"))
        )

    # --------------------------------------------------------
    # TEST 5: RECOVERY DURATION
    # --------------------------------------------------------

    def test_recovery_duration(self):

        valid = self.clean_df.dropna(
            subset=[
                "Injury_Date",
                "Return_Date",
                "Recovery_Days"
            ]
        )

        self.assertFalse(valid.empty)

        calculated_days = (
            valid["Return_Date"]
            - valid["Injury_Date"]
        ).dt.days

        pd.testing.assert_series_equal(
            valid["Recovery_Days"],
            calculated_days,
            check_names=False,
            check_dtype=False
        )

        self.assertTrue(
            (valid["Recovery_Days"] >= 0).all()
        )

    # --------------------------------------------------------
    # TEST 6: PLAYER RATING CHANGE
    # --------------------------------------------------------

    def test_player_rating_change(self):

        valid = self.clean_df.dropna(
            subset=[
                "Before_Avg_Rating",
                "After_Avg_Rating",
                "Rating_Change"
            ]
        )

        self.assertFalse(valid.empty)

        expected = (
            valid["After_Avg_Rating"]
            - valid["Before_Avg_Rating"]
        )

        np.testing.assert_allclose(
            valid["Rating_Change"],
            expected
        )

    # --------------------------------------------------------
    # TEST 7: TEAM PERFORMANCE DROP
    # --------------------------------------------------------

    def test_team_performance_drop(self):

        valid = self.clean_df.dropna(
            subset=[
                "Before_Avg_GD",
                "During_Avg_GD",
                "Team_Performance_Drop"
            ]
        )

        self.assertFalse(valid.empty)

        expected = (
            valid["Before_Avg_GD"]
            - valid["During_Avg_GD"]
        )

        np.testing.assert_allclose(
            valid["Team_Performance_Drop"],
            expected
        )

    # --------------------------------------------------------
    # TEST 8: PLAYER AND CLUB SUMMARIES
    # --------------------------------------------------------

    def test_summary_generation(self):

        player_summary = create_player_summary(
            self.clean_df
        )

        club_summary = create_club_summary(
            self.clean_df
        )

        self.assertFalse(player_summary.empty)

        self.assertFalse(club_summary.empty)

        self.assertIn(
            "Injury_Count",
            player_summary.columns
        )

        self.assertIn(
            "Total_Injuries",
            club_summary.columns
        )

    # --------------------------------------------------------
    # TEST 9: DATA QUALITY REPORT
    # --------------------------------------------------------

    def test_data_quality_report(self):

        report = create_data_quality_report(
            self.raw_df,
            self.clean_df
        )

        self.assertFalse(report.empty)

        self.assertIn(
            "Quality_Metric",
            report.columns
        )

        self.assertIn(
            "Value",
            report.columns
        )

    # --------------------------------------------------------
    # TEST 10: DASHBOARD METRICS
    # --------------------------------------------------------

    def test_dashboard_metrics(self):

        kpis = get_dashboard_kpis(
            self.clean_df
        )

        self.assertEqual(
            kpis["total_injuries"],
            len(self.clean_df)
        )

        self.assertGreater(
            kpis["total_players"],
            0
        )

        self.assertGreater(
            kpis["total_clubs"],
            0
        )

    # --------------------------------------------------------
    # TEST 11: CORRELATION ANALYSIS
    # --------------------------------------------------------

    def test_correlation_analysis(self):

        correlations = get_age_correlations(
            self.clean_df
        )

        self.assertEqual(
            len(correlations),
            3
        )

        self.assertIn(
            "Pearson_Correlation",
            correlations.columns
        )

        valid_correlations = correlations[
            "Pearson_Correlation"
        ].dropna()

        self.assertTrue(
            valid_correlations.between(-1, 1).all()
        )

    # --------------------------------------------------------
    # TEST 12: INJURY HEATMAP
    # --------------------------------------------------------

    def test_heatmap_generation(self):

        heatmap = get_injury_heatmap(
            self.clean_df
        )

        self.assertEqual(
            heatmap.shape[1],
            12
        )

        self.assertTrue(
            (heatmap.to_numpy() >= 0).all()
        )


if __name__ == "__main__":
    unittest.main()
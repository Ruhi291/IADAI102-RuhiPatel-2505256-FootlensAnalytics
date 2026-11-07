# FOOTLENS ANALYTICS
### Player Injuries and Team Performance Dashboard

## Problem Statement

Player injuries are a major challenge in professional football, affecting team performance, match outcomes, squad availability, and player recovery. Football clubs often struggle to understand how injuries influence overall team performance, which players experience the greatest performance changes after recovery, and whether specific injury patterns occur across clubs and seasons.

Without a centralized analytical platform, identifying these trends and making informed decisions about player rotation, recovery management, and squad planning can be difficult.

**FootLens Analytics** addresses this problem by providing an interactive, data-driven football analytics dashboard that examines the relationship between player injuries, recovery patterns, and team performance.

## App Features

### 1. Home — Football Intelligence Dashboard
- Executive overview of injuries, affected players, clubs, and recovery statistics.
- Interactive injury trends, club rankings, and performance comparisons.
- Key performance indicators and automatically generated managerial insights.

### 2. Injuries — Injury Intelligence
- Animated monthly injury trends with interactive playback controls.
- Football pitch visualization displaying injuries by playing position.
- Injury frequency heatmaps across clubs and months.
- Analysis of common injury types, seasonal trends, and frequently injured players.

### 3. Matches — Team Performance Analysis
- Before-injury, during-absence, and after-return performance comparisons.
- Match outcome analysis covering wins, draws, and losses.
- Goal difference, points-per-match, and win-rate comparisons.
- Rankings of injuries associated with the largest observed team performance declines.
- Individual player absence and match performance exploration.

### 4. Recovery — Player Recovery & Comeback Analysis
- Recovery duration distributions and statistical summaries.
- Analysis of recovery patterns across injury types and playing positions.
- Interactive exploration of player age, recovery duration, and rating changes.
- Comeback leaderboard ranking post-injury rating improvements.
- Individual player recovery histories and before-and-after rating comparisons.

### 5. Club Battle — Head-to-Head Club Comparison
- Interactive comparison between two football clubs.
- Side-by-side injury, recovery, and performance statistics.
- Comparisons of injury categories, playing positions, and seasonal trends.
- Head-to-head performance visualizations and normalized radar charts.
- Data-driven club comparison insights.

### 6. Insights — Research & Statistical Analysis
- Analysis of five key research questions related to football injuries and team performance.
- Descriptive statistics, including mean, median, variance, and standard deviation.
- Pearson and Spearman correlation analysis.
- Interactive statistical visualizations and correlation heatmaps.
- Data aggregation using grouped analysis and pivot tables.
- Automatically generated research findings and interpretations.

### 7. Settings — Dashboard Personalization & Data Management
- Customizable dashboard themes and chart color palettes.
- Adjustable visualization, animation, and analytical preferences.
- Dataset quality and missing-value analysis.
- Interactive dataset explorer with search and sorting options.
- CSV downloads of original, processed, and filtered datasets.

## Solution

**FootLens Analytics** provides a centralized, interactive solution for examining football player injuries and their relationship with team performance.

The application processes football injury and match data using Python and Pandas, calculates meaningful performance and recovery indicators, and presents the results through interactive Streamlit and Plotly visualizations.

By integrating injury analysis, match performance comparisons, player recovery tracking, club benchmarking, and statistical research into a single dashboard, the application enables users to:

- Identify injury episodes associated with significant changes in team performance.
- Compare match outcomes before injuries, during player absence, and after recovery.
- Evaluate player recovery durations and post-injury performance changes.
- Discover injury patterns across clubs, seasons, and playing positions.
- Compare football clubs using relevant injury and performance indicators.
- Explore statistical relationships and generate data-driven insights.

The dashboard supports football analysts, coaches, and team managers in understanding injury-related trends and making more informed decisions about player management, recovery planning, and squad strategy.

All findings are based on observed data and should be interpreted as statistical associations rather than proof of causation.

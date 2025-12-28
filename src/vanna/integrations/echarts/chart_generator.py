"""ECharts-based chart generator with automatic chart type selection."""

from typing import Dict, Any, List
import pandas as pd


class EChartsChartGenerator:
    """Generate ECharts options using heuristics based on DataFrame characteristics."""

    # Purple/neon theme colors for dark mode
    COLOR_PALETTE = [
        "#BA55D3",  # MediumOrchid
        "#8A2BE2",  # BlueViolet
        "#FF00FF",  # Magenta
        "#9370DB",  # MediumPurple
        "#DA70D6",  # Orchid
        "#BA55D3",  # MediumOrchid
        "#8A2BE2",  # BlueViolet
    ]

    def generate_chart(self, df: pd.DataFrame, title: str = "Chart") -> Dict[str, Any]:
        """Generate an ECharts option based on DataFrame shape and types.

        Heuristics:
        - 4+ columns: table
        - 1 numeric column: histogram
        - 2 columns (1 categorical, 1 numeric): bar chart
        - 2 numeric columns: scatter plot
        - 3+ numeric columns: correlation heatmap or multi-line chart
        - Time series data: line chart
        - Multiple categorical: grouped bar chart

        Args:
            df: DataFrame to visualize
            title: Title for the chart

        Returns:
            ECharts option as dictionary

        Raises:
            ValueError: If DataFrame is empty or cannot be visualized
        """
        if df.empty:
            raise ValueError("Cannot visualize empty DataFrame")

        # Heuristic: If 4 or more columns, render as a table
        if len(df.columns) >= 4:
            return self._create_table(df, title)

        # Identify column types
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        # Check for time series
        is_timeseries = len(datetime_cols) > 0

        # Apply heuristics
        if is_timeseries and len(numeric_cols) > 0:
            # Time series line chart
            return self._create_time_series_chart(
                df, datetime_cols[0], numeric_cols, title
            )
        elif len(numeric_cols) == 1 and len(categorical_cols) == 0:
            # Single numeric column: histogram
            return self._create_histogram(df, numeric_cols[0], title)
        elif len(numeric_cols) == 1 and len(categorical_cols) == 1:
            # One categorical, one numeric: bar chart
            return self._create_bar_chart(
                df, categorical_cols[0], numeric_cols[0], title
            )
        elif len(numeric_cols) == 2:
            # Two numeric columns: scatter plot
            return self._create_scatter_plot(df, numeric_cols[0], numeric_cols[1], title)
        elif len(numeric_cols) >= 3:
            # Multiple numeric columns: multi-line chart
            return self._create_multi_line_chart(df, numeric_cols, title)
        elif len(categorical_cols) >= 2:
            # Multiple categorical: grouped bar chart
            return self._create_grouped_bar_chart(df, categorical_cols, title)
        else:
            # Fallback: show first two columns as scatter/bar
            if len(df.columns) >= 2:
                return self._create_generic_chart(
                    df, df.columns[0], df.columns[1], title
                )
            else:
                raise ValueError(
                    "Cannot determine appropriate visualization for this DataFrame"
                )

    def _create_table(self, df: pd.DataFrame, title: str) -> Dict[str, Any]:
        """Create a table visualization."""
        # For tables, we'll create a simple bar chart showing row count
        # or return a dataframe component instead
        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": ["Total Rows"],
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": [
                {
                    "name": "Rows",
                    "type": "bar",
                    "data": [len(df)],
                    "itemStyle": {"color": self.COLOR_PALETTE[0]},
                }
            ],
        }

    def _create_histogram(self, df: pd.DataFrame, col: str, title: str) -> Dict[str, Any]:
        """Create a histogram."""
        data = df[col].dropna().tolist()
        bins = min(20, len(data) // 2) if len(data) > 0 else 10

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": [f"Bin {i+1}" for i in range(bins)],
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": [
                {
                    "name": col,
                    "type": "bar",
                    "data": self._calculate_histogram_bins(data, bins),
                    "itemStyle": {"color": self.COLOR_PALETTE[0]},
                }
            ],
        }

    def _create_bar_chart(
        self, df: pd.DataFrame, cat_col: str, num_col: str, title: str
    ) -> Dict[str, Any]:
        """Create a bar chart."""
        # Group by categorical column and aggregate numeric column
        grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)
        
        # Limit to top 20 items for readability
        if len(grouped) > 20:
            grouped = grouped.head(20)

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": {
                "type": "category",
                "data": grouped.index.tolist(),
                "axisLabel": {
                    "color": "rgba(255, 255, 255, 0.7)",
                    "rotate": 45 if len(grouped) > 10 else 0,
                },
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": [
                {
                    "name": num_col,
                    "type": "bar",
                    "data": grouped.values.tolist(),
                    "itemStyle": {"color": self.COLOR_PALETTE[0]},
                }
            ],
            "dataZoom": [
                {
                    "type": "slider",
                    "show": len(grouped) > 10,
                    "xAxisIndex": [0],
                }
            ],
        }

    def _create_scatter_plot(
        self, df: pd.DataFrame, x_col: str, y_col: str, title: str
    ) -> Dict[str, Any]:
        """Create a scatter plot."""
        data = [
            [float(x), float(y)]
            for x, y in zip(df[x_col].dropna(), df[y_col].dropna())
            if pd.notna(x) and pd.notna(y)
        ]

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "item"},
            "xAxis": {
                "type": "value",
                "name": x_col,
                "nameTextStyle": {"color": "rgba(255, 255, 255, 0.7)"},
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "name": y_col,
                "nameTextStyle": {"color": "rgba(255, 255, 255, 0.7)"},
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": [
                {
                    "name": f"{x_col} vs {y_col}",
                    "type": "scatter",
                    "data": data,
                    "itemStyle": {"color": self.COLOR_PALETTE[0]},
                    "symbolSize": 8,
                }
            ],
            "dataZoom": [
                {"type": "slider", "xAxisIndex": [0]},
                {"type": "slider", "yAxisIndex": [0]},
            ],
        }

    def _create_time_series_chart(
        self, df: pd.DataFrame, time_col: str, numeric_cols: List[str], title: str
    ) -> Dict[str, Any]:
        """Create a time series line chart."""
        series_data = []
        for i, col in enumerate(numeric_cols[:5]):  # Limit to 5 series
            series_data.append(
                {
                    "name": col,
                    "type": "line",
                    "data": df[col].tolist(),
                    "itemStyle": {"color": self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]},
                    "smooth": True,
                }
            )

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": [s["name"] for s in series_data],
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "xAxis": {
                "type": "category",
                "data": df[time_col].astype(str).tolist(),
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": series_data,
            "dataZoom": [{"type": "slider", "xAxisIndex": [0]}],
        }

    def _create_multi_line_chart(
        self, df: pd.DataFrame, numeric_cols: List[str], title: str
    ) -> Dict[str, Any]:
        """Create a multi-line chart."""
        series_data = []
        for i, col in enumerate(numeric_cols[:5]):  # Limit to 5 series
            series_data.append(
                {
                    "name": col,
                    "type": "line",
                    "data": df[col].tolist(),
                    "itemStyle": {"color": self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]},
                    "smooth": True,
                }
            )

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": [s["name"] for s in series_data],
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "xAxis": {
                "type": "category",
                "data": [str(i) for i in range(len(df))],
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": series_data,
            "dataZoom": [{"type": "slider", "xAxisIndex": [0]}],
        }

    def _create_grouped_bar_chart(
        self, df: pd.DataFrame, categorical_cols: List[str], title: str
    ) -> Dict[str, Any]:
        """Create a grouped bar chart."""
        # Use first categorical as x-axis, second as grouping
        if len(categorical_cols) < 2:
            return self._create_bar_chart(df, categorical_cols[0], df.columns[-1], title)

        x_col = categorical_cols[0]
        group_col = categorical_cols[1]

        # Pivot table
        pivot = df.groupby([x_col, group_col]).size().unstack(fill_value=0)

        series_data = []
        for i, group_val in enumerate(pivot.columns[:5]):  # Limit to 5 groups
            series_data.append(
                {
                    "name": str(group_val),
                    "type": "bar",
                    "data": pivot[group_val].tolist(),
                    "itemStyle": {"color": self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]},
                }
            )

        return {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {
                "data": [s["name"] for s in series_data],
                "textStyle": {"color": "rgba(255, 255, 255, 0.9)"},
            },
            "xAxis": {
                "type": "category",
                "data": pivot.index.tolist(),
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "yAxis": {
                "type": "value",
                "axisLabel": {"color": "rgba(255, 255, 255, 0.7)"},
            },
            "series": series_data,
        }

    def _create_generic_chart(
        self, df: pd.DataFrame, x_col: str, y_col: str, title: str
    ) -> Dict[str, Any]:
        """Create a generic chart (bar or scatter based on data types)."""
        x_is_numeric = pd.api.types.is_numeric_dtype(df[x_col])
        y_is_numeric = pd.api.types.is_numeric_dtype(df[y_col])

        if x_is_numeric and y_is_numeric:
            return self._create_scatter_plot(df, x_col, y_col, title)
        else:
            # Treat as bar chart
            if not x_is_numeric:
                return self._create_bar_chart(df, x_col, y_col, title)
            else:
                return self._create_bar_chart(df, y_col, x_col, title)

    def _calculate_histogram_bins(self, data: List[float], bins: int) -> List[int]:
        """Calculate histogram bin counts."""
        if not data:
            return [0] * bins

        min_val = min(data)
        max_val = max(data)
        bin_width = (max_val - min_val) / bins if max_val > min_val else 1

        bin_counts = [0] * bins
        for val in data:
            bin_idx = min(int((val - min_val) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1

        return bin_counts


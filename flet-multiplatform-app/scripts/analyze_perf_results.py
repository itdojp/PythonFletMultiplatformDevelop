#!/usr/bin/env python3
"""
Performance Test Results Analyzer

This script analyzes performance test results and generates reports.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set up matplotlib style
plt.style.use("seaborn")
sns.set_palette("husl")


class PerformanceAnalyzer:
    """Analyze performance test results and generate reports."""

    def __init__(self, results_dir: str = "reports/performance"):
        """Initialize the analyzer.

        Args:
            results_dir: Directory containing test results
        """
        self.results_dir = Path(results_dir)
        self.reports_dir = self.results_dir / "reports"
        self.plots_dir = self.reports_dir / "plots"
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create necessary directories."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)

    def load_results(self) -> List[Dict[str, Any]]:
        """Load all test results from the results directory.

        Returns:
            List of test results
        """
        results = []
        for result_file in self.results_dir.glob("*_report.json"):
            try:
                with open(result_file, "r") as f:
                    result = json.load(f)
                    results.append(result)
                logger.info(f"Loaded results from {result_file}")
            except Exception as e:
                logger.error(f"Failed to load {result_file}: {e}")

        return results

    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test results and generate metrics.

        Args:
            results: List of test results

        Returns:
            Dictionary with analysis results
        """
        if not results:
            return {}

        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)

        # Calculate metrics
        analysis = {
            "scenarios": {},
            "summary": {
                "total_tests": len(results),
                "total_requests": df["total_requests"].sum(),
                "total_failures": df["total_failures"].sum(),
                "failure_rate": df["total_failures"].sum()
                / max(1, df["total_requests"].sum()),
                "avg_rps": df["rps"].mean(),
                "avg_response_time": df["response_time"]
                .apply(lambda x: x["p95"])
                .mean(),
            },
        }

        # Per-scenario metrics
        for _, row in df.iterrows():
            analysis["scenarios"][row["scenario"]] = {
                "total_requests": row["total_requests"],
                "total_failures": row["total_failures"],
                "failure_rate": row["failure_rate"],
                "rps": row["rps"],
                "response_time": row["response_time"],
            }

        return analysis

    def generate_plots(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate plots from the analysis.

        Args:
            analysis: Analysis results

        Returns:
            List of paths to generated plot files
        """
        if not analysis or "scenarios" not in analysis:
            return []

        plot_files = []
        scenarios = analysis["scenarios"]

        # Plot 1: Response Time by Scenario
        plt.figure(figsize=(12, 6))
        df_rt = pd.DataFrame(
            {
                "Scenario": list(scenarios.keys()),
                "p95 Response Time (ms)": [
                    s["response_time"]["p95"] for s in scenarios.values()
                ],
            }
        )
        sns.barplot(x="Scenario", y="p95 Response Time (ms)", data=df_rt)
        plt.title("95th Percentile Response Time by Scenario")
        plt.xticks(rotation=45)
        plt.tight_layout()
        rt_plot = self.plots_dir / "response_times.png"
        plt.savefig(rt_plot)
        plt.close()
        plot_files.append(str(rt_plot))

        # Plot 2: Requests per Second by Scenario
        plt.figure(figsize=(12, 6))
        df_rps = pd.DataFrame(
            {
                "Scenario": list(scenarios.keys()),
                "Requests per Second": [s["rps"] for s in scenarios.values()],
            }
        )
        sns.barplot(x="Scenario", y="Requests per Second", data=df_rps)
        plt.title("Requests per Second by Scenario")
        plt.xticks(rotation=45)
        plt.tight_layout()
        rps_plot = self.plots_dir / "rps.png"
        plt.savefig(rps_plot)
        plt.close()
        plot_files.append(str(rps_plot))

        # Plot 3: Failure Rate by Scenario
        plt.figure(figsize=(12, 6))
        df_fr = pd.DataFrame(
            {
                "Scenario": list(scenarios.keys()),
                "Failure Rate (%)": [
                    s["failure_rate"] * 100 for s in scenarios.values()
                ],
            }
        )
        sns.barplot(x="Scenario", y="Failure Rate (%)", data=df_fr)
        plt.axhline(y=1, color="r", linestyle="--", label="1% Threshold")
        plt.title("Failure Rate by Scenario")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        fr_plot = self.plots_dir / "failure_rates.png"
        plt.savefig(fr_plot)
        plt.close()
        plot_files.append(str(fr_plot))

        return plot_files

    def generate_html_report(
        self, analysis: Dict[str, Any], plot_files: List[str]
    ) -> str:
        """Generate an HTML report from the analysis.

        Args:
            analysis: Analysis results
            plot_files: List of paths to plot files

        Returns:
            Path to the generated HTML report
        """
        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(str(Path(__file__).parent / "templates")),
            autoescape=True,
        )

        # Prepare template data
        template_data = {
            "title": "Performance Test Report",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis": analysis,
            "plot_files": [Path(p).name for p in plot_files],
        }

        # Render template
        template = env.get_template("performance_report.html")
        html_content = template.render(**template_data)

        # Save report
        report_file = self.reports_dir / "performance_report.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Generated HTML report: {report_file}")
        return str(report_file)

    def generate_report(self) -> str:
        """Generate a performance test report.

        Returns:
            Path to the generated report
        """
        # Load and analyze results
        results = self.load_results()
        analysis = self.analyze_results(results)

        if not analysis:
            logger.warning("No results to analyze")
            return ""

        # Generate plots
        plot_files = self.generate_plots(analysis)

        # Generate HTML report
        report_file = self.generate_html_report(analysis, plot_files)

        return report_file


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze performance test results")
    parser.add_argument(
        "--results-dir",
        type=str,
        default="reports/performance",
        help="Directory containing test results",
    )
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_args()

    try:
        # Initialize analyzer
        analyzer = PerformanceAnalyzer(args.results_dir)

        # Generate report
        report_file = analyzer.generate_report()

        if report_file:
            print(f"\n=== Report Generated ===")
            print(f"View the report at: {Path(report_file).resolve()}")
        else:
            print("No report was generated.")
            return 1

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

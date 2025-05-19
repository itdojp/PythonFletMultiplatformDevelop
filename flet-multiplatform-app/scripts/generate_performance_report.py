#!/usr/bin/env python3
"""
Performance Report Generator

This script generates HTML reports from performance test results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Configure paths
PROJECT_ROOT = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "performance"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Ensure directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


class PerformanceReportGenerator:
    """Generate performance test reports."""

    def __init__(self, results_dir: Optional[Path] = None):
        """Initialize the report generator.

        Args:
            results_dir: Directory containing test results. Defaults to 'test-results/performance'.
        """
        self.results_dir = results_dir or (
            PROJECT_ROOT / "test-results" / "performance"
        )
        self.report_data: Dict[str, Any] = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "test_suites": [],
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0,
                "execution_time": 0.0,
            },
        }
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True
        )

    def load_test_results(self) -> None:
        """Load test results from JSON files."""
        test_suites = []

        for result_file in self.results_dir.glob("*-metrics.json"):
            try:
                with open(result_file, "r") as f:
                    test_data = json.load(f)
                    test_suites.append(test_data)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load {result_file}: {e}")

        self.report_data["test_suites"] = test_suites
        self._calculate_summary()

    def _calculate_summary(self) -> None:
        """Calculate summary statistics from test results."""
        summary = self.report_data["summary"]

        for suite in self.report_data["test_suites"]:
            summary["total_tests"] += suite.get("total_tests", 0)
            summary["passed_tests"] += suite.get("passed_tests", 0)
            summary["failed_tests"] += suite.get("failed_tests", 0)
            summary["execution_time"] += suite.get("execution_time", 0.0)

        if summary["total_tests"] > 0:
            summary["success_rate"] = (
                summary["passed_tests"] / summary["total_tests"]
            ) * 100

    def generate_charts(self) -> List[Dict[str, str]]:
        """Generate charts from test results.

        Returns:
            List of dictionaries containing chart file paths and titles.
        """
        charts = []

        # Create charts directory
        charts_dir = REPORTS_DIR / "charts"
        charts_dir.mkdir(exist_ok=True)

        # Generate response time chart
        response_times = []
        test_names = []

        for suite in self.report_data["test_suites"]:
            if "metrics" in suite and "response_time_avg" in suite["metrics"]:
                response_times.append(suite["metrics"]["response_time_avg"])
                test_names.append(suite["name"])

        if response_times and len(response_times) == len(test_names):
            plt.figure(figsize=(10, 6))
            plt.bar(test_names, response_times)
            plt.title("Average Response Time by Test")
            plt.xlabel("Test")
            plt.ylabel("Response Time (ms)")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            chart_path = charts_dir / "response_times.png"
            plt.savefig(chart_path)
            plt.close()

            charts.append(
                {
                    "title": "Response Times",
                    "path": str(chart_path.relative_to(REPORTS_DIR)),
                }
            )

        return charts

    def generate_html_report(self) -> str:
        """Generate an HTML report from the test results.

        Returns:
            Path to the generated HTML report.
        """
        # Load the template
        template = self.env.get_template("performance_report.html")

        # Generate charts
        charts = self.generate_charts()

        # Render the template with the test data
        html_content = template.render(
            report=self.report_data,
            charts=charts,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Save the report
        report_path = REPORTS_DIR / "performance_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(report_path)


def main():
    """Main function to generate the performance report."""
    # Create report generator
    report_generator = PerformanceReportGenerator()

    # Load test results
    print("📊 Loading test results...")
    report_generator.load_test_results()

    # Generate HTML report
    print("📝 Generating HTML report...")
    report_path = report_generator.generate_html_report()

    print(f"✅ Report generated successfully: {report_path}")


if __name__ == "__main__":
    main()

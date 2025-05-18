#!/usr/bin/env python3
"""
Performance Test Results Analyzer

This script analyzes the results from performance tests and generates reports.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analyze performance test results and generate reports."""

    def __init__(self, results_dir: str = "results", reports_dir: str = "reports"):
        """Initialize the analyzer with directories for results and reports.
        
        Args:
            results_dir: Directory containing test results
            reports_dir: Directory to save analysis reports
        """
        self.results_dir = Path(results_dir)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_results(self, test_type: str) -> Dict[str, Any]:
        """Load test results from JSON files.
        
        Args:
            test_type: Type of test (load, stress, endurance, scalability)
            
        Returns:
            Dictionary containing test results
        """
        result_file = self.results_dir / f"{test_type}_results.json"
        if not result_file.exists():
            logger.warning(f"No results found for {test_type} test")
            return {}
            
        with open(result_file, 'r') as f:
            return json.load(f)
    
    def load_metrics(self, test_type: str) -> pd.DataFrame:
        """Load metrics from CSV files.
        
        Args:
            test_type: Type of test (load, stress, endurance, scalability)
            
        Returns:
            DataFrame containing test metrics
        """
        metrics_file = self.results_dir / f"{test_type}_metrics.csv"
        if not metrics_file.exists():
            logger.warning(f"No metrics found for {test_type} test")
            return pd.DataFrame()
            
        return pd.read_csv(metrics_file)
    
    def generate_summary(self, test_type: str) -> Dict[str, Any]:
        """Generate a summary of test results.
        
        Args:
            test_type: Type of test (load, stress, endurance, scalability)
            
        Returns:
            Dictionary containing test summary
        """
        results = self.load_results(test_type)
        if not results:
            return {}
            
        metrics = self.load_metrics(test_type)
        
        summary = {
            "test_type": test_type,
            "timestamp": self.timestamp,
            "total_requests": results.get("total_requests", 0),
            "failed_requests": results.get("failed_requests", 0),
            "success_rate": results.get("success_rate", 0),
            "total_rps": results.get("total_rps", 0),
            "avg_response_time": results.get("avg_response_time", 0),
            "median_response_time": results.get("median_response_time", 0),
            "p95_response_time": results.get("p95_response_time", 0),
            "p99_response_time": results.get("p99_response_time", 0),
            "max_response_time": results.get("max_response_time", 0),
            "min_response_time": results.get("min_response_time", 0),
        }
        
        if not metrics.empty:
            summary.update({
                "concurrent_users": metrics["user_count"].max(),
                "total_duration_seconds": metrics["timestamp"].max() - metrics["timestamp"].min(),
                "avg_rps": metrics["current_rps"].mean(),
            })
        
        return summary
    
    def plot_metrics(self, test_type: str) -> None:
        """Generate plots for test metrics.
        
        Args:
            test_type: Type of test (load, stress, endurance, scalability)
        """
        metrics = self.load_metrics(test_type)
        if metrics.empty:
            return
            
        # Create plots directory
        plots_dir = self.reports_dir / "plots"
        plots_dir.mkdir(exist_ok=True)
        
        # Plot response time over time
        plt.figure(figsize=(12, 6))
        plt.plot(metrics["timestamp"], metrics["avg_response_time"], label="Avg Response Time (ms)")
        plt.title(f"{test_type.capitalize()} Test - Response Time Over Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Response Time (ms)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(plots_dir / f"{test_type}_response_time.png")
        plt.close()
        
        # Plot requests per second
        plt.figure(figsize=(12, 6))
        plt.plot(metrics["timestamp"], metrics["current_rps"], label="Requests per Second", color='green')
        plt.title(f"{test_type.capitalize()} Test - Requests per Second")
        plt.xlabel("Time (s)")
        plt.ylabel("Requests/Second")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(plots_dir / f"{test_type}_rps.png")
        plt.close()
        
        # Plot failure rate
        if "fail_ratio" in metrics.columns:
            plt.figure(figsize=(12, 6))
            plt.plot(metrics["timestamp"], metrics["fail_ratio"] * 100, label="Failure Rate (%)", color='red')
            plt.title(f"{test_type.capitalize()} Test - Failure Rate Over Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Failure Rate (%)")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(plots_dir / f"{test_type}_failure_rate.png")
            plt.close()
    
    def generate_html_report(self, test_type: str) -> None:
        """Generate an HTML report for the test results.
        
        Args:
            test_type: Type of test (load, stress, endurance, scalability)
        """
        summary = self.generate_summary(test_type)
        if not summary:
            return
            
        # Generate plots
        self.plot_metrics(test_type)
        
        # Create HTML report
        report_file = self.reports_dir / f"{test_type}_report_{self.timestamp}.html"
        
        # Simple HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{test_type.capitalize()} Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .metrics {{ display: flex; flex-wrap: wrap; gap: 20px; }}
                .metric-card {{ 
                    background: white; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    padding: 15px; 
                    flex: 1; 
                    min-width: 200px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .metric-value {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    color: #2c3e50;
                    margin: 10px 0;
                }}
                .metric-label {{ 
                    color: #7f8c8d; 
                    font-size: 14px;
                }}
                .plots {{ margin-top: 30px; }}
                .plot {{ margin-bottom: 40px; }}
                img {{ max-width: 100%; height: auto; }}
                h1 {{ color: #2c3e50; }}
            </style>
        </head>
        <body>
            <h1>{test_type.capitalize()} Test Report</h1>
            <p>Generated at: {timestamp}</p>
            
            <div class="summary">
                <h2>Test Summary</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{total_requests:,}</div>
                        <div class="metric-label">Total Requests</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: {success_color};">{success_rate:.1f}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_rps:.1f}</div>
                        <div class="metric-label">Requests/Second</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{avg_response_time:.1f} ms</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                </div>
            </div>
            
            <div class="plots">
                <h2>Performance Metrics</h2>
                <div class="plot">
                    <h3>Response Time Over Time</h3>
                    <img src="plots/{test_type}_response_time.png" alt="Response Time">
                </div>
                <div class="plot">
                    <h3>Requests per Second</h3>
                    <img src="plots/{test_type}_rps.png" alt="Requests per Second">
                </div>
                {failure_rate_plot}
            </div>
        </body>
        </html>
        """.format(
            test_type=test_type,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_requests=summary["total_requests"],
            success_rate=summary["success_rate"] * 100,
            success_color="#27ae60" if summary["success_rate"] >= 0.99 else "#e74c3c",
            total_rps=summary["total_rps"],
            avg_response_time=summary["avg_response_time"],
            failure_rate_plot=f'''
                <div class="plot">
                    <h3>Failure Rate Over Time</h3>
                    <img src="plots/{test_type}_failure_rate.png" alt="Failure Rate">
                </div>
            ''' if "fail_ratio" in self.load_metrics(test_type).columns else ""
        )
        
        with open(report_file, 'w') as f:
            f.write(html)
            
        logger.info(f"Generated report: {report_file}")
        return str(report_file)
    
    def analyze_all_tests(self) -> None:
        """Analyze all available test results and generate reports."""
        test_types = ["load", "stress", "endurance", "scalability"]
        
        for test_type in test_types:
            logger.info(f"Analyzing {test_type} test results...")
            try:
                report_path = self.generate_html_report(test_type)
                if report_path:
                    logger.info(f"Generated {test_type} report: {report_path}")
            except Exception as e:
                logger.error(f"Error analyzing {test_type} test: {str(e)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Analyze performance test results")
    parser.add_argument(
        "--results-dir", 
        default="results",
        help="Directory containing test results"
    )
    parser.add_argument(
        "--reports-dir", 
        default="reports",
        help="Directory to save analysis reports"
    )
    parser.add_argument(
        "--test-type",
        choices=["all", "load", "stress", "endurance", "scalability"],
        default="all",
        help="Type of test to analyze"
    )
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer(args.results_dir, args.reports_dir)
    
    if args.test_type == "all":
        analyzer.analyze_all_tests()
    else:
        report_path = analyzer.generate_html_report(args.test_type)
        if report_path:
            print(f"Generated report: {report_path}")


if __name__ == "__main__":
    main()

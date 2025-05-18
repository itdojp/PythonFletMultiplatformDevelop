#!/usr/bin/env python3
"""
Performance Test Results Analyzer

This script analyzes the results from performance tests and generates a summary report.
"""

import json
import os
import statistics
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Configure paths
RESULTS_DIR = Path("test-results/performance")
REPORTS_DIR = Path("reports/performance")
TEMPLATES_DIR = Path("tests/performance/templates")

# Ensure directories exist
for directory in [RESULTS_DIR, REPORTS_DIR, TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

class PerformanceAnalyzer:
    """Analyze performance test results and generate reports."""

    def __init__(self):
        self.results = {
            "load_test": {},
            "stress_test": {},
            "endurance_test": {},
            "scalability_test": {},
        }
        self.metrics = {
            "response_time": [],
            "throughput": [],
            "success_rate": [],
            "error_rate": [],
            "concurrent_users": [],
        }

    def parse_junit_xml(self, xml_file: Path) -> Dict[str, Any]:
        """Parse JUnit XML test results."""
        if not xml_file.exists():
            return {}

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            test_cases = []
            for testcase in root.findall(".//testcase"):
                test_case = {
                    "name": testcase.get("name"),
                    "classname": testcase.get("classname"),
                    "time": float(testcase.get("time", 0)),
                    "status": "passed"
                }

                # Check for failures or errors
                for failure in testcase.findall("failure"):
                    test_case["status"] = "failed"
                    test_case["message"] = failure.get("message")
                    break

                for error in testcase.findall("error"):
                    test_case["status"] = "error"
                    test_case["message"] = error.get("message")
                    break

                test_cases.append(test_case)

            # Calculate summary metrics
            total_tests = len(test_cases)
            passed_tests = len([t for t in test_cases if t["status"] == "passed"])
            failed_tests = len([t for t in test_cases if t["status"] == "failed"])
            error_tests = len([t for t in test_cases if t["status"] == "error"])

            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "test_cases": test_cases,
            }

        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return {}

    def parse_performance_metrics(self, test_type: str) -> Dict[str, Any]:
        """Parse performance metrics from test results."""
        metrics_file = RESULTS_DIR / f"{test_type}-metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file) as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metrics from {metrics_file}: {e}")
        return {}

    def analyze_load_test(self) -> Dict[str, Any]:
        """Analyze load test results."""
        results = {
            "test_cases": self.parse_junit_xml(RESULTS_DIR / "load-test-results.xml"),
            "metrics": self.parse_performance_metrics("load"),
        }
        self.results["load_test"] = results
        return results

    def analyze_stress_test(self) -> Dict[str, Any]:
        """Analyze stress test results."""
        results = {
            "test_cases": self.parse_junit_xml(RESULTS_DIR / "stress-test-results.xml"),
            "metrics": self.parse_performance_metrics("stress"),
        }
        self.results["stress_test"] = results
        return results

    def analyze_endurance_test(self) -> Dict[str, Any]:
        """Analyze endurance test results."""
        results = {
            "test_cases": self.parse_junit_xml(RESULTS_DIR / "endurance-test-results.xml"),
            "metrics": self.parse_performance_metrics("endurance"),
        }
        self.results["endurance_test"] = results
        return results

    def analyze_scalability_test(self) -> Dict[str, Any]:
        """Analyze scalability test results."""
        results = {
            "test_cases": self.parse_junit_xml(RESULTS_DIR / "scalability-test-results.xml"),
            "metrics": self.parse_performance_metrics("scalability"),
        }
        self.results["scalability_test"] = results
        return results

    def generate_plots(self) -> List[Dict[str, str]]:
        """Generate plots for performance metrics."""
        plots = []

        # Create response time plot
        if self.metrics["response_time"] and self.metrics["concurrent_users"]:
            plt.figure(figsize=(10, 6))
            plt.plot(
                self.metrics["concurrent_users"],
                self.metrics["response_time"],
                marker='o',
                label='Response Time (s)'
            )
            plt.title('Response Time vs Concurrent Users')
            plt.xlabel('Concurrent Users')
            plt.ylabel('Response Time (s)')
            plt.grid(True)

            plot_path = REPORTS_DIR / 'response_time_plot.png'
            plt.savefig(plot_path)
            plt.close()
            plots.append({"title": "Response Time vs Load", "path": str(plot_path.relative_to(REPORTS_DIR))})

        # Create throughput plot
        if self.metrics["throughput"] and self.metrics["concurrent_users"]:
            plt.figure(figsize=(10, 6))
            plt.plot(
                self.metrics["concurrent_users"],
                self.metrics["throughput"],
                marker='o',
                color='green',
                label='Throughput (req/s)'
            )
            plt.title('Throughput vs Concurrent Users')
            plt.xlabel('Concurrent Users')
            plt.ylabel('Throughput (req/s)')
            plt.grid(True)

            plot_path = REPORTS_DIR / 'throughput_plot.png'
            plt.savefig(plot_path)
            plt.close()
            plots.append({"title": "Throughput vs Load", "path": str(plot_path.relative_to(REPORTS_DIR))})

        # Create success/error rate plot
        if self.metrics["success_rate"] and self.metrics["concurrent_users"]:
            plt.figure(figsize=(10, 6))
            plt.plot(
                self.metrics["concurrent_users"],
                [r * 100 for r in self.metrics["success_rate"]],
                marker='o',
                color='blue',
                label='Success Rate (%)'
            )

            if self.metrics["error_rate"]:
                plt.plot(
                    self.metrics["concurrent_users"],
                    [r * 100 for r in self.metrics["error_rate"]],
                    marker='x',
                    color='red',
                    label='Error Rate (%)'
                )

            plt.title('Success/Error Rate vs Concurrent Users')
            plt.xlabel('Concurrent Users')
            plt.ylabel('Rate (%)')
            plt.legend()
            plt.grid(True)

            plot_path = REPORTS_DIR / 'success_rate_plot.png'
            plt.savefig(plot_path)
            plt.close()
            plots.append({"title": "Success/Error Rate vs Load", "path": str(plot_path.relative_to(REPORTS_DIR))})

        return plots

    def generate_html_report(self) -> str:
        """Generate an HTML report with test results and metrics."""
        # Load template
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template("report_template.html")

        # Prepare context
        context = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "load_test": self.results["load_test"],
            "stress_test": self.results["stress_test"],
            "endurance_test": self.results["endurance_test"],
            "scalability_test": self.results["scalability_test"],
            "plots": self.generate_plots(),
        }

        # Render template
        report_content = template.render(**context)

        # Save report
        report_path = REPORTS_DIR / "performance_report.html"
        with open(report_path, 'w') as f:
            f.write(report_content)

        return str(report_path)

    def analyze_all(self) -> Dict[str, Any]:
        """Run all analysis methods."""
        print("Analyzing load test results...")
        self.analyze_load_test()

        print("Analyzing stress test results...")
        self.analyze_stress_test()

        print("Analyzing endurance test results...")
        self.analyze_endurance_test()

        print("Analyzing scalability test results...")
        self.analyze_scalability_test()

        print("Generating report...")
        report_path = self.generate_html_report()

        return {
            "report_path": report_path,
            "results": self.results,
        }


def main():
    """Main function to run the analyzer."""
    print("Starting performance test analysis...")

    analyzer = PerformanceAnalyzer()
    results = analyzer.analyze_all()

    print(f"\nAnalysis complete! Report generated at: {results['report_path']}")

    # Print summary
    print("\nTest Summary:")
    print(f"- Load Tests: {results['results']['load_test'].get('test_cases', {}).get('passed_tests', 0)} passed")
    print(f"- Stress Tests: {results['results']['stress_test'].get('test_cases', {}).get('passed_tests', 0)} passed")
    print(f"- Endurance Tests: {results['results']['endurance_test'].get('test_cases', {}).get('passed_tests', 0)} passed")
    print(f"- Scalability Tests: {results['results']['scalability_test'].get('test_cases', {}).get('passed_tests', 0)} passed")


if __name__ == "__main__":
    main()

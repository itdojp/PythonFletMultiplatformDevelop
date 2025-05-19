#!/usr/bin/env python3
"""
Performance Regression Checker

This script compares current performance metrics against baseline metrics
to detect performance regressions.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceRegressionChecker:
    """Check for performance regressions by comparing against baseline metrics."""

    def __init__(self, baseline_path: str, current_path: str, threshold: float = 0.1):
        """Initialize the performance regression checker.

        Args:
            baseline_path: Path to the baseline metrics JSON file
            current_path: Path to the current metrics JSON file
            threshold: Percentage threshold (0-1) for considering a regression
        """
        self.baseline_path = Path(baseline_path)
        self.current_path = Path(current_path)
        self.threshold = threshold
        self.regressions = []

    def load_metrics(self, file_path: Path) -> Dict[str, Any]:
        """Load metrics from a JSON file.

        Args:
            file_path: Path to the metrics JSON file

        Returns:
            Dictionary containing the metrics
        """
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Metrics file not found: {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in metrics file {file_path}: {e}")
            sys.exit(1)

    def check_regression(
        self, baseline: Dict[str, Any], current: Dict[str, Any], prefix: str = ""
    ) -> None:
        """Recursively check for regressions in nested metrics.

        Args:
            baseline: Baseline metrics dictionary
            current: Current metrics dictionary
            prefix: Current path in the metrics hierarchy (for error messages)
        """
        for key, baseline_value in baseline.items():
            current_value = current.get(key)

            if current_value is None:
                logger.warning(f"Key {prefix}{key} not found in current metrics")
                continue

            current_path = f"{prefix}{key}." if prefix else f"{key}."

            # Recursively check nested dictionaries
            if isinstance(baseline_value, dict) and isinstance(current_value, dict):
                self.check_regression(baseline_value, current_value, current_path)
                continue

            # Compare numeric values
            if isinstance(baseline_value, (int, float)) and isinstance(
                current_value, (int, float)
            ):
                if baseline_value == 0:
                    # Avoid division by zero
                    diff_percent = float("inf")
                else:
                    diff_percent = abs(current_value - baseline_value) / baseline_value

                if diff_percent > self.threshold:
                    self.regressions.append(
                        {
                            "metric": prefix + key,
                            "baseline": baseline_value,
                            "current": current_value,
                            "diff_percent": diff_percent * 100,
                        }
                    )

    def generate_report(self) -> str:
        """Generate a human-readable report of performance regressions.

        Returns:
            String containing the formatted report
        """
        if not self.regressions:
            return "✅ No performance regressions detected."

        report = ["⚠️  Performance Regressions Detected ⚠️\n"]
        report.append(f"{'Metric':<40} {'Baseline':>15} {'Current':>15} {'Diff %':>10}")
        report.append("-" * 80)

        for reg in sorted(
            self.regressions, key=lambda x: x["diff_percent"], reverse=True
        ):
            report.append(
                f"{reg['metric']:<40} "
                f"{reg['baseline']:>15.2f} "
                f"{reg['current']:>15.2f} "
                f"{reg['diff_percent']:>9.1f}%"
            )

        return "\n".join(report)

    def run(self) -> bool:
        """Run the performance regression check.

        Returns:
            bool: True if no regressions found, False otherwise
        """
        logger.info(f"Loading baseline metrics from {self.baseline_path}")
        baseline_metrics = self.load_metrics(self.baseline_path)

        logger.info(f"Loading current metrics from {self.current_path}")
        current_metrics = self.load_metrics(self.current_path)

        logger.info("Checking for performance regressions...")
        self.check_regression(baseline_metrics, current_metrics)

        report = self.generate_report()
        print("\n" + report + "\n")

        if self.regressions:
            logger.error(f"Detected {len(self.regressions)} performance regressions")
            return False

        logger.info("No performance regressions detected")
        return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Check for performance regressions.")
    parser.add_argument(
        "--baseline", required=True, help="Path to baseline metrics JSON file"
    )
    parser.add_argument(
        "--current", required=True, help="Path to current metrics JSON file"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="Threshold for considering a regression (0-1, default: 0.1 for 10%)",
    )
    return parser.parse_args()


def main() -> None:
    """Main function."""
    args = parse_args()

    checker = PerformanceRegressionChecker(
        baseline_path=args.baseline, current_path=args.current, threshold=args.threshold
    )

    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

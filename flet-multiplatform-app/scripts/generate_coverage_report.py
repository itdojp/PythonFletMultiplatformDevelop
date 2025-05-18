#!/usr/bin/env python3
"""
Generate comprehensive test coverage reports.

This script generates various test coverage reports including HTML, XML, and console output.
It also provides a summary of the coverage statistics.
"""

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict, Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
COVERAGE_DIR = PROJECT_ROOT / "htmlcov"
COVERAGE_JSON = PROJECT_ROOT / "coverage.json"
COVERAGE_XML = PROJECT_ROOT / "coverage.xml"


def run_command(command: str, cwd: Optional[Path] = None) -> int:
    """Run a shell command and return the exit code."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or PROJECT_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        print(f"✅ Command successful: {command}")
        if result.stdout:
            print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("=== STDOUT ===")
            print(e.stdout)
        if e.stderr:
            print("=== STDERR ===", file=sys.stderr)
            print(e.stderr, file=sys.stderr)
        return e.returncode


def install_dependencies() -> int:
    """Install required dependencies for coverage reporting."""
    print("\n🔧 Installing dependencies...")
    return run_command("pip install pytest-cov coverage")


def run_tests_with_coverage() -> int:
    """Run tests with coverage enabled."""
    print("\n🔍 Running tests with coverage...")
    cmd = (
        "pytest tests/ -v "
        "--cov=src "
        "--cov-report=term-missing "
        "--cov-report=html "
        "--cov-report=xml "
        "--cov-report=json"
    )
    return run_command(cmd)


def generate_coverage_report() -> int:
    """Generate coverage reports in multiple formats."""
    print("\n📊 Generating coverage reports...")

    # Ensure coverage directory exists
    COVERAGE_DIR.mkdir(exist_ok=True)

    # Generate HTML report
    html_cmd = f"coverage html --directory={COVERAGE_DIR} --title='Test Coverage Report'"
    if run_command(html_cmd) != 0:
        return 1

    # Generate XML report (for CI/CD integration)
    if run_command(f"coverage xml -o {COVERAGE_XML}") != 0:
        return 1

    # Generate JSON report (for further processing)
    if run_command(f"coverage json -o {COVERAGE_JSON}") != 0:
        return 1

    return 0


def print_coverage_summary() -> int:
    """Print a summary of the coverage report."""
    if not COVERAGE_JSON.exists():
        print("❌ No coverage report found. Run tests with coverage first.")
        return 1

    try:
        with open(COVERAGE_JSON, encoding='utf-8') as f:
            data = json.load(f)

        print("\n📋 Coverage Summary:")
        print("=" * 50)

        # Overall coverage
        total = data['totals']
        print(f"📊 Overall Coverage: {total['percent_covered']:.2f}%")
        print(f"✅ Covered: {total['covered_lines']} lines")
        print(f"❌ Missing: {total['missing_lines']} lines")
        print(f"📄 Total: {total['num_statements']} lines")

        # Coverage by file
        print("\n📁 File-wise Coverage:")
        print("-" * 50)
        for file_path, file_data in data['files'].items():
            percent = file_data['summary']['percent_covered']
            covered = file_data['summary']['covered_lines']
            missing = file_data['summary']['missing_lines']
            total_lines = file_data['summary']['num_statements']

            # Skip files with 100% coverage for brevity
            if percent < 100:
                print(f"📄 {file_path}")
                print(f"   ✅ {percent:.1f}% covered ({covered}/{total_lines} lines)")
                if missing > 0:
                    print(f"   ❌ Missing lines: {missing}")

        print("=" * 50)
        return 0
    except Exception as e:
        print(f"❌ Error reading coverage report: {e}")
        return 1


def open_coverage_report() -> None:
    """Open the HTML coverage report in the default web browser."""
    index_file = COVERAGE_DIR / "index.html"
    if index_file.exists():
        print(f"\n🌐 Opening coverage report in browser...")
        webbrowser.open(f"file://{index_file.absolute()}")
    else:
        print("❌ No HTML coverage report found.")


def main() -> int:
    """Main function to generate coverage reports."""
    print("🚀 Starting test coverage report generation...")

    # Install dependencies
    if install_dependencies() != 0:
        return 1

    # Run tests with coverage
    if run_tests_with_coverage() != 0:
        return 1

    # Generate coverage reports
    if generate_coverage_report() != 0:
        return 1

    # Print coverage summary
    if print_coverage_summary() != 0:
        return 1

    # Open the HTML report
    open_coverage_report()

    print("\n✨ Coverage report generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

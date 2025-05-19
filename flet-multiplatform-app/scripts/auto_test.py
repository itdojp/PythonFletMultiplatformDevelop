"""テスト実行自動化スクリプト"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

from backend.tests.data.data_optimizer import DataOptimizer
from backend.tests.data.extended_data import ExtendedData


class AutoTest:
    """テスト実行自動化クラス"""

    def __init__(self):
        """初期化"""
        self.test_dir = Path("tests")
        self.results_dir = Path("test-results")
        self.results_dir.mkdir(exist_ok=True)

    def run_tests(self, test_type: str, parallel: bool = False):
        """テストを実行

        Args:
            test_type (str): テストの種類
            parallel (bool): 並列実行するかどうか
        """
        # テストデータの最適化
        self.optimize_test_data(test_type)

        # テスト環境のセットアップ
        self.setup_test_environment(test_type)

        # テストの実行
        self.execute_tests(test_type, parallel)

        # テスト結果の収集
        self.collect_test_results(test_type)

    def optimize_test_data(self, test_type: str):
        """テストデータを最適化

        Args:
            test_type (str): テストの種類
        """
        optimizer = DataOptimizer()

        if test_type == "unit":
            # 単体テスト用データの最適化
            users = optimizer.optimize_user_data(
                ExtendedData.generate_extended_user_data(100)
            )
            items = optimizer.optimize_item_data(
                ExtendedData.generate_extended_item_data(500)
            )
            auth_data = optimizer.optimize_auth_data(
                ExtendedData.generate_extended_auth_data(50)
            )

        elif test_type == "integration":
            # 統合テスト用データの最適化
            users = optimizer.optimize_user_data(
                ExtendedData.generate_extended_user_data(50, with_items=True)
            )
            items = optimizer.optimize_item_data(
                ExtendedData.generate_extended_item_data(200, with_history=True)
            )
            auth_data = optimizer.optimize_auth_data(
                ExtendedData.generate_extended_auth_data(20, with_refresh=True)
            )

        elif test_type == "performance":
            # パフォーマンステスト用データの最適化
            users = optimizer.optimize_user_data(
                ExtendedData.generate_extended_user_data(1000)
            )
            items = optimizer.optimize_item_data(
                ExtendedData.generate_extended_item_data(5000)
            )
            auth_data = optimizer.optimize_auth_data(
                ExtendedData.generate_extended_auth_data(100)
            )

        # データをファイルに保存
        with open(self.results_dir / f"test_data_{test_type}.json", "w") as f:
            json.dump(
                {"users": users, "items": items, "auth_data": auth_data}, f, indent=2
            )

    def setup_test_environment(self, test_type: str):
        """テスト環境をセットアップ

        Args:
            test_type (str): テストの種類
        """
        # 必要なディレクトリの作成
        (self.results_dir / test_type).mkdir(exist_ok=True)

        # テストデータの読み込み
        with open(self.results_dir / f"test_data_{test_type}.json") as f:
            test_data = json.load(f)

        # テスト設定ファイルの作成
        with open(self.results_dir / f"test_config_{test_type}.json", "w") as f:
            json.dump(
                {
                    "test_type": test_type,
                    "data_size": len(test_data["users"]),
                    "timestamp": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    def execute_tests(self, test_type: str, parallel: bool):
        """テストを実行

        Args:
            test_type (str): テストの種類
            parallel (bool): 並列実行するかどうか
        """
        cmd = [
            "python",
            "-m",
            "pytest",
            f"tests/{test_type}/",
            "-v",
            "--cov=src/backend",
            "--cov-report=xml:coverage.xml",
            "--cov-report=term-missing",
        ]

        if parallel:
            cmd.extend(["-n", "auto"])

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            print(f"Output: {e.output}")
            sys.exit(1)

    def collect_test_results(self, test_type: str):
        """テスト結果を収集

        Args:
            test_type (str): テストの種類
        """
        # カバレッジレポートの収集
        coverage_path = self.results_dir / test_type / "coverage.xml"
        coverage_path.parent.mkdir(exist_ok=True)
        coverage_path.touch()

        # パフォーマンスメトリクスの収集
        metrics_path = self.results_dir / test_type / "performance_metrics.json"
        metrics_path.touch()

        # テスト結果のサマリー
        summary_path = self.results_dir / test_type / "test_summary.json"
        with open(summary_path, "w") as f:
            json.dump(
                {
                    "test_type": test_type,
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed",
                },
                f,
                indent=2,
            )

    def main(self):
        """メイン関数"""
        parser = argparse.ArgumentParser(description="Run automated tests")
        parser.add_argument(
            "test_type",
            choices=["unit", "integration", "performance"],
            help="Type of tests to run",
        )
        parser.add_argument(
            "--parallel",
            action="store_true",
            help="Run tests in parallel",
        )

        args = parser.parse_args()
        self.run_tests(args.test_type, args.parallel)


if __name__ == "__main__":
    AutoTest().main()

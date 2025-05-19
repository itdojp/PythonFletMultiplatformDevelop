"""テスト実行スクリプト"""

import argparse
import subprocess
import sys


def run_tests(test_type: str, parallel: bool = False):
    """テストを実行する

    Args:
        test_type (str): テストの種類 ('unit', 'integration', 'performance')
        parallel (bool): 並列実行するかどうか
    """

    # 環境変数の設定
    env = {
        "TESTING": "True",
        "DATABASE_URL": "sqlite+aiosqlite:///:memory:",
    }

    # pytestコマンドの構築
    cmd = [
        "python",
        "-m",
        "pytest",
        f"tests/{test_type}/",
        "-v",
    ]

    # 並列実行の設定
    if parallel:
        cmd.extend(["-n", "auto"])

    # テストタイプに応じた追加オプション
    if test_type == "unit" or test_type == "integration":
        cmd.extend(
            [
                "--cov=src/backend",
                "--cov-report=xml:coverage.xml",
                "--cov-report=term-missing",
            ]
        )
    elif test_type == "performance":
        cmd.extend(
            [
                "--benchmark-autosave",
                "--benchmark-json=benchmark.json",
            ]
        )

    # テストの実行
    try:
        result = subprocess.run(
            cmd,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.output}")
        return 1


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Run tests")
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
    return run_tests(args.test_type, args.parallel)


if __name__ == "__main__":
    sys.exit(main())

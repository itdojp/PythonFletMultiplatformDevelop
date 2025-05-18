"""パフォーマンステスト用のユーティリティ関数"""

import csv
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from locust import events
from locust.runners import MasterRunner, WorkerRunner

from .config import (
    LOGS_DIR, 
    REPORTS_DIR, 
    RESULTS_DIR,
    PERFORMANCE_THRESHOLDS,
    get_test_data_path
)

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / 'performance_test.log')
    ]
)
logger = logging.getLogger(__name__)

class PerformanceTestUtils:
    """パフォーマンステスト用のユーティリティクラス"""
    
    @staticmethod
    def setup_test_environment() -> None:
        """テスト環境のセットアップ"""
        # 必要なディレクトリを作成
        for directory in [RESULTS_DIR, REPORTS_DIR, LOGS_DIR]:
            directory.mkdir(exist_ok=True, parents=True)
        
        logger.info("Test environment setup completed")
    
    @staticmethod
    def generate_test_data(data_size: str = 'small') -> Dict[str, Path]:
        """テストデータを生成
        
        Args:
            data_size: データサイズ (small, medium, large)
            
        Returns:
            生成されたテストデータのパス
        """
        from scripts.generate_performance_test_data import main as generate_data
        
        logger.info(f"Generating test data with size: {data_size}")
        
        # テストデータ生成スクリプトを呼び出す
        output_dir = get_test_data_path('', data_size).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # テストデータを生成
        result = {}
        for data_type in ['users', 'products', 'orders', 'customers', 'transactions']:
            data_path = get_test_data_path(data_type, data_size)
            if not data_path.exists():
                # データが存在しない場合は生成
                generate_data(['--size', data_size, '--output-dir', str(output_dir)])
                break
            result[data_type] = data_path
        
        return result
    
    @staticmethod
    def load_test_data(data_type: str, data_size: str = 'small') -> Any:
        """テストデータを読み込む
        
        Args:
            data_type: データの種類 (users, products, orders, etc.)
            data_size: データサイズ (small, medium, large)
            
        Returns:
            読み込まれたテストデータ
        """
        data_path = get_test_data_path(data_type, data_size)
        
        if not data_path.exists():
            # データが存在しない場合は生成
            PerformanceTestUtils.generate_test_data(data_size)
        
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def setup_locust_handlers() -> None:
        """Locustのイベントハンドラーをセットアップ"""
        @events.test_start.add_listener
        def on_test_start(environment, **kwargs):
            """テスト開始時の処理"""
            if not isinstance(environment.runner, MasterRunner):
                return
                
            logger.info("Performance test started")
            environment.runner.stats_start_time = time.time()
        
        @events.test_stop.add_listener
        def on_test_stop(environment, **kwargs):
            """テスト終了時の処理"""
            if not isinstance(environment.runner, MasterRunner):
                return
                
            logger.info("Performance test completed")
            
            # テスト結果を保存
            PerformanceTestUtils.save_test_results(environment)
    
    @staticmethod
    def save_test_results(environment) -> Dict[str, Any]:
        """テスト結果を保存
        
        Args:
            environment: Locustの環境オブジェクト
            
        Returns:
            保存されたテスト結果のメタデータ
        """
        if not isinstance(environment.runner, MasterRunner):
            return {}
        
        # テスト結果の収集
        stats = environment.runner.stats
        total_requests = stats.total
        
        # 応答時間のパーセンタイルを計算
        response_times = {
            'min': int(stats.total.min_response_time or 0),
            'max': int(stats.total.max_response_time or 0),
            'avg': int(stats.total.avg_response_time or 0),
            'median': int(stats.total.get_response_time_percentile(0.5) or 0),
            'p90': int(stats.total.get_response_time_percentile(0.9) or 0),
            'p95': int(stats.total.get_response_time_percentile(0.95) or 0),
            'p99': int(stats.total.get_response_time_percentile(0.99) or 0)
        }
        
        # エラーレートの計算
        total_failures = stats.total.num_failures
        total_requests = max(1, stats.total.num_requests)
        error_rate = total_failures / total_requests
        
        # スループットの計算
        test_duration = time.time() - environment.runner.stats_start_time
        rps = total_requests / max(1, test_duration)
        
        # パフォーマンス閾値との比較
        thresholds = PERFORMANCE_THRESHOLDS
        performance_status = {
            'response_time': {
                'p50': response_times['p50'] <= thresholds['response_time']['p50'],
                'p90': response_times['p90'] <= thresholds['response_time']['p90'],
                'p95': response_times['p95'] <= thresholds['response_time']['p95'],
                'p99': response_times['p99'] <= thresholds['response_time']['p99'],
                'max': response_times['max'] <= thresholds['response_time']['max']
            },
            'error_rate': error_rate <= thresholds['error_rate']['critical'],
            'throughput': rps >= thresholds['throughput']['min_rps']
        }
        
        # テスト結果のメタデータ
        test_results = {
            'timestamp': datetime.now().isoformat(),
            'test_duration_seconds': round(test_duration, 2),
            'total_requests': total_requests,
            'total_failures': total_failures,
            'error_rate': round(error_rate * 100, 2),  # パーセント表記
            'response_times': response_times,
            'requests_per_second': round(rps, 2),
            'performance_status': performance_status,
            'thresholds': thresholds
        }
        
        # テスト結果をJSONファイルに保存
        results_file = RESULTS_DIR / f"test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        # テスト結果のサマリーをCSVに追記
        csv_file = RESULTS_DIR / 'test_results_summary.csv'
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f, 
                fieldnames=test_results.keys(),
                extrasaction='ignore'
            )
            
            if not file_exists:
                writer.writeheader()
            writer.writerow(test_results)
        
        logger.info(f"Test results saved to {results_file}")
        return test_results
    
    @staticmethod
    def generate_performance_report(test_results: Dict[str, Any]) -> str:
        """パフォーマンスレポートを生成
        
        Args:
            test_results: テスト結果の辞書
            
        Returns:
            生成されたレポートのパス
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = REPORTS_DIR / f"performance_report_{timestamp}"
        report_dir.mkdir(exist_ok=True, parents=True)
        
        # HTMLレポートを生成
        html_report = report_dir / 'index.html'
        PerformanceTestUtils._generate_html_report(test_results, html_report)
        
        # メトリクスをCSVにエクスポート
        csv_file = report_dir / 'metrics.csv'
        PerformanceTestUtils._export_metrics_to_csv(test_results, csv_file)
        
        # パフォーマンスの傾向を可視化
        plot_file = report_dir / 'performance_metrics.png'
        PerformanceTestUtils._plot_performance_metrics(test_results, plot_file)
        
        logger.info(f"Performance report generated at {html_report}")
        return str(html_report)
    
    @staticmethod
    def _generate_html_report(test_results: Dict[str, Any], output_file: Path) -> None:
        """HTMLレポートを生成
        
        Args:
            test_results: テスト結果の辞書
            output_file: 出力ファイルのパス
        """
        # シンプルなHTMLレポートを生成
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ margin-bottom: 30px; }}
                .metrics {{ margin-bottom: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .status {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <h1>Performance Test Report</h1>
            <div class="summary">
                <h2>Test Summary</h2>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Duration:</strong> {duration} seconds</p>
                <p><strong>Total Requests:</strong> {total_requests:,}</p>
                <p><strong>Failures:</strong> {failures:,}</p>
                <p><strong>Error Rate:</strong> {error_rate}%</p>
                <p><strong>Requests per Second:</strong> {rps:.2f}</p>
            </div>
            
            <div class="metrics">
                <h2>Response Times (ms)</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th><th>Threshold</th><th>Status</th></tr>
                    {response_time_rows}
                </table>
            </div>
            
            <div class="thresholds">
                <h2>Performance Thresholds</h2>
                <p>Error Rate: {error_rate_status}</p>
                <p>Throughput (RPS): {throughput_status}</p>
            </div>
        </body>
        </html>
        """
        
        # レスポンスタイムの行を生成
        response_time_rows = []
        thresholds = test_results['thresholds']['response_time']
        
        for metric in ['p50', 'p90', 'p95', 'p99', 'max']:
            value = test_results['response_times'][metric]
            threshold = thresholds[metric]
            passed = value <= threshold
            status = 'PASS' if passed else 'FAIL'
            status_class = 'pass' if passed else 'fail'
            
            row = f"""
            <tr>
                <td>{metric.upper()}</td>
                <td>{value:,} ms</td>
                <td>{threshold:,} ms</td>
                <td class="status {status_class}">{status}</td>
            </tr>
            """
            response_time_rows.append(row)
        
        # エラーレートのステータス
        error_rate_status = (
            f"<span class='pass'>PASS</span> ({test_results['error_rate']}% <= "
            f"{test_results['thresholds']['error_rate']['critical'] * 100}%)"
        )
        
        # スループットのステータス
        min_rps = test_results['thresholds']['throughput']['min_rps']
        throughput_status = (
            f"<span class='pass'>PASS</span> ({test_results['requests_per_second']:.2f} RPS >= {min_rps} RPS)"
            if test_results['requests_per_second'] >= min_rps
            else f"<span class='fail'>FAIL</span> ({test_results['requests_per_second']:.2f} RPS < {min_rps} RPS)"
        )
        
        # HTMLをレンダリング
        html = html.format(
            timestamp=test_results['timestamp'],
            duration=test_results['test_duration_seconds'],
            total_requests=test_results['total_requests'],
            failures=test_results['total_failures'],
            error_rate=test_results['error_rate'],
            rps=test_results['requests_per_second'],
            response_time_rows=''.join(response_time_rows),
            error_rate_status=error_rate_status,
            throughput_status=throughput_status
        )
        
        # ファイルに保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
    
    @staticmethod
    def _export_metrics_to_csv(test_results: Dict[str, Any], output_file: Path) -> None:
        """メトリクスをCSVにエクスポート
        
        Args:
            test_results: テスト結果の辞書
            output_file: 出力ファイルのパス
        """
        # フラットな辞書に変換
        flat_metrics = {
            'timestamp': test_results['timestamp'],
            'test_duration_seconds': test_results['test_duration_seconds'],
            'total_requests': test_results['total_requests'],
            'total_failures': test_results['total_failures'],
            'error_rate': test_results['error_rate'],
            'requests_per_second': test_results['requests_per_second']
        }
        
        # レスポンスタイムを追加
        for metric, value in test_results['response_times'].items():
            flat_metrics[f'response_time_{metric}'] = value
        
        # 閾値を追加
        for category, thresholds in test_results['thresholds'].items():
            if isinstance(thresholds, dict):
                for metric, value in thresholds.items():
                    flat_metrics[f'threshold_{category}_{metric}'] = value
            else:
                flat_metrics[f'threshold_{category}'] = thresholds
        
        # CSVに保存
        df = pd.DataFrame([flat_metrics])
        df.to_csv(output_file, index=False, encoding='utf-8')
    
    @staticmethod
    def _plot_performance_metrics(test_results: Dict[str, Any], output_file: Path) -> None:
        """パフォーマンスメトリクスをプロット
        
        Args:
            test_results: テスト結果の辞書
            output_file: 出力ファイルのパス
        """
        try:
            import matplotlib.pyplot as plt
            
            # レスポンスタイムのデータを準備
            response_times = test_results['response_times']
            metrics = ['p50', 'p90', 'p95', 'p99', 'max']
            values = [response_times[m] for m in metrics]
            thresholds = [test_results['thresholds']['response_time'][m] for m in metrics]
            
            # プロットの作成
            plt.figure(figsize=(12, 6))
            
            # バープロット
            x = range(len(metrics))
            width = 0.35
            
            plt.bar([i - width/2 for i in x], values, width, label='Actual', color='skyblue')
            plt.bar([i + width/2 for i in x], thresholds, width, label='Threshold', color='lightcoral', alpha=0.7)
            
            # ラベルとタイトル
            plt.xlabel('Percentile')
            plt.ylabel('Response Time (ms)')
            plt.title('Response Time Percentiles vs Thresholds')
            plt.xticks(x, [m.upper() for m in metrics])
            plt.legend()
            
            # 値を表示
            for i, v in enumerate(values):
                plt.text(i - width/2, v + 5, f"{v:,}", ha='center')
            
            for i, v in enumerate(thresholds):
                plt.text(i + width/2, v + 5, f"{v:,}", ha='center')
            
            # グリッドを表示
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # 画像を保存
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
        except ImportError:
            logger.warning("matplotlib is not installed. Skipping performance plot generation.")

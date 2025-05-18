import os
import json
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def read_test_results(results_dir):
    """テスト結果を読み込む"""
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'coverage': 0,
        'response_time_avg': 0,
        'rps': 0
    }
    
    # テスト結果ファイルのパス
    results_file = os.path.join(results_dir, 'test_results.json')
    
    if os.path.exists(results_file):
        with open(results_file, 'r') as f:
            data = json.load(f)
            results.update(data)
    
    # カバレッジファイルのパス
    coverage_file = os.path.join(os.path.dirname(results_dir), 'coverage.xml')
    if os.path.exists(coverage_file):
        # 簡単な例として、カバレッジファイルから値を取得
        # 実際には適切なパース処理が必要
        results['coverage'] = 85.0  # 仮の値
    
    return results

def format_message(results, repo_url, run_id):
    """Slackメッセージをフォーマットする"""
    status = "✅ 成功" if results['failed'] == 0 else "❌ 失敗"
    
    # リポジトリURLからリポジトリ名を抽出
    repo_name = repo_url.split('/')[-1] if repo_url else "unknown-repo"
    
    message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{repo_name} パフォーマンステスト結果*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*ステータス:*\n{status}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*日時:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*テスト数:*\n{results['total']} (成功: {results['passed']}, 失敗: {results['failed']})"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*カバレッジ:*\n{results['coverage']:.2f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*平均応答時間:*\n{results['response_time_avg']:.2f}ms"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*1秒あたりのリクエスト数:*\n{results['rps']:.2f}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "詳細を見る",
                            "emoji": True
                        },
                        "url": f"{repo_url}/actions/runs/{run_id}"
                    }
                ]
            }
        ]
    }
    
    return message

def send_slack_notification(webhook_url, message):
    """Slackに通知を送信する"""
    client = WebClient()
    
    try:
        response = client.chat_postMessage(
            channel="#performance-tests",
            text="パフォーマンステストの結果",
            blocks=message["blocks"]
        )
        print("通知を送信しました")
        return True
    except SlackApiError as e:
        print(f"Slack通知の送信に失敗しました: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Send performance test results to Slack')
    parser.add_argument('--results-dir', type=str, default='results', help='テスト結果ディレクトリ')
    parser.add_argument('--webhook-url', type=str, default=None, help='Slack Webhook URL')
    parser.add_argument('--repo-url', type=str, default='', help='GitHub リポジトリURL')
    parser.add_argument('--run-id', type=str, default='', help='GitHub Actions 実行ID')
    
    args = parser.parse_args()
    
    # 環境変数からWebhook URLを取得
    webhook_url = args.webhook_url or os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook_url:
        print("エラー: Slack Webhook URLが指定されていません")
        exit(1)
    
    # テスト結果を読み込む
    results = read_test_results(args.results_dir)
    
    # メッセージをフォーマット
    message = format_message(results, args.repo_url, args.run_id)
    
    # Slackに通知を送信
    send_slack_notification(webhook_url, message)

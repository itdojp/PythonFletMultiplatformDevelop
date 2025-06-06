# パフォーマンステストガイド

このドキュメントでは、アプリケーションのパフォーマンステストの実行方法と結果の解釈方法について説明します。

## 目次
- [テストの種類](#テストの種類)
- [ローカルでの実行方法](#ローカルでの実行方法)
- [CI/CDパイプラインでの実行](#cicdパイプラインでの実行)
- [テスト結果の解釈](#テスト結果の解釈)
- [Slack通知](#slack通知)
- [トラブルシューティング](#トラブルシューティング)

## テストの種類

以下の種類のパフォーマンステストを実行できます：

1. **ロードテスト**
   - 通常の負荷をシミュレート
   - デフォルト: 10ユーザー、30秒間

2. **ストレステスト**
   - 高負荷状態をシミュレート
   - デフォルト: 20ユーザー、1分間

3. **エンデュランステスト**
   - 長時間の負荷に耐えられるかテスト
   - デフォルト: 5ユーザー、2分間

4. **スケーラビリティテスト**
   - ユーザー数を段階的に増加させてテスト
   - デフォルト: 1ユーザーから5ユーザーまで段階的に増加

## ローカルでの実行方法

1. 必要なパッケージをインストール:
   ```bash
   pip install -r tests/performance/requirements-test.txt
   ```

2. テストを実行:
   ```bash
   # すべてのテストを実行
   python -m pytest tests/performance -v

   # 特定のテストを実行（例: ロードテストのみ）
   python -m pytest tests/performance/test_load.py -v
   ```

3. カバレッジレポートを生成:
   ```bash
   coverage run --source=. -m pytest tests/performance
   coverage html
   ```

## CI/CDパイプラインでの実行

プッシュまたはプルリクエスト時に自動的にパフォーマンステストが実行されます。

## テスト結果の解釈

テスト実行後、以下のディレクトリに結果が保存されます：

- `results/`: 生のテスト結果（JSON形式）
- `reports/`: HTML形式のテストレポート
- `coverage_html_report/`: カバレッジレポート
- `plots/`: パフォーマンスメトリクスのグラフ

## Slack通知

CI/CDパイプラインの実行が完了すると、Slackに通知が送信されます。通知には以下の情報が含まれます：

- テストのステータス（成功/失敗）
- テスト数と成功/失敗数
- コードカバレッジ
- 平均応答時間
- 1秒あたりのリクエスト数

## トラブルシューティング

### テストが失敗する場合

1. アプリケーションが正しく起動しているか確認してください
2. データベースに接続できるか確認してください
3. 十分なシステムリソースがあるか確認してください

### カバレッジが正しく計測されない場合

1. `.coveragerc`ファイルの設定を確認してください
2. テストが正しくインポートされているか確認してください
3. 除外パターンが適切に設定されているか確認してください

### Slack通知が届かない場合

1. `SLACK_WEBHOOK_URL`が正しく設定されているか確認してください
2. Slackの権限設定を確認してください
3. GitHub Actionsのログを確認してエラーがないか確認してください

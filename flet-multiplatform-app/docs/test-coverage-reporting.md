# テストカバレッジレポートガイド

## 1. テストカバレッジの基本

### テストカバレッジとは
テストカバレッジは、ソースコードのどの程度がテストによって実行されたかを示す指標です。本プロジェクトでは、コードの品質を客観的に評価するために重要な指標として活用しています。

### 計測対象のカバレッジ
- **ラインカバレッジ**: 実行されたコード行の割合
- **ブランチカバレッジ**: 条件分岐のテスト網羅率
- **関数カバレッジ**: 関数のテスト網羅率

### カバレッジ目標
- 最小要件: 70% (CIで強制)
- 推奨: 80%以上
- 理想: 90%以上

## 2. ローカル環境での確認方法

### カバレッジレポートの生成
```bash
# テストの実行とカバレッジレポートの生成
pytest --cov=src --cov-report=term-missing --cov-report=html

# レポートの表示
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

### 特定のファイルのカバレッジを確認
```bash
# 特定のファイルのカバレッジを確認
pytest --cov=src/path/to/module.py tests/

# カバレッジの詳細を表示
coverage report -m
```

## 3. CI/CDパイプライン

### 3.1 プルリクエストでのチェック
プルリクエストが作成・更新されると、自動的にテストが実行され、以下のチェックが行われます：

1. カバレッジ閾値（70%）の確認
2. カバレッジの増減の検出
3. PRコメントでのカバレッジサマリーの表示

### 3.2 本番環境へのデプロイ
`main`ブランチまたは`develop`ブランチにマージされると、カバレッジレポートがGitHub Pagesに自動的に公開されます。

## 4. カバレッジレポートの見方

### 4.1 カバレッジサマリー
- **Stmts**: ステートメント数
- **Miss**: カバーされていないステートメント数
- **Cover**: カバレッジ率
- **Missing**: カバーされていない行番号

### 4.2 カバレッジレポートの色分け
- **緑色**: テストでカバーされている行
- **赤色**: テストでカバーされていない行
- **黄色**: 部分的にカバーされている行（ブランチカバレッジ）

## 5. カバレッジを向上させるには

1. カバレッジレポートで赤く表示されているファイルを確認
2. テストされていない機能や条件分岐を特定
3. 不足しているテストケースを追加
4. カバレッジが低いモジュールに優先的に取り組む

## 6. トラブルシューティング

### 6.1 カバレッジが正しく計測されない場合
1. テストが正しく実行されているか確認
2. `__init__.py`ファイルが存在するか確認
3. テスト対象のモジュールが正しくインポートされているか確認

### 6.2 レポートが表示されない場合
1. テストが完了しているか確認
2. ブラウザのキャッシュをクリア
3. GitHub Pagesの設定を確認

## 7. ベストプラクティス

1. 新しい機能を実装する際は、必ずテストも追加する
2. バグを修正したら、再発防止のテストケースを追加する
3. 定期的にカバレッジのトレンドを確認し、品質の低下を防ぐ
4. カバレッジ100%を目指すのではなく、重要なロジックに焦点を当てる

## 8. 参考リンク

- [pytest-cov 公式ドキュメント](https://pytest-cov.readthedocs.io/)
- [Python Coverage.py ドキュメント](https://coverage.readthedocs.io/)
- [GitHub Actions ワークフロー構文](https://docs.github.com/ja/actions/using-workflows/workflow-syntax-for-github-actions)

---

## 9. GitHub Pages の設定手順

### 9.1 リポジトリ設定
1. GitHub でリポジトリのトップページにアクセス
2. 上部の「Settings」タブをクリック
3. 左サイドバーから「Pages」を選択

### 9.2 ソースの設定
1. 「Source」セクションで以下を設定:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
2. 「Save」ボタンをクリック

### 9.3 Actions の権限設定
1. リポジトリの「Settings」に戻る
2. 左サイドバーから「Actions」→「General」を選択
3. 「Workflow permissions」セクションで以下を設定:
   - ✅ Read and write permissions を有効化
   - ✅ Allow GitHub Actions to create and approve pull requests を有効化
4. ページ下部の「Save」ボタンをクリック

### 9.4 初回設定後の確認
1. `main` または `develop` ブランチにプッシュ
2. GitHub Actions の実行を確認
3. 数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` にアクセスしてレポートを確認

## 10. トラブルシューティング（GitHub Pages 編）

### 10.1 ページが表示されない場合
1. GitHub Actions のワークフローが正常に完了しているか確認
2. ブランチ名とフォルダの設定が正しいか確認
3. 初回のデプロイには最大10分かかることがあります

### 10.2 404 エラーが表示される場合
1. リポジトリの「Settings」→「Pages」でデプロイの状態を確認
2. ワークフローファイルの `deploy` ステップが実行されているか確認
3. `gh-pages` ブランチに `index.html` が存在するか確認

## 11. カスタムドメインの設定（オプション）

カスタムドメインを使用する場合は、以下の手順で設定できます：

1. リポジトリの「Settings」→「Pages」→「Custom domain」にドメインを入力
2. DNSプロバイダで以下のレコードを設定:
   ```
   CNAME レコード: yourdomain.com → <ユーザー名>.github.io
   CNAME レコード: www → <ユーザー名>.github.io
   ```
3. 「Enforce HTTPS」を有効化

## 12. 参考リンク（追加）

- [GitHub Pages 公式ドキュメント](https://docs.github.com/ja/pages)
- [GitHub Actions ワークフロー構文](https://docs.github.com/ja/actions/using-workflows/workflow-syntax-for-github-actions)
- [カスタムドメインの設定](https://docs.github.com/ja/pages/configuring-a-custom-domain-for-your-github-pages-site)

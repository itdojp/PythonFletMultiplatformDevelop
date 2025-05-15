# uv パッケージ管理運用ガイド

このドキュメントでは、Python プロジェクトにおける [uv](https://github.com/astral-sh/uv) を用いた依存管理・ロックファイル運用のベストプラクティスをまとめます。

---

## 1. 基本方針
- 依存パッケージの宣言は `pyproject.toml` で管理します。
- バージョン固定・再現性確保のために `requirements.lock` を生成して管理します。
- チーム開発やCI/CDでは必ず `requirements.lock` を使ってインストールします。

---

## 2. 依存パッケージの追加・更新

1. `pyproject.toml` を編集して依存パッケージを追加・更新します。
2. 以下のコマンドでロックファイルを生成します：

```bash
uv pip compile pyproject.toml -o requirements.lock
```

3. 生成された `requirements.lock` をコミット・プッシュします。

---

## 3. パッケージのインストール（ロックファイルから）

プロジェクト環境構築やCI/CDでは、必ず以下のコマンドでインストールしてください：

```bash
uv pip install -r requirements.lock
```

これにより、全ての環境で同じバージョンのパッケージがインストールされます。

---

## 4. 依存パッケージのアップグレード

1. `pyproject.toml` のバージョン指定を変更、または `uv pip compile --upgrade pyproject.toml -o requirements.lock` でアップグレードします。
2. `requirements.lock` を再生成し、コミット・プッシュします。

---

## 5. Dependabot との連携

- `requirements.lock` をリポジトリに含めることで、Dependabot が自動で脆弱性チェックやアップデートPRを作成します。
- セキュリティアラートや自動PRが来た場合は、内容を確認し、必要に応じてロックファイルを再生成してください。

---

## 6. よく使うコマンド一覧

| 操作                        | コマンド例                                                |
|----------------------------|----------------------------------------------------------|
| 依存解決＆ロック生成       | `uv pip compile pyproject.toml -o requirements.lock`      |
| ロックファイルからインストール | `uv pip install -r requirements.lock`                     |
| 依存パッケージのアップグレード | `uv pip compile --upgrade pyproject.toml -o requirements.lock` |

---

## 7. 注意事項
- `requirements.lock` を必ずコミット・プッシュしてください。
- `requirements.txt` は uv では省略可能ですが、pip 互換運用や他ツール連携時は生成してもOKです。
- poetry/pipenv など他のツールの lock ファイルと混在しないよう注意してください。

---

## 8. 参考リンク
- [uv 公式ドキュメント](https://github.com/astral-sh/uv)
- [Dependabot 公式ドキュメント](https://docs.github.com/ja/code-security/dependabot)

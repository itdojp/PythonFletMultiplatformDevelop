#!/usr/bin/env python
# filepath: c:\work\PythonFletMultiplatformDevelopmentDocuments\tools\cli_template_generator.py
"""
コマンドライン版テンプレートジェネレーター
GUIなしでテンプレートを生成するためのツール
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# テンプレート定義ファイルのパス
TEMPLATE_DEFINITIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "simple_templates.json"
)


def load_template_definitions():
    """テンプレート定義をJSONファイルから読み込む"""
    try:
        with open(TEMPLATE_DEFINITIONS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"エラー: テンプレート定義ファイルを読み込めませんでした: {e}")
        # エラー時はダミーデータを返す
        return {
            "project_templates": [],
            "component_templates": [],
            "screen_templates": [],
        }


def snake_case(s):
    """文字列をスネークケースに変換"""
    # スペースと特殊文字を削除
    s = re.sub(r"[^\w\s]", "", s)
    # キャメルケースをスネークケースに変換
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    # スペースをアンダースコアに置換し、小文字に変換
    return re.sub(r"\s+", "_", s).lower()


def replace_template_vars(content, vars):
    """テンプレート変数を置換"""
    for key, value in vars.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def list_templates(template_type=None):
    """利用可能なテンプレート一覧を表示"""
    templates = load_template_definitions()

    if template_type:
        # 特定のタイプのテンプレートのみ表示
        template_key = f"{template_type}_templates"
        if template_key in templates:
            print(f"利用可能な{template_type}テンプレート:")
            for idx, template in enumerate(templates[template_key], 1):
                print(f"{idx}. {template['name']} - {template['description']}")
        else:
            print(f"エラー: 不明なテンプレートタイプ '{template_type}'")
    else:
        # すべてのテンプレートを表示
        for template_key, template_list in templates.items():
            type_name = template_key.split("_")[0]
            print(f"利用可能な{type_name}テンプレート:")
            for idx, template in enumerate(template_list, 1):
                print(f"{idx}. {template['name']} - {template['description']}")
            print()


def generate_project_template(template, project_name, output_dir, description=""):
    """プロジェクトテンプレートを生成"""
    # スネークケースのプロジェクト名を作成
    project_dir = os.path.join(output_dir, snake_case(project_name))

    # プロジェクトディレクトリが既に存在するか確認
    if os.path.exists(project_dir):
        print(f"エラー: ディレクトリが既に存在します: {project_dir}")
        return False

    # ディレクトリ作成
    try:
        os.makedirs(project_dir, exist_ok=True)
    except Exception as e:
        print(f"エラー: ディレクトリを作成できませんでした: {e}")
        return False

    # テンプレートに基づいてファイル生成
    for file_template in template["files"]:
        file_path = os.path.join(project_dir, file_template["path"])

        # ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # テンプレート変数
        template_vars = {
            "project_name": project_name,
            "project_description": description or "Fletプロジェクト",
        }

        # テンプレート変数を置換
        content = replace_template_vars(file_template["content"], template_vars)

        # ファイルに書き込み
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"プロジェクトテンプレートが生成されました: {project_dir}")
    return True


def generate_component_template(template, component_name, output_dir, output_path=""):
    """コンポーネントテンプレートを生成"""
    # 出力ディレクトリ
    if output_path:
        component_dir = os.path.join(output_dir, output_path)
    else:
        component_dir = os.path.join(output_dir, "components")

    # ディレクトリが存在しない場合は作成
    try:
        os.makedirs(component_dir, exist_ok=True)
    except Exception as e:
        print(f"エラー: ディレクトリを作成できませんでした: {e}")
        return False

    # ファイル名（スネークケース）
    file_name = snake_case(component_name) + ".py"
    file_path = os.path.join(component_dir, file_name)

    # テンプレート変数
    template_vars = {
        "component_name": component_name,
        "component_description": template["description"],
    }

    # テンプレート変数を置換
    content = replace_template_vars(template["content"], template_vars)

    # クラス名を置換（カスタマイズによる名前変更）
    class_pattern = r"class\s+\w+"
    content = re.sub(class_pattern, f"class {component_name}", content)

    # ファイルに書き込み
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"コンポーネントテンプレートが生成されました: {file_path}")
    return True


def generate_screen_template(template, screen_name, output_dir, output_path=""):
    """画面テンプレートを生成"""
    # 出力ディレクトリ
    if output_path:
        screen_dir = os.path.join(output_dir, output_path)
    else:
        screen_dir = os.path.join(output_dir, "views")

    # ディレクトリが存在しない場合は作成
    try:
        os.makedirs(screen_dir, exist_ok=True)
    except Exception as e:
        print(f"エラー: ディレクトリを作成できませんでした: {e}")
        return False

    # ファイル名（スネークケース）
    file_name = snake_case(screen_name) + ".py"
    file_path = os.path.join(screen_dir, file_name)

    # テンプレート変数
    template_vars = {
        "screen_name": screen_name,
        "screen_description": template["description"],
    }

    # テンプレート変数を置換
    content = replace_template_vars(template["content"], template_vars)

    # クラス名を置換（カスタマイズによる名前変更）
    class_pattern = r"class\s+\w+"
    content = re.sub(class_pattern, f"class {screen_name}", content)

    # ファイルに書き込み
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"画面テンプレートが生成されました: {file_path}")
    return True


def find_template_by_name(template_type, template_name):
    """名前からテンプレートを検索"""
    templates = load_template_definitions()
    template_key = f"{template_type}_templates"

    if template_key not in templates:
        return None

    for template in templates[template_key]:
        if template["name"].lower() == template_name.lower():
            return template

    return None


def find_template_by_index(template_type, index):
    """インデックスからテンプレートを検索"""
    templates = load_template_definitions()
    template_key = f"{template_type}_templates"

    if template_key not in templates:
        return None

    try:
        idx = int(index) - 1  # 1から始まるインデックスを0から始まるインデックスに変換
        if 0 <= idx < len(templates[template_key]):
            return templates[template_key][idx]
    except ValueError:
        pass

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Fletテンプレートジェネレーター（CLI版）"
    )

    # サブコマンド
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # listコマンド
    list_parser = subparsers.add_parser("list", help="テンプレート一覧を表示")
    list_parser.add_argument(
        "--type",
        "-t",
        choices=["project", "component", "screen"],
        help="テンプレートタイプ",
    )

    # generateコマンド
    generate_parser = subparsers.add_parser("generate", help="テンプレートを生成")
    generate_parser.add_argument(
        "--type",
        "-t",
        required=True,
        choices=["project", "component", "screen"],
        help="テンプレートタイプ",
    )
    generate_parser.add_argument(
        "--template",
        "-m",
        required=True,
        help="テンプレート名かインデックス（list コマンドで確認）",
    )
    generate_parser.add_argument(
        "--name", "-n", required=True, help="プロジェクト/コンポーネント/画面の名前"
    )
    generate_parser.add_argument(
        "--output",
        "-o",
        default=os.getcwd(),
        help="出力ディレクトリ（デフォルト: カレントディレクトリ）",
    )
    generate_parser.add_argument(
        "--path", "-p", help="出力パス（components/custom/ や views/ などの相対パス）"
    )
    generate_parser.add_argument(
        "--description", "-d", help="説明（プロジェクトテンプレートのみ）"
    )

    args = parser.parse_args()

    if args.command == "list":
        list_templates(args.type)

    elif args.command == "generate":
        # テンプレートを検索
        template = find_template_by_name(args.type, args.template)
        if template is None:
            template = find_template_by_index(args.type, args.template)

        if template is None:
            print(f"エラー: テンプレート '{args.template}' が見つかりません。")
            print(
                "利用可能なテンプレート一覧を表示するには 'list' コマンドを使用してください。"
            )
            return 1

        # テンプレート生成
        if args.type == "project":
            generate_project_template(
                template, args.name, args.output, args.description
            )

        elif args.type == "component":
            generate_component_template(template, args.name, args.output, args.path)

        elif args.type == "screen":
            generate_screen_template(template, args.name, args.output, args.path)

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())

import flet as ft
import json
import os
import re
import inspect
import importlib.util
import ast
from pathlib import Path

def main(page: ft.Page):
    page.title = "Flet テストジェネレーター"
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    # テーマ設定
    apply_app_theme(page)
    
    # 作業ディレクトリ
    working_dir = ft.TextField(
        label="プロジェクトディレクトリ",
        value=os.path.expanduser("~"),
        width=500,
        hint_text="テストを生成するプロジェクトディレクトリ"
    )
    
    def select_dir(_):
        def result_handler(e: ft.FilePickerResultEvent):
            if e.path:
                working_dir.value = e.path
                update_project_structure()
                page.update()
        
        file_picker = ft.FilePicker(on_result=result_handler)
        page.overlay.append(file_picker)
        page.update()
        file_picker.get_directory_path()
    
    browse_button = ft.ElevatedButton("参照", on_click=select_dir, icon=ft.icons.FOLDER_OPEN)
    
    # テンプレートの読み込み
    test_templates = load_test_templates()
    
    # プロジェクト構造のツリービュー
    project_tree = ft.TreeView(
        data=ft.TreeData(),
        width=250,
        height=400,
        on_select_change=on_file_selected
    )
    
    # 選択したファイルの情報
    selected_file_info = ft.Text()
    
    # ファイル選択時の処理
    def on_file_selected(e):
        if project_tree.selected and project_tree.selected != "root":
            file_path = project_tree.selected
            if os.path.isfile(file_path) and file_path.endswith(".py"):
                analyze_python_file(file_path)
            else:
                selected_file_info.value = "選択されたファイルはPythonファイルではありません。"
                module_functions.controls.clear()
                module_classes.controls.clear()
            page.update()
    
    # モジュール内の関数とクラスの一覧
    module_functions = ft.ListView(spacing=2, height=150)
    module_classes = ft.ListView(spacing=2, height=150)
    
    # テスト設定
    test_type_dropdown = ft.Dropdown(
        label="テストタイプ",
        options=[ft.dropdown.Option(t["name"]) for t in test_templates["test_types"]],
        width=250,
        on_change=update_framework_options
    )
    
    test_framework_dropdown = ft.Dropdown(
        label="テストフレームワーク",
        width=250
    )
    
    # テストタイプ変更時のフレームワークオプション更新
    def update_framework_options(e):
        test_framework_dropdown.options.clear()
        
        if test_type_dropdown.value:
            test_type = next((t for t in test_templates["test_types"] if t["name"] == test_type_dropdown.value), None)
            if test_type:
                test_framework_dropdown.options = [
                    ft.dropdown.Option(f["name"]) for f in test_type["frameworks"]
                ]
                if test_framework_dropdown.options:
                    test_framework_dropdown.value = test_framework_dropdown.options[0].key
        
        page.update()
    
    # テスト出力設定
    test_file_name = ft.TextField(
        label="テストファイル名",
        width=300,
        hint_text="生成するテストファイル名（.pyは自動追加）"
    )
    
    create_test_dir = ft.Checkbox(
        label="テストディレクトリを作成",
        value=True
    )
    
    test_dir_name = ft.TextField(
        label="テストディレクトリ名",
        width=200,
        value="tests"
    )
    
    # 選択された要素
    selected_elements = []
    
    # 選択された要素リスト
    selected_elements_list = ft.ListView(
        spacing=2,
        height=150,
        width=400
    )
    
    # プロジェクト構造の更新
    def update_project_structure():
        project_tree.data.clear()
        project_tree.data.add(ft.TreeItem("root", "プロジェクト", None, True))
        
        if os.path.isdir(working_dir.value):
            scan_directory(working_dir.value, "root")
        
        project_tree.update()
    
    # ディレクトリをスキャンしてツリービューに追加
    def scan_directory(dir_path, parent_id):
        try:
            items = os.listdir(dir_path)
            
            # ディレクトリを先に表示
            dirs = [item for item in items if os.path.isdir(os.path.join(dir_path, item)) and not item.startswith('.')]
            files = [item for item in items if os.path.isfile(os.path.join(dir_path, item)) and item.endswith('.py')]
            
            # ソート
            dirs.sort()
            files.sort()
            
            # ディレクトリを追加
            for dirname in dirs:
                dir_full_path = os.path.join(dir_path, dirname)
                dir_id = dir_full_path
                
                # ディレクトリをツリーに追加
                project_tree.data.add(ft.TreeItem(dir_id, dirname, parent_id, True))
                
                # 再帰的に処理
                scan_directory(dir_full_path, dir_id)
            
            # ファイルを追加
            for filename in files:
                file_full_path = os.path.join(dir_path, filename)
                file_id = file_full_path
                
                # Python ファイルをツリーに追加
                project_tree.data.add(ft.TreeItem(file_id, filename, parent_id, False))
        
        except Exception as e:
            print(f"ディレクトリのスキャン中にエラーが発生しました: {e}")
    
    # Pythonファイルを解析して関数とクラスを抽出
    def analyze_python_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
            
            # ファイル情報を表示
            file_name = os.path.basename(file_path)
            selected_file_info.value = f"選択したファイル: {file_name}"
            
            # ASTパーサーを使用してコード解析
            tree = ast.parse(file_content)
            
            # 関数とクラスのリストをクリア
            module_functions.controls.clear()
            module_classes.controls.clear()
            
            # 関数を抽出
            functions = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    
                    function_item = ft.Row([
                        ft.Checkbox(
                            label=node.name,
                            on_change=lambda e, name=node.name, type="function": toggle_element_selection(e, name, type, file_path)
                        ),
                        ft.Text("関数", color=ft.colors.BLUE)
                    ])
                    module_functions.controls.append(function_item)
            
            # クラスを抽出
            classes = []
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    
                    # クラスメソッドを抽出
                    methods = []
                    for class_node in ast.iter_child_nodes(node):
                        if isinstance(class_node, ast.FunctionDef):
                            methods.append(class_node.name)
                    
                    class_item = ft.Column([
                        ft.Row([
                            ft.Checkbox(
                                label=node.name,
                                on_change=lambda e, name=node.name, type="class", methods=methods: toggle_element_selection(e, name, type, file_path, methods)
                            ),
                            ft.Text("クラス", color=ft.colors.GREEN)
                        ])
                    ])
                    
                    if methods:
                        method_items = ft.Column(
                            [ft.Text("メソッド:", size=12, color=ft.colors.GREY_700)],
                            spacing=0,
                            padding=ft.padding.only(left=20)
                        )
                        
                        for method in methods:
                            if method != "__init__":  # 初期化メソッドは除外
                                method_item = ft.Row([
                                    ft.Checkbox(
                                        label=method,
                                        on_change=lambda e, class_name=node.name, method_name=method: toggle_method_selection(e, class_name, method_name, file_path)
                                    ),
                                    ft.Text("メソッド", color=ft.colors.ORANGE, size=12)
                                ])
                                method_items.controls.append(method_item)
                        
                        class_item.controls.append(method_items)
                    
                    module_classes.controls.append(class_item)
            
            page.update()
            
        except Exception as e:
            selected_file_info.value = f"ファイル解析中にエラーが発生しました: {e}"
            module_functions.controls.clear()
            module_classes.controls.clear()
            page.update()
    
    # 選択要素の切り替え
    def toggle_element_selection(e, name, type, file_path, methods=None):
        if e.control.value:
            # 選択追加
            element = {
                "name": name,
                "type": type,
                "file_path": file_path,
                "methods": methods if methods else []
            }
            selected_elements.append(element)
        else:
            # 選択解除
            for i, el in enumerate(selected_elements):
                if el["name"] == name and el["type"] == type and el["file_path"] == file_path:
                    selected_elements.pop(i)
                    break
        
        update_selected_elements_list()
    
    # メソッド選択の切り替え
    def toggle_method_selection(e, class_name, method_name, file_path):
        # クラスがすでに選択されているか確認
        class_element = None
        for el in selected_elements:
            if el["name"] == class_name and el["type"] == "class" and el["file_path"] == file_path:
                class_element = el
                break
        
        if class_element:
            # クラスの特定メソッドを選択/解除
            class_methods = class_element.get("selected_methods", [])
            
            if e.control.value:
                if method_name not in class_methods:
                    class_methods.append(method_name)
            else:
                if method_name in class_methods:
                    class_methods.remove(method_name)
            
            class_element["selected_methods"] = class_methods
        else:
            # クラスが選択されていない場合は、クラスと選択されたメソッドを追加
            if e.control.value:
                element = {
                    "name": class_name,
                    "type": "class",
                    "file_path": file_path,
                    "methods": [],
                    "selected_methods": [method_name]
                }
                selected_elements.append(element)
        
        update_selected_elements_list()
    
    # 選択された要素リストの更新
    def update_selected_elements_list():
        selected_elements_list.controls.clear()
        
        for element in selected_elements:
            element_text = f"{element['name']} ({element['type']})"
            
            if element['type'] == 'class' and 'selected_methods' in element and element['selected_methods']:
                element_text += f" - メソッド: {', '.join(element['selected_methods'])}"
            
            list_item = ft.Row([
                ft.Text(element_text, width=300),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    tooltip="削除",
                    on_click=lambda _, el=element: remove_selected_element(el)
                )
            ])
            selected_elements_list.controls.append(list_item)
        
        page.update()
    
    # 選択要素の削除
    def remove_selected_element(element):
        selected_elements.remove(element)
        update_selected_elements_list()
    
    # テストコード生成
    def generate_test_code(_):
        if not selected_elements:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("テスト対象を選択してください"),
                action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        if not test_type_dropdown.value or not test_framework_dropdown.value:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("テストタイプとフレームワークを選択してください"),
                action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # テスト対象のファイルパス
        file_path = selected_elements[0]["file_path"]
        module_path = get_module_path(file_path)
        
        # テストファイル名の設定
        if not test_file_name.value:
            base_name = os.path.basename(file_path)
            test_file_name.value = f"test_{base_name}"
        
        # テストディレクトリの設定
        output_dir = os.path.dirname(file_path)
        if create_test_dir.value:
            output_dir = os.path.join(output_dir, test_dir_name.value)
            os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, test_file_name.value)
        
        # テンプレートの取得
        test_type = next((t for t in test_templates["test_types"] if t["name"] == test_type_dropdown.value), None)
        framework = next((f for f in test_type["frameworks"] if f["name"] == test_framework_dropdown.value), None)
        
        if not test_type or not framework:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("テストテンプレートが見つかりませんでした"),
                action="閉じる"
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # コード生成
        code = []
        
        # 特殊なFletテスト処理
        if test_type_dropdown.value == "UI テスト" and test_framework_dropdown.value == "Flet テスト":
            flet_templates = test_templates["flet_test_templates"]
            
            # ページテンプレートかコントロールテンプレートを選択
            template = None
            
            if any(e["type"] == "function" for e in selected_elements):
                # ページテスト
                template = next((t for t in flet_templates if t["name"] == "ページテスト"), None)
            elif any(e["type"] == "class" for e in selected_elements):
                # コントロールテスト
                template = next((t for t in flet_templates if t["name"] == "コントロールテスト"), None)
            
            if template:
                # 選択された関数/クラスに対してテンプレートを適用
                element = selected_elements[0]
                
                if element["type"] == "function":
                    test_code = template["template"].replace("{module_path}", module_path)
                    test_code = test_code.replace("{function_name}", element["name"])
                    test_code = test_code.replace("{class_name}", pascal_case(element["name"]))
                    code.append(test_code)
                elif element["type"] == "class":
                    test_code = template["template"].replace("{module_path}", module_path)
                    test_code = test_code.replace("{class_name}", element["name"])
                    code.append(test_code)
        else:
            # 通常のテスト生成
            for element in selected_elements:
                if element["type"] == "function":
                    # 関数テスト
                    test_code = framework["template"].replace("{module_path}", module_path)
                    test_code = test_code.replace("{method_name}", element["name"])
                    if "{class_name}" in test_code:
                        test_code = test_code.replace("{class_name}", pascal_case(element["name"]))
                    code.append(test_code)
                elif element["type"] == "class":
                    # クラステスト
                    test_code = framework["template"].replace("{module_path}", module_path)
                    test_code = test_code.replace("{class_name}", element["name"])
                    
                    # 選択されたメソッドがある場合
                    if "selected_methods" in element and element["selected_methods"]:
                        for method in element["selected_methods"]:
                            method_test_code = test_code.replace("{method_name}", method)
                            code.append(method_test_code)
                    else:
                        # クラス全体のテスト
                        if "{method_name}" in test_code:
                            test_code = test_code.replace("{method_name}", "class_" + snake_case(element["name"]))
                        code.append(test_code)
        
        # 重複を削除して結合
        full_code = "\n\n".join(code)
        
        # ファイルに保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_code)
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"テストコードが生成されました: {output_path}"),
            action="閉じる"
        )
        page.snack_bar.open = True
        page.update()
    
    # レイアウト構築
    page.add(
        ft.Text("Flet テストジェネレーター", size=30, weight=ft.FontWeight.BOLD),
        ft.Row([
            working_dir,
            browse_button
        ]),
        ft.Row([
            ft.Column([
                ft.Text("プロジェクト構造"),
                project_tree
            ]),
            ft.Column([
                selected_file_info,
                ft.Text("関数"),
                module_functions,
                ft.Text("クラス"),
                module_classes
            ]),
        ]),
        ft.Divider(),
        ft.Text("テスト設定"),
        ft.Row([
            test_type_dropdown,
            test_framework_dropdown
        ]),
        ft.Row([
            test_file_name,
            create_test_dir,
            test_dir_name
        ]),
        ft.Divider(),
        ft.Text("選択された要素"),
        selected_elements_list,
        ft.ElevatedButton(
            "テストコード生成",
            icon=ft.icons.CODE,
            on_click=generate_test_code
        )
    )

# テストテンプレートの読み込み
def load_test_templates():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_path = os.path.join(current_dir, "test_templates.json")
    
    with open(templates_path, "r", encoding="utf-8") as f:
        return json.load(f)

# モジュールパスを取得
def get_module_path(file_path):
    # 絶対パスをPythonモジュールパス形式に変換
    rel_path = os.path.relpath(file_path)
    module_path = rel_path.replace(os.path.sep, ".").replace(".py", "")
    return module_path

# ユーティリティ: スネークケース変換
def snake_case(text):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# ユーティリティ: パスカルケース変換
def pascal_case(s):
    # スネークケースを想定
    words = s.split('_')
    # 各単語の先頭を大文字に
    return ''.join(word.capitalize() for word in words)

# テーマを設定
def apply_app_theme(page):
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )
    page.update()

if __name__ == "__main__":
    ft.app(target=main)

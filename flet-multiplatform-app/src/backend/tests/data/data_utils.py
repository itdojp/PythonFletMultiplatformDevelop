"""テストデータユーティリティモジュール"""

from datetime import datetime, timedelta
from random import choice, randint
from typing import Any, Dict, List, Optional, Type

from ..data.data_generator import DataGenerator
from ..data.extended_data import ExtendedData
from ..validation.advanced_validator import AdvancedValidator


class DataUtils:
    """テストデータユーティリティクラス"""

    @staticmethod
    def optimize_data_size(
        data: List[Dict[str, Any]],
        min_size: int = 10,
        max_size: int = 100
    ) -> List[Dict[str, Any]]:
        """データサイズを最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            min_size (int): 最小データ数
            max_size (int): 最大データ数

        Returns:
            List[Dict[str, Any]]: 最適化されたデータリスト
        """
        current_size = len(data)
        if current_size < min_size:
            # データ数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_data = []
            for _ in range(min_size - current_size):
                new_data = generator.generate_user_data(1)[0]
                additional_data.append(new_data)
            data.extend(additional_data)
        elif current_size > max_size:
            # データ数が最大値を超えた場合、ランダムにサンプリング
            data = random.sample(data, max_size)

        return data

    @staticmethod
    def optimize_data_quality(
        data: List[Dict[str, Any]],
        rules: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """データの品質を最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            List[Dict[str, Any]]: 品質が最適化されたデータリスト

        Raises:
            ValueError: バリデーションエラー
        """
        validated_data = []
        for item in data:
            try:
                validated = AdvancedValidator.validate_with_rules(item, rules)
                validated_data.append(validated)
            except ValueError as e:
                # バリデーションエラーのデータをログに記録し、スキップ
                print(f"Validation failed for data: {item}. Error: {str(e)}")

        return validated_data

    @staticmethod
    def optimize_data_relationships(
        data: List[Dict[str, Any]],
        relationships: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """データ間の関連性を最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            relationships (Dict[str, List[str]]): 関連性の定義

        Returns:
            List[Dict[str, Any]]: 関連性が最適化されたデータリスト
        """
        # データ間の関連性を確認し、整合性を確保
        related_data = defaultdict(list)
        for item in data:
            for field, related_fields in relationships.items():
                if field in item:
                    related_data[field].append(item)

        # 関連性の整合性チェック
        for field, related_fields in relationships.items():
            for item in related_data[field]:
                for related_field in related_fields:
                    if related_field not in item:
                        # 関連フィールドが存在しない場合、追加生成
                        generator = DataGenerator()
                        related_value = generator.generate_dates(1)[0]
                        item[related_field] = related_value

        return data

    @staticmethod
    def optimize_data_distribution(
        data: List[Dict[str, Any]],
        distribution: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """データの分布を最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            distribution (Dict[str, Dict[str, Any]]): 分布の定義

        Returns:
            List[Dict[str, Any]]: 分布が最適化されたデータリスト
        """
        # データの分布を分析し、必要に応じて調整
        field_stats = {}
        for item in data:
            for field, dist in distribution.items():
                if field in item:
                    if field not in field_stats:
                        field_stats[field] = defaultdict(int)
                    field_stats[field][str(item[field])] += 1

        # 分布の調整
        for field, stats in field_stats.items():
            total = sum(stats.values())
            if total > 0:
                for value, count in stats.items():
                    if count / total < distribution[field].get("min_ratio", 0):
                        # 分布が最小値を下回った場合、追加生成
                        generator = DataGenerator()
                        new_data = generator.generate_user_data(1)[0]
                        new_data[field] = value
                        data.append(new_data)

        return data

    @staticmethod
    def optimize_data_performance(
        data: List[Dict[str, Any]],
        performance_targets: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """パフォーマンスを考慮したデータの最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            performance_targets (Dict[str, Dict[str, Any]]): パフォーマンスターゲット

        Returns:
            List[Dict[str, Any]]: パフォーマンスが最適化されたデータリスト
        """
        # パフォーマンスに影響するデータの最適化
        for item in data:
            for field, targets in performance_targets.items():
                if field in item:
                    # データサイズの最適化
                    if "max_size" in targets:
                        item[field] = item[field][:targets["max_size"]]

                    # データ形式の最適化
                    if "format" in targets:
                        item[field] = DataUtils.format_data(item[field], targets["format"])

        return data

    @staticmethod
    def format_data(value: Any, format_type: str) -> Any:
        """データを指定された形式に整形

        Args:
            value (Any): 整形対象の値
            format_type (str): 整形形式

        Returns:
            Any: 整形された値
        """
        if format_type == "json":
            import json
            return json.dumps(value)
        elif format_type == "datetime":
            if isinstance(value, datetime):
                return value.isoformat()
        elif format_type == "number":
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        return value

    @staticmethod
    def generate_test_data(
        data_type: str,
        count: int = 10,
        optimize: bool = True,
        rules: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ) -> List[Dict[str, Any]]:
        """テストデータを生成

        Args:
            data_type (str): データの種類 ('user', 'item', 'auth')
            count (int): 生成するデータ数
            optimize (bool): データを最適化するかどうか
            rules (Optional[Dict[str, List[Dict[str, Any]]]]): バリデーションルール

        Returns:
            List[Dict[str, Any]]: 生成されたテストデータ
        """
        generator = DataGenerator()
        if data_type == "user":
            data = generator.generate_user_data(count)
        elif data_type == "item":
            data = generator.generate_item_data(count)
        elif data_type == "auth":
            data = generator.generate_auth_data(count)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        if optimize:
            data = DataUtils.optimize_data_size(data)
            if rules:
                data = DataUtils.optimize_data_quality(data, rules)

        return data

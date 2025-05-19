"""高度なテストデータバリデーションモジュール"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, ValidationError

from ..data.data_generator import DataGenerator
from ..data.extended_data import ExtendedData
from ..schemas import ItemCreate, UserCreate


class ValidationRule(Enum):
    """バリデーションルールの種類"""

    REQUIRED = "required"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    UNIQUE = "unique"
    DATE_RANGE = "date_range"
    RELATIONSHIP = "relationship"


class AdvancedValidator:
    """高度なバリデーションクラス"""

    @staticmethod
    def validate_with_rules(
        data: Dict[str, Any], rules: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """複数のバリデーションルールを適用

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            Dict[str, Any]: バリデーションされたデータ

        Raises:
            ValueError: バリデーションエラー
        """
        for field, field_rules in rules.items():
            value = data.get(field)
            for rule in field_rules:
                rule_type = rule.get("type")
                if rule_type:
                    try:
                        method = getattr(AdvancedValidator, f"validate_{rule_type}")
                        method(field, value, rule)
                    except AttributeError:
                        raise ValueError(f"Unknown validation rule: {rule_type}")

        return data

    @staticmethod
    def validate_required(field: str, value: Any, rule: Dict[str, Any]):
        """必須フィールドのバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if value is None:
            raise ValueError(f"{field} is required")

    @staticmethod
    def validate_min_length(field: str, value: Any, rule: Dict[str, Any]):
        """最小長のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if isinstance(value, str) and len(value) < rule.get("length", 0):
            raise ValueError(
                f"{field} must be at least {rule['length']} characters long"
            )

    @staticmethod
    def validate_max_length(field: str, value: Any, rule: Dict[str, Any]):
        """最大長のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if isinstance(value, str) and len(value) > rule.get("length", float("inf")):
            raise ValueError(
                f"{field} must be at most {rule['length']} characters long"
            )

    @staticmethod
    def validate_min_value(field: str, value: Any, rule: Dict[str, Any]):
        """最小値のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if isinstance(value, (int, float)) and value < rule.get("value", float("-inf")):
            raise ValueError(f"{field} must be at least {rule['value']}")

    @staticmethod
    def validate_max_value(field: str, value: Any, rule: Dict[str, Any]):
        """最大値のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if isinstance(value, (int, float)) and value > rule.get("value", float("inf")):
            raise ValueError(f"{field} must be at most {rule['value']}")

    @staticmethod
    def validate_pattern(field: str, value: Any, rule: Dict[str, Any]):
        """正規表現パターンのバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        import re

        pattern = rule.get("pattern")
        if pattern and not re.match(pattern, str(value)):
            raise ValueError(f"{field} does not match pattern: {pattern}")

    @staticmethod
    def validate_unique(field: str, value: Any, rule: Dict[str, Any]):
        """一意性のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        # データベースチェックなど、一意性の確認
        pass

    @staticmethod
    def validate_date_range(field: str, value: Any, rule: Dict[str, Any]):
        """日付範囲のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        if isinstance(value, datetime):
            min_date = rule.get("min_date")
            max_date = rule.get("max_date")
            if min_date and value < min_date:
                raise ValueError(f"{field} must be after {min_date}")
            if max_date and value > max_date:
                raise ValueError(f"{field} must be before {max_date}")

    @staticmethod
    def validate_relationship(field: str, value: Any, rule: Dict[str, Any]):
        """関連性のバリデーション

        Args:
            field (str): フィールド名
            value (Any): フィールドの値
            rule (Dict[str, Any]): バリデーションルール

        Raises:
            ValueError: バリデーションエラー
        """
        # 関連データの整合性チェック
        pass

    @staticmethod
    def validate_batch(
        data_list: List[Dict[str, Any]], rules: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """複数のデータを一括でバリデーション

        Args:
            data_list (List[Dict[str, Any]]): バリデーション対象のデータリスト
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            List[Dict[str, Any]]: バリデーションされたデータリスト

        Raises:
            ValueError: バリデーションエラー
        """
        validated_data = []
        for data in data_list:
            try:
                validated = AdvancedValidator.validate_with_rules(data, rules)
                validated_data.append(validated)
            except ValueError as e:
                raise ValueError(f"Validation failed for data: {data}. Error: {str(e)}")
        return validated_data

    @staticmethod
    def validate_user_data(data: Dict[str, Any], strict: bool = True) -> Dict[str, Any]:
        """ユーザーのデータをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ
            strict (bool): 厳格なバリデーションを実行するかどうか

        Returns:
            Dict[str, Any]: バリデーションされたデータ

        Raises:
            ValueError: バリデーションエラー
        """
        rules = {
            "email": [
                {"type": ValidationRule.REQUIRED.value},
                {
                    "type": ValidationRule.PATTERN.value,
                    "pattern": r"^[^@]+@[^@]+\.[^@]+$",
                },
            ],
            "username": [
                {"type": ValidationRule.REQUIRED.value},
                {"type": ValidationRule.MIN_LENGTH.value, "length": 3},
                {"type": ValidationRule.MAX_LENGTH.value, "length": 50},
            ],
            "password": [
                {"type": ValidationRule.REQUIRED.value},
                {"type": ValidationRule.MIN_LENGTH.value, "length": 8},
                {
                    "type": ValidationRule.PATTERN.value,
                    "pattern": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
                },
            ],
        }

        return AdvancedValidator.validate_with_rules(data, rules)

    @staticmethod
    def validate_item_data(data: Dict[str, Any], strict: bool = True) -> Dict[str, Any]:
        """アイテムのデータをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ
            strict (bool): 厳格なバリデーションを実行するかどうか

        Returns:
            Dict[str, Any]: バリデーションされたデータ

        Raises:
            ValueError: バリデーションエラー
        """
        rules = {
            "title": [
                {"type": ValidationRule.REQUIRED.value},
                {"type": ValidationRule.MIN_LENGTH.value, "length": 1},
                {"type": ValidationRule.MAX_LENGTH.value, "length": 100},
            ],
            "price": [
                {"type": ValidationRule.REQUIRED.value},
                {"type": ValidationRule.MIN_VALUE.value, "value": 0.0},
            ],
            "owner_id": [
                {"type": ValidationRule.REQUIRED.value},
                {"type": ValidationRule.UNIQUE.value},
            ],
        }

        return AdvancedValidator.validate_with_rules(data, rules)

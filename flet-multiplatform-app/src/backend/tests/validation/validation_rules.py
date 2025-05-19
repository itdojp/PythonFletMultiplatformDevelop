"""高度なバリデーションルールモジュール"""

from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Tuple, Type

from ..data.data_generator import DataGenerator
from ..data.extended_data import ExtendedData
from ..validation.advanced_validator import AdvancedValidator, ValidationRule


class ValidationType(Enum):
    """バリデーションタイプ"""

    SIMPLE = "simple"
    COMPOSITE = "composite"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"


class ValidationRuleBuilder:
    """バリデーションルールビルダークラス"""

    @staticmethod
    def required(field: str) -> Dict[str, Any]:
        """必須フィールドのバリデーションルール

        Args:
            field (str): フィールド名

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {"type": ValidationRule.REQUIRED.value, "field": field}

    @staticmethod
    def length(
        field: str, min_length: int = 0, max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """長さのバリデーションルール

        Args:
            field (str): フィールド名
            min_length (int): 最小長
            max_length (Optional[int]): 最大長

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.MIN_LENGTH.value,
            "field": field,
            "min_length": min_length,
            "max_length": max_length,
        }

    @staticmethod
    def value(
        field: str, min_value: Optional[Any] = None, max_value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """値のバリデーションルール

        Args:
            field (str): フィールド名
            min_value (Optional[Any]): 最小値
            max_value (Optional[Any]): 最大値

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.MIN_VALUE.value,
            "field": field,
            "min_value": min_value,
            "max_value": max_value,
        }

    @staticmethod
    def pattern(field: str, pattern: str) -> Dict[str, Any]:
        """正規表現パターンのバリデーションルール

        Args:
            field (str): フィールド名
            pattern (str): 正規表現パターン

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.PATTERN.value,
            "field": field,
            "pattern": pattern,
        }

    @staticmethod
    def unique(field: str) -> Dict[str, Any]:
        """一意性のバリデーションルール

        Args:
            field (str): フィールド名

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {"type": ValidationRule.UNIQUE.value, "field": field}

    @staticmethod
    def date_range(
        field: str,
        min_date: Optional[datetime] = None,
        max_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """日付範囲のバリデーションルール

        Args:
            field (str): フィールド名
            min_date (Optional[datetime]): 最小日付
            max_date (Optional[datetime]): 最大日付

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.DATE_RANGE.value,
            "field": field,
            "min_date": min_date,
            "max_date": max_date,
        }

    @staticmethod
    def relationship(field: str, related_fields: List[str]) -> Dict[str, Any]:
        """関連性のバリデーションルール

        Args:
            field (str): フィールド名
            related_fields (List[str]): 関連フィールドのリスト

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.RELATIONSHIP.value,
            "field": field,
            "related_fields": related_fields,
        }

    @staticmethod
    def custom(field: str, validator: callable) -> Dict[str, Any]:
        """カスタムバリデーションルール

        Args:
            field (str): フィールド名
            validator (callable): カスタムバリデーション関数

        Returns:
            Dict[str, Any]: バリデーションルール
        """
        return {
            "type": ValidationRule.CUSTOM.value,
            "field": field,
            "validator": validator,
        }


class ValidationDecorator:
    """バリデーションデコレータクラス"""

    @staticmethod
    def validate(rules: List[Dict[str, Any]]):
        """メソッドをバリデーション付きでラップ

        Args:
            rules (List[Dict[str, Any]]): バリデーションルールリスト

        Returns:
            callable: バリデーション付きのラッパー関数
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # メソッドの引数を取得
                arg_data = kwargs.copy()
                if args:
                    arg_data.update(
                        {
                            k: v
                            for k, v in zip(func.__code__.co_varnames, args)
                            if k != "self" and k != "cls"
                        }
                    )

                # バリデーション実行
                for rule in rules:
                    try:
                        AdvancedValidator.validate_with_rules(
                            arg_data, {rule["field"]: [rule]}
                        )
                    except ValueError as e:
                        raise ValueError(
                            f"Validation failed for {func.__name__}: {str(e)}"
                        )

                return func(*args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def validate_class(rules: Dict[str, List[Dict[str, Any]]]):
        """クラスメソッドをバリデーション付きでラップ

        Args:
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            callable: バリデーション付きのラッパー関数
        """

        def decorator(cls):
            for name, method in cls.__dict__.items():
                if callable(method):
                    setattr(
                        cls, name, ValidationDecorator.validate(rules[name])(method)
                    )
            return cls

        return decorator


class ValidationContext:
    """バリデーションコンテキストクラス"""

    def __init__(self, data: Dict[str, Any]):
        """初期化

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ
        """
        self.data = data
        self.errors = []

    def add_error(self, field: str, message: str):
        """バリデーションエラーを追加

        Args:
            field (str): エラーのフィールド名
            message (str): エラーメッセージ
        """
        self.errors.append({"field": field, "message": message})

    def validate(self, rules: Dict[str, List[Dict[str, Any]]]) -> bool:
        """複数のバリデーションルールを適用

        Args:
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            bool: バリデーション結果
        """
        self.errors = []
        for field, field_rules in rules.items():
            value = self.data.get(field)
            for rule in field_rules:
                try:
                    method = getattr(AdvancedValidator, f"validate_{rule['type']}")
                    method(field, value, rule)
                except ValueError as e:
                    self.add_error(field, str(e))
        return not self.errors

    def get_errors(self) -> List[Dict[str, str]]:
        """バリデーションエラーを取得

        Returns:
            List[Dict[str, str]]: バリデーションエラーのリスト
        """
        return self.errors


class ValidationManager:
    """バリデーションマネージャークラス"""

    @staticmethod
    def validate_data(
        data: Dict[str, Any], rules: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[bool, List[Dict[str, str]]]:
        """データをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            Tuple[bool, List[Dict[str, str]]]: バリデーション結果とエラーのリスト
        """
        context = ValidationContext(data)
        result = context.validate(rules)
        return result, context.get_errors()

    @staticmethod
    def validate_batch(
        data_list: List[Dict[str, Any]], rules: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, str]]]]:
        """複数のデータを一括でバリデーション

        Args:
            data_list (List[Dict[str, Any]]): バリデーション対象のデータリスト
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            Tuple[List[Dict[str, Any]], List[List[Dict[str, str]]]]:
                バリデーションされたデータリストとエラーのリスト
        """
        validated_data = []
        all_errors = []
        for data in data_list:
            result, errors = ValidationManager.validate_data(data, rules)
            if result:
                validated_data.append(data)
            all_errors.append(errors)
        return validated_data, all_errors

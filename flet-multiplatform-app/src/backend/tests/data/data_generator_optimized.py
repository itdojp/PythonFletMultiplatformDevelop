"""最適化されたデータ生成モジュール"""

from datetime import datetime, timedelta
from enum import Enum
from random import choice, randint, random
from string import ascii_letters, digits
from typing import Any, Dict, List, Optional, Tuple, Type

from ..data.extended_data import ExtendedData
from ..validation.validation_rules import ValidationRuleBuilder


class DataGenerationType(Enum):
    """データ生成タイプ"""
    RANDOM = "random"
    SEQUENTIAL = "sequential"
    COMBINED = "combined"
    CUSTOM = "custom"


class DataGenerationStrategy:
    """データ生成戦略クラス"""

    @staticmethod
    def random_strategy(
        field_type: Type,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        length: Optional[int] = None
    ) -> Any:
        """ランダムなデータ生成

        Args:
            field_type (Type): フィールドの型
            min_value (Optional[Any]): 最小値
            max_value (Optional[Any]): 最大値
            length (Optional[int]): 長さ

        Returns:
            Any: 生成されたデータ
        """
        if field_type == str:
            if length:
                return ''.join(choice(ascii_letters + digits) for _ in range(length))
            return ''.join(choice(ascii_letters + digits) for _ in range(randint(5, 20)))
        elif field_type == int:
            if min_value is not None and max_value is not None:
                return randint(min_value, max_value)
            return randint(1, 1000)
        elif field_type == float:
            if min_value is not None and max_value is not None:
                return min_value + random() * (max_value - min_value)
            return random() * 1000
        elif field_type == bool:
            return choice([True, False])
        elif field_type == datetime:
            if min_value is not None and max_value is not None:
                return min_value + timedelta(
                    seconds=random() * (max_value.timestamp() - min_value.timestamp())
                )
            return datetime.now() + timedelta(days=randint(-365, 365))
        return None

    @staticmethod
    def sequential_strategy(
        field_type: Type,
        start_value: Optional[Any] = None,
        increment: Optional[Any] = None
    ) -> Any:
        """連番データ生成

        Args:
            field_type (Type): フィールドの型
            start_value (Optional[Any]): 開始値
            increment (Optional[Any]): 増分

        Returns:
            Any: 生成されたデータ
        """
        if field_type == str:
            if start_value is None:
                start_value = 'A'
            if increment is None:
                increment = 1
            return chr(ord(start_value) + increment)
        elif field_type == int:
            if start_value is None:
                start_value = 1
            if increment is None:
                increment = 1
            return start_value + increment
        elif field_type == float:
            if start_value is None:
                start_value = 0.0
            if increment is None:
                increment = 0.1
            return start_value + increment
        return None

    @staticmethod
    def combined_strategy(
        field_type: Type,
        base_value: Optional[Any] = None,
        variation: Optional[Any] = None
    ) -> Any:
        """組み合わせデータ生成

        Args:
            field_type (Type): フィールドの型
            base_value (Optional[Any]): 基準値
            variation (Optional[Any]): 変動範囲

        Returns:
            Any: 生成されたデータ
        """
        if field_type == str:
            if base_value is None:
                base_value = 'base'
            if variation is None:
                variation = 5
            return base_value + str(randint(0, variation))
        elif field_type == int:
            if base_value is None:
                base_value = 100
            if variation is None:
                variation = 50
            return base_value + randint(-variation, variation)
        elif field_type == float:
            if base_value is None:
                base_value = 100.0
            if variation is None:
                variation = 50.0
            return base_value + random() * variation
        return None


class DataGeneratorOptimized:
    """最適化されたデータ生成クラス"""

    def __init__(self):
        """初期化"""
        self.strategy = DataGenerationStrategy()
        self.validation_builder = ValidationRuleBuilder()

    def generate_user_data(
        self,
        count: int = 1,
        strategy: DataGenerationType = DataGenerationType.RANDOM
    ) -> List[Dict[str, Any]]:
        """ユーザーデータを生成

        Args:
            count (int): 生成するデータ数
            strategy (DataGenerationType): 生成戦略

        Returns:
            List[Dict[str, Any]]: 生成されたユーザーデータ
        """
        users = []
        for i in range(count):
            user = {
                "email": self.generate_field(str, strategy, length=20),
                "username": self.generate_field(str, strategy, length=10),
                "password": self.generate_field(str, strategy, length=12),
                "is_active": self.generate_field(bool, strategy),
                "created_at": self.generate_field(datetime, strategy),
                "updated_at": self.generate_field(datetime, strategy)
            }
            users.append(user)
        return users

    def generate_item_data(
        self,
        count: int = 1,
        strategy: DataGenerationType = DataGenerationType.RANDOM
    ) -> List[Dict[str, Any]]:
        """アイテムデータを生成

        Args:
            count (int): 生成するデータ数
            strategy (DataGenerationType): 生成戦略

        Returns:
            List[Dict[str, Any]]: 生成されたアイテムデータ
        """
        items = []
        for i in range(count):
            item = {
                "title": self.generate_field(str, strategy, length=50),
                "description": self.generate_field(str, strategy, length=200),
                "price": self.generate_field(float, strategy, min_value=0.0),
                "quantity": self.generate_field(int, strategy, min_value=0),
                "created_at": self.generate_field(datetime, strategy),
                "updated_at": self.generate_field(datetime, strategy)
            }
            items.append(item)
        return items

    def generate_auth_data(
        self,
        count: int = 1,
        strategy: DataGenerationType = DataGenerationType.RANDOM
    ) -> List[Dict[str, Any]]:
        """認証データを生成

        Args:
            count (int): 生成するデータ数
            strategy (DataGenerationType): 生成戦略

        Returns:
            List[Dict[str, Any]]: 生成された認証データ
        """
        auth_data = []
        for i in range(count):
            auth = {
                "access_token": self.generate_field(str, strategy, length=32),
                "refresh_token": self.generate_field(str, strategy, length=32),
                "expires_in": self.generate_field(int, strategy, min_value=3600),
                "token_type": self.generate_field(str, strategy, length=10),
                "scope": self.generate_field(str, strategy, length=20)
            }
            auth_data.append(auth)
        return auth_data

    def generate_field(
        self,
        field_type: Type,
        strategy: DataGenerationType,
        min_value: Optional[Any] = None,
        max_value: Optional[Any] = None,
        length: Optional[int] = None,
        start_value: Optional[Any] = None,
        increment: Optional[Any] = None,
        base_value: Optional[Any] = None,
        variation: Optional[Any] = None
    ) -> Any:
        """フィールドを生成

        Args:
            field_type (Type): フィールドの型
            strategy (DataGenerationType): 生成戦略
            min_value (Optional[Any]): 最小値
            max_value (Optional[Any]): 最大値
            length (Optional[int]): 長さ
            start_value (Optional[Any]): 開始値
            increment (Optional[Any]): 増分
            base_value (Optional[Any]): 基準値
            variation (Optional[Any]): 変動範囲

        Returns:
            Any: 生成されたフィールド値
        """
        if strategy == DataGenerationType.RANDOM:
            return self.strategy.random_strategy(
                field_type,
                min_value=min_value,
                max_value=max_value,
                length=length
            )
        elif strategy == DataGenerationType.SEQUENTIAL:
            return self.strategy.sequential_strategy(
                field_type,
                start_value=start_value,
                increment=increment
            )
        elif strategy == DataGenerationType.COMBINED:
            return self.strategy.combined_strategy(
                field_type,
                base_value=base_value,
                variation=variation
            )
        return None

    def optimize_data(
        self,
        data: List[Dict[str, Any]],
        rules: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """データを最適化

        Args:
            data (List[Dict[str, Any]]): 最適化対象のデータ
            rules (Dict[str, List[Dict[str, Any]]]): バリデーションルール

        Returns:
            List[Dict[str, Any]]: 最適化されたデータ
        """
        optimized_data = []
        for item in data:
            for field, field_rules in rules.items():
                if field in item:
                    value = item[field]
                    for rule in field_rules:
                        try:
                            # バリデーションルールに従って最適化
                            if rule["type"] == "required":
                                if not value:
                                    value = self.generate_field(
                                        type(value),
                                        DataGenerationType.RANDOM
                                    )
                            elif rule["type"] == "min_length":
                                if len(str(value)) < rule["min_length"]:
                                    value = self.generate_field(
                                        type(value),
                                        DataGenerationType.RANDOM,
                                        length=rule["min_length"]
                                    )
                            elif rule["type"] == "max_length":
                                if len(str(value)) > rule["max_length"]:
                                    value = str(value)[:rule["max_length"]]
                            elif rule["type"] == "min_value":
                                if value < rule["min_value"]:
                                    value = self.generate_field(
                                        type(value),
                                        DataGenerationType.RANDOM,
                                        min_value=rule["min_value"]
                                    )
                            elif rule["type"] == "max_value":
                                if value > rule["max_value"]:
                                    value = self.generate_field(
                                        type(value),
                                        DataGenerationType.RANDOM,
                                        max_value=rule["max_value"]
                                    )
                            elif rule["type"] == "pattern":
                                if not rule["pattern"].match(str(value)):
                                    value = self.generate_field(
                                        type(value),
                                        DataGenerationType.RANDOM,
                                        length=len(str(value))
                                    )
                            item[field] = value
            optimized_data.append(item)
        return optimized_data

    def generate_test_data_batch(
        self,
        data_type: str,
        count: int = 10,
        strategy: DataGenerationType = DataGenerationType.RANDOM,
        rules: Optional[Dict[str, List[Dict[str, Any]]]] = None
    ) -> List[Dict[str, Any]]:
        """テストデータを一括生成

        Args:
            data_type (str): データタイプ
            count (int): 生成するデータ数
            strategy (DataGenerationType): 生成戦略
            rules (Optional[Dict[str, List[Dict[str, Any]]]]): バリデーションルール

        Returns:
            List[Dict[str, Any]]: 生成されたテストデータ
        """
        if data_type == "user":
            data = self.generate_user_data(count, strategy)
        elif data_type == "item":
            data = self.generate_item_data(count, strategy)
        elif data_type == "auth":
            data = self.generate_auth_data(count, strategy)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        if rules:
            data = self.optimize_data(data, rules)

        return data

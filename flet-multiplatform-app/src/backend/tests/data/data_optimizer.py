"""テストデータ最適化モジュール"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..data.data_generator import DataGenerator
from ..data.extended_data import ExtendedData


class DataOptimizer:
    """テストデータ最適化クラス"""

    @staticmethod
    def optimize_user_data(
        users: List[Dict[str, Any]],
        max_users: int = 100,
        min_users: int = 10
    ) -> List[Dict[str, Any]]:
        """ユーザーのデータを最適化

        Args:
            users (List[Dict[str, Any]]): ユーザーのデータリスト
            max_users (int): 最大ユーザー数
            min_users (int): 最小ユーザー数

        Returns:
            List[Dict[str, Any]]: 最適化されたユーザーのデータ
        """
        if len(users) > max_users:
            # ユーザー数が最大値を超えた場合、ランダムにサンプリング
            users = random.sample(users, max_users)
        elif len(users) < min_users:
            # ユーザー数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_users = generator.generate_user_data(min_users - len(users))
            users.extend(additional_users)

        return users

    @staticmethod
    def optimize_item_data(
        items: List[Dict[str, Any]],
        max_items: int = 500,
        min_items: int = 50
    ) -> List[Dict[str, Any]]:
        """アイテムのデータを最適化

        Args:
            items (List[Dict[str, Any]]): アイテムのデータリスト
            max_items (int): 最大アイテム数
            min_items (int): 最小アイテム数

        Returns:
            List[Dict[str, Any]]: 最適化されたアイテムのデータ
        """
        if len(items) > max_items:
            # アイテム数が最大値を超えた場合、ランダムにサンプリング
            items = random.sample(items, max_items)
        elif len(items) < min_items:
            # アイテム数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_items = generator.generate_item_data(min_items - len(items))
            items.extend(additional_items)

        return items

    @staticmethod
    def optimize_auth_data(
        auth_data: List[Dict[str, str]],
        max_auth: int = 50,
        min_auth: int = 5
    ) -> List[Dict[str, str]]:
        """認証データを最適化

        Args:
            auth_data (List[Dict[str, str]]): 認証データリスト
            max_auth (int): 最大認証情報数
            min_auth (int): 最小認証情報数

        Returns:
            List[Dict[str, str]]: 最適化された認証データ
        """
        if len(auth_data) > max_auth:
            # 認証情報数が最大値を超えた場合、ランダムにサンプリング
            auth_data = random.sample(auth_data, max_auth)
        elif len(auth_data) < min_auth:
            # 認証情報数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_auth = generator.generate_auth_data(min_auth - len(auth_data))
            auth_data.extend(additional_auth)

        return auth_data

    @staticmethod
    def optimize_date_data(
        dates: List[Dict[str, Any]],
        max_dates: int = 100,
        min_dates: int = 10,
        time_range_days: int = 365
    ) -> List[Dict[str, Any]]:
        """日付データを最適化

        Args:
            dates (List[Dict[str, Any]]): 日付データリスト
            max_dates (int): 最大日付数
            min_dates (int): 最小日付数
            time_range_days (int): 時間範囲（日数）

        Returns:
            List[Dict[str, Any]]: 最適化された日付データ
        """
        if len(dates) > max_dates:
            # 日付数が最大値を超えた場合、ランダムにサンプリング
            dates = random.sample(dates, max_dates)
        elif len(dates) < min_dates:
            # 日付数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_dates = generator.generate_dates(
                min_dates - len(dates),
                -time_range_days,
                time_range_days
            )
            dates.extend(additional_dates)

        return dates

    @staticmethod
    def optimize_batch_data(
        data: List[Dict[str, Any]],
        max_size: int = 1000,
        min_size: int = 100,
        validator: callable = None
    ) -> List[Dict[str, Any]]:
        """複数のデータを最適化

        Args:
            data (List[Dict[str, Any]]): データリスト
            max_size (int): 最大データ数
            min_size (int): 最小データ数
            validator (callable): バリデーション関数

        Returns:
            List[Dict[str, Any]]: 最適化されたデータリスト
        """
        if len(data) > max_size:
            # データ数が最大値を超えた場合、ランダムにサンプリング
            data = random.sample(data, max_size)
        elif len(data) < min_size:
            # データ数が最小値を下回った場合、追加生成
            generator = DataGenerator()
            additional_data = []
            for _ in range(min_size - len(data)):
                new_data = generator.generate_user_data(1)[0]
                if validator:
                    validator(new_data)
                additional_data.append(new_data)
            data.extend(additional_data)

        return data

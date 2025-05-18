"""テスト用のモックデータモジュール"""

from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

from ..data.data_generator import DataGenerator
from ..schemas import ItemCreate, UserCreate


class TestMocks:
    """テスト用のモッククラス"""

    @staticmethod
    def get_mock_user_data(
        count: int = 1,
        is_superuser: bool = False,
        invalid: bool = False
    ) -> List[Dict[str, Any]]:
        """モックユーザーのデータを取得

        Args:
            count (int): モックユーザー数
            is_superuser (bool): スーパーユーザーかどうか
            invalid (bool): 無効なデータかどうか

        Returns:
            List[Dict[str, Any]]: モックユーザーのデータ
        """
        generator = DataGenerator()
        users = generator.generate_user_data(count, is_superuser, invalid)
        return [
            {
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser,
            }
            for user in users
        ]

    @staticmethod
    def get_mock_item_data(
        count: int = 1,
        owner_id: Optional[int] = None,
        invalid: bool = False
    ) -> List[Dict[str, Any]]:
        """モックアイテムのデータを取得

        Args:
            count (int): モックアイテム数
            owner_id (Optional[int]): 所有者のID
            invalid (bool): 無効なデータかどうか

        Returns:
            List[Dict[str, Any]]: モックアイテムのデータ
        """
        generator = DataGenerator()
        items = generator.generate_item_data(count, owner_id, invalid)
        return [
            {
                "title": item.title,
                "description": item.description,
                "price": item.price,
                "owner_id": item.owner_id,
            }
            for item in items
        ]

    @staticmethod
    def get_mock_auth_data(
        count: int = 1,
        invalid: bool = False
    ) -> List[Dict[str, str]]:
        """モック認証データを取得

        Args:
            count (int): モック認証情報数
            invalid (bool): 無効なデータかどうか

        Returns:
            List[Dict[str, str]]: モック認証情報
        """
        generator = DataGenerator()
        return generator.generate_auth_data(count, invalid)

    @staticmethod
    def get_mock_date_data(
        count: int = 1,
        past_days: int = 30,
        future_days: int = 30
    ) -> List[Dict[str, Any]]:
        """モック日付データを取得

        Args:
            count (int): モック日付数
            past_days (int): 過去の日数範囲
            future_days (int): 未来の日数範囲

        Returns:
            List[Dict[str, Any]]: モック日付データ
        """
        generator = DataGenerator()
        dates = generator.generate_dates(count, past_days, future_days)
        return [
            {
                "date": date,
                "timestamp": date.timestamp(),
                "iso_format": date.isoformat(),
            }
            for date in dates
        ]

    @staticmethod
    def get_mock_async_session() -> AsyncMock:
        """モックの非同期セッションを取得

        Returns:
            AsyncMock: モックの非同期セッション
        """
        mock_session = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        return mock_session

    @staticmethod
    def get_mock_test_client() -> MagicMock:
        """モックのテストクライアントを取得

        Returns:
            MagicMock: モックのテストクライアント
        """
        mock_client = MagicMock()
        mock_client.post = MagicMock()
        mock_client.get = MagicMock()
        mock_client.put = MagicMock()
        mock_client.delete = MagicMock()
        return mock_client

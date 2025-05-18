"""テストデータバリデーションモジュール"""

from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

from ..schemas import ItemCreate, UserCreate


class DataValidator:
    """テストデータバリデーションクラス"""

    @staticmethod
    def validate_user_data(data: Dict[str, Any]) -> UserCreate:
        """ユーザーのデータをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ

        Returns:
            UserCreate: バリデーションされたユーザーのデータ

        Raises:
            HTTPException: バリデーションエラー
        """
        try:
            return UserCreate(**data)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

    @staticmethod
    def validate_item_data(data: Dict[str, Any]) -> ItemCreate:
        """アイテムのデータをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ

        Returns:
            ItemCreate: バリデーションされたアイテムのデータ

        Raises:
            HTTPException: バリデーションエラー
        """
        try:
            return ItemCreate(**data)
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

    @staticmethod
    def validate_auth_data(data: Dict[str, str]) -> Dict[str, str]:
        """認証データをバリデーション

        Args:
            data (Dict[str, str]): バリデーション対象のデータ

        Returns:
            Dict[str, str]: バリデーションされた認証データ

        Raises:
            HTTPException: バリデーションエラー
        """
        if not all(key in data for key in ["email", "password"]):
            raise HTTPException(
                status_code=422,
                detail="Missing required fields: email, password"
            )
        return data

    @staticmethod
    def validate_date_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """日付データをバリデーション

        Args:
            data (Dict[str, Any]): バリデーション対象のデータ

        Returns:
            Dict[str, Any]: バリデーションされた日付データ

        Raises:
            HTTPException: バリデーションエラー
        """
        try:
            date = data.get("date")
            if not date:
                raise ValueError("Date is required")
            return data
        except ValueError as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

    @staticmethod
    def validate_batch_data(
        data_list: List[Dict[str, Any]],
        validator: callable
    ) -> List[Dict[str, Any]]:
        """複数のデータを一括でバリデーション

        Args:
            data_list (List[Dict[str, Any]]): バリデーション対象のデータリスト
            validator (callable): バリデーション関数

        Returns:
            List[Dict[str, Any]]: バリデーションされたデータリスト

        Raises:
            HTTPException: バリデーションエラー
        """
        validated_data = []
        for data in data_list:
            try:
                validated = validator(data)
                validated_data.append(validated)
            except HTTPException as e:
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"Validation failed for data: {data}. Error: {e.detail}"
                )
        return validated_data

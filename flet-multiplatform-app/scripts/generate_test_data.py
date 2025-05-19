"""テストデータ生成スクリプト"""

import json
import logging
import os
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/test_data_generation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# テストデータジェネレーターをインポート
sys.path.append(str(Path(__file__).parent.parent / "src"))
from backend.tests.data.data_generation_optimizer import (
    DataGenerationOptimizer,
    GenerationPattern,
    GenerationStrategy,
)


class TestDataGenerator:
    """テストデータ生成クラス"""

    def __init__(self):
        """初期化"""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.data_dir = self.project_root / "test_data"
        self.data_dir.mkdir(exist_ok=True)

        # データ生成の設定
        self.generation_configs = {
            "user": {
                "count": 100,
                "strategy": GenerationStrategy.RANDOM,
                "pattern": GenerationPattern.NORMAL,
                "params": {
                    "username": {"min_length": 5, "max_length": 20},
                    "email": {"domain": "example.com"},
                    "password": {"min_length": 8, "max_length": 30},
                    "is_active": {"true_probability": 0.9},
                },
            },
            "product": {
                "count": 50,
                "strategy": GenerationStrategy.DISTRIBUTION,
                "pattern": GenerationPattern.UNIFORM,
                "params": {
                    "name": {"prefix": "Product_", "min_length": 5, "max_length": 30},
                    "price": {"min": 10.0, "max": 1000.0, "decimal_places": 2},
                    "stock": {"min": 0, "max": 1000},
                    "is_available": {"true_probability": 0.8},
                },
            },
            "order": {
                "count": 200,
                "strategy": GenerationStrategy.CORRELATION,
                "pattern": GenerationPattern.NORMAL,
                "params": {
                    "order_date": {
                        "start_date": "2023-01-01",
                        "end_date": "2023-12-31",
                        "distribution": "uniform",
                    },
                    "total_amount": {
                        "min": 10.0,
                        "max": 5000.0,
                        "distribution": "normal",
                        "mean": 500.0,
                        "std_dev": 300.0,
                    },
                    "status": {
                        "values": [
                            "pending",
                            "processing",
                            "shipped",
                            "delivered",
                            "cancelled",
                        ],
                        "probabilities": [0.1, 0.2, 0.3, 0.35, 0.05],
                    },
                },
            },
        }

    def _generate_users(self, count: int) -> List[Dict[str, Any]]:
        """ユーザーデータを生成

        Args:
            count: 生成するユーザー数

        Returns:
            生成されたユーザーデータのリスト
        """
        logger.info(f"Generating {count} test users...")

        # データ生成の設定
        config = self.generation_configs["user"]
        optimizer = DataGenerationOptimizer()

        # データを生成
        users = []
        for i in range(count):
            user = {
                "id": str(uuid.uuid4()),
                "username": f"user_{i+1}",
                "email": f"user_{i+1}@example.com",
                "password_hash": f"hashed_password_{i+1}",
                "is_active": random.random() < 0.9,  # 90%の確率で有効
                "created_at": self._random_datetime(
                    "2022-01-01", "2023-12-31"
                ).isoformat(),
                "updated_at": self._random_datetime(
                    "2022-01-01", "2023-12-31"
                ).isoformat(),
            }
            users.append(user)

        return users

    def _generate_products(self, count: int) -> List[Dict[str, Any]]:
        """商品データを生成

        Args:
            count: 生成する商品数

        Returns:
            生成された商品データのリスト
        """
        logger.info(f"Generating {count} test products...")

        # データ生成の設定
        categories = ["Electronics", "Books", "Clothing", "Home", "Sports", "Toys"]

        # データを生成
        products = []
        for i in range(count):
            product = {
                "id": str(uuid.uuid4()),
                "name": f"Product {i+1}",
                "description": f"This is a test product {i+1}",
                "price": round(random.uniform(10.0, 1000.0), 2),
                "category": random.choice(categories),
                "stock": random.randint(0, 1000),
                "is_available": random.random() < 0.8,  # 80%の確率で利用可能
                "created_at": self._random_datetime(
                    "2022-01-01", "2023-12-31"
                ).isoformat(),
                "updated_at": self._random_datetime(
                    "2022-01-01", "2023-12-31"
                ).isoformat(),
            }
            products.append(product)

        return products

    def _generate_orders(
        self, count: int, users: List[Dict[str, Any]], products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """注文データを生成

        Args:
            count: 生成する注文数
            users: ユーザーリスト
            products: 商品リスト

        Returns:
            生成された注文データのリスト
        """
        logger.info(f"Generating {count} test orders...")

        statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]

        # データを生成
        orders = []
        for i in range(count):
            # ランダムなユーザーを選択
            user = random.choice(users)

            # 注文日を生成（過去2年間のランダムな日付）
            order_date = self._random_datetime("2022-01-01", "2023-12-31")

            # ステータスを決定
            status = random.choices(
                statuses, weights=[0.1, 0.2, 0.3, 0.35, 0.05], k=1  # 確率の重み
            )[0]

            # 配送予定日を計算（注文日から1〜7日後）
            shipping_date = order_date + timedelta(days=random.randint(1, 7))

            # 合計金額を計算
            total_amount = round(random.uniform(10.0, 5000.0), 2)

            order = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "order_date": order_date.isoformat(),
                "shipping_date": shipping_date.isoformat(),
                "status": status,
                "total_amount": total_amount,
                "shipping_address": f"{random.randint(1, 999)} Test St, Test City, TS {random.randint(10000, 99999)}",
                "created_at": order_date.isoformat(),
                "updated_at": order_date.isoformat(),
            }
            orders.append(order)

        return orders

    def _generate_order_items(
        self, orders: List[Dict[str, Any]], products: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """注文明細データを生成

        Args:
            orders: 注文リスト
            products: 商品リスト

        Returns:
            生成された注文明細データのリスト
        """
        logger.info("Generating order items...")

        order_items = []
        for order in orders:
            # 1注文あたり1〜5個の商品をランダムに選択
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))

            for product in selected_products:
                quantity = random.randint(1, 10)
                price = product["price"]

                order_item = {
                    "id": str(uuid.uuid4()),
                    "order_id": order["id"],
                    "product_id": product["id"],
                    "quantity": quantity,
                    "unit_price": price,
                    "total_price": round(price * quantity, 2),
                }
                order_items.append(order_item)

        return order_items

    def _random_datetime(self, start_date: str, end_date: str) -> datetime:
        """指定された範囲内のランダムな日時を生成

        Args:
            start_date: 開始日 (YYYY-MM-DD形式)
            end_date: 終了日 (YYYY-MM-DD形式)

        Returns:
            ランダムな日時
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        delta = end - start
        random_days = random.randrange(delta.days)
        random_seconds = random.randrange(24 * 60 * 60)  # 1日分の秒数

        return start + timedelta(days=random_days, seconds=random_seconds)

    def _save_to_file(self, data: List[Dict[str, Any]], filename: str) -> None:
        """データをJSONファイルに保存

        Args:
            data: 保存するデータ
            filename: ファイル名
        """
        filepath = self.data_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(data)} records to {filepath}")

    def generate_test_data(self) -> None:
        """テストデータを生成して保存"""
        try:
            logger.info("Starting test data generation...")

            # 1. ユーザーデータを生成
            users = self._generate_users(100)
            self._save_to_file(users, "users.json")

            # 2. 商品データを生成
            products = self._generate_products(50)
            self._save_to_file(products, "products.json")

            # 3. 注文データを生成
            orders = self._generate_orders(200, users, products)
            self._save_to_file(orders, "orders.json")

            # 4. 注文明細データを生成
            order_items = self._generate_order_items(orders, products)
            self._save_to_file(order_items, "order_items.json")

            logger.info("Test data generation completed successfully!")

        except Exception as e:
            logger.error(f"Failed to generate test data: {e}")
            raise


def main():
    """メイン関数"""
    try:
        generator = TestDataGenerator()
        generator.generate_test_data()
        print("\n✅ Test data generated successfully!")
    except Exception as e:
        print(f"\n❌ Error generating test data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

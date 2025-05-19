"""パフォーマンステスト用のテストデータ生成スクリプト"""

import json
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from faker import Faker

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/perf_test_data_generation.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PerfTestDataGenerator:
    """パフォーマンステスト用テストデータ生成クラス"""

    def __init__(self, output_dir: str = "test_data/perf"):
        """初期化"""
        self.fake = Faker()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_users(self, count: int = 1000) -> List[Dict[str, Any]]:
        """テストユーザーデータを生成"""
        logger.info(f"Generating {count} test users...")
        users = []

        for i in range(1, count + 1):
            user = {
                "id": i,
                "username": f"testuser_{i}",
                "email": f"user_{i}@example.com",
                "password": f"Password123!{i}",
                "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(),
                "is_active": True,
                "created_at": self.fake.date_time_this_year().isoformat(),
                "updated_at": self.fake.date_time_this_month().isoformat(),
            }
            users.append(user)

        return users

    def generate_categories(self, count: int = 20) -> List[Dict[str, Any]]:
        """商品カテゴリーデータを生成"""
        logger.info(f"Generating {count} product categories...")
        categories = []

        for i in range(1, count + 1):
            category = {
                "id": i,
                "name": f"Category {i}",
                "description": self.fake.sentence(),
                "slug": f"category-{i}",
                "is_active": True,
                "created_at": self.fake.date_time_this_year().isoformat(),
            }
            categories.append(category)

        return categories

    def generate_products(
        self, count: int = 1000, category_count: int = 20
    ) -> List[Dict[str, Any]]:
        """商品データを生成"""
        logger.info(f"Generating {count} products...")
        products = []

        # 価格の分布を正規分布で生成（平均100ドル、標準偏差50ドル）
        prices = np.random.normal(100, 50, count).clip(1, 1000)

        for i in range(1, count + 1):
            product = {
                "id": i,
                "name": f"Product {i}",
                "description": self.fake.paragraph(nb_sentences=3),
                "price": round(float(prices[i - 1]), 2),
                "stock": random.randint(0, 1000),
                "category_id": random.randint(1, category_count),
                "sku": f"SKU-{random.randint(10000, 99999)}",
                "is_active": random.choices([True, False], weights=[0.9, 0.1])[0],
                "created_at": self.fake.date_time_this_year().isoformat(),
                "updated_at": self.fake.date_time_this_month().isoformat(),
            }
            products.append(product)

        return products

    def generate_orders(
        self, count: int = 5000, user_count: int = 1000
    ) -> List[Dict[str, Any]]:
        """注文データを生成"""
        logger.info(f"Generating {count} orders...")
        orders = []

        for i in range(1, count + 1):
            order_date = self.fake.date_time_between(start_date="-1y", end_date="now")

            order = {
                "id": i,
                "user_id": random.randint(1, user_count),
                "order_number": f"ORD-{order_date.strftime('%Y%m%d')}-{i:06d}",
                "status": random.choice(
                    ["pending", "processing", "shipped", "delivered", "cancelled"]
                ),
                "total_amount": 0,  # 後で計算
                "shipping_address": self.fake.address(),
                "billing_address": self.fake.address(),
                "created_at": order_date.isoformat(),
                "updated_at": (
                    order_date + timedelta(days=random.randint(0, 7))
                ).isoformat(),
            }
            orders.append(order)

        return orders

    def generate_order_items(
        self, order_count: int = 5000, product_count: int = 1000
    ) -> List[Dict[str, Any]]:
        """注文明細データを生成"""
        logger.info(f"Generating order items...")
        order_items = []

        for order_id in range(1, order_count + 1):
            # 1注文あたり1〜5個の商品をランダムに選択
            item_count = random.randint(1, 5)
            product_ids = random.sample(range(1, product_count + 1), item_count)

            for item_num in range(1, item_count + 1):
                product_id = product_ids[item_num - 1]
                quantity = random.randint(1, 5)
                price = round(random.uniform(10, 1000), 2)

                order_item = {
                    "id": len(order_items) + 1,
                    "order_id": order_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": price,
                    "total_price": round(price * quantity, 2),
                    "created_at": self.fake.date_time_this_year().isoformat(),
                }
                order_items.append(order_item)

        return order_items

    def save_to_file(self, data: List[Dict[str, Any]], filename: str) -> str:
        """データをJSONファイルに保存"""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(data)} records to {filepath}")
        return str(filepath)

    def generate_all(self):
        """すべてのテストデータを生成"""
        try:
            # ユーザーデータの生成
            users = self.generate_users(count=1000)
            self.save_to_file(users, "users.json")

            # カテゴリーデータの生成
            categories = self.generate_categories(count=20)
            self.save_to_file(categories, "categories.json")

            # 商品データの生成
            products = self.generate_products(
                count=1000, category_count=len(categories)
            )
            self.save_to_file(products, "products.json")

            # 注文データの生成
            orders = self.generate_orders(count=5000, user_count=len(users))
            self.save_to_file(orders, "orders.json")

            # 注文明細データの生成
            order_items = self.generate_order_items(
                order_count=len(orders), product_count=len(products)
            )
            self.save_to_file(order_items, "order_items.json")

            logger.info("All test data has been generated successfully!")
            return True

        except Exception as e:
            logger.error(f"Error generating test data: {str(e)}", exc_info=True)
            return False


def main():
    """メイン関数"""
    try:
        generator = PerfTestDataGenerator()
        success = generator.generate_all()

        if success:
            print("\nTest data generation completed successfully!")
            print(f"Output directory: {generator.output_dir.absolute()}")
        else:
            print("\nTest data generation failed. Please check the logs for details.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        print(f"\nAn error occurred: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())

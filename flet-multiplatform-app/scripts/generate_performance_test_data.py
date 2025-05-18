"""パフォーマンステスト用のテストデータ生成スクリプト"""

import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/performance_test_data_generation.log')
    ]
)
logger = logging.getLogger(__name__)

class PerformanceDataGenerator:
    """パフォーマンステスト用のテストデータ生成クラス"""

    def __init__(self, output_dir: str = 'test_data/performance'):
        """初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # テストデータの設定
        self.configs = {
            'small': {
                'users': 100,
                'products': 1000,
                'orders': 10000,
                'customers': 1000,
                'transactions': 50000
            },
            'medium': {
                'users': 1000,
                'products': 10000,
                'orders': 100000,
                'customers': 5000,
                'transactions': 500000
            },
            'large': {
                'users': 10000,
                'products': 50000,
                'orders': 1000000,
                'customers': 50000,
                'transactions': 5000000
            }
        }
        
        # テストデータのオプション
        self.user_roles = ['admin', 'manager', 'user', 'guest']
        self.product_categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Toys', 'Sports', 'Beauty', 'Food']
        self.order_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        self.payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'cash_on_delivery']
    
    def generate_name(self, prefix: str = '') -> str:
        """ランダムな名前を生成"""
        names = [
            'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry',
            'Ivy', 'Jack', 'Karen', 'Liam', 'Mia', 'Noah', 'Olivia', 'Peter',
            'Quinn', 'Rachel', 'Steve', 'Tina', 'Uma', 'Victor', 'Wendy', 'Xander', 'Yvonne', 'Zack'
        ]
        return f"{prefix}_{random.choice(names)}{random.randint(1, 1000)}"
    
    def generate_email(self, name: str) -> str:
        """メールアドレスを生成"""
        domains = ['example.com', 'test.org', 'demo.net', 'sample.io']
        return f"{name.lower().replace(' ', '.')}@{random.choice(domains)}"
    
    def generate_address(self) -> Dict[str, str]:
        """住所を生成"""
        streets = ['Main St', 'Oak Ave', 'Pine St', 'Maple Dr', 'Cedar Ln', 'Elm St', 'Birch Blvd', 'Spruce Way']
        cities = ['Tokyo', 'Osaka', 'Kyoto', 'Yokohama', 'Nagoya', 'Sapporo', 'Kobe', 'Fukuoka']
        return {
            'street': f"{random.randint(1, 999)} {random.choice(streets)}",
            'city': random.choice(cities),
            'state': 'Kanto',
            'postal_code': f"{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            'country': 'Japan'
        }
    
    def generate_phone(self) -> str:
        """電話番号を生成"""
        return f"0{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    
    def generate_date(self, start_date: str, end_date: str) -> str:
        """指定範囲内の日付を生成"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        delta = end - start
        random_days = random.randint(0, delta.days)
        return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')
    
    def generate_users(self, count: int) -> List[Dict[str, Any]]:
        """ユーザーデータを生成"""
        logger.info(f"Generating {count} users...")
        users = []
        
        for i in range(1, count + 1):
            user = {
                'id': i,
                'username': self.generate_name('user'),
                'email': f"user{i}@example.com",
                'first_name': self.generate_name(),
                'last_name': self.generate_name(),
                'is_active': random.choice([True, True, True, True, False]),  # 80% true
                'date_joined': self.generate_date('2020-01-01', '2023-12-31'),
                'role': random.choices(
                    self.user_roles,
                    weights=[0.05, 0.15, 0.75, 0.05],  # 確率を調整
                    k=1
                )[0],
                'metadata': {
                    'last_login': self.generate_date('2023-01-01', '2023-12-31'),
                    'login_count': random.randint(1, 1000)
                }
            }
            users.append(user)
        
        return users
    
    def generate_products(self, count: int) -> List[Dict[str, Any]]:
        """商品データを生成"""
        logger.info(f"Generating {count} products...")
        products = []
        
        for i in range(1, count + 1):
            price = round(random.uniform(10.0, 1000.0), 2)
            product = {
                'id': i,
                'name': f"Product {i}",
                'description': f"This is a test product {i} for performance testing",
                'price': price,
                'discounted_price': round(price * random.uniform(0.7, 0.95), 2),
                'category': random.choice(self.product_categories),
                'stock': random.randint(0, 1000),
                'rating': round(random.uniform(1.0, 5.0), 1),
                'is_available': random.choice([True, True, True, True, False]),  # 80% true
                'created_at': self.generate_date('2020-01-01', '2023-12-31'),
                'tags': random.sample(['sale', 'new', 'popular', 'limited'], k=random.randint(0, 3)),
                'metadata': {
                    'views': random.randint(0, 10000),
                    'purchases': random.randint(0, 5000)
                }
            }
            products.append(product)
        
        return products
    
    def generate_orders(self, count: int, customer_count: int, product_count: int) -> List[Dict[str, Any]]:
        """注文データを生成"""
        logger.info(f"Generating {count} orders...")
        orders = []
        
        for i in range(1, count + 1):
            order_date = self.generate_date('2023-01-01', '2023-12-31')
            status = random.choices(
                self.order_statuses,
                weights=[0.1, 0.2, 0.3, 0.35, 0.05],  # 確率を調整
                k=1
            )[0]
            
            # 注文明細の生成
            order_items = []
            num_items = random.randint(1, 10)
            total_amount = 0.0
            
            for _ in range(num_items):
                product_id = random.randint(1, product_count)
                quantity = random.randint(1, 5)
                price = round(random.uniform(10.0, 1000.0), 2)
                subtotal = round(price * quantity, 2)
                total_amount += subtotal
                
                order_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': price,
                    'subtotal': subtotal
                })
            
            total_amount = round(total_amount, 2)
            
            order = {
                'id': i,
                'customer_id': random.randint(1, customer_count),
                'order_date': order_date,
                'status': status,
                'total_amount': total_amount,
                'shipping_address': self.generate_address(),
                'payment_method': random.choice(self.payment_methods),
                'items': order_items,
                'metadata': {
                    'discount': round(random.uniform(0, 0.3) * total_amount, 2) if random.random() < 0.3 else 0.0,
                    'tax': round(total_amount * 0.1, 2)  # 10% tax
                }
            }
            
            # 配送日と支払い日の設定
            if status in ['shipped', 'delivered']:
                order['shipped_date'] = self.generate_date(order_date, '2023-12-31')
                if status == 'delivered':
                    order['delivered_date'] = self.generate_date(order['shipped_date'], '2023-12-31')
            
            orders.append(order)
        
        return orders
    
    def generate_customers(self, count: int) -> List[Dict[str, Any]]:
        """顧客データを生成"""
        logger.info(f"Generating {count} customers...")
        customers = []
        
        for i in range(1, count + 1):
            customer = {
                'id': i,
                'first_name': self.generate_name(),
                'last_name': self.generate_name(),
                'email': self.generate_email(f"customer{i}"),
                'phone': self.generate_phone(),
                'address': self.generate_address(),
                'join_date': self.generate_date('2018-01-01', '2023-12-31'),
                'segment': random.choice(['new', 'returning', 'vip', 'churned']),
                'lifetime_value': round(random.uniform(0, 10000.0), 2),
                'metadata': {
                    'last_purchase': self.generate_date('2023-01-01', '2023-12-31'),
                    'total_orders': random.randint(0, 100),
                    'total_spent': round(random.uniform(0, 50000.0), 2)
                }
            }
            customers.append(customer)
        
        return customers
    
    def generate_transactions(self, count: int, customer_count: int) -> List[Dict[str, Any]]:
        """取引データを生成"""
        logger.info(f"Generating {count} transactions...")
        transactions = []
        transaction_types = ['purchase', 'refund', 'payment', 'withdrawal', 'deposit']
        
        for i in range(1, count + 1):
            transaction_type = random.choices(
                transaction_types,
                weights=[0.6, 0.1, 0.15, 0.1, 0.05],  # 確率を調整
                k=1
            )[0]
            
            amount = round(random.uniform(10.0, 5000.0), 2)
            if transaction_type in ['refund', 'withdrawal']:
                amount = -amount
            
            transaction = {
                'id': i,
                'transaction_id': f"TXN{random.randint(100000, 999999)}",
                'customer_id': random.randint(1, customer_count) if customer_count > 0 else None,
                'type': transaction_type,
                'amount': amount,
                'currency': 'JPY',
                'status': random.choice(['completed', 'pending', 'failed', 'refunded']),
                'transaction_date': self.generate_date('2023-01-01', '2023-12-31'),
                'payment_method': random.choice(self.payment_methods),
                'metadata': {
                    'processor': random.choice(['stripe', 'paypal', 'bank_transfer', 'cash']),
                    'fee': round(abs(amount) * random.uniform(0.01, 0.03), 2)  # 1-3% fee
                }
            }
            
            if transaction_type in ['purchase', 'refund']:
                transaction['order_id'] = f"ORD{random.randint(10000, 99999)}"
            
            transactions.append(transaction)
        
        return transactions
    
    def save_to_json(self, data: List[Dict], filename: str) -> str:
        """データをJSONファイルに保存"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(data)} records to {filepath}")
        return str(filepath)
    
    def generate_all(self, dataset_size: str = 'small') -> Dict[str, str]:
        """すべてのテストデータを生成"""
        if dataset_size not in self.configs:
            raise ValueError(f"Invalid dataset size. Choose from: {', '.join(self.configs.keys())}")
        
        config = self.configs[dataset_size]
        logger.info(f"Generating {dataset_size} dataset with config: {config}")
        
        # 各データを生成
        users = self.generate_users(config['users'])
        customers = self.generate_customers(config['customers'])
        products = self.generate_products(config['products'])
        orders = self.generate_orders(config['orders'], len(customers), len(products))
        transactions = self.generate_transactions(config['transactions'], len(customers))
        
        # ファイルに保存
        result = {
            'users': self.save_to_json(users, 'users'),
            'customers': self.save_to_json(customers, 'customers'),
            'products': self.save_to_json(products, 'products'),
            'orders': self.save_to_json(orders, 'orders'),
            'transactions': self.save_to_json(transactions, 'transactions')
        }
        
        # メタデータを保存
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'dataset_size': dataset_size,
            'record_counts': {
                'users': len(users),
                'customers': len(customers),
                'products': len(products),
                'orders': len(orders),
                'transactions': len(transactions)
            }
        }
        
        metadata_path = self.output_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Test data generation completed. Metadata saved to {metadata_path}")
        return result

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='パフォーマンステスト用のテストデータを生成')
    parser.add_argument('--size', type=str, default='small', 
                       choices=['small', 'medium', 'large'],
                       help='生成するデータセットのサイズ (small, medium, large)')
    parser.add_argument('--output-dir', type=str, default='test_data/performance',
                       help='出力ディレクトリのパス')
    
    args = parser.parse_args()
    
    try:
        generator = PerformanceDataGenerator(output_dir=args.output_dir)
        result = generator.generate_all(args.size)
        print(f"\nTest data generation completed successfully!")
        print(f"Files generated in: {args.output_dir}")
    except Exception as e:
        logger.error(f"Error generating test data: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

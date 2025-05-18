"""テスト用データベース初期化スクリプト"""

import json
import logging
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_db_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestDatabaseInitializer:
    """テスト用データベース初期化クラス"""

    def __init__(self):
        """初期化"""
        self.project_root = Path(__file__).parent.parent.resolve()
        self.config = self._load_config()
        self.db_path = self._get_db_path()

    def _load_config(self) -> Dict[str, Any]:
        """設定をロード"""
        config_path = self.project_root / "src" / "backend" / "tests" / "config" / "test_config.py"

        if not config_path.exists():
            logger.warning(f"Test config file not found: {config_path}")
            return {}

        # 設定ファイルを読み込む
        config = {}
        try:
            with open(config_path, encoding='utf-8') as f:
                # 簡易的な設定のパース
                for line in f:
                    line = line.strip()
                    if line.startswith('DATABASE_URL'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip().strip('"\'')
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

        return config

    def _get_db_path(self) -> Path:
        """データベースのパスを取得"""
        # 設定からデータベースのURLを取得
        db_url = self.config.get('DATABASE_URL', '')

        # SQLiteの場合はファイルパスを抽出
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            return Path(db_path)

        # デフォルトのパス
        return self.project_root / 'test.db'

    def _create_database(self) -> None:
        """データベースを作成"""
        # データベースディレクトリが存在しない場合は作成
        db_dir = self.db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)

        # 既存のデータベースをバックアップ
        if self.db_path.exists():
            backup_path = self.db_path.with_suffix(f'.{datetime.now().strftime("%Y%m%d%H%M%S")}.bak')
            logger.info(f"Backing up existing database to {backup_path}")
            self.db_path.rename(backup_path)

        # 新しいデータベースを作成
        logger.info(f"Creating new database at {self.db_path}")
        conn = sqlite3.connect(str(self.db_path))
        conn.close()

    def _create_tables(self) -> None:
        """テーブルを作成"""
        # マイグレーションスクリプトが存在する場合は実行
        migration_dir = self.project_root / 'migrations'
        if migration_dir.exists():
            self._run_migrations()
            return

        # マイグレーションスクリプトが存在しない場合は直接テーブルを作成
        schema_file = self.project_root / 'schema.sql'
        if schema_file.exists():
            self._create_tables_from_schema(schema_file)
            return

        # スキーマファイルも存在しない場合は最小限のテーブルを作成
        self._create_minimal_tables()

    def _run_migrations(self) -> None:
        """マイグレーションを実行"""
        logger.info("Running database migrations...")

        try:
            # 仮想環境のPythonを使用してAlembicを実行
            python_path = os.path.join(os.path.dirname(sys.executable), 'python')
            subprocess.run(
                [python_path, '-m', 'alembic', 'upgrade', 'head'],
                check=True,
                cwd=str(self.project_root)
            )
            logger.info("Database migrations completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to run migrations: {e}")
            raise

    def _create_tables_from_schema(self, schema_file: Path) -> None:
        """スキーマファイルからテーブルを作成"""
        logger.info(f"Creating tables from schema file: {schema_file}")

        try:
            with open(schema_file, encoding='utf-8') as f:
                schema_sql = f.read()

            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # トランザクション内で実行
            cursor.executescript(schema_sql)
            conn.commit()

            logger.info("Tables created successfully.")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def _create_minimal_tables(self) -> None:
        """最小限のテーブルを作成"""
        logger.info("Creating minimal test tables...")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # ユーザーテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # ロールテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # ユーザーロール関連テーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
                )
            ''')

            # テストデータを挿入
            self._insert_test_data(cursor)

            conn.commit()
            logger.info("Minimal test tables created successfully.")
        except Exception as e:
            logger.error(f"Failed to create minimal tables: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def _insert_test_data(self, cursor) -> None:
        """テストデータを挿入"""
        logger.info("Inserting test data...")

        # ロールを挿入
        roles = [
            (1, 'admin', 'Administrator'),
            (2, 'user', 'Regular User'),
            (3, 'guest', 'Guest User')
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO roles (id, name, description) VALUES (?, ?, ?)',
            roles
        )

        # テストユーザーを挿入
        users = [
            (1, 'admin', 'admin@example.com', 'hashed_password_here', 1),
            (2, 'user1', 'user1@example.com', 'hashed_password_here', 1),
            (3, 'guest1', 'guest1@example.com', 'hashed_password_here', 1)
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO users (id, username, email, password_hash, is_active) VALUES (?, ?, ?, ?, ?)',
            users
        )

        # ユーザーロールを関連付け
        user_roles = [
            (1, 1),  # admin has admin role
            (2, 2),  # user1 has user role
            (3, 3)   # guest1 has guest role
        ]
        cursor.executemany(
            'INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)',
            user_roles
        )

        logger.info("Test data inserted successfully.")

    def initialize(self) -> None:
        """データベースを初期化"""
        try:
            logger.info("Starting test database initialization...")

            # 1. データベースを作成
            self._create_database()

            # 2. テーブルを作成
            self._create_tables()

            logger.info("Test database initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize test database: {e}")
            raise


def main():
    """メイン関数"""
    try:
        initializer = TestDatabaseInitializer()
        initializer.initialize()
        print("\n✅ Test database initialized successfully!")
    except Exception as e:
        print(f"\n❌ Error initializing test database: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.db.base import Base
from backend.app.db.database import engine

# テーブルを作成するためにすべてのモデルをインポートする
from backend.app.models import *
from backend.app.models.item import Item
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate


def init_db(db: Session) -> None:
    # テーブルを作成
    Base.metadata.create_all(bind=engine)

    # 初期ユーザーを作成
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user_in = UserCreate(
            email="admin@example.com",
            password="admin",
            full_name="Admin User",
            is_superuser=True,
        )
        user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_superuser=user_in.is_superuser,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # テスト用アイテムを作成
        item = Item(
            title="テストアイテム",
            description="これはテスト用のアイテムです。",
            owner_id=user.id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)


if __name__ == "__main__":
    from backend.app.db.database import SessionLocal

    print("データベースを初期化しています...")
    db = SessionLocal()
    try:
        init_db(db)
        print("データベースの初期化が完了しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        db.close()

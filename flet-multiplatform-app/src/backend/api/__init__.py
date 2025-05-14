"""APIモジュールの初期化ファイル"""

# 絶対インポートを使用
from backend.api.v1.api import api_router

__all__ = ["api_router"]

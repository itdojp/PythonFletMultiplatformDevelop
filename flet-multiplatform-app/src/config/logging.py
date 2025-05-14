"""ロギングの設定を管理するモジュール"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .settings import settings


def setup_logging() -> None:
    """ロギングの設定を行う"""
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    # フォーマッターの設定
    formatter = logging.Formatter(settings.LOG_FORMAT)

    # コンソールハンドラーの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ファイルハンドラーの設定
    log_file = Path(settings.LOG_DIR) / settings.LOG_FILE
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # サードパーティライブラリのログレベルを設定
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("flet").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """指定された名前のロガーを取得する"""
    return logging.getLogger(name)

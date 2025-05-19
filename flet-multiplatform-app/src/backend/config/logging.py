"""ロギング設定モジュール"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

from .config import settings


class JsonFormatter(jsonlogger.JsonFormatter):
    """JSON形式のログフォーマッタ"""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """ロギングの設定を行う

    Args:
        log_level: ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: ログファイルのパス (指定しない場合はコンソールに出力)
    """
    log_level = log_level or ("DEBUG" if settings.DEBUG else "INFO")
    log_file = Path(log_file) if log_file else None

    # ログディレクトリが存在しない場合は作成
    if log_file and not log_file.parent.exists():
        log_file.parent.mkdir(parents=True, exist_ok=True)

    # ログフォーマット
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    json_formatter = JsonFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        timestamp=True,
    )

    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 既存のハンドラをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # コンソールハンドラの設定
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # ファイルハンドラの設定 (ログファイルが指定されている場合)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """ロガーを取得する

    Args:
        name: ロガー名 (Noneの場合はルートロガー)

    Returns:
        logging.Logger: ロガーインスタンス
    """
    return logging.getLogger(name)

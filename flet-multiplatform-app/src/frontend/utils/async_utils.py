"""非同期処理のユーティリティ"""
import asyncio
import functools
from typing import Any, Callable, Coroutine, TypeVar, cast

from flet import Page, ProgressBar, Text

T = TypeVar("T")

class AsyncError(Exception):
    """非同期処理のエラー"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error

def handle_async_errors(
    error_message: str = "エラーが発生しました",
    show_error: bool = True,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """非同期処理のエラーハンドリングデコレータ"""
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if show_error:
                    # エラーメッセージを表示する処理を実装
                    pass
                raise AsyncError(error_message, e) from e
        return cast(Callable[..., Coroutine[Any, Any, T]], wrapper)
    return decorator

class LoadingManager:
    """ローディング状態管理クラス"""
    def __init__(self, page: Page):
        self.page = page
        self._loading_count = 0
        self._progress_bar = ProgressBar(visible=False)
        self._loading_text = Text("読み込み中...", visible=False)
        self.page.add(self._progress_bar, self._loading_text)

    def start_loading(self) -> None:
        """ローディング開始"""
        self._loading_count += 1
        if self._loading_count == 1:
            self._progress_bar.visible = True
            self._loading_text.visible = True
            self.page.update()

    def stop_loading(self) -> None:
        """ローディング終了"""
        self._loading_count = max(0, self._loading_count - 1)
        if self._loading_count == 0:
            self._progress_bar.visible = False
            self._loading_text.visible = False
            self.page.update()

    async def with_loading(self, coro: Coroutine[Any, Any, T]) -> T:
        """ローディング状態で非同期処理を実行"""
        self.start_loading()
        try:
            return await coro
        finally:
            self.stop_loading()

def with_loading(loading_manager: LoadingManager) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T]]]:
    """ローディング状態で非同期処理を実行するデコレータ"""
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await loading_manager.with_loading(func(*args, **kwargs))
        return cast(Callable[..., Coroutine[Any, Any, T]], wrapper)
    return decorator 
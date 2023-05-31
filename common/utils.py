from typing import Callable
import asyncio


def is_async_callable(func: Callable) -> bool:
    """Check if function is async."""
    return asyncio.iscoroutinefunction(func) or asyncio.iscoroutine(func)


def is_valid_url(url: str) -> bool:
    """Check if url is valid."""
    return url.startswith('http://') or url.startswith('https://')

"""
异步工具模块
提供异步操作的安全包装和工具函数
"""

import asyncio
import logging
import streamlit as st
from typing import Any, Callable, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def safe_run_async(coro_func: Callable, *args, **kwargs) -> Any:
    """
    安全地运行异步函数

    Args:
        coro_func: 异步函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数执行结果，如果出错则返回None
    """
    try:
        # 检查是否已经在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，使用create_task
            if loop.is_running():
         import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(coro_func(*args, **kwargs))
        except RuntimeError:
            # 没有运行的事件循环，直接使用asyncio.run
            return asyncio.run(coro_func(*args, **kwargs))

    except Exception as e:
        logger.error(f"异步函数执行失败: {e}", exc_info=True)
        st.error(f"操作失败: {str(e)}")
        return None


def async_cache(ttl: int = 300):
    """
    异步函数缓存装饰器

    Args:
        ttl: 缓存时间（秒）
    """
    def decorator(func):
        cache = {}

        @wraps(func)
        async def wrapper(*args, **kwargs):
         import time
         import hashlib

            # 生成缓存键
            key_data = str(args) + str(sorted(kwargs.items()))
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # 检查缓存
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())

            # 清理过期缓存
            current_time = time.time()
            expired_keys = [k for k, (_, ts) in cache.items() if current_time - ts >= ttl]
            for k in expired_keys:
                del cache[k]

            return result

        return wrapper
    return decorator


def run_in_background(coro_func: Callable, *args, **kwargs):
    """
    在后台运行异步函数，不阻塞主线程

    Args:
        coro_func: 异步函数
        *args: 位置参数
        **kwargs: 关键字参数
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，创建任务
            task = loop.create_task(coro_func(*args, **kwargs))
            return task
        else:
            # 如果没有事件循环，启动新的
            return asyncio.run(coro_func(*args, **kwargs))
    except Exception as e:
        logger.error(f"后台任务执行失败: {e}", exc_info=True)
        return None


async def timeout_wrapper(coro_func: Callable, timeout: float = 30.0, *args, **kwargs):
    """
    为异步函数添加超时控制

    Args:
        coro_func: 异步函数
        timeout: 超时时间（秒）
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        函数执行结果，超时则抛出TimeoutError
    """
    try:
        return await asyncio.wait_for(coro_func(*args, **kwargs), timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"异步函数执行超时: {coro_func.__name__}")
        raise TimeoutError(f"操作超时 ({timeout}秒)")


def batch_async_execute(coro_funcs: list, max_concurrent: int = 5) -> list:
    """
    批量执行异步函数，控制并发数量

    Args:
        coro_funcs: 异步函数列表
        max_concurrent: 最大并发数

    Returns:
        执行结果列表
    """
    async def _batch_execute():
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _execute_with_semaphore(coro):
            async with semaphore:
                try:
                    return await coro
                except Exception as e:
                    logger.error(f"批量执行中的函数失败: {e}")
                    return None

        tasks = [_execute_with_semaphore(coro) for coro in coro_funcs]
        return await asyncio.gather(*tasks, return_exceptions=True)

    return safe_run_async(_batch_execute)

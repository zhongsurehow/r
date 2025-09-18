"""
优化的缓存管理器
提供高性能的异步缓存、批量操作和智能过期机制
"""

import asyncio
import time
import hashlib
import pickle
import weakref
from typing import Any, Dict, Optional, Callable, Union, List
from functools import wraps
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    timestamp: float
    ttl: float
    access_count: int = 0
    last_access: float = 0

    @property
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.timestamp > self.ttl

    def touch(self):
        """更新访问时间"""
        self.access_count += 1
        self.last_access = time.time()


class OptimizedAsyncCache:
    """优化的异步缓存管理器"""

    def __init__(self, max_size: int = 1000, cleanup_interval: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._max_size = max_size
        self._cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0
        }

    async def __aenter__(self):
        """异步上下文管理器入口"""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """生成缓存键"""
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats['misses'] += 1
                return None

            if entry.is_expired:
                del self._cache[key]
                self._stats['misses'] += 1
                return None

            entry.touch()
            self._stats['hits'] += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: float = 300):
        """设置缓存值"""
        async with self._lock:
            # 检查缓存大小限制
            if len(self._cache) >= self._max_size:
                await self._evict_lru()

            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl
            )

    async def _evict_lru(self):
        """驱逐最少使用的缓存项"""
        if not self._cache:
            return

        # 找到最少使用的项
        lru_key = min(
            self._cache.keys(),
            key=lambda k: (self._cache[k].access_count, self._cache[k].last_access)
        )
        del self._cache[lru_key]
        self._stats['evictions'] += 1

    async def _periodic_cleanup(self):
        """定期清理过期缓存"""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"缓存清理失败: {e}")

    async def _cleanup_expired(self):
        """清理过期缓存"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                self._stats['cleanups'] += 1
                logger.debug(f"清理了 {len(expired_keys)} 个过期缓存项")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            **self._stats,
            'cache_size': len(self._cache),
            'hit_rate': hit_rate,
            'max_size': self._max_size
        }

    async def clear(self):
        """清空缓存"""
        async with self._lock:
            self._cache.clear()


# 全局缓存实例
_global_cache = OptimizedAsyncCache()


def async_cached(ttl: float = 300, key_prefix: str = ""):
    """
    优化的异步缓存装饰器
    
    Args:
        ttl: 缓存时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            cache_key = _global_cache._generate_key(func_name, args, kwargs)

            # 尝试从缓存获取
            cached_value = await _global_cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # 执行函数并缓存结果
            try:
                result = await func(*args, **kwargs)
                await _global_cache.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"缓存函数 {func_name} 执行失败: {e}")
                raise

        return wrapper
    return decorator


class BatchProcessor:
    """批量处理器，优化并发操作"""

    def __init__(self, max_concurrent: int = 10, batch_size: int = 50):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_batch(self, items: List[Any], processor: Callable) -> List[Any]:
        """
        批量处理项目
        
        Args:
            items: 要处理的项目列表
            processor: 处理函数（异步）
        
        Returns:
            处理结果列表
        """
        async def _process_with_semaphore(item):
            async with self.semaphore:
                try:
                    return await processor(item)
                except Exception as e:
                    logger.error(f"批量处理项目失败: {e}")
                    return None

        # 分批处理
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_tasks = [_process_with_semaphore(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

        return results


class MemoryOptimizer:
    """内存优化器"""

    @staticmethod
    def optimize_dataframe(df: 'pd.DataFrame') -> 'pd.DataFrame':
        """优化DataFrame内存使用"""
        import pandas as pd
        
        optimized_df = df.copy()
        
        for col in optimized_df.columns:
            col_type = optimized_df[col].dtype
            
            if col_type == 'object':
                # 尝试转换为category
                if optimized_df[col].nunique() / len(optimized_df) < 0.5:
                    optimized_df[col] = optimized_df[col].astype('category')
            elif col_type == 'int64':
                # 优化整数类型
                c_min = optimized_df[col].min()
                c_max = optimized_df[col].max()
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    optimized_df[col] = optimized_df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    optimized_df[col] = optimized_df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    optimized_df[col] = optimized_df[col].astype(np.int32)
            elif col_type == 'float64':
                # 优化浮点类型
                optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')
        
        return optimized_df

    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """获取内存使用情况"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent()
        }


# 导出主要接口
__all__ = [
    'OptimizedAsyncCache',
    'async_cached',
    'BatchProcessor',
    'MemoryOptimizer',
    '_global_cache'
]
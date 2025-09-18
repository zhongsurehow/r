"""
数据处理和缓存优化工具
提供高效的数据缓存和处理机制
"""

import pickle
import hashlib
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, Union
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class PersistentCache:
    """持久化缓存类"""

    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用MD5哈希避免文件名过长
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def _is_expired(self, cache_path: Path, ttl: int) -> bool:
        """检查缓存是否过期"""
        if not cache_path.exists():
            return True

        file_time = cache_path.stat().st_mtime
        return time.time() - file_time > ttl

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """获取缓存数据"""
        ttl = ttl or self.default_ttl
        cache_path = self._get_cache_path(key)

        if self._is_expired(cache_path, ttl):
            return None

        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存数据"""
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            logger.error(f"写入缓存失败: {e}")

    def delete(self, key: str) -> None:
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

    def clear(self) -> None:
        """清空所有缓存"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'file_count': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }

class SessionDataManager:
    """会话数据管理器"""

    @staticmethod
    def get_or_generate(key: str, generator: Callable, *args, **kwargs) -> Any:
        """从session state获取数据，如果不存在则生成"""
        if key not in st.session_state:
            st.session_state[key] = generator(*args, **kwargs)
        return st.session_state[key]

    @staticmethod
    def invalidate(key: str) -> None:
        """使session state中的数据失效"""
        if key in st.session_state:
            del st.session_state[key]

    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """获取session state内存使用情况"""
        total_items = len(st.session_state)

        # 估算内存使用（简化版本）
        estimated_size = 0
        for key, value in st.session_state.items():
            if isinstance(value, (pd.DataFrame, np.ndarray)):
                estimated_size += value.nbytes if hasattr(value, 'nbytes') else 1000
            elif isinstance(value, (list, dict)):
                estimated_size += len(str(value))
            else:
                estimated_size += 100  # 基础估算

        return {
            'total_items': total_items,
            'estimated_size_mb': estimated_size / (1024 * 1024)
        }

class DataProcessor:
    """数据处理工具"""

    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """优化DataFrame内存使用"""
        if df.empty:
            return df

        optimized_df = df.copy()

        # 优化数值列
        for col in optimized_df.select_dtypes(include=['int64']).columns:
            col_min = optimized_df[col].min()
            col_max = optimized_df[col].max()

            if col_min >= -128 and col_max <= 127:
                optimized_df[col] = optimized_df[col].astype('int8')
            elif col_min >= -32768 and col_max <= 32767:
                optimized_df[col] = optimized_df[col].astype('int16')
            elif col_min >= -2147483648 and col_max <= 2147483647:
                optimized_df[col] = optimized_df[col].astype('int32')

        # 优化浮点数列
        for col in optimized_df.select_dtypes(include=['float64']).columns:
            optimized_df[col] = pd.to_numeric(optimized_df[col], downcast='float')

        # 优化字符串列
        for col in optimized_df.select_dtypes(include=['object']).columns:
            if optimized_df[col].nunique() / len(optimized_df) < 0.5:  # 如果重复值较多
                optimized_df[col] = optimized_df[col].astype('category')

        return optimized_df

    @staticmethod
    def filter_recent_data(df: pd.DataFrame, time_col: str, hours: int = 24) -> pd.DataFrame:
        """过滤最近的数据"""
        if df.empty or time_col not in df.columns:
            return df

        cutoff_time = datetime.now() - timedelta(hours=hours)
        return df[pd.to_datetime(df[time_col]) >= cutoff_time]

    @staticmethod
    def aggregate_data(df: pd.DataFrame, group_cols: list, agg_dict: dict) -> pd.DataFrame:
        """聚合数据"""
        if df.empty:
            return df

        return df.groupby(group_cols).agg(agg_dict).reset_index()

def cached_function(ttl: int = 3600, use_persistent: bool = False):
    """缓存装饰器"""
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"

            if use_persistent:
                # 使用持久化缓存
                cache = PersistentCache()
                cached_result = cache.get(cache_key, ttl)

                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)
                cache.set(cache_key, result)
                return result
            else:
                # 使用Streamlit缓存
                @st.cache_data(ttl=ttl)
                def cached_func(*args, **kwargs):
                    return func(*args, **kwargs)

                return cached_func(*args, **kwargs)

        return wrapper
    return decorator

# 全局缓存实例
persistent_cache = PersistentCache()

def display_cache_stats():
    """显示缓存统计信息"""
    st.subheader("📊 缓存统计")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**持久化缓存**")
        cache_info = persistent_cache.get_cache_info()
        st.metric("缓存文件数", cache_info['file_count'])
        st.metric("缓存大小 (MB)", f"{cache_info['total_size_mb']:.2f}")

        if st.button("清空持久化缓存"):
            persistent_cache.clear()
            st.success("持久化缓存已清空")

    with col2:
        st.markdown("**会话缓存**")
        session_info = SessionDataManager.get_memory_usage()
        st.metric("会话项目数", session_info['total_items'])
        st.metric("估算大小 (MB)", f"{session_info['estimated_size_mb']:.2f}")

        if st.button("清空会话缓存"):
            st.session_state.clear()
            st.success("会话缓存已清空")

def optimize_app_performance():
    """应用性能优化建议"""
    st.subheader("⚡ 性能优化建议")

    # 检查缓存使用情况
    cache_info = persistent_cache.get_cache_info()
    session_info = SessionDataManager.get_memory_usage()

    suggestions = []

    if cache_info['total_size_mb'] > 100:
        suggestions.append("持久化缓存过大，建议清理旧缓存文件")

    if session_info['estimated_size_mb'] > 50:
        suggestions.append("会话数据过多，建议清理不必要的session state")

    if session_info['total_items'] > 20:
        suggestions.append("会话项目过多，考虑使用更高效的数据结构")

    if suggestions:
        for suggestion in suggestions:
            st.warning(f"⚠️ {suggestion}")
    else:
        st.success("✅ 应用性能良好，无需优化")

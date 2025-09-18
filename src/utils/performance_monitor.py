"""
性能监控工具
提供应用程序性能监控、资源使用统计和性能分析功能
"""

import time
import psutil
import threading
import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import functools
import streamlit as st
from src.utils.logging_utils import logger


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    response_time: float = 0.0
    active_connections: int = 0
    cache_hit_rate: float = 0.0
    error_count: int = 0


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: List[PerformanceMetrics] = []
        self.function_stats: Dict[str, Dict] = {}
        self.is_monitoring = False
        self._lock = threading.Lock()
        
    def start_monitoring(self, interval: float = 5.0):
        """开始性能监控"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        
        def monitor_loop():
            while self.is_monitoring:
                try:
                    metrics = self._collect_system_metrics()
                    with self._lock:
                        self.metrics_history.append(metrics)
                        if len(self.metrics_history) > self.max_history:
                            self.metrics_history.pop(0)
                except Exception as e:
                    logger.error(f"性能监控错误: {e}")
                
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        logger.info("性能监控已停止")
    
    def _collect_system_metrics(self) -> PerformanceMetrics:
        """收集系统性能指标"""
        process = psutil.Process()
        
        return PerformanceMetrics(
            cpu_percent=process.cpu_percent(),
            memory_percent=process.memory_percent(),
            memory_used_mb=process.memory_info().rss / 1024 / 1024,
            active_connections=len(process.connections()),
        )
    
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        with self._lock:
            return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, minutes: int = 60) -> List[PerformanceMetrics]:
        """获取指定时间范围内的性能历史"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        with self._lock:
            return [
                metric for metric in self.metrics_history
                if metric.timestamp >= cutoff_time
            ]
    
    def get_function_stats(self) -> Dict[str, Dict]:
        """获取函数性能统计"""
        with self._lock:
            return self.function_stats.copy()
    
    def record_function_call(self, func_name: str, duration: float, success: bool = True):
        """记录函数调用性能"""
        with self._lock:
            if func_name not in self.function_stats:
                self.function_stats[func_name] = {
                    'total_calls': 0,
                    'total_duration': 0.0,
                    'avg_duration': 0.0,
                    'min_duration': float('inf'),
                    'max_duration': 0.0,
                    'error_count': 0,
                    'success_rate': 100.0
                }
            
            stats = self.function_stats[func_name]
            stats['total_calls'] += 1
            stats['total_duration'] += duration
            stats['avg_duration'] = stats['total_duration'] / stats['total_calls']
            stats['min_duration'] = min(stats['min_duration'], duration)
            stats['max_duration'] = max(stats['max_duration'], duration)
            
            if not success:
                stats['error_count'] += 1
            
            stats['success_rate'] = ((stats['total_calls'] - stats['error_count']) / 
                                   stats['total_calls']) * 100


def performance_monitor(monitor_instance: PerformanceMonitor):
    """性能监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor_instance.record_function_call(
                    func.__name__, duration, success
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                monitor_instance.record_function_call(
                    func.__name__, duration, success
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# 全局性能监控实例
global_monitor = PerformanceMonitor()


def display_performance_dashboard():
    """显示性能监控仪表板"""
    st.subheader("🔍 性能监控仪表板")
    
    # 当前性能指标
    current_metrics = global_monitor.get_current_metrics()
    if current_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "CPU使用率", 
                f"{current_metrics.cpu_percent:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "内存使用率", 
                f"{current_metrics.memory_percent:.1f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                "内存使用量", 
                f"{current_metrics.memory_used_mb:.1f}MB",
                delta=None
            )
        
        with col4:
            st.metric(
                "活跃连接", 
                current_metrics.active_connections,
                delta=None
            )
    
    # 性能历史图表
    history = global_monitor.get_metrics_history(30)  # 30分钟历史
    if history:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('CPU使用率', '内存使用率', '内存使用量', '活跃连接'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        timestamps = [m.timestamp for m in history]
        
        # CPU使用率
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[m.cpu_percent for m in history],
                name="CPU%",
                line=dict(color='#ff6b6b')
            ),
            row=1, col=1
        )
        
        # 内存使用率
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[m.memory_percent for m in history],
                name="Memory%",
                line=dict(color='#4ecdc4')
            ),
            row=1, col=2
        )
        
        # 内存使用量
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[m.memory_used_mb for m in history],
                name="Memory MB",
                line=dict(color='#45b7d1')
            ),
            row=2, col=1
        )
        
        # 活跃连接
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[m.active_connections for m in history],
                name="Connections",
                line=dict(color='#96ceb4')
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            title_text="性能监控历史"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 函数性能统计
    function_stats = global_monitor.get_function_stats()
    if function_stats:
        st.subheader("📊 函数性能统计")
        
        stats_data = []
        for func_name, stats in function_stats.items():
            stats_data.append({
                '函数名': func_name,
                '调用次数': stats['total_calls'],
                '平均耗时(s)': f"{stats['avg_duration']:.3f}",
                '最小耗时(s)': f"{stats['min_duration']:.3f}",
                '最大耗时(s)': f"{stats['max_duration']:.3f}",
                '成功率(%)': f"{stats['success_rate']:.1f}",
                '错误次数': stats['error_count']
            })
        
        if stats_data:
            import pandas as pd
            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)


# 启动全局监控
if not global_monitor.is_monitoring:
    global_monitor.start_monitoring()
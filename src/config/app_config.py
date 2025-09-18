"""
应用程序配置管理系统
提供统一的配置管理、环境变量处理和配置验证功能
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import streamlit as st
from src.utils.logging_utils import logger


@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = "localhost"
    port: int = 5432
    database: str = "trading_intelligence"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30


@dataclass
class CacheConfig:
    """缓存配置"""
    default_ttl: int = 300  # 5分钟
    max_size: int = 1000
    cleanup_interval: int = 600  # 10分钟
    enable_compression: bool = True
    memory_threshold: float = 0.8  # 80%内存使用率阈值


@dataclass
class APIConfig:
    """API配置"""
    rate_limit: int = 100  # 每分钟请求数
    timeout: int = 30  # 超时时间（秒）
    retry_attempts: int = 3
    retry_delay: float = 1.0
    max_concurrent_requests: int = 10


@dataclass
class UIConfig:
    """用户界面配置"""
    theme: str = "light"
    page_title: str = "交易智能分析平台"
    page_icon: str = "📈"
    layout: str = "wide"
    sidebar_state: str = "expanded"
    show_performance_metrics: bool = True


@dataclass
class TradingConfig:
    """交易配置"""
    default_exchanges: List[str] = field(default_factory=lambda: ["binance", "okx", "bybit"])
    default_symbols: List[str] = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT", "BNB/USDT"])
    min_profit_threshold: float = 0.1  # 最小利润阈值（%）
    max_position_size: float = 10000.0  # 最大仓位大小（USDT）
    risk_level: str = "medium"  # low, medium, high


@dataclass
class PerformanceConfig:
    """性能配置"""
    enable_monitoring: bool = True
    monitoring_interval: float = 5.0  # 监控间隔（秒）
    max_history_records: int = 1000
    enable_profiling: bool = False
    log_slow_queries: bool = True
    slow_query_threshold: float = 1.0  # 慢查询阈值（秒）


@dataclass
class AppConfig:
    """应用程序主配置"""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    api: APIConfig = field(default_factory=APIConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # 环境配置
    environment: str = "development"  # development, staging, production
    debug: bool = True
    log_level: str = "INFO"
    
    # 安全配置
    secret_key: str = ""
    encryption_key: str = ""
    
    def __post_init__(self):
        """配置初始化后处理"""
        self._load_from_environment()
        self._validate_config()
    
    def _load_from_environment(self):
        """从环境变量加载配置"""
        # 数据库配置
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", self.database.port))
        self.database.database = os.getenv("DB_NAME", self.database.database)
        self.database.username = os.getenv("DB_USER", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)
        
        # API配置
        self.api.rate_limit = int(os.getenv("API_RATE_LIMIT", self.api.rate_limit))
        self.api.timeout = int(os.getenv("API_TIMEOUT", self.api.timeout))
        
        # 环境配置
        self.environment = os.getenv("ENVIRONMENT", self.environment)
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", self.log_level)
        
        # 安全配置
        self.secret_key = os.getenv("SECRET_KEY", self.secret_key)
        self.encryption_key = os.getenv("ENCRYPTION_KEY", self.encryption_key)
    
    def _validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 验证数据库配置
        if not self.database.host:
            errors.append("数据库主机地址不能为空")
        
        if self.database.port <= 0 or self.database.port > 65535:
            errors.append("数据库端口必须在1-65535范围内")
        
        # 验证缓存配置
        if self.cache.default_ttl <= 0:
            errors.append("缓存TTL必须大于0")
        
        if self.cache.max_size <= 0:
            errors.append("缓存最大大小必须大于0")
        
        # 验证API配置
        if self.api.rate_limit <= 0:
            errors.append("API速率限制必须大于0")
        
        if self.api.timeout <= 0:
            errors.append("API超时时间必须大于0")
        
        # 验证交易配置
        if self.trading.min_profit_threshold < 0:
            errors.append("最小利润阈值不能为负数")
        
        if self.trading.max_position_size <= 0:
            errors.append("最大仓位大小必须大于0")
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"- {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout
            },
            "cache": {
                "default_ttl": self.cache.default_ttl,
                "max_size": self.cache.max_size,
                "cleanup_interval": self.cache.cleanup_interval,
                "enable_compression": self.cache.enable_compression,
                "memory_threshold": self.cache.memory_threshold
            },
            "api": {
                "rate_limit": self.api.rate_limit,
                "timeout": self.api.timeout,
                "retry_attempts": self.api.retry_attempts,
                "retry_delay": self.api.retry_delay,
                "max_concurrent_requests": self.api.max_concurrent_requests
            },
            "ui": {
                "theme": self.ui.theme,
                "page_title": self.ui.page_title,
                "page_icon": self.ui.page_icon,
                "layout": self.ui.layout,
                "sidebar_state": self.ui.sidebar_state,
                "show_performance_metrics": self.ui.show_performance_metrics
            },
            "trading": {
                "default_exchanges": self.trading.default_exchanges,
                "default_symbols": self.trading.default_symbols,
                "min_profit_threshold": self.trading.min_profit_threshold,
                "max_position_size": self.trading.max_position_size,
                "risk_level": self.trading.risk_level
            },
            "performance": {
                "enable_monitoring": self.performance.enable_monitoring,
                "monitoring_interval": self.performance.monitoring_interval,
                "max_history_records": self.performance.max_history_records,
                "enable_profiling": self.performance.enable_profiling,
                "log_slow_queries": self.performance.log_slow_queries,
                "slow_query_threshold": self.performance.slow_query_threshold
            },
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level
        }
    
    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        try:
            config_dict = self.to_dict()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"配置已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'AppConfig':
        """从文件加载配置"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"配置文件不存在: {file_path}，使用默认配置")
                return cls()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            config = cls()
            
            # 更新数据库配置
            if 'database' in config_dict:
                db_config = config_dict['database']
                config.database.host = db_config.get('host', config.database.host)
                config.database.port = db_config.get('port', config.database.port)
                config.database.database = db_config.get('database', config.database.database)
                config.database.username = db_config.get('username', config.database.username)
                config.database.pool_size = db_config.get('pool_size', config.database.pool_size)
                config.database.max_overflow = db_config.get('max_overflow', config.database.max_overflow)
                config.database.pool_timeout = db_config.get('pool_timeout', config.database.pool_timeout)
            
            # 更新其他配置...
            # （为了简洁，这里只展示数据库配置的更新）
            
            logger.info(f"配置已从文件加载: {file_path}")
            return config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            logger.info("使用默认配置")
            return cls()


class ConfigManager:
    """配置管理器"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置"""
        config_file = os.getenv("CONFIG_FILE", "config/app_config.json")
        
        # 确保配置目录存在
        config_dir = os.path.dirname(config_file)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        self._config = AppConfig.load_from_file(config_file)
        logger.info("配置管理器初始化完成")
    
    @property
    def config(self) -> AppConfig:
        """获取配置实例"""
        if self._config is None:
            self._load_config()
        return self._config
    
    def reload_config(self):
        """重新加载配置"""
        self._config = None
        self._load_config()
        logger.info("配置已重新加载")
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        self._config._validate_config()
        logger.info("配置已更新")


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """获取应用程序配置"""
    return config_manager.config


def display_config_panel():
    """显示配置面板"""
    st.subheader("⚙️ 系统配置")
    
    config = get_config()
    
    # 基本配置
    with st.expander("🔧 基本配置", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("环境", value=config.environment, disabled=True)
            st.checkbox("调试模式", value=config.debug, disabled=True)
        
        with col2:
            st.text_input("日志级别", value=config.log_level, disabled=True)
    
    # 性能配置
    with st.expander("📊 性能配置"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("启用监控", value=config.performance.enable_monitoring, disabled=True)
            st.number_input("监控间隔(秒)", value=config.performance.monitoring_interval, disabled=True)
        
        with col2:
            st.number_input("最大历史记录", value=config.performance.max_history_records, disabled=True)
            st.checkbox("启用性能分析", value=config.performance.enable_profiling, disabled=True)
    
    # 缓存配置
    with st.expander("💾 缓存配置"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.number_input("默认TTL(秒)", value=config.cache.default_ttl, disabled=True)
            st.number_input("最大大小", value=config.cache.max_size, disabled=True)
        
        with col2:
            st.number_input("清理间隔(秒)", value=config.cache.cleanup_interval, disabled=True)
            st.checkbox("启用压缩", value=config.cache.enable_compression, disabled=True)
    
    # 交易配置
    with st.expander("💰 交易配置"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.multiselect("默认交易所", options=config.trading.default_exchanges, 
                          default=config.trading.default_exchanges, disabled=True)
            st.number_input("最小利润阈值(%)", value=config.trading.min_profit_threshold, disabled=True)
        
        with col2:
            st.multiselect("默认交易对", options=config.trading.default_symbols,
                          default=config.trading.default_symbols, disabled=True)
            st.number_input("最大仓位(USDT)", value=config.trading.max_position_size, disabled=True)
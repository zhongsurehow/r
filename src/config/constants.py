"""
统一常量配置
整合所有重复的常量定义
"""

from typing import List, Dict, Any

# 交易所配置
class ExchangeConstants:
    """交易所相关常量"""

    # 主要交易所列表
    MAJOR_EXCHANGES = [
        'Binance', 'OKX', 'Huobi', 'KuCoin', 'Bybit',
        'Gate.io', 'Coinbase', 'Kraken', 'Bitget', 'MEXC'
    ]

    # 免费API交易所
    FREE_API_EXCHANGES = [
        'binance', 'okx', 'bybit', 'kucoin', 'gate',
        'mexc', 'bitget', 'htx', 'coinbase', 'kraken'
    ]

    # 交易所显示名称映射
    EXCHANGE_DISPLAY_NAMES = {
        'binance': 'Binance',
        'okx': 'OKX',
        'bybit': 'Bybit',
        'kucoin': 'KuCoin',
        'gate': 'Gate.io',
        'mexc': 'MEXC',
        'bitget': 'Bitget',
        'htx': 'HTX',
        'huobi': 'Huobi',
        'coinbase': 'Coinbase',
        'kraken': 'Kraken'
    }

    # 默认选择的交易所
    DEFAULT_EXCHANGES = ['Binance', 'OKX', 'Bybit', 'KuCoin']

# 货币配置
class CurrencyConstants:
    """货币相关常量"""

    # 主要加密货币
    MAJOR_CURRENCIES = [
        'BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT',
        'MATIC', 'AVAX', 'LINK', 'UNI', 'LTC', 'XRP'
    ]

    # 稳定币
    STABLECOINS = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD']

    # 所有支持的货币
    ALL_CURRENCIES = MAJOR_CURRENCIES + STABLECOINS + [
        'DOGE', 'SHIB', 'ATOM', 'FTM', 'NEAR', 'ALGO',
        'VET', 'ICP', 'SAND', 'MANA', 'CRV', 'COMP'
    ]

    # 交易对
    MAJOR_TRADING_PAIRS = [f"{curr}/USDT" for curr in MAJOR_CURRENCIES]

    # 默认选择的货币
    DEFAULT_CURRENCIES = ['BTC', 'ETH', 'BNB', 'ADA']

# 时间配置
class TimeConstants:
    """时间相关常量"""

    # 时间范围选项
    TIME_RANGES = {
        '1小时': 1,
        '4小时': 4,
        '12小时': 12,
        '1天': 24,
        '3天': 72,
        '1周': 168,
        '1月': 720
    }

    # 默认时间范围
    DEFAULT_TIME_RANGE = 24

    # 缓存TTL设置
    CACHE_TTL = {
        'real_time': 30,      # 实时数据30秒
        'market_data': 300,   # 市场数据5分钟
        'historical': 3600,   # 历史数据1小时
        'config': 86400       # 配置数据1天
    }

# 交易配置
class TradingConstants:
    """交易相关常量"""

    # 最小交易金额
    MIN_TRADE_AMOUNTS = {
        'BTC': 0.001,
        'ETH': 0.01,
        'BNB': 0.1,
        'USDT': 10,
        'default': 1
    }

    # 手续费率 (%)
    DEFAULT_FEE_RATES = {
        'maker': 0.1,
        'taker': 0.1,
        'withdrawal': 0.0005
    }

    # 风险等级
    RISK_LEVELS = {
        'low': {'min': 0, 'max': 3, 'color': '🟢', 'label': '低风险'},
        'medium': {'min': 3, 'max': 7, 'color': '🟡', 'label': '中风险'},
        'high': {'min': 7, 'max': 10, 'color': '🔴', 'label': '高风险'}
    }

# UI配置
class UIConstants:
    """UI相关常量"""

    # 状态颜色
    STATUS_COLORS = {
        '正常': '🟢',
        '健康': '🟢',
        '在线': '🟢',
        '警告': '🟡',
        '延迟': '🟡',
        '异常': '🔴',
        '错误': '🔴',
        '离线': '⚫',
        '未知': '⚪'
    }

    # 默认图表颜色
    CHART_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
        '#bcbd22', '#17becf'
    ]

    # 页面配置
    PAGE_CONFIG = {
        'layout': 'wide',
        'initial_sidebar_state': 'expanded',
        'menu_items': {
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    }

# 数据配置
class DataConstants:
    """数据相关常量"""

    # 数据精度
    DECIMAL_PLACES = {
        'price': 6,
        'percentage': 2,
        'volume': 0,
        'amount': 4
    }

    # 数据格式
    FORMAT_TEMPLATES = {
        'price': '${:.6f}',
        'percentage': '{:.2f}%',
        'volume': '{:,.0f}',
        'currency': '{:.4f}',
        'usd': '${:,.2f}'
    }

    # 默认数据量
    DEFAULT_DATA_LIMITS = {
        'opportunities': 50,
        'history_days': 30,
        'real_time_items': 20,
        'chart_points': 100
    }

# API配置
class APIConstants:
    """API相关常量"""

    # 请求超时设置
    TIMEOUT_SETTINGS = {
        'connect': 5,
        'read': 10,
        'total': 15
    }

    # 重试配置
    RETRY_CONFIG = {
        'max_attempts': 3,
        'backoff_factor': 1,
        'status_forcelist': [500, 502, 503, 504]
    }

    # 速率限制
    RATE_LIMITS = {
        'requests_per_second': 10,
        'requests_per_minute': 600,
        'burst_limit': 20
    }

# 性能配置
class PerformanceConstants:
    """性能相关常量"""

    # 批处理大小
    BATCH_SIZES = {
        'data_processing': 1000,
        'api_requests': 10,
        'database_operations': 100
    }

    # 内存限制
    MEMORY_LIMITS = {
        'max_dataframe_size': 10000,
        'max_cache_items': 1000,
        'max_session_size_mb': 100
    }

    # 性能阈值
    PERFORMANCE_THRESHOLDS = {
        'slow_operation_seconds': 1.0,
        'memory_warning_mb': 50,
        'cpu_warning_percent': 80
    }

# 安全配置
class SecurityConstants:
    """安全相关常量"""

    # 输入验证
    INPUT_LIMITS = {
        'max_string_length': 1000,
        'max_number_value': 1e12,
        'min_number_value': -1e12,
        'max_list_items': 100
    }

    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'api[_-]?key',
        r'secret[_-]?key',
        r'password',
        r'token',
        r'private[_-]?key'
    ]

# 全局配置类
class GlobalConfig:
    """全局配置管理"""

    def __init__(self):
        self.exchanges = ExchangeConstants()
        self.currencies = CurrencyConstants()
        self.time = TimeConstants()
        self.trading = TradingConstants()
        self.ui = UIConstants()
        self.data = DataConstants()
        self.api = APIConstants()
        self.performance = PerformanceConstants()
        self.security = SecurityConstants()

    def get_exchange_list(self, include_free_only: bool = False) -> List[str]:
        """获取交易所列表"""
        if include_free_only:
            return self.exchanges.FREE_API_EXCHANGES
        return self.exchanges.MAJOR_EXCHANGES

    def get_currency_list(self, include_stablecoins: bool = True) -> List[str]:
        """获取货币列表"""
        if include_stablecoins:
            return self.currencies.ALL_CURRENCIES
        return self.currencies.MAJOR_CURRENCIES

    def get_trading_pairs(self, base_currency: str = 'USDT') -> List[str]:
        """获取交易对列表"""
        return [f"{curr}/{base_currency}" for curr in self.currencies.MAJOR_CURRENCIES]

    def format_value(self, value: float, value_type: str) -> str:
        """格式化数值"""
        template = self.data.FORMAT_TEMPLATES.get(value_type, '{:.2f}')
        return template.format(value)

    def get_risk_info(self, risk_score: float) -> Dict[str, Any]:
        """获取风险等级信息"""
        for level, info in self.trading.RISK_LEVELS.items():
            if info['min'] <= risk_score < info['max']:
                return {
                    'level': level,
                    'color': info['color'],
                    'label': info['label'],
                    'score': risk_score
                }
        return {
            'level': 'unknown',
            'color': '⚪',
            'label': '未知风险',
            'score': risk_score
        }

# 全局配置实例
config = GlobalConfig()

# 便利函数
def get_exchanges(free_only: bool = False) -> List[str]:
    """获取交易所列表的便利函数"""
    return config.get_exchange_list(free_only)

def get_currencies(include_stablecoins: bool = True) -> List[str]:
    """获取货币列表的便利函数"""
    return config.get_currency_list(include_stablecoins)

def get_trading_pairs(base: str = 'USDT') -> List[str]:
    """获取交易对列表的便利函数"""
    return config.get_trading_pairs(base)

def format_price(price: float) -> str:
    """格式化价格的便利函数"""
    return config.format_value(price, 'price')

def format_percentage(pct: float) -> str:
    """格式化百分比的便利函数"""
    return config.format_value(pct, 'percentage')

def get_status_color(status: str) -> str:
    """获取状态颜色的便利函数"""
    return config.ui.STATUS_COLORS.get(status, '⚪')

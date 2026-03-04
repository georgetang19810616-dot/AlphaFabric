"""辅助工具函数"""
import os
import yaml
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
import pandas as pd


def load_config(config_path: str = "./config/config.yaml") -> Dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def setup_logging(config: Dict) -> logging.Logger:
    """设置日志"""
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', './logs/alphafabric.log')
    
    # 创建日志目录
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('AlphaFabric')


def get_trade_dates(start_date: str, end_date: str) -> List[str]:
    """获取交易日历（简化版，实际应从TUSHARE获取）"""
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    
    dates = []
    current = start
    while current <= end:
        # 跳过周末
        if current.weekday() < 5:
            dates.append(current.strftime('%Y%m%d'))
        current += timedelta(days=1)
    
    return dates


def optimize_dataframe(df: pd.DataFrame, use_float32: bool = True) -> pd.DataFrame:
    """优化DataFrame内存占用"""
    if not use_float32:
        return df
    
    # float64 -> float32
    float_cols = df.select_dtypes(include=['float64']).columns
    df[float_cols] = df[float_cols].astype('float32')
    
    # int64 -> int32
    int_cols = df.select_dtypes(include=['int64']).columns
    df[int_cols] = df[int_cols].astype('int32')
    
    return df


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03) -> float:
    """计算夏普比率"""
    if len(returns) == 0 or returns.std() == 0:
        return 0.0
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / returns.std()


def calculate_max_drawdown(nav: pd.Series) -> float:
    """计算最大回撤"""
    if len(nav) == 0:
        return 0.0
    cummax = nav.cummax()
    drawdown = (nav - cummax) / cummax
    return drawdown.min()


def calculate_annual_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """计算年化收益"""
    if len(returns) == 0:
        return 0.0
    total_return = (1 + returns).prod() - 1
    n_periods = len(returns)
    return (1 + total_return) ** (periods_per_year / n_periods) - 1


def format_stock_code(code: str) -> str:
    """格式化股票代码"""
    # 去除后缀
    if '.' in code:
        code = code.split('.')[0]
    
    # 添加后缀
    if code.startswith('6'):
        return f"{code}.SH"
    else:
        return f"{code}.SZ"


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class MemoryMonitor:
    """内存监控器"""
    def __init__(self, limit_mb: int = 3500):
        self.limit_mb = limit_mb
        self.logger = logging.getLogger('MemoryMonitor')
    
    def check_memory(self) -> bool:
        """检查内存使用情况"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb > self.limit_mb:
                self.logger.warning(f"内存使用过高: {memory_mb:.1f}MB / {self.limit_mb}MB")
                return False
            return True
        except ImportError:
            return True

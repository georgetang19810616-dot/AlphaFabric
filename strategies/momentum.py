"""动量策略"""
import pandas as pd
import numpy as np
from typing import Optional, List
from .base import BaseStrategy, Signal


class MomentumStrategy(BaseStrategy):
    """动量策略：选择近期涨幅居前的股票"""
    
    def __init__(self, config: dict = None):
        super().__init__("Momentum", config)
        self.lookback = config.get('lookback', 20)
        self.top_n = config.get('top_n', 50)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析单只股票（用于筛选）"""
        if len(data) < self.lookback + 5:
            return None
        
        # 计算动量
        momentum = (data['close'].iloc[-1] / data['close'].iloc[-self.lookback] - 1) * 100
        
        latest = data.iloc[-1]
        code = latest.get('ts_code', '')
        
        # 动量策略主要用于排序，不直接产生买卖信号
        return Signal(
            code=code,
            action='hold',
            price=latest['close'],
            confidence=min(abs(momentum) / 20, 0.9),
            reason=f"{self.lookback}日动量: {momentum:.2f}%"
        )
    
    def select_top_stocks(self, stock_data: dict, n: int = None) -> List[str]:
        """选择动量最强的n只股票"""
        if n is None:
            n = self.top_n
        
        momentums = []
        for code, data in stock_data.items():
            if len(data) < self.lookback + 5:
                continue
            try:
                momentum = (data['close'].iloc[-1] / data['close'].iloc[-self.lookback] - 1) * 100
                momentums.append((code, momentum))
            except:
                continue
        
        # 按动量排序
        momentums.sort(key=lambda x: x[1], reverse=True)
        return [code for code, _ in momentums[:n]]

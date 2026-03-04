"""双均线策略"""
import pandas as pd
import numpy as np
from typing import Optional
from .base import BaseStrategy, Signal


class DoubleMAStrategy(BaseStrategy):
    """双均线策略：金叉买入，死叉卖出"""
    
    def __init__(self, config: dict = None):
        super().__init__("DoubleMA", config)
        self.fast_period = config.get('fast_period', 5)
        self.slow_period = config.get('slow_period', 20)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析股票数据"""
        if len(data) < self.slow_period + 5:
            return None
        
        # 计算均线
        data = data.copy()
        data['fast_ma'] = data['close'].rolling(window=self.fast_period).mean()
        data['slow_ma'] = data['close'].rolling(window=self.slow_period).mean()
        
        # 获取最新数据
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # 判断金叉死叉
        golden_cross = (prev['fast_ma'] <= prev['slow_ma']) and (latest['fast_ma'] > latest['slow_ma'])
        death_cross = (prev['fast_ma'] >= prev['slow_ma']) and (latest['fast_ma'] < latest['slow_ma'])
        
        code = latest.get('ts_code', '')
        
        if golden_cross:
            return Signal(
                code=code,
                action='buy',
                price=latest['close'],
                confidence=0.7,
                reason=f"均线金叉: 快线{self.fast_period}日上穿慢线{self.slow_period}日"
            )
        elif death_cross:
            return Signal(
                code=code,
                action='sell',
                price=latest['close'],
                confidence=0.6,
                reason=f"均线死叉: 快线{self.fast_period}日下穿慢线{self.slow_period}日"
            )
        
        return Signal(code=code, action='hold', price=latest['close'])

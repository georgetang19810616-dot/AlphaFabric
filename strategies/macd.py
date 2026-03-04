"""MACD策略"""
import pandas as pd
import numpy as np
from typing import Optional
from .base import BaseStrategy, Signal


class MACDStrategy(BaseStrategy):
    """MACD策略：DIF上穿DEA买入"""
    
    def __init__(self, config: dict = None):
        super().__init__("MACD", config)
        self.fast = config.get('fast', 12)
        self.slow = config.get('slow', 26)
        self.signal = config.get('signal', 9)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析股票数据"""
        if len(data) < self.slow + 10:
            return None
        
        data = data.copy()
        close = data['close']
        
        # 计算MACD
        ema_fast = close.ewm(span=self.fast, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow, adjust=False).mean()
        data['dif'] = ema_fast - ema_slow
        data['dea'] = data['dif'].ewm(span=self.signal, adjust=False).mean()
        data['macd'] = 2 * (data['dif'] - data['dea'])
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # 判断信号
        golden_cross = (prev['dif'] <= prev['dea']) and (latest['dif'] > latest['dea'])
        death_cross = (prev['dif'] >= prev['dea']) and (latest['dif'] < latest['dea'])
        
        code = latest.get('ts_code', '')
        
        if golden_cross and latest['macd'] > 0:
            return Signal(
                code=code,
                action='buy',
                price=latest['close'],
                confidence=0.75,
                reason="MACD金叉且MACD柱为正"
            )
        elif death_cross and latest['macd'] < 0:
            return Signal(
                code=code,
                action='sell',
                price=latest['close'],
                confidence=0.65,
                reason="MACD死叉且MACD柱为负"
            )
        
        return Signal(code=code, action='hold', price=latest['close'])

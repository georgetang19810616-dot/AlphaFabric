"""价值策略"""
import pandas as pd
import numpy as np
from typing import Optional, List
from .base import BaseStrategy, Signal


class ValueStrategy(BaseStrategy):
    """价值策略：选择低估值、高质量的股票"""
    
    def __init__(self, config: dict = None):
        super().__init__("Value", config)
        self.max_pe = config.get('max_pe', 30)
        self.max_pb = config.get('max_pb', 3)
        self.min_roe = config.get('min_roe', 0.1)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析股票数据（需要基本面数据）"""
        if len(data) < 60:
            return None
        
        latest = data.iloc[-1]
        code = latest.get('ts_code', '')
        
        # 这里简化处理，实际应从daily_basic获取PE/PB
        # 使用价格数据估算
        avg_price = data['close'].mean()
        latest_price = latest['close']
        
        # 简单判断：价格低于均线可能低估
        is_undervalued = latest_price < avg_price * 0.95
        
        if is_undervalued:
            return Signal(
                code=code,
                action='buy',
                price=latest_price,
                confidence=0.6,
                reason="价格低于历史均价，可能存在价值"
            )
        
        return Signal(code=code, action='hold', price=latest_price)
    
    def filter_by_value(self, stock_data: dict, pe_data: dict = None) -> List[str]:
        """根据估值指标筛选股票"""
        selected = []
        
        for code, data in stock_data.items():
            if len(data) < 60:
                continue
            
            try:
                # 使用价格趋势作为价值判断的简化
                ma60 = data['close'].rolling(60).mean().iloc[-1]
                latest = data['close'].iloc[-1]
                
                # 价格低于60日均线，可能低估
                if latest < ma60 * 0.95:
                    selected.append(code)
            except:
                continue
        
        return selected

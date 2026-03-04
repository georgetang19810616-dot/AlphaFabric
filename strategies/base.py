"""策略基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd
import numpy as np


@dataclass
class Signal:
    """交易信号"""
    code: str
    action: str  # 'buy', 'sell', 'hold'
    price: float
    quantity: int = 0
    confidence: float = 0.5
    reason: str = ""


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析单只股票数据，生成信号"""
        pass
    
    def run(self, stock_data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """运行策略，分析多只股票"""
        signals = []
        for code, data in stock_data.items():
            if len(data) < 30:  # 数据不足
                continue
            try:
                signal = self.analyze(data)
                if signal is not None and signal.action != 'hold':
                    signals.append(signal)
            except Exception as e:
                continue
        return signals
    
    def filter_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[str]:
        """筛选符合条件的股票"""
        selected = []
        for code, data in stock_data.items():
            if len(data) < 30:
                continue
            try:
                signal = self.analyze(data)
                if signal is not None and signal.action == 'buy':
                    selected.append(code)
            except:
                continue
        return selected

"""因子基类"""
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class BaseFactor(ABC):
    """因子基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """计算因子值"""
        pass
    
    def normalize(self, series: pd.Series) -> pd.Series:
        """因子标准化（z-score）"""
        mean = series.mean()
        std = series.std()
        if std == 0:
            return pd.Series(0, index=series.index)
        return (series - mean) / std

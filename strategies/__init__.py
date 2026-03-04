"""策略模块"""
from .base import BaseStrategy, Signal
from .double_ma import DoubleMAStrategy
from .macd import MACDStrategy
from .momentum import MomentumStrategy
from .value import ValueStrategy
from .ai_predict import LiteAIPredictStrategy

__all__ = [
    'BaseStrategy', 'Signal',
    'DoubleMAStrategy', 'MACDStrategy', 'MomentumStrategy',
    'ValueStrategy', 'LiteAIPredictStrategy'
]

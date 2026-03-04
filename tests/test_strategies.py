"""策略模块测试"""
import unittest
import sys
import os
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies import (
    DoubleMAStrategy, MACDStrategy, MomentumStrategy,
    ValueStrategy, LiteAIPredictStrategy
)


class TestStrategies(unittest.TestCase):
    """测试策略"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟数据
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        self.test_data = pd.DataFrame({
            'trade_date': [d.strftime('%Y%m%d') for d in dates],
            'open': 100 + np.random.randn(100).cumsum(),
            'high': 102 + np.random.randn(100).cumsum(),
            'low': 98 + np.random.randn(100).cumsum(),
            'close': 100 + np.random.randn(100).cumsum(),
            'volume': np.random.randint(1000000, 10000000, 100),
            'amount': np.random.randint(10000000, 100000000, 100),
        })
        
        # 确保high >= low
        self.test_data['high'] = np.maximum(self.test_data['high'], self.test_data['low'] + 1)
        self.test_data['high'] = np.maximum(self.test_data['high'], self.test_data['open'])
        self.test_data['high'] = np.maximum(self.test_data['high'], self.test_data['close'])
        
        self.test_data['low'] = np.minimum(self.test_data['low'], self.test_data['high'] - 1)
        self.test_data['low'] = np.minimum(self.test_data['low'], self.test_data['open'])
        self.test_data['low'] = np.minimum(self.test_data['low'], self.test_data['close'])
    
    def test_double_ma(self):
        """测试双均线策略"""
        strategy = DoubleMAStrategy({'fast_period': 5, 'slow_period': 20})
        signal = strategy.analyze(self.test_data)
        
        self.assertIsNotNone(signal)
        self.assertIn(signal.action, ['buy', 'sell', 'hold'])
        print(f"双均线策略信号: {signal.action}")
    
    def test_macd(self):
        """测试MACD策略"""
        strategy = MACDStrategy({'fast': 12, 'slow': 26, 'signal': 9})
        signal = strategy.analyze(self.test_data)
        
        self.assertIsNotNone(signal)
        self.assertIn(signal.action, ['buy', 'sell', 'hold'])
        print(f"MACD策略信号: {signal.action}")
    
    def test_momentum(self):
        """测试动量策略"""
        strategy = MomentumStrategy({'lookback': 20})
        signal = strategy.analyze(self.test_data)
        
        self.assertIsNotNone(signal)
        print(f"动量策略信号: {signal.action}")
    
    def test_value(self):
        """测试价值策略"""
        strategy = ValueStrategy({'max_pe': 30})
        signal = strategy.analyze(self.test_data)
        
        self.assertIsNotNone(signal)
        print(f"价值策略信号: {signal.action}")
    
    def test_ai_predict(self):
        """测试AI预测策略"""
        strategy = LiteAIPredictStrategy({'threshold': 0.6})
        signal = strategy.analyze(self.test_data)
        
        self.assertIsNotNone(signal)
        print(f"AI预测策略信号: {signal.action}")


if __name__ == '__main__':
    unittest.main()

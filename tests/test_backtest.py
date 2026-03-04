"""回测模块测试"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest import LiteBacktestEngine, BacktestConfig
from strategies import DoubleMAStrategy


class TestBacktest(unittest.TestCase):
    """测试回测引擎"""
    
    def test_backtest_config(self):
        """测试回测配置"""
        config = BacktestConfig(
            token='test_token',
            start_date='20240101',
            end_date='20241231',
            initial_capital=1000000
        )
        
        self.assertEqual(config.initial_capital, 1000000)
        self.assertEqual(config.commission_rate, 0.0003)
        print("回测配置测试通过")
    
    def test_backtest_engine_init(self):
        """测试回测引擎初始化"""
        config = BacktestConfig(
            token='test_token',
            start_date='20240101',
            end_date='20241231'
        )
        
        engine = LiteBacktestEngine(config)
        self.assertIsNotNone(engine)
        print("回测引擎初始化测试通过")
    
    def test_simulated_broker(self):
        """测试模拟券商"""
        from backtest.engine import SimulatedBroker
        
        broker = SimulatedBroker(initial_cash=1000000)
        self.assertEqual(broker.cash, 1000000)
        self.assertEqual(broker.total_value, 1000000)
        print("模拟券商测试通过")


if __name__ == '__main__':
    unittest.main()

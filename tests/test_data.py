"""数据模块测试"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_source import LiteTushareDataSource


class TestDataSource(unittest.TestCase):
    """测试数据源"""
    
    def setUp(self):
        """测试前准备"""
        self.token = os.getenv('TUSHARE_TOKEN', 'test_token')
        self.data_source = LiteTushareDataSource(self.token, './data/test_cache.db')
    
    def test_get_hs300_stocks(self):
        """测试获取沪深300成分股"""
        stocks = self.data_source.get_hs300_stocks()
        self.assertGreater(len(stocks), 0)
        print(f"沪深300成分股数量: {len(stocks)}")
    
    def test_get_daily_data(self):
        """测试获取日线数据"""
        stocks = self.data_source.get_hs300_stocks()
        if len(stocks) > 0:
            df = self.data_source.get_daily_data(stocks[0], days=30)
            if df is not None:
                self.assertIn('close', df.columns)
                self.assertIn('volume', df.columns)
                print(f"获取数据成功: {len(df)}条")


if __name__ == '__main__':
    unittest.main()

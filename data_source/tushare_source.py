"""TUSHARE PRO 轻量数据源"""
import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import tushare as ts

from utils.helpers import optimize_dataframe

logger = logging.getLogger('AlphaFabric')


class LiteDataCache:
    """轻量级SQLite缓存"""
    
    def __init__(self, db_path: str = "./data/cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
        self.max_cache_size = 100  # 最多缓存100只股票
    
    def _init_tables(self):
        """初始化数据表"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_data (
                ts_code TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (ts_code, trade_date)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_basic (
                ts_code TEXT PRIMARY KEY,
                name TEXT,
                industry TEXT,
                market TEXT,
                list_date TEXT
            )
        ''')
        self.conn.commit()
    
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """从缓存获取日线数据"""
        query = '''
            SELECT * FROM daily_data 
            WHERE ts_code = ? AND trade_date >= ? AND trade_date <= ?
            ORDER BY trade_date
        '''
        df = pd.read_sql_query(query, self.conn, params=(ts_code, start_date, end_date))
        if len(df) > 0:
            return df
        return None
    
    def save_daily_data(self, ts_code: str, df: pd.DataFrame):
        """保存日线数据到缓存"""
        if len(df) == 0:
            return
        
        df = df.copy()
        df['ts_code'] = ts_code
        
        # 确保列名正确
        required_cols = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume', 'amount']
        for col in required_cols:
            if col not in df.columns:
                if col == 'amount':
                    df[col] = 0
        
        # 只保留需要的列
        df = df[required_cols]
        
        # 保存到数据库
        df.to_sql('daily_data', self.conn, if_exists='append', index=False)
        self.conn.commit()
    
    def clear_old_data(self, before_date: str):
        """清理过期数据"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM daily_data WHERE trade_date < ?', (before_date,))
        self.conn.commit()
        logger.info(f"清理了 {before_date} 之前的数据")


class LiteTushareDataSource:
    """轻量TUSHARE数据源 - AlphaFabric"""
    
    def __init__(self, token: str, cache_path: str = "./data/cache.db"):
        self.token = token
        self.pro = ts.pro_api(token)
        self.cache = LiteDataCache(cache_path)
        self.all_stocks: List[str] = []
        self.hs300_stocks: List[str] = []
        self._load_all_stocks()
        self._load_hs300_stocks()
    
    def _load_all_stocks(self):
        """加载所有A股股票列表"""
        try:
            # 获取所有上市股票（排除退市股）
            df = self.pro.stock_basic(exchange='', list_status='L', 
                                      fields='ts_code,name,industry,market,list_date')
            if df is not None and len(df) > 0:
                # 过滤掉北交所、新三板等，只保留沪深主板、创业板、科创板
                df = df[df['ts_code'].str.endswith(('.SH', '.SZ'))]
                # 过滤掉ST股票
                df = df[~df['name'].str.contains('ST', na=False)]
                self.all_stocks = df['ts_code'].tolist()
                logger.info(f"AlphaFabric: 加载A股全市场股票: {len(self.all_stocks)}只")
            else:
                logger.warning("无法获取全市场股票列表，使用默认列表")
                self.all_stocks = self._get_default_all_stocks()
        except Exception as e:
            logger.error(f"加载全市场股票失败: {e}")
            self.all_stocks = self._get_default_all_stocks()
    
    def _load_hs300_stocks(self):
        """加载沪深300成分股"""
        try:
            # 获取最新沪深300成分股
            df = self.pro.index_weight(index_code='000300.SH')
            if df is not None and len(df) > 0:
                self.hs300_stocks = df['con_code'].tolist()[:300]
                logger.info(f"AlphaFabric: 加载沪深300成分股: {len(self.hs300_stocks)}只")
        except Exception as e:
            logger.error(f"加载沪深300成分股失败: {e}")
    
    def _get_default_all_stocks(self) -> List[str]:
        """获取默认全市场股票列表（简化版）"""
        # 返回约500只代表性股票
        return [
            # 沪深300部分
            '000001.SZ', '000002.SZ', '000063.SZ', '000100.SZ', '000333.SZ',
            '000538.SZ', '000568.SZ', '000651.SZ', '000725.SZ', '000768.SZ',
            '000858.SZ', '000895.SZ', '002001.SZ', '002007.SZ', '002024.SZ',
            '002027.SZ', '002044.SZ', '002120.SZ', '002142.SZ', '002230.SZ',
            '002236.SZ', '002271.SZ', '002304.SZ', '002352.SZ', '002415.SZ',
            '002460.SZ', '002475.SZ', '002594.SZ', '002714.SZ', '002812.SZ',
            '300003.SZ', '300014.SZ', '300015.SZ', '300033.SZ', '300059.SZ',
            '300122.SZ', '300124.SZ', '300142.SZ', '300274.SZ', '300408.SZ',
            '300413.SZ', '300433.SZ', '300498.SZ', '300750.SZ', '600000.SH',
            '600009.SH', '600016.SH', '600028.SH', '600029.SH', '600030.SH',
            '600031.SH', '600036.SH', '600048.SH', '600050.SH', '600104.SH',
            '600276.SH', '600309.SH', '600406.SH', '600436.SH', '600438.SH',
            '600519.SH', '600585.SH', '600588.SH', '600690.SH', '600745.SH',
            '600809.SH', '600837.SH', '600887.SH', '600893.SH', '600900.SH',
            '601012.SH', '601066.SH', '601088.SH', '601100.SH', '601138.SH',
            '601166.SH', '601211.SH', '601288.SH', '601318.SH', '601336.SH',
            '601398.SH', '601601.SH', '601628.SH', '601668.SH', '601688.SH',
            '601766.SH', '601857.SH', '601888.SH', '601899.SH', '601919.SH',
            '601995.SH', '603019.SH', '603259.SH', '603288.SH', '603501.SH',
            '603659.SH', '603799.SH', '603986.SH', '688008.SH', '688009.SH',
            '688012.SH', '688036.SH', '688111.SH', '688169.SH', '688223.SH',
            '688235.SH', '688271.SH', '688303.SH', '688599.SH', '688981.SH',
        ]
    
    def get_all_stocks(self) -> List[str]:
        """获取所有A股股票列表"""
        return self.all_stocks
    
    def get_hs300_stocks(self) -> List[str]:
        """获取沪深300成分股列表"""
        return self.hs300_stocks
    
    def get_daily_data(self, ts_code: str, days: int = 500) -> Optional[pd.DataFrame]:
        """获取日线数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days * 1.5)  # 多取一些，避免节假日
        
        end_str = end_date.strftime('%Y%m%d')
        start_str = start_date.strftime('%Y%m%d')
        
        # 先尝试从缓存获取
        df = self.cache.get_daily_data(ts_code, start_str, end_str)
        
        if df is None or len(df) < days * 0.8:  # 缓存数据不足
            try:
                # 从TUSHARE获取
                df = self.pro.daily(ts_code=ts_code, start_date=start_str, end_date=end_str)
                if df is not None and len(df) > 0:
                    df = df.sort_values('trade_date')
                    # 保存到缓存
                    self.cache.save_daily_data(ts_code, df)
            except Exception as e:
                logger.error(f"获取{ts_code}日线数据失败: {e}")
                return df  # 返回缓存数据（如果有）
        
        if df is not None and len(df) > 0:
            df = optimize_dataframe(df)
        
        return df
    
    def get_daily_data_batch(self, ts_codes: List[str], days: int = 500) -> Dict[str, pd.DataFrame]:
        """批量获取日线数据"""
        results = {}
        for i, code in enumerate(ts_codes):
            if i % 50 == 0:
                logger.info(f"数据获取进度: {i}/{len(ts_codes)}")
            df = self.get_daily_data(code, days)
            if df is not None and len(df) > 0:
                results[code] = df
        return results
    
    def get_stock_basic(self, ts_code: str) -> Optional[Dict]:
        """获取股票基本信息"""
        try:
            df = self.pro.stock_basic(ts_code=ts_code)
            if df is not None and len(df) > 0:
                return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"获取{ts_code}基本信息失败: {e}")
        return None
    
    def get_daily_basic(self, ts_code: str, trade_date: str) -> Optional[Dict]:
        """获取每日指标（PE/PB等）"""
        try:
            df = self.pro.daily_basic(ts_code=ts_code, trade_date=trade_date)
            if df is not None and len(df) > 0:
                return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"获取{ts_code}每日指标失败: {e}")
        return None

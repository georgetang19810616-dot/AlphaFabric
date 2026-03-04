"""轻量回测引擎"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from tqdm import tqdm

from data_source import LiteTushareDataSource
from strategies import BaseStrategy
from utils.helpers import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_annual_return,
    get_trade_dates
)

logger = logging.getLogger('AlphaFabric')


@dataclass
class Position:
    """持仓"""
    code: str
    quantity: int = 0
    avg_price: float = 0.0
    market_value: float = 0.0


@dataclass
class Order:
    """订单"""
    code: str
    action: str  # 'buy', 'sell'
    price: float
    quantity: int
    date: str


@dataclass
class BacktestConfig:
    """回测配置"""
    token: str
    start_date: str
    end_date: str
    initial_capital: float = 1000000
    commission_rate: float = 0.0003
    slippage: float = 0.001
    position_limit: float = 0.2


@dataclass
class BacktestResults:
    """回测结果"""
    daily_values: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    trades: List[Order] = field(default_factory=list)
    positions_history: List[Dict] = field(default_factory=list)
    
    # 绩效指标
    total_return: float = 0.0
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    volatility: float = 0.0
    win_rate: float = 0.0
    profit_loss_ratio: float = 0.0
    
    def record_daily_value(self, date: str, total_value: float):
        """记录每日净值"""
        new_row = pd.DataFrame({'date': [date], 'nav': [total_value]})
        self.daily_values = pd.concat([self.daily_values, new_row], ignore_index=True)
    
    def calculate_metrics(self):
        """计算绩效指标"""
        if len(self.daily_values) < 2:
            return
        
        nav = self.daily_values['nav']
        
        # 总收益率
        self.total_return = (nav.iloc[-1] / nav.iloc[0]) - 1
        
        # 日收益率
        daily_returns = nav.pct_change().dropna()
        
        # 年化收益
        self.annual_return = calculate_annual_return(daily_returns)
        
        # 最大回撤
        self.max_drawdown = calculate_max_drawdown(nav)
        
        # 夏普比率
        self.sharpe_ratio = calculate_sharpe_ratio(daily_returns)
        
        # 波动率
        self.volatility = daily_returns.std() * np.sqrt(252)
        
        # 胜率
        if len(self.trades) > 0:
            # 简化计算
            self.win_rate = 0.5
        
        logger.info(f"回测完成: 总收益={self.total_return:.2%}, 最大回撤={self.max_drawdown:.2%}, 夏普={self.sharpe_ratio:.2f}")
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'volatility': self.volatility,
            'win_rate': self.win_rate,
            'trade_count': len(self.trades)
        }


class SimulatedBroker:
    """模拟券商"""
    
    def __init__(self, initial_cash: float, commission_rate: float = 0.0003, slippage: float = 0.001):
        self.cash = initial_cash
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
    
    @property
    def total_value(self) -> float:
        """总资产"""
        positions_value = sum(p.market_value for p in self.positions.values())
        return self.cash + positions_value
    
    def execute(self, order: Order):
        """执行订单"""
        if order.action == 'buy':
            self._buy(order)
        else:
            self._sell(order)
        
        self.orders.append(order)
    
    def _buy(self, order: Order):
        """买入"""
        # 考虑滑点
        price = order.price * (1 + self.slippage)
        cost = price * order.quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission
        
        if total_cost > self.cash:
            # 资金不足，调整数量
            max_quantity = int(self.cash / (price * (1 + self.commission_rate)))
            if max_quantity <= 0:
                return
            order.quantity = max_quantity
            cost = price * order.quantity
            commission = cost * self.commission_rate
            total_cost = cost + commission
        
        # 更新持仓
        code = order.code
        if code not in self.positions:
            self.positions[code] = Position(code=code)
        
        pos = self.positions[code]
        total_cost_basis = pos.avg_price * pos.quantity + price * order.quantity
        pos.quantity += order.quantity
        if pos.quantity > 0:
            pos.avg_price = total_cost_basis / pos.quantity
        pos.market_value = pos.quantity * price
        
        # 扣除现金
        self.cash -= total_cost
        
        logger.info(f"买入 {code}: {order.quantity}股 @ {price:.2f}, 手续费:{commission:.2f}")
    
    def _sell(self, order: Order):
        """卖出"""
        code = order.code
        if code not in self.positions or self.positions[code].quantity < order.quantity:
            logger.warning(f"持仓不足，无法卖出 {code}")
            return
        
        # 考虑滑点
        price = order.price * (1 - self.slippage)
        revenue = price * order.quantity
        commission = revenue * self.commission_rate
        net_revenue = revenue - commission
        
        # 更新持仓
        pos = self.positions[code]
        pos.quantity -= order.quantity
        pos.market_value = pos.quantity * price
        
        if pos.quantity == 0:
            pos.avg_price = 0
        
        # 增加现金
        self.cash += net_revenue
        
        logger.info(f"卖出 {code}: {order.quantity}股 @ {price:.2f}, 手续费:{commission:.2f}")
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓市值"""
        for code, price in prices.items():
            if code in self.positions:
                self.positions[code].market_value = self.positions[code].quantity * price


class LiteBacktestEngine:
    """轻量回测引擎"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data_source = LiteTushareDataSource(config.token)
        self.strategy: Optional[BaseStrategy] = None
        self.broker: Optional[SimulatedBroker] = None
        self.results = BacktestResults()
    
    def set_strategy(self, strategy: BaseStrategy):
        """设置策略"""
        self.strategy = strategy
    
    def run(self) -> BacktestResults:
        """执行回测"""
        if self.strategy is None:
            raise ValueError("请先设置策略")
        
        logger.info(f"开始回测: {self.config.start_date} ~ {self.config.end_date}")
        
        # 初始化券商
        self.broker = SimulatedBroker(
            initial_cash=self.config.initial_capital,
            commission_rate=self.config.commission_rate,
            slippage=self.config.slippage
        )
        
        # 获取交易日历
        trade_dates = get_trade_dates(self.config.start_date, self.config.end_date)
        
        # 预加载股票数据
        stock_codes = self.data_source.get_hs300_stocks()[:50]  # 取前50只
        logger.info(f"预加载 {len(stock_codes)} 只股票数据")
        
        stock_data_cache = {}
        for code in tqdm(stock_codes, desc="加载数据"):
            df = self.data_source.get_daily_data(code, days=600)
            if df is not None and len(df) > 60:
                stock_data_cache[code] = df
        
        logger.info(f"成功加载 {len(stock_data_cache)} 只股票")
        
        # 逐日回测
        for date in tqdm(trade_dates, desc="回测进度"):
            # 获取当日数据
            daily_data = self._get_daily_data_for_date(stock_data_cache, date)
            
            if len(daily_data) == 0:
                continue
            
            # 策略生成信号
            signals = self.strategy.run(daily_data)
            
            # 执行交易
            for signal in signals:
                if signal.action in ['buy', 'sell']:
                    order = Order(
                        code=signal.code,
                        action=signal.action,
                        price=signal.price,
                        quantity=100,  # 简化：固定100股
                        date=date
                    )
                    self.broker.execute(order)
            
            # 更新持仓市值
            prices = {code: df['close'].iloc[-1] for code, df in daily_data.items()}
            self.broker.update_prices(prices)
            
            # 记录每日净值
            self.results.record_daily_value(date, self.broker.total_value)
            
            # 记录持仓
            self.results.positions_history.append({
                'date': date,
                'positions': {k: v.__dict__ for k, v in self.broker.positions.items()},
                'cash': self.broker.cash,
                'total_value': self.broker.total_value
            })
        
        # 计算绩效指标
        self.results.calculate_metrics()
        
        logger.info("回测完成")
        return self.results
    
    def _get_daily_data_for_date(self, stock_data_cache: Dict, date: str) -> Dict[str, pd.DataFrame]:
        """获取某日的股票数据"""
        result = {}
        for code, df in stock_data_cache.items():
            # 获取date之前的数据
            mask = df['trade_date'] <= date
            hist_data = df[mask]
            if len(hist_data) >= 30:
                result[code] = hist_data
        return result
    
    def generate_report(self) -> str:
        """生成回测报告"""
        if self.results.total_return == 0:
            return "请先执行回测"
        
        report = f"""
====================================
        回测报告
====================================
回测区间: {self.config.start_date} ~ {self.config.end_date}
初始资金: {self.config.initial_capital:,.0f}

【绩效指标】
总收益率:     {self.results.total_return:>10.2%}
年化收益:     {self.results.annual_return:>10.2%}
最大回撤:     {self.results.max_drawdown:>10.2%}
夏普比率:     {self.results.sharpe_ratio:>10.2f}
波动率:       {self.results.volatility:>10.2%}
交易次数:     {len(self.results.trades):>10}

====================================
"""
        return report

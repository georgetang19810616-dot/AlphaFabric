"""模拟交易接口"""
import logging
from typing import List, Dict
from .base import BaseTrader, Position, Order

logger = logging.getLogger('AlphaFabric')


class SimulatedTrader(BaseTrader):
    """模拟交易接口（用于测试）"""
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.initial_cash = config.get('initial_cash', 1000000) if config else 1000000
        self.cash = self.initial_cash
        self.positions: Dict[str, Position] = {}
        self.order_history: List[dict] = []
        self.commission_rate = 0.0003
        self.slippage = 0.001
    
    def connect(self) -> bool:
        """连接（模拟）"""
        self.connected = True
        logger.info("模拟交易连接成功")
        return True
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        logger.info("模拟交易断开连接")
    
    @property
    def total_value(self) -> float:
        """总资产"""
        positions_value = sum(p.market_value for p in self.positions.values())
        return self.cash + positions_value
    
    def buy(self, code: str, price: float, quantity: int) -> bool:
        """买入"""
        if not self.connected:
            logger.error("未连接交易服务器")
            return False
        
        # 考虑滑点
        exec_price = price * (1 + self.slippage)
        cost = exec_price * quantity
        commission = cost * self.commission_rate
        total_cost = cost + commission
        
        if total_cost > self.cash:
            logger.warning(f"资金不足: 需要{total_cost:.2f}, 可用{self.cash:.2f}")
            return False
        
        # 更新持仓
        if code not in self.positions:
            self.positions[code] = Position(code=code)
        
        pos = self.positions[code]
        total_cost_basis = pos.avg_price * pos.quantity + exec_price * quantity
        pos.quantity += quantity
        pos.avg_price = total_cost_basis / pos.quantity
        pos.market_value = pos.quantity * exec_price
        
        # 扣除现金
        self.cash -= total_cost
        
        # 记录订单
        self.order_history.append({
            'action': 'buy',
            'code': code,
            'price': exec_price,
            'quantity': quantity,
            'commission': commission
        })
        
        logger.info(f"买入成功: {code} {quantity}股 @ {exec_price:.2f}")
        return True
    
    def sell(self, code: str, price: float, quantity: int) -> bool:
        """卖出"""
        if not self.connected:
            logger.error("未连接交易服务器")
            return False
        
        if code not in self.positions or self.positions[code].quantity < quantity:
            logger.warning(f"持仓不足: {code}")
            return False
        
        # 考虑滑点
        exec_price = price * (1 - self.slippage)
        revenue = exec_price * quantity
        commission = revenue * self.commission_rate
        net_revenue = revenue - commission
        
        # 更新持仓
        pos = self.positions[code]
        pos.quantity -= quantity
        pos.market_value = pos.quantity * exec_price
        
        if pos.quantity == 0:
            pos.avg_price = 0
        
        # 增加现金
        self.cash += net_revenue
        
        # 记录订单
        self.order_history.append({
            'action': 'sell',
            'code': code,
            'price': exec_price,
            'quantity': quantity,
            'commission': commission
        })
        
        logger.info(f"卖出成功: {code} {quantity}股 @ {exec_price:.2f}")
        return True
    
    def query_positions(self) -> List[Position]:
        """查询持仓"""
        return list(self.positions.values())
    
    def query_cash(self) -> float:
        """查询可用资金"""
        return self.cash
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓市值"""
        for code, price in prices.items():
            if code in self.positions:
                self.positions[code].market_value = self.positions[code].quantity * price
    
    def get_portfolio_summary(self) -> dict:
        """获取组合摘要"""
        positions_value = sum(p.market_value for p in self.positions.values())
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': self.total_value,
            'return_pct': (self.total_value / self.initial_cash - 1) * 100,
            'position_count': len([p for p in self.positions.values() if p.quantity > 0]),
            'order_count': len(self.order_history)
        }

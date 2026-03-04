"""交易接口基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional


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


class BaseTrader(ABC):
    """交易接口基类"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """连接交易服务器"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开连接"""
        pass
    
    @abstractmethod
    def buy(self, code: str, price: float, quantity: int) -> bool:
        """买入"""
        pass
    
    @abstractmethod
    def sell(self, code: str, price: float, quantity: int) -> bool:
        """卖出"""
        pass
    
    @abstractmethod
    def query_positions(self) -> List[Position]:
        """查询持仓"""
        pass
    
    @abstractmethod
    def query_cash(self) -> float:
        """查询可用资金"""
        pass
    
    def execute_order(self, order: Order) -> bool:
        """执行订单"""
        if order.action == 'buy':
            return self.buy(order.code, order.price, order.quantity)
        else:
            return self.sell(order.code, order.price, order.quantity)

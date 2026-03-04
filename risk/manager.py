"""轻量风险管理器"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass

logger = logging.getLogger('AlphaFabric')


@dataclass
class Signal:
    """交易信号"""
    code: str
    action: str
    price: float
    quantity: int = 0


@dataclass
class Portfolio:
    """投资组合"""
    cash: float
    positions: Dict[str, dict]
    total_value: float


class RiskRule(ABC):
    """风控规则基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def check(self, portfolio: Portfolio, signal: Signal) -> bool:
        """检查是否通过风控"""
        pass


class PositionLimitRule(RiskRule):
    """仓位限制规则"""
    
    def __init__(self, max_pct: float = 0.2):
        super().__init__("PositionLimit")
        self.max_pct = max_pct
    
    def check(self, portfolio: Portfolio, signal: Signal) -> bool:
        """检查仓位限制"""
        if signal.action != 'buy':
            return True
        
        code = signal.code
        position_value = portfolio.positions.get(code, {}).get('market_value', 0)
        new_value = position_value + signal.price * signal.quantity
        
        if portfolio.total_value > 0:
            position_pct = new_value / portfolio.total_value
            if position_pct > self.max_pct:
                logger.warning(f"仓位限制: {code} 仓位将达到 {position_pct:.1%} > {self.max_pct:.1%}")
                return False
        
        return True


class StopLossRule(RiskRule):
    """止损规则"""
    
    def __init__(self, loss_pct: float = 0.08):
        super().__init__("StopLoss")
        self.loss_pct = loss_pct
    
    def check(self, portfolio: Portfolio, signal: Signal) -> bool:
        """检查止损条件"""
        if signal.action != 'sell':
            return True
        
        code = signal.code
        position = portfolio.positions.get(code)
        
        if position is None or position.get('quantity', 0) == 0:
            return True
        
        avg_price = position.get('avg_price', 0)
        current_price = signal.price
        
        if avg_price > 0:
            loss_pct = (current_price - avg_price) / avg_price
            if loss_pct <= -self.loss_pct:
                logger.info(f"止损触发: {code} 亏损 {abs(loss_pct):.1%}")
                return True  # 允许卖出
        
        return True


class MaxDrawdownRule(RiskRule):
    """最大回撤规则"""
    
    def __init__(self, max_dd: float = 0.15):
        super().__init__("MaxDrawdown")
        self.max_dd = max_dd
        self.peak_value = 0
    
    def check(self, portfolio: Portfolio, signal: Signal) -> bool:
        """检查最大回撤"""
        # 更新峰值
        if portfolio.total_value > self.peak_value:
            self.peak_value = portfolio.total_value
        
        # 计算回撤
        if self.peak_value > 0:
            drawdown = (self.peak_value - portfolio.total_value) / self.peak_value
            if drawdown > self.max_dd:
                logger.warning(f"最大回撤超限: {drawdown:.1%} > {self.max_dd:.1%}")
                # 回撤超限时禁止买入
                if signal.action == 'buy':
                    return False
        
        return True


class LiteRiskManager:
    """轻量风险管理器"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.rules: List[RiskRule] = []
        self._init_rules()
    
    def _init_rules(self):
        """初始化风控规则"""
        risk_config = self.config.get('risk', {})
        
        self.rules = [
            PositionLimitRule(max_pct=risk_config.get('position_limit', 0.2)),
            StopLossRule(loss_pct=risk_config.get('stop_loss', 0.08)),
            MaxDrawdownRule(max_dd=risk_config.get('max_drawdown', 0.15))
        ]
        
        logger.info(f"初始化风控管理器: {len(self.rules)}条规则")
    
    def check(self, portfolio: Portfolio, signal: Signal) -> bool:
        """检查交易信号是否通过风控"""
        for rule in self.rules:
            if not rule.check(portfolio, signal):
                logger.warning(f"风控拦截: {rule.name}")
                return False
        return True
    
    def add_rule(self, rule: RiskRule):
        """添加风控规则"""
        self.rules.append(rule)

"""核心因子集合（30个）"""
import pandas as pd
import numpy as np
from .base import BaseFactor


# ========== 估值因子（4个）==========
class PEFactor(BaseFactor):
    """市盈率因子"""
    def __init__(self):
        super().__init__("PE")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版：使用价格/均线作为PE代理
        return data['close'] / data['close'].rolling(252).mean()


class PBFactor(BaseFactor):
    """市净率因子"""
    def __init__(self):
        super().__init__("PB")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版
        return data['close'] / data['close'].rolling(60).min()


class PSFactor(BaseFactor):
    """市销率因子"""
    def __init__(self):
        super().__init__("PS")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'] / (data['amount'] / data['volume'] + 1e-8)


class PCFFactor(BaseFactor):
    """市现率因子"""
    def __init__(self):
        super().__init__("PCF")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'] / (data['amount'] + 1e-8)


# ========== 质量因子（4个）==========
class ROEFactor(BaseFactor):
    """ROE因子"""
    def __init__(self):
        super().__init__("ROE")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 使用价格涨幅代理
        return data['close'].pct_change(60)


class ROAFactor(BaseFactor):
    """ROA因子"""
    def __init__(self):
        super().__init__("ROA")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(30)


class GrossMarginFactor(BaseFactor):
    """毛利率因子"""
    def __init__(self):
        super().__init__("GrossMargin")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        high_low = data['high'] - data['low']
        close_open = abs(data['close'] - data['open'])
        return (high_low - close_open) / (high_low + 1e-8)


class NetMarginFactor(BaseFactor):
    """净利率因子"""
    def __init__(self):
        super().__init__("NetMargin")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return (data['close'] - data['open']) / (data['open'] + 1e-8)


# ========== 动量因子（3个）==========
class Momentum1MFactor(BaseFactor):
    """1月动量"""
    def __init__(self):
        super().__init__("Momentum_1M")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(20)


class Momentum3MFactor(BaseFactor):
    """3月动量"""
    def __init__(self):
        super().__init__("Momentum_3M")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(60)


class Momentum6MFactor(BaseFactor):
    """6月动量"""
    def __init__(self):
        super().__init__("Momentum_6M")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change(120)


# ========== 波动因子（3个）==========
class VolatilityFactor(BaseFactor):
    """波动率因子"""
    def __init__(self):
        super().__init__("Volatility")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change().rolling(20).std() * np.sqrt(252)


class MaxDrawdownFactor(BaseFactor):
    """最大回撤因子"""
    def __init__(self):
        super().__init__("MaxDrawdown")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        cummax = data['close'].cummax()
        drawdown = (data['close'] - cummax) / cummax
        return drawdown.rolling(60).min()


class BetaFactor(BaseFactor):
    """Beta因子"""
    def __init__(self):
        super().__init__("Beta")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        returns = data['close'].pct_change()
        return returns.rolling(60).mean() / (returns.rolling(60).std() + 1e-8)


# ========== 技术因子（6个）==========
class RSIFactor(BaseFactor):
    """RSI因子"""
    def __init__(self, period: int = 14):
        super().__init__(f"RSI_{period}")
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / (loss + 1e-8)
        return 100 - (100 / (1 + rs))


class MACDFactor(BaseFactor):
    """MACD因子"""
    def __init__(self):
        super().__init__("MACD")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ema12 = data['close'].ewm(span=12).mean()
        ema26 = data['close'].ewm(span=26).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9).mean()
        return (dif - dea) * 2


class MA5Factor(BaseFactor):
    """5日均线因子"""
    def __init__(self):
        super().__init__("MA5")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ma5 = data['close'].rolling(5).mean()
        return (data['close'] - ma5) / (ma5 + 1e-8)


class MA20Factor(BaseFactor):
    """20日均线因子"""
    def __init__(self):
        super().__init__("MA20")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ma20 = data['close'].rolling(20).mean()
        return (data['close'] - ma20) / (ma20 + 1e-8)


class MA60Factor(BaseFactor):
    """60日均线因子"""
    def __init__(self):
        super().__init__("MA60")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ma60 = data['close'].rolling(60).mean()
        return (data['close'] - ma60) / (ma60 + 1e-8)


class BollingerFactor(BaseFactor):
    """布林带因子"""
    def __init__(self):
        super().__init__("Bollinger")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        ma20 = data['close'].rolling(20).mean()
        std20 = data['close'].rolling(20).std()
        upper = ma20 + 2 * std20
        lower = ma20 - 2 * std20
        return (data['close'] - lower) / (upper - lower + 1e-8)


# ========== 资金因子（4个）==========
class TurnoverFactor(BaseFactor):
    """换手率因子"""
    def __init__(self):
        super().__init__("Turnover")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版：成交量/20日均量
        return data['volume'] / (data['volume'].rolling(20).mean() + 1e-8)


class VolumeRatioFactor(BaseFactor):
    """量比因子"""
    def __init__(self):
        super().__init__("VolumeRatio")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['volume'] / (data['volume'].rolling(5).mean() + 1e-8)


class AmountFactor(BaseFactor):
    """成交额因子"""
    def __init__(self):
        super().__init__("Amount")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['amount'] / (data['amount'].rolling(20).mean() + 1e-8)


class CapitalInflowFactor(BaseFactor):
    """资金流入因子"""
    def __init__(self):
        super().__init__("CapitalInflow")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版：上涨日成交量为正
        price_change = data['close'].diff()
        inflow = np.where(price_change > 0, data['volume'], -data['volume'])
        return pd.Series(inflow, index=data.index).rolling(5).sum()


# ========== 情绪因子（3个）==========
class PriceChangeFactor(BaseFactor):
    """涨跌幅因子"""
    def __init__(self):
        super().__init__("PriceChange")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return data['close'].pct_change()


class AmplitudeFactor(BaseFactor):
    """振幅因子"""
    def __init__(self):
        super().__init__("Amplitude")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return (data['high'] - data['low']) / (data['close'] + 1e-8)


class LimitUpFactor(BaseFactor):
    """涨停因子"""
    def __init__(self):
        super().__init__("LimitUp")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        change = data['close'].pct_change()
        return (change > 0.095).astype(float).rolling(20).sum()


# ========== 其他因子（3个）==========
class MarketCapFactor(BaseFactor):
    """市值因子（价格代理）"""
    def __init__(self):
        super().__init__("MarketCap")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        return -np.log(data['close'] + 1e-8)  # 负号表示小市值偏好


class DividendFactor(BaseFactor):
    """股息率因子"""
    def __init__(self):
        super().__init__("Dividend")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版：使用价格稳定性代理
        return 1 / (data['close'].pct_change().rolling(60).std() + 1e-8)


class InstHoldFactor(BaseFactor):
    """机构持仓因子"""
    def __init__(self):
        super().__init__("InstHold")
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 简化版：使用成交量代理
        return data['volume'].rolling(60).mean() / (data['volume'] + 1e-8)


# ========== 因子引擎 ==========
class FactorEngine:
    """因子计算引擎"""
    
    def __init__(self):
        self.factors = self._load_core_factors()
    
    def _load_core_factors(self):
        """加载30个核心因子"""
        return [
            # 估值因子（4个）
            PEFactor(), PBFactor(), PSFactor(), PCFFactor(),
            # 质量因子（4个）
            ROEFactor(), ROAFactor(), GrossMarginFactor(), NetMarginFactor(),
            # 动量因子（3个）
            Momentum1MFactor(), Momentum3MFactor(), Momentum6MFactor(),
            # 波动因子（3个）
            VolatilityFactor(), MaxDrawdownFactor(), BetaFactor(),
            # 技术因子（6个）
            RSIFactor(14), MACDFactor(), MA5Factor(), MA20Factor(), MA60Factor(), BollingerFactor(),
            # 资金因子（4个）
            TurnoverFactor(), VolumeRatioFactor(), AmountFactor(), CapitalInflowFactor(),
            # 情绪因子（3个）
            PriceChangeFactor(), AmplitudeFactor(), LimitUpFactor(),
            # 其他因子（3个）
            MarketCapFactor(), DividendFactor(), InstHoldFactor()
        ]
    
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有因子得分"""
        scores = pd.DataFrame(index=[data.index[-1]])
        
        for factor in self.factors:
            try:
                score = factor.calculate(data)
                if isinstance(score, pd.Series):
                    scores[factor.name] = score.iloc[-1]
                else:
                    scores[factor.name] = score
            except Exception as e:
                scores[factor.name] = 0
        
        return scores
    
    def calculate_batch(self, stock_data: dict) -> pd.DataFrame:
        """批量计算因子"""
        all_scores = []
        
        for code, data in stock_data.items():
            if len(data) < 60:
                continue
            try:
                scores = self.calculate(data)
                scores['code'] = code
                all_scores.append(scores)
            except:
                continue
        
        if len(all_scores) == 0:
            return pd.DataFrame()
        
        return pd.concat(all_scores, ignore_index=True)

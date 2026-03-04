"""AI预测策略"""
import pandas as pd
import numpy as np
from typing import Optional
from .base import BaseStrategy, Signal


class LiteAIPredictStrategy(BaseStrategy):
    """轻量AI预测策略：使用简单模型预测涨跌"""
    
    def __init__(self, config: dict = None):
        super().__init__("AI_Predict", config)
        self.model_path = config.get('model_path', './ai/models/lstm_lite.onnx')
        self.threshold = config.get('threshold', 0.6)
        self.model = None
    
    def _load_model(self):
        """加载ONNX模型"""
        if self.model is None:
            try:
                import onnxruntime as ort
                self.model = ort.InferenceSession(self.model_path)
            except Exception as e:
                print(f"加载AI模型失败: {e}")
                self.model = None
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """准备特征"""
        # 使用简单的技术指标作为特征
        features = []
        
        close = data['close'].values[-20:]  # 最近20天
        
        # 归一化
        close_norm = (close - close.mean()) / (close.std() + 1e-8)
        
        # 计算收益率
        returns = np.diff(close) / (close[:-1] + 1e-8)
        
        # 简单特征
        features.extend([
            close_norm[-1],  # 最新价格
            returns[-1] if len(returns) > 0 else 0,  # 最新收益
            returns.mean() if len(returns) > 0 else 0,  # 平均收益
            returns.std() if len(returns) > 0 else 0,  # 波动率
            (close[-1] - close.mean()) / close.std() if close.std() > 0 else 0,  # z-score
        ])
        
        return np.array(features).reshape(1, -1).astype(np.float32)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Signal]:
        """分析股票数据"""
        if len(data) < 30:
            return None
        
        latest = data.iloc[-1]
        code = latest.get('ts_code', '')
        
        # 准备特征
        features = self._prepare_features(data)
        
        # 简单规则预测（如果没有模型）
        if self.model is None:
            # 使用简单规则：趋势向上则买入
            ma5 = data['close'].rolling(5).mean().iloc[-1]
            ma20 = data['close'].rolling(20).mean().iloc[-1]
            
            if ma5 > ma20 * 1.02:  # 短期均线突破长期均线
                return Signal(
                    code=code,
                    action='buy',
                    price=latest['close'],
                    confidence=0.55,
                    reason="AI趋势预测：上升趋势"
                )
        else:
            # 使用模型预测
            try:
                prediction = self.model.run(None, {'input': features})[0][0][0]
                
                if prediction > self.threshold:
                    return Signal(
                        code=code,
                        action='buy',
                        price=latest['close'],
                        confidence=prediction,
                        reason=f"AI模型预测上涨概率: {prediction:.2%}"
                    )
            except Exception as e:
                print(f"模型预测失败: {e}")
        
        return Signal(code=code, action='hold', price=latest['close'])
